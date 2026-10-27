"""Pick the check-worthy sentence(s) out of a long forwarded message.

Halio only checks verifiable factual claims, never opinions (docs/PRIVACY.md,
"aturan netral topik"). This is a transparent heuristic, not a trained model;
its limits are reported in eval/RESULTS.md.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .pii import scrub
from .textnorm import fold, tokens

_SENT_SPLIT = re.compile(r"(?<=[.!?…])\s+|\n+")

CLAIM_CUES = {
    "akan", "telah", "sudah", "resmi", "membagikan", "dibagikan", "bantuan", "terjadi",
    "menyebabkan", "menyembuhkan", "mengobati", "obat", "dibuka", "pendaftaran", "gratis",
    "gempa", "tsunami", "meninggal", "korban", "penculik", "penculikan", "virus", "vaksin",
    "presiden", "menteri", "tni", "polri", "bmkg", "kemenkes", "pemerintah", "dijamin",
    "lulus", "hadiah", "kuota", "saldo", "transfer", "biaya", "persen", "ribu", "juta",
    "miliar", "tanggal", "terbukti", "ditemukan", "mengandung", "dilarang", "wajib",
    "harga", "naik", "turun", "lipat", "ditutup", "dibuka", "ditangkap", "diblokir",
    "memblokir", "menang", "kalah", "mencatat", "diprediksi", "prediksi",
}
OPINION_CUES = (
    "menurut saya", "menurutku", "saya rasa", "aku rasa", "kayaknya", "semoga",
    "selamat pagi", "selamat siang", "selamat malam", "assalamualaikum", "amin",
    "salam sehat", "terima kasih", "mohon maaf",
)


@dataclass
class Claim:
    text: str          # scrubbed, <= 300 chars
    score: float       # check-worthiness 0..1
    is_factual: bool


def sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENT_SPLIT.split(text) if len(s.strip()) > 3]


def checkworthiness(sentence: str) -> float:
    low = fold(sentence)
    if sentence.strip().endswith("?") and not re.search(r"\d", sentence):
        return 0.05
    toks = tokens(sentence)
    if not toks:
        return 0.0
    score = 0.0
    score += min(0.45, 0.15 * sum(t in CLAIM_CUES for t in toks))
    if re.search(r"\d", sentence):
        score += 0.2
    # Mid-sentence capitalised words ~ named entities.
    if re.search(r"(?<=\s)[A-Z][a-z]{2,}", sentence):
        score += 0.15
    if len(toks) >= 5:
        score += 0.15
    if any(cue in low for cue in OPINION_CUES):
        score -= 0.4
    return max(0.0, min(1.0, score))


def extract(text: str, max_sentences: int = 2) -> Claim:
    """Return the most check-worthy part of the message, scrubbed of PII."""
    sents = sentences(text) or [text]
    scored = sorted(((checkworthiness(s), i, s) for i, s in enumerate(sents)), reverse=True)
    top = sorted(scored[:max_sentences], key=lambda x: x[1])  # keep original order
    best = scored[0][0]
    chosen = " ".join(s for sc, _, s in top if sc >= max(0.2, best * 0.5)) or scored[0][2]
    return Claim(text=scrub(chosen), score=best, is_factual=best >= 0.3)
