"""Who does the message say said it, versus whom the matching debunk is about?

Retrieval matches on WHAT is claimed ("a big quake on a given date"). A scammer or a prankster swaps WHO supposedly said it
("according to PMI" instead of "according to BMKG"). The verdict on the content can still be right, but the user must be told
that the named source differs, and an official-source "sejalan" must not stay green when the message names someone else.
"""

from __future__ import annotations

import re

from .textnorm import fold

# canonical name -> pattern (matched on folded text, whole words)
ORGS = {
    "BMKG": r"bmkg|badan meteorologi",
    "BNPB": r"bnpb|badan nasional penanggulangan bencana",
    "PMI": r"pmi|palang merah",
    "WHO": r"who|organisasi kesehatan dunia",
    "Kemenkes": r"kemenkes|kementerian kesehatan",
    "Kemensos": r"kemensos|kementerian sosial",
    "Komdigi": r"komdigi|kominfo|kementerian komunikasi",
    "TNI": r"tni|tentara nasional",
    "Polri": r"polri|kepolisian",
    "BPOM": r"bpom|badan pom",
    "OJK": r"ojk|otoritas jasa keuangan",
    "BI": r"bank indonesia",
    "BPJS": r"bpjs",
    "KPU": r"kpu|komisi pemilihan umum",
    "Presiden": r"presiden|prabowo|jokowi",
    "Pemerintah": r"pemerintah",
}
_COMPILED = {name: re.compile(rf"\b(?:{pat})\b") for name, pat in ORGS.items()}


def orgs_in(text: str) -> set[str]:
    low = fold(text)
    found = {name for name, rx in _COMPILED.items() if rx.search(low)}
    # "Pemerintah" is generic: only count it when nothing more specific is named.
    return found - {"Pemerintah"} if found - {"Pemerintah"} else found


def mismatch(message: str, debunk_text: str) -> dict | None:
    said, covered = orgs_in(message), orgs_in(debunk_text)
    if not said or not covered or said & covered:
        return None
    a, b = ", ".join(sorted(said)), ", ".join(sorted(covered))
    return {
        "pesan": sorted(said), "bantahan": sorted(covered),
        "catatan": (
            f"Pesan ini menyebut {a} sebagai sumber, sedangkan bantahan yang cocok membahas klaim serupa yang dikaitkan dengan {b}. "
            f"Mencatut nama lembaga adalah trik yang umum. Periksa langsung ke kanal resmi {a}."
        ),
    }
