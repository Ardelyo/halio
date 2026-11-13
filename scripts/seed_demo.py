"""Fill the Radar with clearly-labelled simulated checks for the demo video.

    python scripts/seed_demo.py [--n 300] [--days 14]

Writes straight to the database at HALIO_DB (default ./halio.db), spreading
events over the past days. Every event has channel="demo" and the Radar page
shows a banner with the simulated count, so simulation is never passed off as
real usage.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from halio import pipeline  # noqa: E402
from halio.config import settings  # noqa: E402
from halio.store import Store, today  # noqa: E402

# contoh isu baru yg blm ada di korpus buat nunjukin cara kerja ambang k-anonymity di Radar
UNKNOWN_RUMOUR = "Beredar kabar markas Kodim akan ditutup dan semua prajurit dipindah ke luar daerah mulai pekan depan, sebarkan"
OTHER_UNKNOWN = [
    "Bank akan memblokir semua rekening tidak aktif tiga bulan mulai Januari",
    "Harga BBM naik besok pagi jam 6, segera isi penuh",
    "Sekolah diliburkan seminggu karena ada virus baru",
]
# bobot kategori biar penipuan catut TNI & bansos muncul lebih sering kaya kondisi lapangan
WEIGHTS = {"penipuan_catut_tni": 5, "penipuan_bansos": 4, "phishing": 3, "bencana": 2, "kesehatan": 2, "keamanan_publik": 2}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=300)
    ap.add_argument("--days", type=int, default=14)
    args = ap.parse_args()
    # kunci seed acak biar grafik demo tetep konsisten kl direkam ulang
    random.seed(7)

    store = Store(settings.db_path, k_anonymity=settings.k_anonymity)
    corpus = json.loads(settings.corpus_path.read_text(encoding="utf-8"))["debunks"]
    # bikin variasi pesan berantai dr korpus trus jalanin cek sekali per teks unik
    texts = [v + " segera sebarkan!" for d in corpus for v in [d["klaim"], *d["varian"]] for _ in range(WEIGHTS.get(d["kategori"], 1))]
    results = {t: pipeline.check(t, settings) for t in set(texts)}

    end = date.fromisoformat(today())
    days = [(end - timedelta(days=i)).isoformat() for i in range(args.days)][::-1]
    # bobot harian dibikin nanjak pelan biar grafiknya keliatan kaya gelombang isu yg baru naik
    day_weights = [1 + i / len(days) * 2 for i in range(len(days))]
    for _ in range(args.n):
        day = random.choices(days, day_weights)[0]
        store.record(results[random.choice(texts)], "demo", None, day=day)

    # satu isu baru dilaporin 7 orang beda hari ini, jadi tembus ambang k=5 & boleh tampil...
    rumour = pipeline.check(UNKNOWN_RUMOUR, settings)
    for i in range(7):
        store.record(rumour, "demo", f"demo:r{i}")
    # ...sedangkan yg di bawah ini cuma 2 pelapor, teks aslinya jgn smpe kesimpen di Radar
    for t in OTHER_UNKNOWN:
        r = pipeline.check(t, settings)
        for i in range(2):
            store.record(r, "demo", f"demo:o{i}")
    print(f"Seeded simulated checks into {settings.db_path}. Open /radar")


if __name__ == "__main__":
    main()
