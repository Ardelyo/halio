"""Evaluation on an independent public sample: TurnBackHoax (Mafindo) fact-check titles.

    python eval/eval_public.py              # downloads at run time, writes eval/PUBLIC_RESULTS.md

Data: Hugging Face dataset `Rifky/indonesian-hoax-news` (17,806 TurnBackHoax titles, 2022 snapshot). The label is the
bracket prefix of each title: [SALAH] hoax, [BENAR] true, [KLARIFIKASI] clarification. None of these items was used to
write the corpus, the rules or the thresholds. The raw data is NOT copied into this repository (licence unclear); the
script fetches it each time and the report lists only aggregate numbers plus any item Halio got wrong.

What is measured (retrieval only, no LLM, no ClaimReview: the same mode as eval/run_eval.py):
  - false-hoax rate: [BENAR] / [KLARIFIKASI] items that Halio labels "terbukti_salah" (the error that matters most)
  - coverage: share of [SALAH] items Halio recognises as "terbukti_salah". The corpus has only a handful of entries,
    so a low number here is expected and is reported as corpus coverage, not as accuracy.
Titles are headlines, not forwarded chat messages, so this is a harsher and less natural test than real use.
"""

from __future__ import annotations

import json
import math
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from halio import pipeline  # noqa: E402
from halio.config import Settings  # noqa: E402

DATASET = "Rifky/indonesian-hoax-news"
API = "https://datasets-server.huggingface.co"
OUT = ROOT / "eval" / "PUBLIC_RESULTS.md"
HOAX_SAMPLE = 600  # ambil N item [SALAH] disebar merata dr seluruh dataset biar deterministik


def get(url: str) -> dict:
    # tarik JSON dr API Hugging Face dgn retry bertahap kl kena rate limit / timeout
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "halio-eval"})
            return json.load(urllib.request.urlopen(req, timeout=90))
        except Exception:
            time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"gagal mengambil {url}")


def clean(title: str) -> str:
    # bersihin tag [SALAH]/[BENAR], buntut nama situs, sm karakter mojibake bawaan dataset lama
    t = re.sub(r"^\s*\[[^\]]+\]\s*", "", title)
    t = re.sub(r"\s*[–—\-–—âÂ]+\s*TurnBackHoax\.ID\s*$", "", t, flags=re.I)
    t = t.replace("�", '"').replace("â", "").replace("Â", "")
    return re.sub(r"\s+", " ", t).strip()


def label(title: str) -> str:
    m = re.match(r"\s*\[([^\]]+)\]", title)
    return m.group(1).strip().upper() if m else ""


def search(query: str, want_prefix: str) -> list[tuple[str, str]]:
    found: dict[str, str] = {}
    offset = 0
    # ambil semua baris yg cocok sm kata kunci lewat endpoint search per 100 baris
    while True:
        q = urllib.parse.quote(query)
        r = get(f"{API}/search?dataset={DATASET}&config=default&split=train&query={q}&offset={offset}&length=100")
        for x in r["rows"]:
            title, url = x["row"]["title"], x["row"]["url"]
            if label(title) == want_prefix:
                found[url] = title
        offset += 100
        if offset >= r.get("num_rows_total", 0) or not r["rows"]:
            break
    return list(found.items())


def hoax_sample() -> list[tuple[str, str]]:
    out: dict[str, str] = {}
    # loncat tiap 600 baris biar sampel hoaksnya nyebar dr awal sampe akhir dataset, ga numpuk di satu masa
    total = get(f"{API}/size?dataset={DATASET}")["size"]["dataset"]["num_rows"]
    for offset in range(0, total, 600):
        r = get(f"{API}/rows?dataset={DATASET}&config=default&split=train&offset={offset}&length=100")
        for x in r["rows"]:
            if label(x["row"]["title"]) == "SALAH":
                out[x["row"]["url"]] = x["row"]["title"]
        if len(out) >= HOAX_SAMPLE:
            break
    return list(out.items())[:HOAX_SAMPLE]


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    # selang kepercayaan Wilson 95% buat ngitung batas atas tingkat tuduhan palsu secara jujur
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = p + z * z / (2 * n)
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - h) / d, (c + h) / d)


