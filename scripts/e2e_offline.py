"""Uji end-to-end mode luring di browser sungguhan (Chrome via Playwright), HP 390x844.

    pip install playwright            # sekali; pake Chrome yg udah terpasang (channel="chrome")
    python scripts/e2e_offline.py [folder_screenshot]

Alur: nyalain server Halio lokal (profil T1) -> buka beranda & halaman cek (service worker kepasang) -> PUTUS jaringan browser ->
reload -> cek 3 pesan -> cocokin vonisnya dgn jawaban server utk teks yg sama. Exit code 1 kalo ada yg meleset.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
PORT = int(os.getenv("E2E_PORT", "8012"))
BASE = f"http://localhost:{PORT}"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "e2e_out"
OUT.mkdir(parents=True, exist_ok=True)

MESSAGES = [
    ("hoaks di korpus", "Ada video Presiden bagi-bagi bantuan tunai, daftar lewat WA dan bayar biaya admin Rp150 ribu. SEBARKAN!!", "terbukti_salah"),
    ("sapaan/opini", "Selamat pagi semua, semoga hari ini menyenangkan.", "tidak_yakin"),
    ("di luar korpus", "Besok Jakarta akan diguyur hujan es sebesar bola tenis menurut ramalan warga.", None),
]


def server_check(text: str) -> dict:
    req = urllib.request.Request(f"{BASE}/api/check", data=json.dumps({"text": text, "mode": "tanpa_ai"}).encode(), headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=30))


def main() -> int:
    env = dict(os.environ, HALIO_LLM="0", HALIO_MEDIA="0", HALIO_LINK_CHECK="0", HALIO_SENSOR="0", HALIO_DB=str(OUT / "e2e.db"))
    srv = subprocess.Popen([sys.executable, "-m", "uvicorn", "halio.api:app", "--port", str(PORT)], cwd=ROOT / "backend", env=env,
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    failures: list[str] = []
    try:
        for _ in range(40):
            try:
                urllib.request.urlopen(f"{BASE}/health", timeout=2)
                break
            except Exception:
                time.sleep(0.5)
        expected = [server_check(t)["status"] for _, t, _ in MESSAGES]  # jawaban server utk teks yg sama (pembanding)

        with sync_playwright() as p:
            browser = p.chromium.launch(channel="chrome")
            ctx = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=2, is_mobile=True, has_touch=True)
            page = ctx.new_page()
            errors: list[str] = []
            page.on("pageerror", lambda e: errors.append(str(e)))

            # 1) online: beranda -> cek (service worker ke-cache) dan jawaban datang dr server
            page.goto(f"{BASE}/index.html")
            page.wait_for_function("navigator.serviceWorker && navigator.serviceWorker.ready.then(() => true)", timeout=15000)
            page.goto(f"{BASE}/cek.html")
            page.wait_for_function("navigator.serviceWorker.controller !== null || true")
            page.evaluate("navigator.serviceWorker.ready")
            page.reload()
            page.wait_for_function("navigator.serviceWorker.controller !== null", timeout=15000)
            page.fill("#msg", MESSAGES[0][1])
            page.click("#go")
            page.wait_for_selector(".verdict-card", timeout=20000)
            if page.locator(".mode-banner:has-text('Mode luring')").count():
                failures.append("online tapi tampil banner luring")
            page.screenshot(path=str(OUT / "01_online.png"))

            # 2) PUTUS jaringan, reload dr cache service worker
            ctx.set_offline(True)
            page.reload()
            page.wait_for_selector("#msg", timeout=15000)
            ready = page.evaluate("Boolean(window.HalioLocal && window.HalioLocal.available)")
            if not ready:
                failures.append("mesin luring tidak tersedia saat offline")
            for (name, text, want), srv_status in zip(MESSAGES, expected):
                page.fill("#msg", text)
                page.click("#go")
                page.wait_for_selector(".mode-banner:has-text('Mode luring')", timeout=15000)
                got = page.evaluate("document.querySelector('.verdict-card').className.replace('verdict-card','').trim()")
                print(f"[offline] {name}: luring={got} server={srv_status}")
                if got != srv_status:
                    failures.append(f"{name}: luring={got} != server={srv_status}")
                if want and got != want:
                    failures.append(f"{name}: harusnya {want}, dapat {got}")
                page.screenshot(path=str(OUT / f"02_offline_{name.split()[0]}.png"), full_page=True)
                page.click("#check-again")
            # 3) tombol yg butuh server harus jujur, bukan nge-hang
            if page.locator("#appeal, #human").count():
                failures.append("tombol banding/pemeriksa manusia muncul pada hasil luring")
            if errors:
                failures.append("pageerror: " + "; ".join(errors[:3]))
            browser.close()
    finally:
        srv.terminate()
    if failures:
        print("GAGAL:\n - " + "\n - ".join(failures))
        return 1
    print("OK: mode luring sama dgn server pada semua pesan uji, tanpa jaringan")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
