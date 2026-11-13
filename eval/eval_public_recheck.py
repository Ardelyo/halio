"""Pemeriksaan ulang tuduhan palsu pada sampel publik TurnBackHoax, bisa diulang siapa pun.

    python eval/eval_public_recheck.py          # unduh sampel saat dijalankan, tulis eval/PUBLIC_RECHECK.md

Beda dgn eval_public.py: sampel diambil lewat endpoint /rows (halaman tersebar tiap 450 baris), bukan /search yg sering gagal.
Protokol: kode & korpus dibekukan (commit dicatat di laporan, beserta status pohon kerja) SEBELUM skrip dijalankan; tidak ada
yg disetel setelah melihat hasil. Mode: pencocokan lokal tanpa AI & tanpa cek tautan (sama dgn eval/run_eval.py).
Data mentah ga disalin ke repo (lisensi ga jelas); laporan cuma memuat angka agregat + judul yg salah dituduh (bila ada).
"""

from __future__ import annotations

import collections
import importlib.util
import subprocess
import sys
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from halio import pipeline  # noqa: E402
from halio.config import Settings  # noqa: E402

spec = importlib.util.spec_from_file_location("eval_public", ROOT / "eval" / "eval_public.py")
ep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ep)

OUT = ROOT / "eval" / "PUBLIC_RECHECK.md"
STEP = 450
TOTAL_ROWS = 17800


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def main() -> int:
    cfg = replace(Settings(), google_factcheck_key=None, llm_enabled=False, link_check_enabled=False)
    commit, dirty = git("rev-parse", "HEAD"), bool(git("status", "--porcelain", "--", "backend", "data", "eval/run_eval.py"))
    titles, failed_pages = [], 0
    for off in range(0, TOTAL_ROWS, STEP):
        try:
            r = ep.get(f"{ep.API}/rows?dataset={ep.DATASET}&config=default&split=train&offset={off}&length=100")
        except Exception:
            failed_pages += 1
            continue
        titles += [x["row"]["title"] for x in r["rows"]]
    counts: collections.Counter = collections.Counter()
    false_acc, recognised = [], collections.Counter()
    for title in titles:
        lab, text = ep.label(title), ep.clean(title)
        res = pipeline.check(text, cfg)
        counts[(lab, res["status"])] += 1
        if res["status"] == "terbukti_salah":
            recognised[(res["match"] or {}).get("debunk_id")] += 1
            if lab in ("BENAR", "KLARIFIKASI"):
                false_acc.append((lab, (res["match"] or {}).get("debunk_id"), text[:140]))
    benign = sum(v for (lab, _), v in counts.items() if lab in ("BENAR", "KLARIFIKASI"))
    hoax = sum(v for (lab, _), v in counts.items() if lab == "SALAH")
    lo, hi = ep.wilson(len(false_acc), benign) if benign else (0.0, 0.0)
    hoax_hit = counts[("SALAH", "terbukti_salah")]
    lines = [
        "# Pemeriksaan ulang tuduhan palsu pada sampel publik TurnBackHoax",
        "",
        "> **Jenis:** Bukti · **Untuk:** juri dan pengembang · dibuat otomatis oleh `eval/eval_public_recheck.py`",
        "",
        f"- Tanggal: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"- Commit yang diuji: `{commit[:10]}` (berkas backend/data bersih dari perubahan yang belum di-commit: **{'tidak' if dirty else 'ya'}**)",
        f"- Sampel: {len(titles)} judul dari `{ep.DATASET}` (halaman tersebar tiap {STEP} baris; {failed_pages} halaman gagal diunduh dan dilewati)",
        "- Mode: pencocokan lokal tanpa AI dan tanpa cek tautan. Korpus: `data/debunks.json` apa adanya pada commit itu",
        "- Protokol: kode dan korpus dibekukan sebelum skrip dijalankan; tidak ada penyetelan setelah melihat hasil",
        "",
        "## Hasil",
        "",
        f"| Metrik | Nilai |",
        "|---|---|",
        f"| Judul berlabel BENAR atau KLARIFIKASI | {benign} |",
        f"| **Salah dicap \"terbukti salah\" (tuduhan palsu)** | **{len(false_acc)}** |",
        f"| Batas atas 95% (Wilson) tingkat tuduhan palsu | {hi:.2%} |",
        f"| Judul berlabel SALAH | {hoax} |",
        f"| SALAH yang dikenali \"terbukti salah\" (cakupan korpus, bukan akurasi) | {hoax_hit} ({hoax_hit / max(1, hoax):.1%}) |",
        "",
    ]
    if false_acc:
        lines += ["## Tuduhan palsu (dicatat terbuka)", "", "| Label | Bantahan yang cocok | Judul |", "|---|---|---|"]
        lines += [f"| {a} | {b} | {c} |" for a, b, c in false_acc]
        lines.append("")
    lines += ["## Per status", "", "| Label | Status | n |", "|---|---|---|"]
    lines += [f"| {lab or '(tanpa label)'} | {st} | {n} |" for (lab, st), n in sorted(counts.items())]
    lines += ["", "Ini judul artikel, bukan pesan berantai, jadi lebih sulit dan kurang alami daripada pemakaian nyata. "
              "Angka lama 0 dari 1.043 (`PUBLIC_RESULTS.md`) diukur dengan korpus 7 entri dan tidak dibuat ulang.", ""]
    OUT.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"sampel {len(titles)} | benign {benign} | tuduhan palsu {len(false_acc)} | batas atas {hi:.2%} | SALAH dikenali {hoax_hit}/{hoax} | commit {commit[:10]} bersih={not dirty}")
    return 1 if false_acc else 0


if __name__ == "__main__":
    raise SystemExit(main())
