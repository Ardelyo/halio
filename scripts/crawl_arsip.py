"""Collect fact-check HEADLINES and links from turnbackhoax.id's public listing into data/arsip.jsonl.

    python scripts/crawl_arsip.py --pages 150           # about 1,500 newest articles, ~5 minutes

Polite by design: robots.txt allows it (checked 7 Nov 2026), one request every --delay seconds, an identifying User-Agent, and only
the headline, link and listing metadata are stored (no article text). Keep it that way: Mafindo's terms of use were not found, so
for anything beyond a demo ask Mafindo for a data partnership. The file is not committed (see .gitignore).
"""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from halio.archive import says_false  # noqa: E402

UA = "HalioSensor/0.1 (riset anti-disinformasi; hanya judul dan tautan publik; kontak: lihat github.com/Ardelyo/halio)"
CARD = re.compile(r'<a href="(https://turnbackhoax\.id/articles/(\d+)-[^"]+)"[^>]*>\s*<img[^>]*alt="([^"]+)"', re.S)
OUT = ROOT / "data" / "arsip.jsonl"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=150)
    ap.add_argument("--start", type=int, default=1, help="first listing page; resume a longer crawl here")
    ap.add_argument("--delay", type=float, default=2.0)
    args = ap.parse_args()

    have = set()
    if OUT.exists():
        have = {json.loads(line)["url"] for line in OUT.read_text(encoding="utf-8").splitlines() if line.strip()}
    added = kept_false = 0
    with httpx.Client(headers={"User-Agent": UA}, timeout=25, follow_redirects=True) as client, OUT.open("a", encoding="utf-8") as out:
        for page in range(args.start, args.start + args.pages):
            try:
                r = client.get("https://turnbackhoax.id/articles", params={"page": page})
            except httpx.HTTPError as exc:
                print(f"page {page}: {type(exc).__name__}, stopping")
                break
            if r.status_code != 200:
                print(f"page {page}: HTTP {r.status_code}, stopping")
                break
            cards = CARD.findall(r.text)
            if not cards:
                print(f"page {page}: no articles, stopping")
                break
            for url, _id, alt in cards:
                title = " ".join(html.unescape(alt).split())
                if url in have or not says_false(title):
                    continue
                have.add(url)
                out.write(json.dumps({"klaim": title, "url": url, "penerbit": "TurnBackHoax (Mafindo)", "tanggal": "",
                                      "label": "salah"}, ensure_ascii=False) + "\n")
                added += 1
            kept_false += 0
            if page % 10 == 0:
                print(f"page {page}: {added} new headlines so far", flush=True)
                out.flush()
            time.sleep(args.delay)
    print(f"done: {added} new false-claim headlines -> {OUT}")


if __name__ == "__main__":
    main()
