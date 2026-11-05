"""The check pipeline: message in, evidence-bounded verdict out.

    claim extraction -> PII scrub -> T1 retrieval (local corpus + ClaimReview)
    -> optional T2 grounded LLM -> verdict + voice script + manipulation hints

Verdict states (never a bare "TRUE/FALSE" from the model):
    terbukti_salah          a named fact-checker/official source already debunked it
    sejalan_dengan_sumber   current official evidence supports the whole claim, with AI grounding
    tidak_yakin             evidence is incomplete, conflicting, expired, or only topically related
    belum_ada_pemeriksaan   no fact-check exists yet; Halio refuses to guess
"""

from __future__ import annotations

import uuid
from datetime import date, datetime

from . import claims, factcheck_api, google_agent, link_check, llm_verdict, manipulation
from .config import Settings
from .pii import extract_domains
from .retrieval import Match, get_index, is_correction
from .store import WIB

STATUS_LABEL = {
    "terbukti_salah": "Terbukti salah",
    "sejalan_dengan_sumber": "Sejalan dengan sumber",
    "tidak_yakin": "Halio tidak yakin",
    "belum_ada_pemeriksaan": "Belum ada pemeriksaan",
}

SHORTENERS = {"bit.ly", "s.id", "cutt.ly", "tinyurl.com", "shorturl.at", "rb.gy", "t.ly", "linktr.ee", "wa.me"}
# Only domains a scammer cannot register. .ac.id / .sch.id are run by thousands of schools and get hijacked.
OFFICIAL_SUFFIXES = (".go.id", ".mil.id")

DISCLAIMER = "Halio tidak membuat vonis sendiri. Hasil ini berasal dari pemeriksa fakta atau sumber resmi yang disebutkan."


def _link_warnings(domains: list[str]) -> list[str]:
    warnings = []
    for d in domains:
        # d is the parsed hostname, so "kemensos.go.id.bansos.xyz" or "x.go.id?.xyz" does not pass.
        if d.endswith(OFFICIAL_SUFFIXES):
            continue
        if d in SHORTENERS:
            warnings.append(f"Tautan {d} menyembunyikan alamat aslinya. Jangan diklik sebelum tahu tujuannya.")
        else:
            warnings.append(f"Tautan {d} bukan situs pemerintah (.go.id). Hati-hati bila diminta mengisi data.")
    return warnings


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


def _voice(status: str, reason: str, sapaan: str, match: Match | None, manip: dict) -> str:
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


def check(text: str, cfg: Settings, sapaan: str = "Bapak, Ibu") -> dict:
    claim = claims.extract(text)
    manip = manipulation.analyze(text)
    domains = extract_domains(text)

    index = get_index(cfg.corpus_path)
    candidates = index.search(claim.text, k=3)
    method = ["lokal"]
    if cfg.google_factcheck_key:
        remote = factcheck_api.search(claim.text, cfg.google_factcheck_key)
        if remote:
            method.append("claimreview")
            candidates = sorted(candidates + remote, key=lambda m: m.score, reverse=True)[:3]

    best = candidates[0] if candidates else None
    correction = is_correction(text)
    if best and best.score >= cfg.unsure_threshold and correction and not best.debunk.is_positive:
        # It warns about or corrects the hoax ("itu hoaks", "BMKG membantah"): never call that a hoax.
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
    if cfg.llm_enabled and cfg.llm_provider == "google" and claim.is_factual:
        seed_urls = [
            source["url"]
            for candidate in candidates
            for source in candidate.debunk.sumber
            if source.get("jenis") in {"resmi", "cek_fakta"}
        ][:3]
        agent = google_agent.investigate(claim.text, cfg, seed_urls=seed_urls)
        # A named, curated debunk stays when the web search is down or finds nothing new; only verified
        # conflicting evidence may lower it (see the final branch below).
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
            # For a debunk the LLM may confirm, or lift a "mirip" case, but never past the core-claim
            # guard or a correction. Positive evidence keeps its own gate below.
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
        # Any later stage (web agent, LLM) may only confirm a hoax, never turn a warning into one.
        status, reason = "tidak_yakin", "tampak_meluruskan"

    checked_links = link_check.check_links(text) if cfg.link_check_enabled else []
    shown = best if status != "belum_ada_pemeriksaan" and reason != "bukan_klaim_faktual" else None
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
        "reading": (llm_note or {}).get("bacaan", {"items": [], "disaring": 0}),
        "manipulation": manip,
        "links": {"domains": domains, "warnings": _all_link_warnings(domains, checked_links), "checked": checked_links},
        "voice_script": _voice(status, reason, sapaan, shown, manip),
        "offer_human_review": status not in {"terbukti_salah", "sejalan_dengan_sumber"},
        "method": "+".join(method),
        "disclaimer": DISCLAIMER,
    }
