"""Strip personal data before a claim is processed, stored, or sent to any API.

Privacy rule (docs/PRIVACY.md): only the scrubbed claim text (max 300 chars)
ever leaves the device or reaches a third-party service.
"""

from __future__ import annotations

import re

MAX_CLAIM_CHARS = 300

_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # NIK: 16 digits in any grouping (6-6-4, 4-4-4-4, contiguous).
    (re.compile(r"\b(?:\d[\s.-]?){15}\d\b"), "[NIK]"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[EMAIL]"),
    # Indonesian phone numbers: +62 / 62 / 08 prefixes, with or without separators.
    (re.compile(r"(?:\+?62[\s.-]?|\b0)8\d{1,3}[\s.-]?\d{3,4}[\s.-]?\d{3,5}"), "[NOMOR]"),
    # Bank account style numbers (10-15 digits) left after the above.
    (re.compile(r"\b\d{10,15}\b"), "[REKENING]"),
    # @mentions identify private accounts.
    (re.compile(r"(?<!\w)@\w{3,}"), "[AKUN]"),
]

_URL = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)


def extract_domains(text: str) -> list[str]:
    domains = []
    for url in _URL.findall(text):
        host = re.sub(r"^(https?://)?(www\.)?", "", url, flags=re.IGNORECASE).split("/")[0].lower()
        host = host.rstrip(".,)!?")
        if host and host not in domains:
            domains.append(host)
    return domains


def scrub(text: str, max_chars: int = MAX_CLAIM_CHARS) -> str:
    """Remove URLs and personal identifiers, collapse whitespace, truncate."""
    out = _URL.sub("[TAUTAN]", text)
    for pattern, repl in _PATTERNS:
        out = pattern.sub(repl, out)
    out = re.sub(r"\s+", " ", out).strip()
    if len(out) > max_chars:
        out = out[: max_chars - 1].rsplit(" ", 1)[0] + "…"
    return out
