"""T2: grounded LLM judgement over retrieved debunks (optional, HALIO_LLM=1).

The model never produces a verdict from its own knowledge. It may only say
whether the user's claim is the same claim as one of the retrieved debunks,
and must quote the debunk text it relied on. The quote is checked as an exact
substring; any failure falls back to "tidak yakin".
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass

from .retrieval import Match

log = logging.getLogger(__name__)

SYSTEM = (
    "Kamu adalah pemeriksa kecocokan klaim untuk Halio, alat cek hoaks keluarga Indonesia. "
    "Kamu TIDAK menilai benar/salah dari pengetahuanmu sendiri. Tugasmu hanya memutuskan apakah "
    "klaim pengguna adalah klaim yang SAMA dengan salah satu kandidat bantahan yang diberikan. "
    "Jika ragu, atau klaim hanya mirip topiknya, pilih 'tidak_cukup_bukti'. "
    "Kutipan harus disalin persis, kata per kata, dari teks 'fakta' kandidat yang kamu pilih. "
    "Penjelasan ditulis untuk orang tua berusia 60-an: maksimal dua kalimat pendek, sopan, tanpa istilah teknis."
)

SCHEMA = {
    "type": "object",
    "properties": {
        "relasi": {"type": "string", "enum": ["sama", "berbeda", "tidak_cukup_bukti"]},
        "kandidat_id": {"type": ["string", "null"]},
        "kutipan": {"type": "string"},
        "penjelasan": {"type": "string"},
    },
    "required": ["relasi", "kandidat_id", "kutipan", "penjelasan"],
    "additionalProperties": False,
}


@dataclass
class LlmJudgement:
    relation: str            # sama | berbeda | tidak_cukup_bukti
    debunk_id: str | None
    quote: str
    explanation: str
    grounded: bool


def judge(claim: str, candidates: list[Match], model: str) -> LlmJudgement | None:
    """Return a grounded judgement, or None if the LLM is unavailable."""
    try:
        import anthropic
    except ImportError:
        log.warning("HALIO_LLM=1 but the 'anthropic' package is not installed")
        return None

    cands = [
        {"id": m.debunk.id, "klaim_yang_dibantah": m.debunk.klaim, "fakta": m.debunk.fakta}
        for m in candidates
    ]
    prompt = (
        f"Klaim pengguna:\n<klaim>{claim}</klaim>\n\n"
        f"Kandidat bantahan (JSON):\n{json.dumps(cands, ensure_ascii=False, indent=2)}"
    )

    client = anthropic.Anthropic()
    try:
        response = client.beta.messages.create(
            model=model,
            max_tokens=2048,
            system=SYSTEM,
            messages=[{"role": "user", "content": prompt}],
            output_config={"effort": "medium", "format": {"type": "json_schema", "schema": SCHEMA}},
            betas=["server-side-fallback-2026-07-01"],
            fallbacks="default",
        )
    except anthropic.RateLimitError:
        log.warning("LLM rate limited; falling back to retrieval-only verdict")
        return None
    except anthropic.APIStatusError as exc:
        log.warning("LLM API error %s; falling back", exc.status_code)
        return None
    except anthropic.APIConnectionError:
        log.warning("LLM unreachable; falling back")
        return None

    if response.stop_reason in ("refusal", "max_tokens"):
        log.warning("LLM stopped with %s; falling back", response.stop_reason)
        return None

    text = next((b.text for b in response.content if b.type == "text"), "")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None

    chosen = next((m for m in candidates if m.debunk.id == data.get("kandidat_id")), None)
    quote = data.get("kutipan", "").strip()
    grounded = bool(chosen and quote and quote in chosen.debunk.fakta)
    return LlmJudgement(
        relation=data["relasi"] if grounded or data["relasi"] != "sama" else "tidak_cukup_bukti",
        debunk_id=chosen.debunk.id if chosen else None,
        quote=quote,
        explanation=data.get("penjelasan", ""),
        grounded=grounded,
    )
