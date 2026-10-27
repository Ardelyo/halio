"""Prebunking layer: name the manipulation *technique*, not the topic.

Flags techniques (urgency, fake authority, chain-forward pressure, ...) with a
plain-language explanation and a 30-second lesson. Topic-neutral by design, so
it never judges political opinion. Keep in sync with extension/lexicon.js.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass

from .textnorm import fold


@dataclass(frozen=True)
class Technique:
    id: str
    label: str
    explain: str
    lesson: str
    patterns: tuple[str, ...]


TECHNIQUES: tuple[Technique, ...] = (
    Technique(
        "ajakan_sebar", "Desakan untuk menyebarkan",
        "Pesan ini menyuruh Anda meneruskannya. Info yang benar tidak perlu memaksa.",
        "Pesan yang berbunyi 'sebarkan!' atau 'jangan berhenti di Anda' sedang memakai Anda sebagai pengantar. Berhenti dulu, cek dulu.",
        (r"\bsebar(kan|luaskan)?\b", r"\bviral(kan)?\b", r"\bteruskan\b", r"\bbagikan\b",
         r"jangan berhenti di", r"kirim(kan)? ke \d+", r"\bshare\b", r"broadcast"),
    ),
    Technique(
        "urgensi", "Dibuat terburu-buru",
        "Pesan ini membuat Anda merasa harus bertindak sekarang juga.",
        "Penipu ingin Anda bergerak sebelum berpikir. Batas waktu palsu seperti 'hari ini terakhir' adalah tanda bahaya.",
        (r"\bsegera\b", r"sekarang juga", r"\bburuan\b", r"hari ini terakhir", r"batas (waktu|akhir)",
         r"\bcepat\b", r"terbatas", r"\b(hanya|cuma) \d+ (jam|hari)"),
    ),
    Technique(
        "otoritas_palsu", "Mengaku dari orang penting",
        "Pesan ini mengaku berasal dari pejabat, dokter, atau 'orang dalam' tanpa sumber yang bisa dicek.",
        "Kalimat 'info dari teman di kepolisian' atau 'kata dokter' tanpa nama dan tautan resmi tidak bisa dipercaya begitu saja.",
        (r"info (a1|valid|dari dalam)", r"orang dalam", r"kata (dokter|intel|teman)",
         r"(dari|menurut) (grup|teman) sebelah", r"sumber terpercaya", r"info dari (polda|polres|kodim|kodam|mabes)",
         r"\bresmi dari\b"),
    ),
    Technique(
        "rasa_takut", "Menakut-nakuti",
        "Pesan ini memakai rasa takut agar Anda tidak sempat berpikir jernih.",
        "Rasa takut membuat kita cepat percaya. Kata seperti 'waspada', 'bahaya', atau 'penculik' perlu dicek ke sumber resmi.",
        (r"\bwaspada\b", r"\bbahaya\b", r"\bawas\b", r"mematikan", r"penculik", r"\bdarurat\b",
         r"\bmencekam\b", r"tsunami besar", r"gempa besar"),
    ),
    Technique(
        "iming_iming", "Iming-iming hadiah",
        "Pesan ini menjanjikan uang, hadiah, atau kelulusan dengan mudah.",
        "Kalau terdengar terlalu bagus untuk jadi kenyataan, biasanya memang tidak nyata. Bantuan resmi tidak meminta biaya.",
        (r"\bgratis\b", r"\bhadiah\b", r"bantuan (tunai|langsung|sosial)", r"\bbansos\b", r"dijamin lulus",
         r"kuota \d+ ?gb", r"saldo", r"\bbonus\b", r"rp ?\d"),
    ),
    Technique(
        "minta_data_uang", "Meminta data atau uang",
        "Pesan ini meminta data pribadi, kode OTP, atau transfer uang.",
        "Lembaga resmi tidak pernah meminta kode OTP, PIN, atau 'biaya administrasi' lewat chat. Jangan isi tautan yang meminta data.",
        (r"biaya (admin|administrasi|pendaftaran)", r"\btransfer\b", r"kode otp", r"\botp\b", r"\bpin\b",
         r"isi (data|formulir)", r"klik (link|tautan)", r"\bnik\b", r"nomor rekening"),
    ),
)

_COMPILED = [(t, [re.compile(p) for p in t.patterns]) for t in TECHNIQUES]


def _shouting(text: str) -> bool:
    letters = [c for c in text if c.isalpha()]
    caps_ratio = sum(c.isupper() for c in letters) / max(1, len(letters))
    return (len(letters) > 30 and caps_ratio > 0.6) or "!!!" in text


def analyze(text: str) -> dict:
    low = fold(text)
    found = []
    for tech, patterns in _COMPILED:
        hits = sorted({m.group(0) for p in patterns for m in p.finditer(low)})
        if hits:
            d = asdict(tech)
            d.pop("patterns")
            d["evidence"] = hits[:3]
            found.append(d)
    shouting = _shouting(text)
    score = min(1.0, 0.25 * len(found) + (0.15 if shouting else 0.0))
    return {"techniques": found, "shouting": shouting, "score": round(score, 2), "needs_check": score >= 0.5}
