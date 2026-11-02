"""T1 remote: Google Fact Check Tools (ClaimReview) lookup.

Optional; enabled when GOOGLE_FACTCHECK_API_KEY is set. Indonesian coverage is
unverified (docs/PROJECT_PLAN.md risk R2), so results are merged with the local
corpus and still have to clear the same similarity threshold.
"""

from __future__ import annotations

import logging

import httpx

from .retrieval import Debunk, Index, Match

log = logging.getLogger(__name__)

ENDPOINT = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
FALSE_RATINGS = ("salah", "hoaks", "hoax", "keliru", "palsu", "menyesatkan", "false", "misleading", "fake", "disinformasi")


def is_false_rating(value: object) -> bool:
    if not isinstance(value, str):
        return False
    rating = value.strip().lower()
    if any(negated in rating for negated in ("tidak salah", "bukan hoaks", "bukan hoax", "not false", "not a hoax")):
        return False
    return any(word in rating for word in FALSE_RATINGS)


def search(query: str, api_key: str, limit: int = 5, timeout: float = 4.0) -> list[Match]:
    try:
        resp = httpx.get(
            ENDPOINT,
            params={"query": query, "languageCode": "id", "pageSize": limit, "key": api_key},
            timeout=timeout,
        )
        resp.raise_for_status()
        payload = resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        log.warning("Fact Check API unavailable: %s", type(exc).__name__)
        return []

    debunks = []
    for i, claim in enumerate(payload.get("claims", [])):
        if not isinstance(claim, dict) or not claim.get("text"):
            continue
        reviews = [r for r in claim.get("claimReview", []) if isinstance(r, dict) and is_false_rating(r.get("textualRating"))]
        if not reviews:
            continue
        r = reviews[0]
        url = r.get("url", "")
        if not isinstance(url, str) or not url.startswith(("https://", "http://")):
            continue
        publisher = r.get("publisher", {}).get("name") or r.get("publisher", {}).get("site")
        if not publisher:
            continue
        debunks.append(
            Debunk(
                id=f"claimreview-{i}",
                kategori="claimreview",
                klaim=claim["text"],
                varian=[],
                fakta=f"{publisher} menilai klaim ini: {r.get('textualRating')}. {r.get('title', '')}".strip(),
                sederhana=f"Pemeriksa fakta {publisher} sudah memeriksa ini dan menilainya {r.get('textualRating', '').lower()}.",
                sumber=[{"nama": publisher, "url": url, "jenis": "cek_fakta"}],
            )
        )
    if not debunks:
        return []
    # Re-score with our own similarity so remote hits obey the same threshold.
    return Index(debunks).search(query, k=limit)
