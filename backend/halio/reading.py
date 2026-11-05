"""Reading list: pages the web search found, each really opened by our code.

These are background reading, NOT evidence for the verdict. Only official and fact-check pages whose text was
matched by code can change a verdict (source_verifier / google_agent). Dead links, soft-404 pages and pages that
block automated checks are filtered out, so a user is never sent to an error page.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from .link_check import check_link

KIND_LABEL = {"resmi": "Situs resmi", "cek_fakta": "Pemeriksa fakta", "media": "Media / situs lain"}
ORDER = {"resmi": 0, "cek_fakta": 1, "media": 2}


def build(grounding: list[dict], limit: int = 5, max_check: int = 8) -> dict:
    cands = [g for g in grounding if g.get("uri")][:max_check]
    if not cands:
        return {"items": [], "disaring": 0}
    with ThreadPoolExecutor(max_workers=len(cands)) as pool:
        checked = list(pool.map(lambda g: check_link(g["uri"]), cands))
    items, seen = [], set()
    for g, c in zip(cands, checked):
        if c["state"] != "terbuka" or c["final_url"] in seen:
            continue
        seen.add(c["final_url"])
        kind = c["kind"] or "media"
        items.append({
            "title": c["title"] or g.get("title") or c["final_host"],
            "url": c["final_url"], "host": c["final_host"], "kind": kind, "kind_label": KIND_LABEL[kind],
        })
    items.sort(key=lambda i: ORDER[i["kind"]])
    return {"items": items[:limit], "disaring": len(cands) - len(items)}
