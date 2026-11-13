"""The check pipeline: message in, evidence-bounded verdict out.

    claim extraction -> PII scrub -> T1 retrieval (local corpus + ClaimReview)
    -> optional T2 grounded LLM -> verdict + voice script + manipulation hints

Verdict states (never a bare "TRUE/FALSE" from the model):
    terbukti_salah          a named fact-checker/official source already debunked it
    sejalan_dengan_sumber   current official evidence supports the whole claim, with AI grounding
    dilaporkan_media        independent outlets report it and nobody refutes it: reporting, NOT a fact-check
    tidak_yakin             evidence is incomplete, conflicting, expired, or only topically related
    belum_ada_pemeriksaan   no fact-check exists yet; Halio refuses to guess
"""

from __future__ import annotations

import re
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime

from . import archive, attribution, claims, evidence, factcheck_api, google_agent, link_check, llm_verdict, manipulation
from .config import Settings
from .dates import human_date
from .pii import extract_domains
from .retrieval import Match, get_index, is_correction
from .store import WIB
from .textnorm import tokens

STATUS_LABEL = {
    "terbukti_salah": "Terbukti salah",
    "sejalan_dengan_sumber": "Sejalan dengan sumber",
    "dilaporkan_media": "Dilaporkan media",
    "tidak_yakin": "Halio tidak yakin",
    "belum_ada_pemeriksaan": "Belum ada pemeriksaan",
}

SHORTENERS = {"bit.ly", "s.id", "cutt.ly", "tinyurl.com", "shorturl.at", "rb.gy", "t.ly", "linktr.ee", "wa.me"}
# cuma masukin domain negara yg ga bisa didaftarin umum; .ac.id / .sch.id sengaja ga masuk krn sering kena deface/bajak
OFFICIAL_SUFFIXES = (".go.id", ".mil.id")

# jenis hasil yg sifatnya cuma ngasih info isi halaman (bukan rumor buat divonis), jadi ga perlu kartu koreksi / tombol sanggah
PLAIN_KINDS = {"berita_media_dikenal", "kumpulan_judul"}

DISCLAIMER = "Halio tidak membuat vonis sendiri. Hasil ini berasal dari pemeriksa fakta atau sumber resmi yang disebutkan."


def _link_warnings(domains: list[str]) -> list[str]:
    warnings = []
    for d in domains:
        # d udah berupa hostname murni hasil parse, jadi trik tipuan kayak "kemensos.go.id.bansos.xyz" ga bakal lolos
        if d.endswith(OFFICIAL_SUFFIXES):
            continue
        if d in SHORTENERS:
            warnings.append(f"Tautan {d} menyembunyikan alamat aslinya. Jangan diklik sebelum tahu tujuannya.")
        else:
            warnings.append(f"Tautan {d} bukan situs pemerintah (.go.id). Hati-hati bila diminta mengisi data.")
    return warnings


_URL = re.compile(r"https?://\S+", re.I)
_TITLE_TAIL = re.compile(r"\s+[-|–—]\s+[^-|–—]{2,40}$")


def _clean_title(title: str) -> str:
    """'Judul berita - detikNews' -> 'Judul berita'."""
    out = _TITLE_TAIL.sub("", title.strip())
    return out if len(out) >= 12 else title.strip()


def _describe(c: dict) -> dict:
    """What an opened page says about itself: who published it, the headline, the date, its own summary."""
    return {
        "penerbit": c.get("outlet") or c.get("site_name") or c.get("final_host", ""),
        "grup": c.get("outlet_group", ""),
        "judul": _clean_title(c.get("title", "")),
        "terbit": (c.get("published") or "")[:10],
        "ringkasan": (c.get("description") or "")[:260],
        "url": c.get("final_url", ""),
        "dikenal": bool(c.get("outlet")),
    }


def _kind_and_info(text: str, checked: list[dict], manip: dict) -> tuple[str, dict | None]:
    """pesan | berita_media | kumpulan_judul.

    'berita_media': the message is essentially a link to an article of a known outlet. Such a message is not a rumour
    to be judged; the useful answer is what the article is. A message that also pushes urgency, money or "share this"
    stays an ordinary message and is judged as one.
    """
    pushy = len(manip["techniques"]) >= 2
    for c in checked:
        if c["state"] != "terbuka" or not c.get("outlet") or pushy:
            continue
        rest = _URL.sub(" ", text)
        want = set(tokens(_clean_title(c["title"])))
        overlap = len(want & set(tokens(rest))) / len(want) if want else 0
        if overlap >= 0.5 or len(rest.split()) <= 40:
            return "berita_media", _describe(c)
    if not _URL.search(text):
        lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
        short = [ln for ln in lines if len(ln.split()) <= 12 and not ln.endswith((".", "?", "!"))]
        if len(lines) >= 3 and len(short) >= 0.8 * len(lines):
            return "kumpulan_judul", {"judul_list": lines[:8]}
    return "pesan", None