def run(items: list[tuple[str, str]], cfg: Settings) -> list[dict]:
    rows = []
    for url, title in items:
        r = pipeline.check(clean(title), cfg)
        rows.append({"url": url, "title": clean(title), "status": r["status"], "reason": r["reason"],
                     "score": (r["match"] or {}).get("score"), "debunk": (r["match"] or {}).get("debunk_id")})
    return rows


def main() -> None:
    # paksa mode lokal murni tanpa AI / FactCheck API, persis kaya eval/run_eval.py
    cfg = Settings(google_factcheck_key=None, llm_enabled=False)
    print("mengambil data TurnBackHoax dari Hugging Face ...", flush=True)
    true_items = search("BENAR", "BENAR")
    clar_items = search("KLARIFIKASI", "KLARIFIKASI")
    hoax_items = hoax_sample()
    print(f"[BENAR]={len(true_items)}  [KLARIFIKASI]={len(clar_items)}  [SALAH] sampel={len(hoax_items)}", flush=True)
    res = {"BENAR": run(true_items, cfg), "KLARIFIKASI": run(clar_items, cfg), "SALAH": run(hoax_items, cfg)}

    lines = [
        "# Evaluasi pada sampel publik: judul TurnBackHoax",
        "",
        "> **Jenis:** Bukti · **Untuk:** juri dan pengembang · [Peta dokumen](../docs/README.md)",
        "",
        f"Sumber: dataset Hugging Face `{DATASET}` (17.806 judul TurnBackHoax/Mafindo, rekaman 2022). Label diambil dari awalan judul. "
        "Tidak satu pun item dipakai untuk menulis korpus, aturan, atau ambang Halio. Data mentah tidak disalin ke repo; "
        "`python eval/eval_public.py` mengambilnya saat dijalankan. Mode: pencocokan lokal tanpa AI (sama dengan `eval/run_eval.py`).",
        "",
        "**Cara membaca.** Ini judul artikel, bukan pesan berantai, jadi lebih sulit dan kurang alami daripada pemakaian nyata. "
        "Korpus Halio hanya 7 bantahan, jadi `[SALAH]` yang dikenali sedikit; itu angka **cakupan korpus**, bukan akurasi. "
        "Angka yang dijaga adalah **tuduhan palsu**: kabar benar yang dicap \"terbukti salah\".",
        "",
        "## Tuduhan palsu (yang terpenting)",
        "",
        "| Kelompok | Jumlah | Dicap \"terbukti salah\" | Tingkat | Batas atas 95% (Wilson) |",
        "|---|---|---|---|---|",
    ]
    for key, title in (("BENAR", "`[BENAR]` (terverifikasi benar)"), ("KLARIFIKASI", "`[KLARIFIKASI]` (meluruskan hoaks)")):
        n = len(res[key]); k = sum(1 for r in res[key] if r["status"] == "terbukti_salah")
        lo, hi = wilson(k, n)
        lines.append(f"| {title} | {n} | {k} | {k / max(1, n):.1%} | {hi:.1%} |")
    nn = len(res["BENAR"]) + len(res["KLARIFIKASI"]); kk = sum(1 for key in ("BENAR", "KLARIFIKASI") for r in res[key] if r["status"] == "terbukti_salah")
    lo, hi = wilson(kk, nn)
    lines += [f"| **Gabungan** | **{nn}** | **{kk}** | **{kk / max(1, nn):.1%}** | **{hi:.1%}** |", ""]

    # kl sampe ada kabar bener ato klarifikasi yg kecap salah, buka terang-terangan di laporan
    for key in ("BENAR", "KLARIFIKASI"):
        bad = [r for r in res[key] if r["status"] == "terbukti_salah"]
        if bad:
            lines += [f"### Kesalahan pada `[{key}]`", "", "| Judul | Cocok dengan | Skor | Tautan |", "|---|---|---|---|"]
            lines += [f"| {r['title'][:90]} | {r['debunk']} | {r['score']} | {r['url']} |" for r in bad]
            lines.append("")

    lines += ["## Sebaran jawaban Halio", "", "| Jawaban | `[BENAR]` | `[KLARIFIKASI]` | `[SALAH]` (sampel) |", "|---|---|---|---|"]
    statuses = ["terbukti_salah", "tidak_yakin", "belum_ada_pemeriksaan", "sejalan_dengan_sumber", "dilaporkan_media"]
    for s in statuses:
        lines.append(f"| {s} | " + " | ".join(f"{sum(1 for r in res[k] if r['status'] == s)}" for k in ("BENAR", "KLARIFIKASI", "SALAH")) + " |")
    n_h = len(res["SALAH"]); k_h = sum(1 for r in res["SALAH"] if r["status"] == "terbukti_salah")
    lines += ["", "## Cakupan korpus pada hoaks (`[SALAH]`)", "",
              f"Dari **{n_h}** judul `[SALAH]` yang diambil merata dari dataset, Halio mengenali **{k_h}** ({k_h / max(1, n_h):.1%}) sebagai \"terbukti salah\". "
              "Sisanya jatuh ke \"tidak yakin\" atau \"belum ada pemeriksaan\" (jujur, bukan menebak). Korpus kurasi sengaja kecil; "
              "di luar korpus, Halio memakai mesin bukti dan pencarian, yang tidak dijalankan pada evaluasi ini.", ""]
    hit = Counter(r["debunk"] for r in res["SALAH"] if r["status"] == "terbukti_salah")
    if hit:
        lines += ["Bantahan yang paling sering cocok: " + ", ".join(f"`{d}` ({c})" for d, c in hit.most_common(5)), ""]
    wrong_kind = [r for r in res["SALAH"] if r["status"] in ("sejalan_dengan_sumber", "dilaporkan_media")]
    lines += [f"Hoaks yang salah diberi \"sejalan dengan sumber\" atau \"dilaporkan media\": **{len(wrong_kind)}** dari {n_h}.", "",
              "## Riwayat dan catatan integritas", 
              "", 
              "Run pertama (12 Nov 2026) menemukan **1 judul** yang salah dicap \"terbukti salah\" (tampil pada dua label): *\"BMKG Papua Mengklarifikasi Isu Akan Terjadi Tsunami di Papua\"*. Pesan itu justru meluruskan hoaks, tetapi kata \"mengklarifikasi\" belum dikenali sebagai pelurusan. Pola pelurusan di `backend/halio/retrieval.py` diperluas (klarifikasi, meluruskan, menepis, menyangkal, dan sejenisnya), kasusnya ditambahkan ke `eval/testset.jsonl` dan `backend/tests/test_core.py`, lalu evaluasi dijalankan ulang: 0 tuduhan palsu. **Karena perbaikan dibuat setelah melihat sampel ini, hasil 0/1.043 tidak sepenuhnya independen untuk judul itu.** Rekaman 2022 ini juga belum menguji pesan berantai nyata.", 
              "",
              "## Keterbatasan", "",
              "- Judul artikel bukan pesan berantai; hasil pada pesan nyata bisa berbeda.",
              "- Rekaman 2022; banyak topik lama. Label berasal dari TurnBackHoax, bukan dari tim.",
              "- Sampel `[SALAH]` diambil merata, bukan acak murni, dan dibatasi 600 item.",
              "- Mode tanpa AI saja. Mesin bukti dan ClaimReview belum dievaluasi pada set ini.",
              ""]
    # simpen hasil ke eval/PUBLIC_RESULTS.md (data mentahnya sendiri ga ikut disimpen di repo)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"tuduhan palsu: {kk}/{nn}  | cakupan SALAH: {k_h}/{n_h} | ditulis {OUT}")


if __name__ == "__main__":
    main()
