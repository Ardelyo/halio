"""Links that open the source page with the copied sentence highlighted (the browser's "text fragment" feature).

A link such as  https://site/article#:~:text=Brigjen%20Wahyu%20memastikan,harus%20membayar  opens the page, scrolls to that
sentence and marks it. It turns "the quote was copied from the page by code" from a claim into something the user sees.

Rules of the syntax we respect: the start and end of the match are given as `start,end` (so a long sentence is matched by its first and
last words, and everything in between must be contiguous text), and the characters  , - &  must be percent-encoded.
Chrome and Edge support it; browsers that do not simply open the page without a highlight (the plain link still works).
"""

from __future__ import annotations

from urllib.parse import quote, urlparse, urlunparse

START_WORDS = 6
END_WORDS = 6
MIN_WORDS_FOR_RANGE = START_WORDS + END_WORDS + 2   # kutipan pendek langsung dicocokin utuh semua katanya


def _enc(text: str) -> str:
    # quote() bawaan Python ngebiarin tanda "-", padahal aturan text fragment wajibin "-", ",", sm "&" ikut di-encode
    return quote(text, safe="").replace("-", "%2D")


def fragment_url(url: str, quotation: str) -> str:
    """`url` with a text fragment pointing at `quotation`; the original url if it cannot be done safely."""
    words = " ".join((quotation or "").replace("…", " ").split()).split(" ")
    words = [w for w in words if w]
    if len(words) < 3 or not url.startswith(("http://", "https://")):
        return url
    parts = urlparse(url)
    # bersihin fragment lama di URL sebelum nempel sorotan kutipan baru
    base = urlunparse(parts._replace(fragment=""))
    if len(words) >= MIN_WORDS_FOR_RANGE:
        # kl kalimatnya panjang cukup pasang potongan kata awal & akhir biar URL ga kepanjangan
        spec = f"{_enc(' '.join(words[:START_WORDS]))},{_enc(' '.join(words[-END_WORDS:]))}"
    else:
        spec = _enc(" ".join(words))
    return f"{base}#:~:text={spec}"
