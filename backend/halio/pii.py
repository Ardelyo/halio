"""Strip personal data before a claim is processed, stored, or sent to any API.

Privacy rule (docs/PRIVACY.md): only the scrubbed claim text (max 300 chars)
ever leaves the device or reaches a third-party service.
"""

from __future__ import annotations

import re
from urllib.parse import urlsplit

MAX_CLAIM_CHARS = 300

_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # NIK: 16 digits, optionally grouped.
    (re.compile(r"\b\d{2}[\s.-]?\d{2}[\s.-]?\d{2}[\s.-]?\d{6}[\s.-]?\d{4}\b"), "[NIK]"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"), "[EMAIL]"),
    # Indonesian phone numbers: +62 / 62 / 08 prefixes.
    # Also "+62 812-3456-7890", "(0812) 3456 7890", "0812 345 678 90".
    (re.compile(r"(?:\+?62[\s.-]?|\(?0)8\d{1,3}\)?(?:[\s.-]?\d{2,5}){2,3}\b"), "[NOMOR]"),
    # Bank account style numbers (10-15 digits) left after the above.
    (re.compile(r"\b\d{10,15}\b"), "[REKENING]"),
    # @mentions identify private accounts.
    (re.compile(r"(?<!\w)@\w{3,}"), "[AKUN]"),
]

_URL = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
# Bare links people type without a scheme: "bit.ly/abc", "bansos-kemensos.xyz/daftar".
_BARE = re.compile(
    r"(?<![\w@.-])((?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+(?:id|com|net|org|xyz|info|site|online|top|ly|me|io|co|click|link|biz|ee|at|gl))"
    r"(?=[/:?#]|\s|$|[.,)!])", re.IGNORECASE)

_BARE_WITH_PATH = re.compile(_BARE.pattern + r"(?:[/?#]\S*)?", re.IGNORECASE)


def _host(url: str) -> str:
    if not re.match(r"^https?://", url, re.IGNORECASE):
        url = "http://" + url
    host = (urlsplit(url).hostname or "").lower().rstrip(".")
    return host.removeprefix("www.")


def extract_domains(text: str) -> list[str]:
    """Hostnames of every link, with or without http:// (query, fragment and port ignored)."""
    domains = []
    for url in _URL.findall(text):
        host = _host(url.rstrip(".,)!?"))
        if host and host not in domains:
            domains.append(host)
    for m in _BARE.finditer(_URL.sub(" ", text)):
        host = m.group(1).lower().removeprefix("www.")
        if host not in domains:
            domains.append(host)
    return domains


def scrub(text: str, max_chars: int = MAX_CLAIM_CHARS) -> str:
    """Remove URLs and personal identifiers, collapse whitespace, truncate."""
    out = _URL.sub("[TAUTAN]", text)
    out = _BARE_WITH_PATH.sub("[TAUTAN]", out)
    for pattern, repl in _PATTERNS:
        out = pattern.sub(repl, out)
    out = re.sub(r"\s+", " ", out).strip()
    if len(out) > max_chars:
        out = out[: max_chars - 1].rsplit(" ", 1)[0] + "…"
    return out