# urutan prioritas kl satu pesan memuat beberapa klaim sekaligus: tampilin status yg paling perlu diwaspadai di atas
_SEVERITY = ["terbukti_salah", "tidak_yakin", "belum_ada_pemeriksaan", "dilaporkan_media", "sejalan_dengan_sumber"]
_SHORT = {
    "terbukti_salah": "sudah dibantah", "tidak_yakin": "belum bisa dipastikan", "belum_ada_pemeriksaan": "belum ada yang memeriksa",
    "dilaporkan_media": "dilaporkan beberapa media", "sejalan_dengan_sumber": "sejalan dengan sumber resmi",
}


def _check_many(text: str, units: list[str], cfg: Settings, sapaan: str, manip: dict, domains: list[str]) -> dict:
    """One answer per claim. The message-level status is the most worrying of them, so the card, Radar and buttons still make sense."""
    with ThreadPoolExecutor(max_workers=len(units)) as pool:
        subs = list(pool.map(lambda u: check(u, cfg, sapaan, _depth=1), units))
    lead = min(subs, key=lambda r: _SEVERITY.index(r["status"]))
    n = len(subs)
    parts = "; ".join(f"klaim {i}: {_SHORT[r['status']]}" for i, r in enumerate(subs, 1))
    top = dict(lead)
    top.update({
        "id": uuid.uuid4().hex,
        "reason": "beberapa_klaim",
        "manipulation": manip,
        "links": {"domains": domains, "warnings": [], "checked": []},
        "claims": [{k: r.get(k) for k in ("claim", "status", "status_label", "reason", "match", "evidence", "kind", "info")} for r in subs],
        "voice_script": f"{sapaan}, pesan ini berisi {n} klaim yang berbeda. {parts.capitalize()}. Halio menjawab satu per satu di bawah.",
        "offer_human_review": any(r["offer_human_review"] for r in subs),
        "method": "+".join(dict.fromkeys(m for r in subs for m in r["method"].split("+"))),
    })
    return top


def _apply_evidence(ev, claim: str, status: str, reason: str, best):
    """Merge the v2 decision with what the curated corpus already said. A curated debunk is only lowered by conflicting evidence."""
    curated_false = status == "terbukti_salah"
    lead = next((i for i in ev.items if i["tingkat"] in "AB" and i["hubungan"] in ("refutes", "supports")), None)
    if ev.status == "terbukti_salah" and lead:
        return "terbukti_salah", ev.reason, evidence.match_from(lead, claim, positive=False)
    if ev.status in ("sejalan_dengan_sumber", "dilaporkan_media"):
        if curated_false:
            return "tidak_yakin", "bukti_bertentangan", best
        if ev.status == "sejalan_dengan_sumber" and lead:
            return ev.status, ev.reason, evidence.match_from(lead, claim, positive=True)
        return ev.status, ev.reason, best
    if ev.status == "tidak_yakin":
        if (curated_false and ev.reason == "bukti_bertentangan") or status == "belum_ada_pemeriksaan":
            return "tidak_yakin", ev.reason, best
        return status, reason, best
    # kl penelusuran web ga nemu bukti penentu, pertahanin status awal sambil tetep ngasih alasan hasil cari web
    return (status, ev.reason, best) if status == "belum_ada_pemeriksaan" else (status, reason, best)


_HOAX_TITLE = re.compile(r"hoa[xk]s?|tidak benar|keliru|disinformasi|penipuan|bohong|\bsalah\b", re.I)


def _factcheck_warns(reading: dict) -> bool:
    return any(i["kind"] == "cek_fakta" and _HOAX_TITLE.search(i["title"]) for i in reading.get("items", []))


def _search_links(claim: str) -> list[dict]:
    """Plain search pages (they cannot be dead links) so the user always has a next step."""
    from urllib.parse import quote_plus

    q = quote_plus(" ".join(claim.split())[:140])
    return [
        {"nama": "Cari beritanya di Google", "url": f"https://www.google.com/search?q={q}"},
        {"nama": "Cari di Google dengan kata \"hoaks\" / \"cek fakta\"", "url": f"https://www.google.com/search?q={q}+hoaks+OR+%22cek+fakta%22"},
        {"nama": "Cari di TurnBackHoax", "url": f"https://turnbackhoax.id/?s={q}"},
    ]


