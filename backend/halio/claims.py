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

# kata-kata pemicu yg biasanya muncul di klaim faktual vs basa-basi/opini grup WA
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
    text: str          # udah dibersihin dari data pribadi (PII), maksmal 300 karakter
    score: float       # skor kelayakan cek 0..1
    is_factual: bool


def sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENT_SPLIT.split(text) if len(s.strip()) > 3]


def checkworthiness(sentence: str) -> float:
    low = fold(sentence)
    # kalimat tanya murni tanpa angka biasanya cuma nanya kabar, bukan klaim
    if sentence.strip().endswith("?") and not re.search(r"\d", sentence):
        return 0.05
    toks = tokens(sentence)
    if not toks:
        return 0.0
    score = 0.0
    score += min(0.45, 0.15 * sum(t in CLAIM_CUES for t in toks))
    if re.search(r"\d", sentence):
        score += 0.2
    # kata huruf besar di tengah kalimat biasanya nama orang, tempat, atau instansi
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
    top = sorted(scored[:max_sentences], key=lambda x: x[1])  # urutin balik sesuai urutan kalimat aslinya
    best = scored[0][0]
    chosen = " ".join(s for sc, _, s in top if sc >= max(0.2, best * 0.5)) or scored[0][2]
    # wajib sikat dulu nomor HP/NIK dkk sebelum teks klaim dipake ke tahap berikutnya
    return Claim(text=scrub(chosen), score=best, is_factual=best >= 0.3)


def _same(a: str, b: str) -> bool:
    ta, tb = set(tokens(a)), set(tokens(b))
    return bool(ta and tb) and len(ta & tb) / len(ta | tb) >= 0.6


def split_units(text: str, max_units: int = 3, min_score: float = 0.5, min_tokens: int = 5) -> list[str]:
    """Split a message into separate claims, each with the sentences that belong to it. Empty unless there are at least two.

    A claim is a check-worthy sentence (score >= min_score, long enough); a near-duplicate of an earlier one is the same claim.
    The sentences after a claim, up to the next claim, stay attached to it ("Pendaftaran lewat WhatsApp" belongs to the
    handout claim before it), because the core-claim guard needs that context. A message whose only check-worthy sentence
    is one claim, however long, is not split.
    """
    sents = sentences(text)
    marks: list[int] = []
    for i, s in enumerate(sents):
        if checkworthiness(s) >= min_score and len(tokens(s)) >= min_tokens and not any(_same(s, sents[j]) for j in marks):
            marks.append(i)
    if len(marks) < 2:
        return []  # kl cuma satu klaim ga usah dipecah
    marks = marks[:max_units]
    units = []
    for k, start in enumerate(marks):
        end = marks[k + 1] if k + 1 < len(marks) else len(sents)
        units.append(" ".join(sents[start:end]))
    return units
