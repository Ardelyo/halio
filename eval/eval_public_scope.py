"""Recall BERSIH pada judul [SALAH] TurnBackHoax yang topiknya ada dalam cakupan korpus (penipuan, APK, bansos, TNI, rekrutmen, ...).

    python eval/eval_public_scope.py        # mengunduh dataset publik saat dijalankan, menulis eval/PUBLIC_SCOPE_RESULTS.md

Mengapa ini lebih jujur daripada set holdout tulisan tim: judul ditulis dan diberi label oleh Mafindo (pihak luar), dataset rekaman 2022,
dan tidak satu pun dipakai menyetel korpus, aturan, atau ambang. Pemilihan "dalam cakupan" memakai daftar kata kunci TETAP di bawah ini
(ditulis sebelum menjalankan), bukan melihat hasil Halio.

Yang dilaporkan: berapa judul dalam cakupan yang dikenali "terbukti_salah" dan, untuk setiap yang dikenali, apakah bantahan yang cocok
benar topiknya (dinilai MANUSIA dari daftar di berkas hasil, bukan oleh skrip). Judul adalah headline, bukan pesan berantai: lebih sulit.
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
sys.path.insert(0, str(ROOT / "eval"))

import eval_public as ep  # noqa: E402
from halio import pipeline  # noqa: E402
from halio.config import Settings  # noqa: E402

OUT = ROOT / "eval" / "PUBLIC_SCOPE_RESULTS.md"
# daftar tetap, ditulis dari kategori korpus (bukan dari hasil eval)
SCOPE = re.compile(
    r"penipuan|penipu|\bapk\b|bansos|bantuan (sosial|tunai|dana)|calo|\btni\b|prajurit|tamtama|bintara|akmil|akpol|cpns|pppk|rekrutmen|lowongan|"
    r"kuota gratis|saldo|e-?toll|hadiah|undian|pinjol|pinjaman online|investasi|\botp\b|kode verifikasi|tilang|bpjs|kurir|paket|"
    r"gempa|tsunami|penculikan|obat herbal|air kelapa|kanker|diabetes|tbc|deepfake|video palsu|akun palsu|mengatasnamakan|catut", re.I)


def main() -> None:
    cfg = Settings(google_factcheck_key=None, llm_enabled=False, link_check_enabled=False)
    print("membaca dataset ...", flush=True)
    rows = list({ep.clean(t).lower(): (u, t) for u, t in ep.scan_all() if ep.label(t) == "SALAH"}.values())  # judul ganda (URL berbeda) dihitung sekali
    scoped = [(u, ep.clean(t)) for u, t in rows if SCOPE.search(ep.clean(t))]
    res = []
    for url, title in scoped:
        r = pipeline.check(title, cfg)
        res.append((url, title, r["status"], (r["match"] or {}).get("debunk_id"), (r["match"] or {}).get("score")))
    hits = [x for x in res if x[2] == "terbukti_salah"]
    by = Counter(x[2] for x in res)
    lines = [
        "# Recall bersih pada judul `[SALAH]` TurnBackHoax dalam cakupan korpus",
        "",
        f"Dataset `{ep.DATASET}` (rekaman 2022, label oleh Mafindo), mode lokal tanpa AI, korpus {sum(not d.signed for d in pipeline.get_index(cfg.corpus_path).debunks)} entri bantahan. "
        "Pemilihan dalam cakupan memakai daftar kata kunci tetap di `eval/eval_public_scope.py`. **Judul = headline, bukan pesan berantai.**",
        "",
        f"- Judul `[SALAH]` unik di seluruh dataset: **{len(rows)}**; dalam cakupan kata kunci: **{len(scoped)}**",
        f"- Dikenali `terbukti_salah`: **{len(hits)}** ({len(hits) / max(1, len(scoped)):.1%})",
        f"- Sebaran: " + ", ".join(f"{k} {v}" for k, v in by.most_common()),
        "",
        "Kata kunci cakupan itu longgar (mis. `gempa`, `paket`), jadi banyak judul yang cocok kata tetapi bukan topik penipuan yang dibantah korpus; "
        "angka ini batas bawah yang konservatif, bukan akurasi. Halio sengaja memilih diam daripada menebak.",
        "",
        "## Yang dikenali: dinilai manusia, benar topiknya?",
        "",
        "| Judul | Bantahan yang cocok | Skor | Topik benar? |",
        "|---|---|---|---|",
    ]
    for _, title, _, did, score in hits:
        lines.append(f"| {title[:150]} | `{did}` | {score} | _belum dinilai_ |")
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"SALAH={len(rows)} dalam_cakupan={len(scoped)} dikenali={len(hits)} sebaran={dict(by)}")
    for _, title, _, did, score in hits:
        print(f"  {score} {did:36} | {title[:110]}")


if __name__ == "__main__":
    main()