def _all_link_warnings(domains: list[str], checked: list[dict]) -> list[str]:
    if not checked:
        return _link_warnings(domains)
    out = [w for w in map(link_check.warning_for, checked) if w]
    seen = {c["host"] for c in checked}
    return out + _link_warnings([d for d in domains if d not in seen])


def _match_payload(m: Match) -> dict:
    d = m.debunk
    return {
        "debunk_id": d.id, "kategori": d.kategori, "score": m.score,
        "klaim_dibantah": d.klaim, "fakta": d.fakta, "sederhana": d.sederhana, "sumber": d.sumber,
        "jenis": d.jenis, "kutipan_sumber": d.kutipan_sumber,
        "valid_from": d.valid_from, "valid_until": d.valid_until, "wilayah": d.wilayah,
    }


def _positive_evidence_reason(
    match: Match,
    candidates: list[Match],
    judgement: llm_verdict.LlmJudgement,
    today: date,
    threshold: float,
) -> str | None:
    d = match.debunk
    source = d.sumber[0] if d.sumber else {}
    if match.score < threshold:
        return "kandidat_kurang_cocok"
    if source.get("jenis") != "resmi" or not source.get("nama") or not source.get("url", "").startswith("https://"):
        return "sumber_bukan_resmi"
    if (
        not judgement.quote
        or not d.kutipan_sumber
        or d.kutipan_sumber not in d.fakta
        or judgement.quote not in d.kutipan_sumber
    ):
        return "kutipan_sumber_tidak_cocok"
    if not d.is_current(today):
        return "sumber_belum_berlaku" if d.valid_from and d.valid_from > today.isoformat() else "sumber_kedaluwarsa"
    if any(m.debunk.id != d.id and m.score >= threshold for m in candidates):
        return "bukti_bertentangan"
    return None


def _voice(status: str, reason: str, sapaan: str, match: Match | None, manip: dict, info: dict | None = None, alasan: str = "") -> str:
    if status == "dilaporkan_media":
        return (
            f"{sapaan}, kabar ini dilaporkan oleh beberapa media yang berbeda. Ini pelaporan, bukan pemeriksaan fakta: "
            f"belum ada pemeriksa fakta yang memastikannya. Boleh dibagikan dengan menyebut sumbernya, tetapi cek tanggal dan bandingkan dulu."
        )
    if reason in ("satu_media_melaporkan", "laporan_media_tanpa_tanggal_baru", "tidak_ada_sumber_relevan", "media_melaporkan_bantahan") and alasan:
        tail = (" Itu belum berarti pasti salah, tetapi belum ada dasar untuk meneruskannya. Cek tautan bacaan dan pencarian yang Halio sertakan."
                if reason == "tidak_ada_sumber_relevan" else " Halio belum bisa memastikan benar atau salahnya.")
        return f"{sapaan}, {alasan[0].lower() + alasan[1:] if not alasan.startswith('Halio') else alasan}{tail}"
    if reason == "berita_media_dikenal" and info:
        tgl = f" pada {human_date(info['terbit'])}" if info.get("terbit") else ""
        return (
            f"{sapaan}, ini artikel dari {info['penerbit']}{tgl}. Halio belum menemukan pemeriksa fakta yang membahasnya, "
            f"dan itu wajar untuk berita biasa. Halio belum menilai isinya. Untuk hal yang penting, bandingkan dengan satu atau dua media lain."
        )
    if reason == "kumpulan_judul":
        return (
            f"{sapaan}, gambar ini berisi beberapa judul berita sekaligus. Kirim satu judul atau satu berita per pesan, "
            f"supaya Halio bisa memeriksanya satu per satu."
        )
    if status == "terbukti_salah" and match:
        src = match.debunk.sumber[0]["nama"].split(":")[0]
        return (
            f"{sapaan}, pesan ini sudah dicek dan ternyata tidak benar. {match.debunk.sederhana} "
            f"Sumbernya dari {src}. Sebaiknya jangan diteruskan, ya."
        )
    if status == "sejalan_dengan_sumber" and match:
        src = match.debunk.sumber[0]["nama"].split(":")[0]
        return (
            f"{sapaan}, isi pesan ini sejalan dengan keterangan dari {src}. {match.debunk.sederhana} "
            f"Tetap cek tanggal dan konteksnya sebelum diteruskan."
        )
    if status == "tidak_yakin" and match and reason == "tampak_meluruskan":
        return (
            f"{sapaan}, pesan ini tampaknya justru memperingatkan soal kabar bohong, bukan menyebarkannya. "
            f"Yang sudah dicek: {match.debunk.sederhana}"
        )
    if status == "tidak_yakin" and match and reason == "inti_klaim_tidak_ada" and not match.debunk.is_positive:
        # topiknya mirip hoaks lama, tp bagian bohong intinya (bayar admin, link palsu, tanggalnya) ga ada di pesan ini.
        # seringnya malah info beneran, jadi jgn disuruh tahan seolah-olah ini hoaksnya.
        return (
            f"{sapaan}, topik pesan ini sama dengan kabar bohong yang pernah beredar, tetapi pesan ini tidak memuat bagian "
            f"yang bohong itu. Halio belum memeriksa isinya lebih jauh. Yang sudah dicek: {match.debunk.sederhana}"
        )
    if status == "tidak_yakin" and match:
        topic = "informasi dari sumber resmi" if match.debunk.is_positive else "kabar bohong yang pernah beredar"
        return (
            f"{sapaan}, Halio belum yakin. Pesan ini mirip dengan {topic}, "
            f"tapi buktinya belum cukup. Lebih aman ditahan dulu. Kalau mau, Halio bisa tanyakan ke pemeriksa manusia."
        )
    if status == "tidak_yakin":
        return (
            f"{sapaan}, pesan ini lebih mirip pendapat atau salam, bukan kabar yang bisa dicek benar atau salahnya. "
            f"Halio tidak menilai pendapat orang."
        )
    trick = ""
    if manip["techniques"]:
        trick = f" Tapi hati-hati: {manip['techniques'][0]['explain']}"
    return (
        f"{sapaan}, belum ada pemeriksa fakta yang memeriksa pesan ini, jadi Halio tidak mau menebak.{trick} "
        f"Sebaiknya jangan diteruskan dulu. Halio bisa tanyakan ke pemeriksa manusia."
    )


