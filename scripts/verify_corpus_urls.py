"""Buka SETIAP tautan sumber di data/debunks.json dan periksa apakah halamannya mendukung entrinya.

    python scripts/verify_corpus_urls.py                 # semua entri, tulis docs/verifikasi_korpus.json
    python scripts/verify_corpus_urls.py --id apk-tagihan-pln

Pemeriksaan OTOMATIS dan sengaja konservatif; ini bukan pengganti membaca:
  - terjangkau : HTTP 200 dan ada teks. 403/429 = "ditolak" (tidak dicari jalan lain; buka manual)
  - topik      : berapa persen kata kunci klaim entri itu muncul di teks halaman
  - isyarat    : halaman memuat kata bantahan/peringatan (hoaks, penipuan, tidak benar, waspada, klarifikasi, ...)
  - status     : eksplisit (topik >= 0.5 dan ada isyarat) | sebagian | tidak_cocok | gagal
Isi halaman tidak disalin ke repo; hanya angka dan penanda.
"""

from __future__ import annotations

import html
import json
import re
import sys
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from halio.textnorm import STOPWORDS  # noqa: E402

CORPUS = ROOT / "data" / "debunks.json"
OUT = ROOT / "docs" / "verifikasi_korpus.json"
UA = "halio-eval (riset anti-disinformasi; hanya halaman publik)"  # sama dengan eval/eval_resmi_tni.py
CUES = re.compile(
    r"hoaks|hoax|penipuan|penipu|tidak benar|bohong|klarifikasi|waspada|modus|palsu|menyesatkan|tidak ada bukti|belum terbukti|"
    r"tidak pernah|tidak dipungut|gratis|bukan prediksi|tidak bisa diprediksi|tidak mungkin|jangan percaya|hati-hati|awas|disinformasi|"
    r"bukan ramalan|tidak ada satu obat|deepfake|calo", re.I)


def fold(t: str) -> str:
    t = unicodedata.normalize("NFKD", t)
    return "".join(c for c in t if not unicodedata.combining(c)).lower()


def page_text(raw: str) -> str:
    raw = re.sub(r"(?is)<(script|style|noscript|svg|nav|footer|header)\b.*?</\1>", " ", raw)
    raw = re.sub(r"(?s)<[^>]+>", " ", raw)
    return re.sub(r"\s+", " ", html.unescape(raw)).strip()


def fetch(client: httpx.Client, url: str) -> tuple[str, str, int]:
    """(teks, cara, http). Halaman yang menolak program (403, dst.) dilaporkan apa adanya sebagai "ditolak", TIDAK dicari jalan lain:
    pemeriksa manusia membukanya lewat peramban."""
    try:
        r = client.get(url)
    except httpx.HTTPError:
        return "", "gagal", 0
    if r.status_code == 200 and len(r.text) > 500:
        return page_text(r.text), "langsung", 200
    return "", "ditolak" if r.status_code in (401, 403, 429) else "gagal", r.status_code


def keywords(entry: dict) -> list[str]:
    toks = re.findall(r"[a-z0-9]{4,}", fold(entry["klaim"]))
    return sorted({t for t in toks if t not in STOPWORDS})


def snippet(text: str, kws: list[str]) -> str:
    low = fold(text)
    for m in CUES.finditer(low):
        s = max(0, m.start() - 70)
        near = low[s : m.end() + 90]
        if any(k in near for k in kws):
            return re.sub(r"\s+", " ", text[s : m.end() + 90]).strip()
    m = CUES.search(low)
    return re.sub(r"\s+", " ", text[max(0, m.start() - 60) : m.end() + 80]).strip() if m else ""


def check(client: httpx.Client, entry: dict, src: dict) -> dict:
    text, how, code = fetch(client, src["url"])
    if not text:
        return {"url": src["url"], "status": "gagal", "http": code, "cara": how}
    low = fold(text)
    kws = keywords(entry)
    topic = round(sum(k in low for k in kws) / max(1, len(kws)), 2)
    cue = bool(CUES.search(low))
    status = "eksplisit" if topic >= 0.5 and cue else "sebagian" if topic >= 0.3 else "tidak_cocok"
    return {"url": src["url"], "status": status, "http": 200, "cara": how, "topik": topic, "isyarat": cue, "cuplikan_ada": bool(snippet(text, kws))}


def main() -> int:
    only = sys.argv[sys.argv.index("--id") + 1] if "--id" in sys.argv else None
    entries = [d for d in json.loads(CORPUS.read_text(encoding="utf-8"))["debunks"] if not only or d["id"] == only]
    jobs = [(e, s) for e in entries for s in e["sumber"]]
    with httpx.Client(headers={"User-Agent": UA, "Accept-Language": "id,en;q=0.8"}, follow_redirects=True, timeout=25) as client, ThreadPoolExecutor(3) as pool:
        results = list(pool.map(lambda j: check(client, *j), jobs))
    report: dict[str, list] = {}
    for (e, _), r in zip(jobs, results):
        report.setdefault(e["id"], []).append(r)
    OUT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    order = {"eksplisit": 0, "sebagian": 1, "tidak_cocok": 2, "gagal": 3}
    for eid, rs in report.items():
        best = min((r["status"] for r in rs), key=order.get)
        print(f"{best:11} {eid:42} " + " ".join(f"{r['status'][:3]}:{r.get('topik', '-')}" for r in rs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
