"""Run the real pipeline (real Gemini, real web) on CURRENT headlines the sensor already collected, and report honestly.

    HALIO_LLM=1 HALIO_ENGINE=v2 HALIO_DB=/data/halio.db python scripts/eval_live.py --news 20 --hoax 20

Two sets, both taken from the sensor database (no hand-written data):
  news   recent headlines from news feeds. A true headline must NEVER come out "terbukti salah".
  hoax   titles of fact-check articles ("Hoaks! ...", "[PENIPUAN] ..."), prefix removed. Should come out "terbukti salah" or at
         least not "sejalan" / "dilaporkan media". CAVEAT: the search will often find the very article the title came from,
         so this set measures the plumbing (search, read, judge, policy), not independent accuracy.

Writes eval/LIVE_RESULTS.md. Costs real model calls: keep --news/--hoax small. Exit code 1 when a headline was falsely accused.
"""

from __future__ import annotations

import argparse
import re
import statistics
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

PREFIX = re.compile(r"^\s*(\[[^\]]{2,20}\]|hoaks?!?:?|hoax!?:?|cek fakta:|fakta atau hoaks:?|disinformasi:?|misinformasi:?|klarifikasi:?)\s*", re.I)
HOAX_WORD = re.compile(r"\b(hoaks|hoax|penipuan|disinformasi|misinformasi)\b", re.I)


def strip_prefix(title: str) -> str:
    """'[PENIPUAN] Akun Telegram Pendaftaran Program X' -> 'Akun Telegram Pendaftaran Program X' (repeated prefixes too)."""
    out = title.strip()
    for _ in range(3):
        new = PREFIX.sub("", out, count=1).strip()
        if new == out:
            break
        out = new
    return out


def build_sets(rows: list[dict], kinds: dict[str, str], n_news: int, n_hoax: int) -> tuple[list[str], list[str]]:
    """rows: sensor items {source_id,title}; kinds: source_id -> berita|cek_fakta|resmi."""
    news, hoax, seen = [], [], set()
    for r in rows:
        title = " ".join(r["title"].split())
        if title in seen or len(title.split()) < 5:
            continue
        seen.add(title)
        if kinds.get(r["source_id"]) == "cek_fakta" and HOAX_WORD.search(title):
            claim = strip_prefix(title)
            if len(claim.split()) >= 4:
                hoax.append(claim)
        elif kinds.get(r["source_id"]) == "berita" and not HOAX_WORD.search(title):
            news.append(title)
    return news[:n_news], hoax[:n_hoax]


def summarize(results: list[dict]) -> dict:
    lat = sorted(r["seconds"] for r in results)
    pct = lambda p: lat[min(len(lat) - 1, int(p * len(lat)))] if lat else 0  # noqa: E731
    rejected = Counter(x["alasan"] for r in results for x in ((r["result"].get("evidence") or {}).get("ditolak") or []))
    return {
        "n": len(results), "status": Counter(r["result"]["status"] for r in results),
        "p50": round(statistics.median(lat), 1) if lat else 0, "p95": round(pct(0.95), 1),
        "informative": sum(1 for r in results if (r["result"].get("evidence") or {}).get("items") or r["result"].get("info") or r["result"].get("match")),
        "rejected": rejected,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--news", type=int, default=20)
    ap.add_argument("--hoax", type=int, default=20)
    ap.add_argument("--out", default=str(ROOT / "eval" / "LIVE_RESULTS.md"))
    args = ap.parse_args()

    from halio import pipeline
    from halio.config import settings
    from halio.ingest.sources import SOURCES
    from halio.ingest.store import SensorStore

    if not settings.llm_enabled:
        raise SystemExit("HALIO_LLM=1 diperlukan: skrip ini mengukur pencarian web yang sebenarnya.")
    store = SensorStore(settings.db_path)
    rows = store.recent_items(limit=200)
    news, hoax = build_sets(rows, {s.id: s.kind for s in SOURCES}, args.news, args.hoax)
    if not news or (args.hoax and not hoax):
        raise SystemExit(f"Sensor belum punya cukup judul (berita {len(news)}, pemeriksaan fakta {len(hoax)}). Jalankan dengan HALIO_SENSOR=1 beberapa jam dulu.")

    def run(claims: list[str]) -> list[dict]:
        out = []
        for c in claims:
            t0 = time.time()
            out.append({"text": c, "result": pipeline.check(c, settings), "seconds": time.time() - t0})
            print(f"{out[-1]['result']['status']:<24} {out[-1]['seconds']:5.1f}s  {c[:80]}")
        return out

    print(f"engine={settings.evidence_engine} model={settings.llm_model}\n-- berita ({len(news)})")
    rn = run(news)
    print(f"\n-- pemeriksaan fakta ({len(hoax)})")
    rh = run(hoax)

    false_accusations = [r for r in rn if r["result"]["status"] == "terbukti_salah"]
    dangerous = [r for r in rh if r["result"]["status"] in ("sejalan_dengan_sumber", "dilaporkan_media")]
    caught = [r for r in rh if r["result"]["status"] == "terbukti_salah"]
    sn, sh = summarize(rn), summarize(rh)
    lines = [
        "# Evaluasi langsung (judul terkini dari Sensor)", "",
        f"Dijalankan {datetime.now().isoformat(timespec='minutes')}, mesin `{settings.evidence_engine}`, model `{settings.llm_model}`. "
        "Set diambil otomatis dari basis data Sensor, bukan ditulis tim. Set hoaks mudah (pencarian sering menemukan artikel asalnya): "
        "angka ini mengukur saluran, bukan ketepatan independen.", "",
        "| Ukuran | Nilai |", "|---|---|",
        f"| **Berita benar dituduh salah** (harus 0) | **{len(false_accusations)}/{len(rn)}** |",
        f"| Hoaks yang dibantah ('terbukti salah') | {len(caught)}/{len(rh)} |",
        f"| **Hoaks yang dikira benar** (sejalan/dilaporkan; harus 0) | **{len(dangerous)}/{len(rh)}** |",
        f"| Jawaban informatif (ada bukti, info artikel, atau bantahan) | {sn['informative'] + sh['informative']}/{sn['n'] + sh['n']} |",
        f"| Waktu jawab p50 / p95 (detik) | {max(sn['p50'], sh['p50'])} / {max(sn['p95'], sh['p95'])} |", "",
        f"Status berita: {dict(sn['status'])}", f"Status pemeriksaan fakta: {dict(sh['status'])}", "",
        "Alasan penolakan halaman (teratas): " + (", ".join(f"{k} ×{v}" for k, v in (sn['rejected'] + sh['rejected']).most_common(5)) or "tidak ada"), "",
    ]
    for title, rows_ in (("Berita yang dituduh salah", false_accusations), ("Hoaks yang dikira benar", dangerous)):
        if rows_:
            lines += [f"## {title}", ""] + [f"- {r['text']}  →  {r['result']['status']} ({r['result']['reason']})" for r in rows_] + [""]
    Path(args.out).write_text("\n".join(lines), encoding="utf-8")
    print(f"\nTertulis: {args.out}")
    sys.exit(1 if false_accusations or dangerous else 0)


if __name__ == "__main__":
    main()
