"""Ambil tangkapan layar untuk README dari server dev yang sedang jalan (http://127.0.0.1:8000).

    python scripts/make_readme_shots.py

Keluaran: docs/img/*.png. Radar memakai data simulasi (scripts/seed_demo.py) dan diberi label di README.
Kartu contoh yang dihasilkan ditandatangani kunci lokal; verifikasi dengan kunci publik server yang sama.
"""

from __future__ import annotations

import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "img"
BASE = "http://127.0.0.1:8000"
OUT.mkdir(parents=True, exist_ok=True)

CALO = "Bisa bantu masuk bintara TNI lwt kenalan perwira, dijamin lulus, ada uang pelicin 150 juta"
APK = "Surat dinas Kodam: harap buka SuratDinas_Kodam.apk dan install sekarang, daftar lewat rekrutmen-tniad.xyz"


def check(page, text: str, name: str, mobile: bool = False) -> None:
    page.goto(f"{BASE}/cek.html")
    page.fill("#msg", text)
    page.click("#go")
    page.wait_for_selector("#result:not(.hidden)", timeout=30000)
    page.wait_for_timeout(1200)
    # tangkap kartu hasilnya saja (utuh, termasuk peringatan forensik di bagian bawah)
    page.locator("#result").screenshot(path=str(OUT / name))


def uji_sheet(page) -> None:
    # Medan Uji: jalankan semua kartu
    page.goto(f"{BASE}/uji.html")
    page.wait_for_selector("[data-nama] button")
    for b in page.locator("[data-nama] button").all():
        b.click()
        page.wait_for_timeout(700)
    page.wait_for_timeout(2500)
    # susun kartu uji utuh jadi dua kolom (tanpa memotong kartu di tengah)
    from PIL import Image
    import io

    shots = [Image.open(io.BytesIO(c.screenshot())).convert("RGB") for c in page.locator("[data-nama]").all()]
    cols = [shots[:4], shots[4:]]
    gap, width = 24, shots[0].width
    height = max(sum(i.height for i in col) + gap * (len(col) - 1) for col in cols)
    sheet = Image.new("RGB", (width * 2 + gap * 3, height + gap * 2), (248, 243, 240))
    for ci, col in enumerate(cols):
        y = gap
        for im in col:
            sheet.paste(im, (gap + ci * (width + gap), y))
            y += im.height + gap
    sheet.save(OUT / "medan-uji.png", optimize=True)



def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome")
        desk = browser.new_context(viewport={"width": 1280, "height": 860}, device_scale_factor=1.5, locale="id-ID")
        page = desk.new_page()

        if "--uji" in sys.argv:  # hanya tangkapan Medan Uji (mis. setelah AI diaktifkan)
            uji_sheet(page)
            browser.close()
            return 0

        check(page, CALO, "cek-calo-tni.png")
        # kartu Halio bertanda tangan dari hasil yang sama
        cid = page.evaluate("() => document.querySelector('#result').innerHTML.match(/api\\/card\\/([0-9a-f]{32})/)?.[1] || ''")
        if not cid:
            r = page.request.post(f"{BASE}/api/check", data={"text": CALO, "channel": "web"})
            cid = r.json()["id"]
        card = page.request.get(f"{BASE}/api/card/{cid}.png").body()
        (OUT / "kartu-halio-contoh.png").write_bytes(card)
        flipped = bytearray(card)
        flipped[len(flipped) // 2] ^= 1
        (OUT / "kartu-halio-diubah.png").write_bytes(bytes(flipped))

        check(page, APK, "cek-apk-forensik.png")

        uji_sheet(page)

        # Verifikasi: kartu asli, lalu diubah 1 byte
        page.goto(f"{BASE}/verifikasi.html")
        page.set_input_files("#file", str(OUT / "kartu-halio-contoh.png"))
        page.wait_for_selector(".verdict.ok", timeout=15000)
        page.wait_for_timeout(400)
        page.screenshot(path=str(OUT / "verifikasi-sah.png"), full_page=True)
        page.click("#tamper")
        page.wait_for_selector(".verdict.bad", timeout=15000)
        page.wait_for_timeout(400)
        page.screenshot(path=str(OUT / "verifikasi-ditolak.png"), full_page=True)

        # Radar (data simulasi)
        page.set_viewport_size({"width": 1440, "height": 1000})
        page.goto(f"{BASE}/radar.html")
        page.wait_for_selector("#metrics .metric, #metrics > *", timeout=15000)
        page.wait_for_timeout(2000)
        page.screenshot(path=str(OUT / "radar-simulasi.png"), full_page=False)

        # Seluler: layar sentuh adalah kanal utama
        phone = browser.new_context(viewport={"width": 390, "height": 844}, device_scale_factor=3, is_mobile=True, has_touch=True, locale="id-ID")
        mp = phone.new_page()
        check(mp, CALO, "cek-calo-tni-hp.png", mobile=True)
        browser.close()
    print("ok:", ", ".join(sorted(f.name for f in OUT.glob("*.png"))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
