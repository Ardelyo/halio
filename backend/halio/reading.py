"""Reading list: pages the web search found, each really opened by our code.

These are background reading, NOT evidence for the verdict. Only official and fact-check pages whose text was
matched by code can change a verdict (source_verifier / google_agent). Dead links, soft-404 pages and pages that
block automated checks are filtered out, so a user is never sent to an error page.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from . import outlets
from .link_check import check_link

# urutan prioritas daftar bacaan: utamain situs resmi & pemeriksa fakta di paling atas
KIND_LABEL = {"resmi": "Situs resmi", "cek_fakta": "Pemeriksa fakta", "media": "Media / situs lain"}
ORDER = {"resmi": 0, "cek_fakta": 1, "media": 2}


def build(grounding: list[dict], limit: int = 5, max_check: int = 8) -> dict:
    cands = [g for g in grounding if g.get("uri")][:max_check]
    if not cands:
        return {"items": [], "disaring": 0}
    # buka paralel semua kandidat link biar user ga pernah dikasih tautan mati atau soft-404
    with ThreadPoolExecutor(max_workers=len(cands)) as pool:
        checked = list(pool.map(lambda g: check_link(g["uri"]), cands))
    items, seen = [], set()
    for g, c in zip(cands, checked):
        # halaman mesin pencari / redirect cuma perantara bukan sumber bacaan (link grounding yg mentok biasanya nyangkut di situ)
        if c["state"] != "terbuka" or c["final_url"] in seen or outlets.is_not_a_source(c["final_url"]):
            continue
        seen.add(c["final_url"])
        kind = c["kind"] or "media"
        name = c.get("outlet") or c.get("site_name") or c["final_host"].removeprefix("www.")
        items.append({
            "title": c["title"] or name,
            "url": c["final_url"], "host": c["final_host"], "kind": kind,
            "kind_label": name if kind == "media" else f"{KIND_LABEL[kind]}: {name}",
        })
    # urutin dari tingkat sumber yg paling otoritatif sebelum dipotong sesuai limit
    items.sort(key=lambda i: ORDER[i["kind"]])
    return {"items": items[:limit], "disaring": len(cands) - len(items)}
