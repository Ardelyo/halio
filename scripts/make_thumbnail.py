"""Submission thumbnail: 1200x630 px, PNG/JPG, <= 500 KB (Rulebook section G.2).

    python scripts/make_thumbnail.py   ->  docs/submission/thumbnail.jpg

Brand system: video/BRAND.md. Background is the generated field from video/tools/make_fields.py.
"""

from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from halio.card import BLUE, CREAM, INK, draw_mark, font  # noqa: E402

W, H = 1200, 630
out = ROOT / "docs" / "submission" / "thumbnail.jpg"
out.parent.mkdir(parents=True, exist_ok=True)

field = ROOT / "video" / "assets" / "field-day.jpg"
img = Image.open(field).convert("RGB").resize((1200, 675)).crop((0, 20, W, H + 20)) if field.exists() else Image.new("RGB", (W, H), CREAM)
# cream wash on the sky so ink type reads cleanly
wash = Image.new("RGBA", (W, H), (248, 243, 240, 0))
dw = ImageDraw.Draw(wash)
for y in range(H):
    dw.line([(0, y), (W, y)], fill=(248, 243, 240, int(190 * max(0.0, 1 - y / 430))))
img = Image.alpha_composite(img.convert("RGBA"), wash).convert("RGB")
d = ImageDraw.Draw(img)

draw_mark(img, 64, 56, 84)
wf = font("serif", 92)
d.text((166, 50), "halio", font=wf, fill=INK)
d.text((166 + d.textlength("halio", font=wf), 50), ".", font=wf, fill=BLUE)

sf = font("serif", 70)
d.text((64, 196), "Keluarga sebagai lini pertama", font=sf, fill=INK)
d.text((64, 268), "pertahanan ", font=sf, fill=INK)
from PIL import ImageFont  # noqa: E402
try:
    it = ImageFont.truetype(str(ROOT / "video" / "fonts" / "InstrumentSerif-italic-latin.woff2"), 70)
except OSError:
    it = sf
d.text((64 + d.textlength("pertahanan ", font=sf), 268), "kognitif.", font=it, fill=BLUE)

tag = "Cek pesan untuk keluarga · sensor narasi untuk satuan siber"
tf = font("medium", 26)
d.rounded_rectangle([56, 384, 56 + d.textlength(tag, font=tf) + 36, 432], radius=24, fill=CREAM)
d.text((74, 393), tag, font=tf, fill=INK)

y = 520
x = 64
for label, color in [("TERBUKTI SALAH", "#B42318"), ("TIDAK YAKIN", "#B54708"), ("BELUM ADA PEMERIKSAAN", "#475467")]:
    f = font("display", 22)
    w = d.textlength(label, font=f) + 40
    d.rounded_rectangle([x, y, x + w, y + 46], radius=23, fill=color)
    d.text((x + 20, y + 10), label, font=f, fill=CREAM)
    x += w + 14
hf = font("semibold", 17)
label = "KARTIKA CYBER HACKATHON 2026 · SIBER SOSIAL"
lw = d.textlength(label, font=hf)
d.rounded_rectangle([W - 64 - lw - 40, 64, W - 64, 106], radius=21, fill=BLUE)
d.text((W - 64 - lw - 20, 76), label, font=hf, fill=CREAM)

img.save(out, quality=90, optimize=True, progressive=True)
size = out.stat().st_size
print(f"{out.relative_to(ROOT)}  {size / 1024:.0f} KB  {'OK' if size <= 500 * 1024 else 'TOO LARGE (>500 KB)'}")
