"""Bikin paket luring Halio: satu folder yg bisa dibawa lewat flashdisk, dibuka tanpa instalasi dan tanpa server.

    python scripts/make_luring_package.py              # tulis dist/Halio-Luring.zip
    python scripts/make_luring_package.py --selftest   # + ekstrak ke folder sementara, buka dari file:// dgn jaringan diputus (butuh playwright)

Isi: web/ (halaman cek + mesin luring + font), peluncur Windows/macOS/Linux, PANDUAN.txt, VERSI.txt.
Batas (ditulis jujur di PANDUAN.txt): cuma mengenali bantahan di korpus; tanpa AI, web, Telegram, foto/suara, kartu dr server.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "Halio-Luring.zip"
TOP = "Halio-Luring"

PANDUAN = """HALIO LURING: cek pesan tanpa internet
======================================

Cara pakai
  Windows : klik dua kali  Buka-Halio.bat
  macOS   : klik dua kali  Buka-Halio.command  (sekali: chmod +x Buka-Halio.command)
  Linux   : jalankan       ./buka-halio.sh
  Atau    : buka berkas  web/cek.html  dengan Chrome, Edge, atau Firefox.

Lalu tempel pesan yang mencurigakan dan tekan "Cek pesan ini". Jawaban muncul di perangkat ini.

Yang terjadi
  - Pesan dicocokkan di browser dengan korpus bantahan Halio ({n} bantahan). Tidak ada pesan yang dikirim ke mana pun.
  - Tidak memakai AI, pencarian web, atau server.

Batasnya (tolong dibaca)
  - Hanya mengenali kabar yang ada di korpus. Di luar itu jawabannya "Belum ada pemeriksaan", bukan tebakan.
  - Tidak ada: Telegram, baca foto atau suara, Telusur, kartu dari server, tombol banding dan pemeriksa manusia.
  - Korpus adalah salinan saat paket dibuat (lihat VERSI.txt). Untuk korpus terbaru, ambil paket baru.
  - Bila halaman cek terbuka lewat server Halio dan internet ada, Halio memakai server seperti biasa.

Untuk satuan dengan jaringan tertutup
  Server lengkap tanpa AI bisa dijalankan di satu laptop atau mini-PC (lihat docs/LURING.md di repo Halio),
  lalu dibuka dari perangkat lain di Wi-Fi atau hotspot yang sama.

Kode dan dokumen: https://github.com/Ardelyo/halio
"""

BAT = '@echo off\r\nstart "" "%~dp0web\\cek.html"\r\n'
COMMAND = '#!/bin/sh\ncd "$(dirname "$0")" && open "web/cek.html"\n'
SH = '#!/bin/sh\ncd "$(dirname "$0")" && (xdg-open "web/cek.html" 2>/dev/null || sensible-browser "web/cek.html")\n'


def build() -> Path:
    corpus = (ROOT / "data" / "debunks.json").read_bytes()
    n = len(json.loads(corpus.decode("utf-8"))["debunks"])
    try:
        commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip() or "tanpa-git"
    except OSError:
        commit = "tanpa-git"
    versi = (
        f"Halio Luring\ncommit: {commit}\nkorpus: {n} bantahan\nsha256 korpus: {hashlib.sha256(corpus).hexdigest()}\n"
        f"dibuat: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n"
    )
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted((ROOT / "web").rglob("*")):
            if p.is_file():
                z.write(p, f"{TOP}/web/{p.relative_to(ROOT / 'web').as_posix()}")
        z.writestr(f"{TOP}/Buka-Halio.bat", BAT)
        info = zipfile.ZipInfo(f"{TOP}/Buka-Halio.command"); info.external_attr = 0o755 << 16; z.writestr(info, COMMAND)
        info = zipfile.ZipInfo(f"{TOP}/buka-halio.sh"); info.external_attr = 0o755 << 16; z.writestr(info, SH)
        z.writestr(f"{TOP}/PANDUAN.txt", PANDUAN.format(n=n).replace("\n", "\r\n"))
        z.writestr(f"{TOP}/VERSI.txt", versi.replace("\n", "\r\n"))
    print(f"ditulis {OUT.relative_to(ROOT)}: {OUT.stat().st_size // 1024} KB, {n} bantahan, commit {commit}")
    return OUT


def selftest(zip_path: Path) -> int:
    from playwright.sync_api import sync_playwright

    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(zip_path) as z:
            z.extractall(tmp)
        page_url = (Path(tmp) / TOP / "web" / "cek.html").as_uri()
        with sync_playwright() as p:
            b = p.chromium.launch(channel="chrome")
            ctx = b.new_context(viewport={"width": 390, "height": 844}, is_mobile=True)
            ctx.set_offline(True)  # jaringan putus sepenuhnya
            pg = ctx.new_page()
            errs: list[str] = []
            pg.on("pageerror", lambda e: errs.append(str(e)))
            pg.goto(page_url)
            pg.wait_for_function("window.HalioLocal && window.HalioLocal.available", timeout=10000)
            results = []
            for text, want in (
                ("Ada video Presiden bagi-bagi bantuan tunai, daftar lewat WA dan bayar biaya admin Rp150 ribu. SEBARKAN!!", "terbukti_salah"),
                ("Polisi kirim surat tilang digital lewat WhatsApp, pasang file apk ini untuk lihat dendanya", "terbukti_salah"),
                ("Besok Jakarta akan diguyur hujan es sebesar bola tenis menurut ramalan warga.", "belum_ada_pemeriksaan"),
            ):
                pg.fill("#msg", text)
                pg.click("#go")
                pg.wait_for_selector(".verdict-card", timeout=10000)
                got = pg.evaluate("document.querySelector('.verdict-card').className.replace('verdict-card','').trim()")
                banner = pg.locator(".mode-banner:has-text('Mode luring')").count()
                print(f"[paket dari file://, offline] {want:24} -> {got:24} banner luring={banner}")
                results.append(got == want and banner == 1)
                pg.click("#check-again")
            b.close()
    if errs:
        print("pageerror:", errs[:2])
    ok = all(results) and not errs
    print("OK" if ok else "GAGAL")
    return 0 if ok else 1


def main() -> int:
    z = build()
    return selftest(z) if "--selftest" in sys.argv else 0


if __name__ == "__main__":
    raise SystemExit(main())
