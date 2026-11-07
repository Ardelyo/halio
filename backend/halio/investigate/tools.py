"""Where candidate pages come from. Every tool returns plain dicts and never raises: a dead source is a blind spot, not a crash.

    search(query)     Google Search through Gemini grounding (evidence.gemini_discover)
    sensor(claim)     our own archive of public news / fact-check feeds (realtime, ingest/)
    claimreview(q)    Google Fact Check Tools: every ClaimReview, any rating (needs GOOGLE_FACTCHECK_API_KEY)
    gdelt(q)          GDELT DOC 2.0 article list (multilingual news; its time window is not guaranteed)
    wayback_first(u)  the Internet Archive's first capture of a URL (CDX API)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime

import httpx

from ..config import Settings
from ..textnorm import tokens

log = logging.getLogger(__name__)
UA = {"User-Agent": "HalioTelusur/0.1 (riset anti-disinformasi; hanya sumber publik)"}


def _distinct(text: str, n: int = 6) -> list[str]:
    """The claim's most specific words, longest first: what an index search should look for."""
    seen: list[str] = []
    for t in sorted(tokens(text), key=len, reverse=True):
        if len(t) >= 4 and t not in seen:
            seen.append(t)
    return seen[:n]


@dataclass
class Toolbox:
    cfg: Settings

    def search(self, query: str) -> list[dict]:
        from ..evidence import gemini_discover

        try:
            found, _ = gemini_discover(query, self.cfg)
        except Exception as exc:  # model or quota: this query becomes a blind spot
            log.warning("search unavailable for a query: %s", type(exc).__name__)
            return []
        return [{"uri": f["uri"], "title": f.get("title", ""), "via": "google"} for f in found]

    def sensor(self, claim: str, limit: int = 15) -> list[dict]:
        want = set(tokens(claim))
        if len(want) < 3:
            return []
        try:
            from ..ingest.store import SensorStore

            rows = SensorStore(self.cfg.db_path).search_items(_distinct(claim, 4), limit=400)
        except Exception as exc:
            log.info("sensor archive unavailable: %s", type(exc).__name__)
            return []
        scored = []
        for r in rows:
            shared = len(want & set(tokens(r["title"])))
            if shared >= 2 and shared / len(want) >= 0.3:
                scored.append((shared / len(want), r))
        scored.sort(key=lambda x: -x[0])
        return [{"uri": r["url"], "title": r["title"], "via": "sensor", "seen": (r.get("published") or r.get("first_seen") or "")[:10],
                 "source_id": r["source_id"]} for _, r in scored[:limit]]

    def archive(self, claim: str, limit: int = 8) -> list[dict]:
        """Fact-check articles about a very similar claim (archive.py): leads that the evidence engine will open."""
        from .. import archive

        try:
            hits = archive.search(claim, self.cfg, k=limit, floor=0.28)
        except Exception as exc:
            log.info("archive unavailable: %s", type(exc).__name__)
            return []
        return [{"uri": m.debunk.sumber[0]["url"], "title": m.debunk.klaim, "via": "arsip",
                 "seen": m.debunk.sumber[0].get("tanggal", ""), "mirip": m.score} for m in hits]

    def claimreview(self, query: str) -> list[dict]:
        key = self.cfg.google_factcheck_key
        if not key:
            return []
        try:
            resp = httpx.get("https://factchecktools.googleapis.com/v1alpha1/claims:search",
                             params={"query": query[:200], "pageSize": 10, "key": key}, timeout=8)
            resp.raise_for_status()
            claims = resp.json().get("claims", [])
        except (httpx.HTTPError, ValueError) as exc:
            log.warning("ClaimReview unavailable: %s", type(exc).__name__)
            return []
        out = []
        for c in claims:
            for r in c.get("claimReview", [])[:1]:
                url = r.get("url", "")
                if url.startswith("https://"):
                    out.append({"uri": url, "title": r.get("title") or c.get("text", ""), "via": "claimreview",
                                "klaim": c.get("text", ""), "penilaian": r.get("textualRating", ""),
                                "penerbit": (r.get("publisher") or {}).get("name") or (r.get("publisher") or {}).get("site", ""),
                                "tanggal": (r.get("reviewDate") or c.get("claimDate") or "")[:10]})
        return out

    def gdelt(self, claim: str, limit: int = 40) -> list[dict]:
        words = _distinct(claim, 4)
        if len(words) < 2:
            return []
        try:
            resp = httpx.get("https://api.gdeltproject.org/api/v2/doc/doc", headers=UA, timeout=12, params={
                "query": " ".join(words), "mode": "artlist", "format": "json", "maxrecords": limit, "sort": "dateasc"})
            resp.raise_for_status()
            arts = resp.json().get("articles", []) if resp.text.strip().startswith("{") else []
        except (httpx.HTTPError, ValueError) as exc:
            log.info("GDELT unavailable: %s", type(exc).__name__)
            return []
        out = []
        for a in arts:
            url, seen = a.get("url", ""), a.get("seendate", "")
            if url.startswith("https://"):
                d = f"{seen[:4]}-{seen[4:6]}-{seen[6:8]}" if len(seen) >= 8 else ""
                out.append({"uri": url, "title": a.get("title", ""), "via": "gdelt", "seen": d, "domain": a.get("domain", "")})
        return out

    def reverse_image(self, image: tuple[bytes, str]) -> dict:
        from .reverse_image import web_detection

        return web_detection(image[0], self.cfg)

    def wayback_first(self, url: str) -> str:
        """ISO date of the first archived capture, or ''."""
        try:
            resp = httpx.get("https://web.archive.org/cdx/search/cdx", headers=UA, timeout=8,
                             params={"url": url, "output": "json", "limit": 1, "fl": "timestamp", "filter": "statuscode:200"})
            rows = resp.json() if resp.status_code == 200 and resp.text.strip().startswith("[") else []
        except (httpx.HTTPError, ValueError):
            return ""
        if len(rows) >= 2 and rows[1] and len(rows[1][0]) >= 8:
            ts = rows[1][0]
            try:
                return date(int(ts[:4]), int(ts[4:6]), int(ts[6:8])).isoformat()
            except ValueError:
                return ""
        return ""


def today_iso() -> str:
    return datetime.now().date().isoformat()
