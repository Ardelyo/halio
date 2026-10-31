"""The check pipeline: message in, honest three-state verdict out.

    claim extraction -> PII scrub -> T1 retrieval (local corpus + ClaimReview)
    -> optional T2 grounded LLM -> verdict + voice script + manipulation hints

Verdict states (never a bare "TRUE/FALSE" from the model):
    terbukti_salah         a named fact-checker/official source already debunked it
    tidak_yakin            looks related but not the same claim, or not a factual claim
    belum_ada_pemeriksaan  no fact-check exists yet; Halio refuses to guess
"""

from __future__ import annotations

import uuid
from datetime import datetime

from . import claims, factcheck_api, llm_verdict, manipulation
from .config import Settings
from .pii import extract_domains
from .retrieval import Match, get_index
from .store import WIB

STATUS_LABEL = {
    "terbukti_salah": "Terbukti salah",
    "tidak_yakin": "Halio tidak yakin",
    "belum_ada_pemeriksaan": "Belum ada pemeriksaan",
}

SHORTENERS = {"bit.ly", "s.id", "cutt.ly", "tinyurl.com", "shorturl.at", "rb.gy", "t.ly", "linktr.ee", "wa.me"}
OFFICIAL_SUFFIXES = (".go.id", ".mil.id", ".polri.go.id", ".ac.id", ".sch.id")

DISCLAIMER = "Halio tidak membuat vonis sendiri. Hasil ini berasal dari pemeriksa fakta atau sumber resmi yang disebutkan."


def _link_warnings(domains: list[str]) -> list[str]:
    warnings = []
    for d in domains:
        if d in SHORTENERS:
            warnings.append(f"Tautan {d} menyembunyikan alamat aslinya. Jangan diklik sebelum tahu tujuannya.")
        elif not d.endswith(OFFICIAL_SUFFIXES):
            warnings.append(f"Tautan {d} bukan situs pemerintah (.go.id). Hati-hati bila diminta mengisi data.")
    return warnings


def _match_payload(m: Match) -> dict:
    d = m.debunk
    return {
        "debunk_id": d.id, "kategori": d.kategori, "score": m.score,
        "klaim_dibantah": d.klaim, "fakta": d.fakta, "sederhana": d.sederhana, "sumber": d.sumber,
    }


def _voice(status: str, sapaan: str, match: Match | None, manip: dict) -> str:
    if status == "terbukti_salah" and match:
        src = match.debunk.sumber[0]["nama"].split(":")[0]
        return (
            f"{sapaan}, pesan ini sudah dicek dan ternyata tidak benar. {match.debunk.sederhana} "
            f"Sumbernya dari {src}. Sebaiknya jangan diteruskan, ya."
        )
    if status == "tidak_yakin" and match:
        return (
            f"{sapaan}, Halio belum yakin. Pesan ini mirip dengan kabar bohong yang pernah beredar, "
            f"tapi tidak sama persis. Lebih aman ditahan dulu. Kalau mau, Halio bisa tanyakan ke pemeriksa manusia."
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
    if not claim.is_factual and (not best or best.score < cfg.match_threshold):
        status, reason = "tidak_yakin", "bukan_klaim_faktual"
    elif best and best.score >= cfg.match_threshold and not best.debunk.core_present(text):
        # Same topic, but the core of the false claim is missing or negated.
        status, reason = "tidak_yakin", "inti_klaim_tidak_ada"
    elif best and best.score >= cfg.match_threshold:
        status, reason = "terbukti_salah", "cocok_dengan_bantahan"
    elif best and best.score >= cfg.unsure_threshold:
        status, reason = "tidak_yakin", "mirip_tapi_tidak_sama"
    else:
        status, reason = "belum_ada_pemeriksaan", "tidak_ada_bantahan"

    llm_note = None
    if cfg.llm_enabled and best and best.score >= cfg.unsure_threshold:
        j = llm_verdict.judge(claim.text, candidates, cfg.llm_model)
        if j is not None:
            method.append("llm")
            if j.relation == "sama" and j.grounded:
                best = next(m for m in candidates if m.debunk.id == j.debunk_id)
                status, reason = "terbukti_salah", "cocok_dikonfirmasi_llm"
                llm_note = {"kutipan": j.quote, "penjelasan": j.explanation}
            elif status == "terbukti_salah":
                # LLM could not ground the match: downgrade, never upgrade without a quote.
                status, reason = "tidak_yakin", "llm_tidak_dapat_membuktikan"

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
        "manipulation": manip,
        "links": {"domains": domains, "warnings": _link_warnings(domains)},
        "voice_script": _voice(status, sapaan, shown, manip),
        "offer_human_review": status != "terbukti_salah",
        "method": "+".join(method),
        "disclaimer": DISCLAIMER,
    }
