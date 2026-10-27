"""Submission thumbnail: 1200x630 px, PNG/JPG, <= 500 KB (Rulebook section G.2).

    python scripts/make_thumbnail.py   ->  docs/submission/thumbnail.png
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from halio.card import _font  # noqa: E402

W, H = 1200, 630
out = ROOT / "docs" / "submission" / "thumbnail.png"
out.parent.mkdir(parents=True, exist_ok=True)

img = Image.new("RGB", (W, H), "#0c111d")
d = ImageDraw.Draw(img)
d.rectangle([0, 0, 14, H], fill="#1d4ed8")
icon = Image.open(ROOT / "web" / "icons" / "icon-192.png").convert("RGBA").resize((120, 120))
img.paste(icon, (80, 80), icon)
d.text((230, 86), "Halio", font=_font(96, bold=True), fill="#ffffff")
d.text((80, 250), "Keluarga sebagai lini pertama", font=_font(52, bold=True), fill="#ffffff")
d.text((80, 318), "pertahanan kognitif", font=_font(52, bold=True), fill="#ffffff")
d.text((80, 420), "Teruskan pesan → jawaban jujur bersumber, kartu, dan suara.", font=_font(30), fill="#cecfd2")
d.text((80, 462), "Radar tren hoaks anonim untuk satuan siber.", font=_font(30), fill="#cecfd2")
d.text((80, 548), "Kartika Cyber Hackathon 2026 · Siber Sosial", font=_font(26), fill="#94969c")
for i, (label, color) in enumerate([("TERBUKTI SALAH", "#f97066"), ("TIDAK YAKIN", "#fdb022"), ("BELUM ADA PEMERIKSAAN", "#cecfd2")]):
    y = 64 + i * 52
    d.rounded_rectangle([780, y, 1130, y + 42], radius=21, outline=color, width=3)
    d.text((800, y + 6), label, font=_font(24, bold=True), fill=color)

img.save(out, optimize=True)
size = out.stat().st_size
print(f"{out.relative_to(ROOT)}  {size / 1024:.0f} KB  {'OK' if size <= 500 * 1024 else 'TOO LARGE (>500 KB)'}")
