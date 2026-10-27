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


def search(query: str, api_key: str, limit: int = 5, timeout: float = 4.0) -> list[Match]:
    try:
        resp = httpx.get(
            ENDPOINT,
            params={"query": query, "languageCode": "id", "pageSize": limit, "key": api_key},
            timeout=timeout,
        )
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        log.warning("Fact Check API unavailable: %s", exc)
        return []

    debunks = []
    for i, claim in enumerate(resp.json().get("claims", [])):
        reviews = [r for r in claim.get("claimReview", []) if any(w in r.get("textualRating", "").lower() for w in FALSE_RATINGS)]
        if not reviews:
            continue
        r = reviews[0]
        publisher = r.get("publisher", {}).get("name") or r.get("publisher", {}).get("site", "Pemeriksa fakta")
        debunks.append(
            Debunk(
                id=f"claimreview-{i}",
                kategori="claimreview",
                klaim=claim.get("text", ""),
                varian=[],
                fakta=f"{publisher} menilai klaim ini: {r.get('textualRating')}. {r.get('title', '')}".strip(),
                sederhana=f"Pemeriksa fakta {publisher} sudah memeriksa ini dan menilainya {r.get('textualRating', '').lower()}.",
                sumber=[{"nama": publisher, "url": r.get("url", ""), "jenis": "cek_fakta"}],
            )
        )
    if not debunks:
        return []
    # Re-score with our own similarity so remote hits obey the same threshold.
    return Index(debunks).search(query, k=limit)
