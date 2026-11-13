"""Measure Halio Telusur (the investigation swarm) with real Gemini and the real web, and report it as it is.

    HALIO_LLM=1 python eval/eval_agent.py --hoax 10 --news 10        # run on the server (needs the sensor archive)

Sets
  hoax  the curated corpus (data/debunks.json) plus fact-check headlines from the sensor, "Hoaks!" prefix removed.
        Must NEVER come out green (sejalan / dilaporkan media). Caveat: the search often finds the very article a
        fact-check headline came from, so this measures plumbing more than independent accuracy.
  news  ordinary headlines from news feeds. Must NEVER come out "terbukti salah" (a false accusation).

Writes eval/AGENT_RESULTS.md. Exit code 1 on any false accusation or any green hoax. Costs real model calls.
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "scripts"))

# status "hijau" yg pantang banget keluar buat klaim hoaks
GREEN = {"sejalan_dengan_sumber", "dilaporkan_media"}


def corpus_hoaxes() -> list[str]:
    # ambil klaim hoaks dr korpus kurasi (skip entri yg sifatnya verifikasi positif)
    data = json.loads((ROOT / "data" / "debunks.json").read_text(encoding="utf-8"))
    items = data["debunks"] if isinstance(data, dict) else data
    return [d["klaim"] for d in items if d.get("jenis") != "verifikasi_positif"]


def main() -> None:
    from eval_live import build_sets

    from halio import investigate
    from halio.config import settings
    from halio.ingest.sources import SOURCES
    from halio.ingest.store import SensorStore

    ap = argparse.ArgumentParser()
    ap.add_argument("--hoax", type=int, default=10)
    ap.add_argument("--news", type=int, default=10)
    args = ap.parse_args()
    # evaluasi agen telusur butuh Gemini + Google Search hidup, kl mati langsung tolak aja
    if not settings.llm_enabled:
        raise SystemExit("HALIO_LLM=1 diperlukan.")

    # gabungin korpus hoaks kita sm judul cek fakta terbaru hasil tangkapan sensor
    rows = SensorStore(settings.db_path).recent_items(limit=200)
    news, sensor_hoax = build_sets(rows, {s.id: s.kind for s in SOURCES}, args.news, args.hoax)
    hoax = (corpus_hoaxes() + sensor_hoax)[: args.hoax]
    results = []
    # jalankan telusur penuh satu-satu; lumayan makan waktu jd cetak progres per baris
    for kind, claims in (("hoax", hoax), ("news", news)):
        for claim in claims:
            t0 = time.time()
            try:
                rep = investigate.run(claim, settings)
                err = ""
            except Exception as exc:  # catet aja errornya, jgn berenti di tengah jalan
                rep, err = {}, type(exc).__name__
            sec = round(time.time() - t0, 1)
            m = rep.get("metode", {})
            k = m.get("kalimat", {})
            results.append({"set": kind, "klaim": claim, "detik": sec, "galat": err, "status": rep.get("status", "galat"),
                            "reason": rep.get("reason", ""), "dibuka": m.get("dibuka", 0), "kandidat": m.get("kandidat", 0),
                            "bukti": len(rep.get("bukti", [])), "ditulis": k.get("ditulis", 0), "dibuang": k.get("dibuang", 0),
                            "asal": (rep.get("asal") or {}).get("pertama", {}).get("tanggal", ""),
                            "agen": len(rep.get("agen", []))})
            r = results[-1]
            print(f"{kind:<4} {r['status']:<24} {sec:>6}s dibuka {r['dibuka']:>3} bukti {r['bukti']:>2} asal {r['asal'] or '-':<10} {claim[:70]}", flush=True)

    # cek dua syarat keselamatan utma: 0 berita dituduh salah & 0 hoaks lolos hijau
    bad_news = [r for r in results if r["set"] == "news" and r["status"] == "terbukti_salah"]
    green_hoax = [r for r in results if r["set"] == "hoax" and r["status"] in GREEN]
    secs = sorted(r["detik"] for r in results if not r["galat"]) or [0]
    written = sum(r["ditulis"] for r in results)
    dropped = sum(r["dibuang"] for r in results)
    lines = [
        f"# Halio Telusur: hasil evaluasi hidup ({datetime.now().isoformat(timespec='minutes')})",
        "",
        f"Model `{settings.llm_model}`, web dan Google Search sungguhan. {len(hoax)} klaim hoaks, {len(news)} judul berita.",
        "",
        "| Ukuran | Nilai |",
        "|---|---|",
        f"| Tuduhan palsu (berita dicap terbukti salah) | **{len(bad_news)} / {len(news)}** |",
        f"| Hoaks yang keluar hijau | **{len(green_hoax)} / {len(hoax)}** |",
        f"| Waktu p50 / p90 | {statistics.median(secs):.0f} s / {secs[min(len(secs) - 1, int(0.9 * len(secs)))]:.0f} s |",
        f"| Halaman dibuka (rata-rata) | {statistics.mean(r['dibuka'] for r in results):.0f} |" if results else "| Halaman dibuka | - |",
        f"| Kalimat laporan ditulis / dibuang pemeriksa | {written} / {dropped} |",
        f"| Kemunculan paling awal ditemukan | {sum(1 for r in results if r['asal'])} / {len(results)} |",
        f"| Galat | {sum(1 for r in results if r['galat'])} |",
        "",
        "Status hoaks: " + ", ".join(f"{k} {v}" for k, v in Counter(r["status"] for r in results if r["set"] == "hoax").items()),
        "",
        "Status berita: " + ", ".join(f"{k} {v}" for k, v in Counter(r["status"] for r in results if r["set"] == "news").items()),
        "",
        "| Set | Status | Detik | Dibuka | Bukti | Asal | Klaim |",
        "|---|---|---|---|---|---|---|",
        *[f"| {r['set']} | {r['status']} | {r['detik']} | {r['dibuka']} | {r['bukti']} | {r['asal'] or '-'} | {r['klaim'][:90].replace('|', '/')} |" for r in results],
        "",
        "Catatan jujur: set hoaks sebagian berasal dari judul artikel cek fakta, sehingga pencarian sering menemukan artikel itu sendiri;",
        "ini mengukur jalur kerja (cari, buka, kutip, nilai, putuskan), bukan akurasi independen.",
    ]
    out = ROOT / "eval" / "AGENT_RESULTS.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\nTertulis: {out}")
    # gagalin proses kl ada pelanggaran keselamatan biar ketauan jelas
    sys.exit(1 if bad_news or green_hoax else 0)


if __name__ == "__main__":
    main()
