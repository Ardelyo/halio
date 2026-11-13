"""Render docs/submission/Halio_Ringkasan_Keputusan.html jadi PDF 2 halaman A4 pake Microsoft Edge headless.

    python docs/submission/build_ringkasan.py        # perlu Microsoft Edge; gagal kalo hasilnya bukan tepat 2 halaman
"""

from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
SRC = HERE / "Halio_Ringkasan_Keputusan.html"
OUT = HERE / "Halio_Ringkasan_Keputusan.pdf"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([EDGE, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=6000",
                        f"--user-data-dir={tmp}\\edge", f"--print-to-pdf={OUT}", SRC.resolve().as_uri()],
                       check=True, capture_output=True)
    from pypdf import PdfReader

    n = len(PdfReader(OUT).pages)
    assert n == 2, f"harus tepat 2 halaman, dapat {n}"
    print(f"{n} halaman -> {OUT}")


if __name__ == "__main__":
    main()