def _search_sentences(index, claim_text: str, k: int = 3, min_tokens: int = 5) -> list:
    """Score the claim as a whole AND each of its sentences, keeping each debunk's best score.

    A scam line followed by a call to action ("... transfer 75 juta ke orang dalam Kodam. Hubungi Pak Budi segera.") dilutes
    the whole-claim score below the threshold. Every guard (correction, core claim, negation) still runs on the full message,
    so this only changes how well a matching sentence is recognised. Eval: 0 false accusations on both sets before and after.
    """
    best = {m.debunk.id: m for m in index.search(claim_text, k=len(index.debunks))}
    parts = [p for p in claims.sentences(claim_text) if len(tokens(p)) >= min_tokens]
    if len(parts) >= 2:
        for part in parts:
            for m in index.search(part, k=len(index.debunks)):
                if m.debunk.id not in best or m.score > best[m.debunk.id].score:
                    best[m.debunk.id] = m
    return sorted(best.values(), key=lambda m: m.score, reverse=True)[:k]


def check(text: str, cfg: Settings, sapaan: str = "Bapak, Ibu", _depth: int = 0) -> dict:
    claim = claims.extract(text)
    manip = manipulation.analyze(text)
    domains = extract_domains(text)

    checked_links = link_check.check_links(text) if cfg.link_check_enabled else []
    kind, info = _kind_and_info(text, checked_links, manip)

    index = get_index(cfg.corpus_path)
    candidates = _search_sentences(index, claim.text)
    method = ["lokal"]
    if cfg.google_factcheck_key:
        remote = factcheck_api.search(claim.text, cfg.google_factcheck_key)
        if remote:
            method.append("claimreview")
            candidates = sorted(candidates + remote, key=lambda m: m.score, reverse=True)[:3]

    best = candidates[0] if candidates else None
    if kind == "kumpulan_judul" and ((best and best.score >= cfg.unsure_threshold) or manip["techniques"]):
        # pesan berantai hoaks juga kadang diketik baris pendek-pendek; baru anggap kumpulan judul kl bersih dari cocok & manipulasi
        kind, info = "pesan", None
    if kind == "pesan" and _depth == 0 and not _URL.search(text):
        units = claims.split_units(text)
        # dua kalimat yg baru keliatan cocok sm hoaks pas digabung ("bagi uang lewat video!" + "daftar WA bayar admin") itu satu klaim utuh;
        # kl dipecah malah skor tiap potongannya jadi lemah. kl emang ada klaim lain yg terpisah tetep dipecah.
        if len(units) >= 2 and best and best.score >= cfg.match_threshold and not best.debunk.is_positive \
                and best.debunk.core_present(text) and not is_correction(text):
            alone = [next((m.score for m in _search_sentences(index, u) if m.debunk.id == best.debunk.id), 0.0) for u in units]
            if max(alone) < cfg.match_threshold:
                units = []
        if len(units) >= 2:
            return _check_many(text, units, cfg, sapaan, manip, domains)
    correction = is_correction(text)
    # jgn disentuh kl blm ngopi, urutan prioritas penentuan vonis di bawah ini krusial bgt biar ga salah tuduh
    if best and best.score >= cfg.unsure_threshold and correction and not best.debunk.is_positive:
        # pesannya lagi ngingetin/ngelurusin hoaks ("awas itu hoaks", "BMKG membantah"), jangan malah dicap hoaks!
        status, reason = "tidak_yakin", "tampak_meluruskan"
    elif not claim.is_factual and (not best or best.score < cfg.match_threshold):
        status, reason = "tidak_yakin", "bukan_klaim_faktual"
    elif best and best.score >= cfg.match_threshold and best.debunk.is_positive:
        status, reason = "tidak_yakin", "memerlukan_verifikasi_ai"
    elif best and best.score >= cfg.match_threshold and not best.debunk.core_present(text):
        status, reason = "tidak_yakin", "inti_klaim_tidak_ada"
    elif best and best.score >= cfg.match_threshold:
        status, reason = "terbukti_salah", "cocok_dengan_bantahan"
    elif best and best.score >= cfg.unsure_threshold:
        status, reason = "tidak_yakin", "mirip_tapi_tidak_sama"
    else:
        status, reason = "belum_ada_pemeriksaan", "tidak_ada_bantahan"

    llm_note = None
    evidence_out = None
    engine_fallback = False
    # khusus link artikel media biasa atau tangkapan kumpulan judul ga usah nyalain agen web,
    # soalnya cuma bakal buang waktu 30 detik demi hasil "0 terverifikasi".
    if cfg.llm_enabled and cfg.llm_provider == "google" and claim.is_factual and kind == "pesan":
        seed_urls = [
            source["url"]
            for candidate in candidates
            for source in candidate.debunk.sumber
            if source.get("jenis") in {"resmi", "cek_fakta"}
        ][:3]
        # tambahan petunjuk awal dari arsip judul cek fakta yg mirip: cuma disodorin sbg URL buat dibuka & dikutip mesin bukti,
        # arsipnya sendiri ga pernah langsung mutusin vonis.
        seed_urls += [m.debunk.sumber[0]["url"] for m in archive.search(claim.text, cfg, k=3) if m.debunk.sumber[0]["url"] not in seed_urls]
        ev = evidence.investigate_v2(claim.text, cfg, seed_urls=seed_urls) if cfg.evidence_engine == "v2" else None
        if ev is not None:
            method.append("bukti_v2")
            evidence_out = evidence.as_dict(ev)
            status, reason, best = _apply_evidence(ev, claim.text, status, reason, best)
            agent = None
        else:
            # jalanin mesin v1 kl disetel HALIO_ENGINE=v1 atau pas pencarian/penilaian v2 lagi gangguan
            engine_fallback = cfg.evidence_engine == "v2"
            agent = google_agent.investigate(claim.text, cfg, seed_urls=seed_urls)
        # bantahan dari korpus kurasi tetep dipertahanin kl pencarian web mati atau ga nemu apa-apa;
        # cuma bukti terverifikasi yg bertentangan yg boleh nurunin statusnya.
        if agent is not None:
            method.append("gemini_search")
            llm_note = agent.note
            if agent.match:
                best = agent.match
            if agent.status == "sejalan_dengan_sumber" and agent.judgement:
                gate = _positive_evidence_reason(
                    best, [best], agent.judgement, datetime.now(WIB).date(), cfg.match_threshold
                )
                status = "sejalan_dengan_sumber" if gate is None else "tidak_yakin"
                reason = gate or agent.reason
            elif agent.status == "terbukti_salah":
                status, reason = agent.status, agent.reason
            elif agent.match or (status == "terbukti_salah" and agent.reason == "bukti_bertentangan"):
                status, reason = "tidak_yakin", agent.reason
    elif cfg.llm_enabled and cfg.llm_provider == "anthropic" and best and best.score >= cfg.unsure_threshold:
        j = llm_verdict.judge(claim.text, candidates, cfg.llm_model)
        if j is not None:
            method.append("llm")
            hit = next((m for m in candidates if m.debunk.id == j.debunk_id), None)
            # LLM boleh nguatin bantahan atau ngangkat kasus "mirip", tp ga boleh ngelompatin penjaga inti klaim
            # atau pesan klarifikasi. klaim positif tetep wajib lewat gerbang cek tersendiri di bawah.
            liftable = bool(hit) and (
                hit.debunk.is_positive
                or status == "terbukti_salah"
                or (reason == "mirip_tapi_tidak_sama" and hit.debunk.core_present(text))
            )
            if j.relation == "sama" and j.grounded and hit and liftable:
                best = hit
                llm_note = {"kutipan": j.quote, "penjelasan": j.explanation}
                if best.debunk.is_positive:
                    gate = _positive_evidence_reason(
                        best, candidates, j, datetime.now(WIB).date(), cfg.match_threshold
                    )
                    status = "sejalan_dengan_sumber" if gate is None else "tidak_yakin"
                    reason = gate or "cocok_dengan_sumber_resmi"
                else:
                    status, reason = "terbukti_salah", "cocok_dikonfirmasi_llm"
            elif status == "terbukti_salah" or reason == "memerlukan_verifikasi_ai":
                status, reason = "tidak_yakin", "llm_tidak_dapat_membuktikan"

    if correction and status == "terbukti_salah" and not (best and best.debunk.is_positive):
        # pengaman berlapis: tahap web agent / LLM ga boleh ngubah pesan peringatan hoaks jadi divonis hoaks
        status, reason = "tidak_yakin", "tampak_meluruskan"

    if status == "belum_ada_pemeriksaan" and kind == "berita_media":
        reason = "berita_media_dikenal"
    elif kind == "kumpulan_judul" and status != "terbukti_salah":
        status, reason = "belum_ada_pemeriksaan", "kumpulan_judul"

    shown = best if status not in ("belum_ada_pemeriksaan", "dilaporkan_media") and reason != "bukan_klaim_faktual" else None
    reading_out = (evidence_out or {}).get("bacaan") or (llm_note or {}).get("bacaan", {"items": [], "disaring": 0})
    if status == "sejalan_dengan_sumber" and _factcheck_warns(reading_out):
        # kl di daftar bacaan ada pemeriksa fakta yg ngebahas topik ini sbg hoaks, jgn kasih lampu hijau biar ga nyesatin
        status, reason = "tidak_yakin", "pemeriksa_fakta_membahas_topik_ini"
    attrib = None
    if shown is not None:
        d = shown.debunk
        attrib = attribution.mismatch(text, f"{d.klaim} {d.fakta} {d.sederhana}")
        if attrib and status == "sejalan_dengan_sumber":
            # situs resmi cuma ngedukung pernyataan lembaganya sendiri; kl pesan user nyatut nama lembaga lain, tahan jangan hijau
            status, reason = "tidak_yakin", "sumber_berbeda_dari_pesan"
    check_id = uuid.uuid4().hex
    return {
        "id": check_id,
        "created": datetime.now(WIB).isoformat(timespec="seconds"),
        "status": status,
        "status_label": STATUS_LABEL[status],
        "reason": reason,
        "claim": claim.text,
        "checkworthiness": round(claim.score, 2),
        "match": _match_payload(shown) if shown else None,
        "llm": llm_note,
        "evidence": evidence_out,
        "engine_fallback": engine_fallback,
        "reading": reading_out,
        "cari_sendiri": _search_links(claim.text) if status in ("belum_ada_pemeriksaan", "tidak_yakin") else [],
        "attribution": attrib,
        "manipulation": manip,
        "links": {"domains": domains, "warnings": _all_link_warnings(domains, checked_links), "checked": checked_links},
        "kind": kind,
        "info": info,
        "voice_script": _voice(status, reason, sapaan, shown, manip, info, (evidence_out or {}).get("alasan", "")),
        "offer_human_review": status not in {"terbukti_salah", "sejalan_dengan_sumber"} and reason not in PLAIN_KINDS,
        "method": "+".join(method),
        "disclaimer": DISCLAIMER,
    }
