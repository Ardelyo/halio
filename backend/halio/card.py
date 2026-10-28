"""Kartu Halio: a 1080x1080 correction card sized for WhatsApp family groups.

Brand system: video/BRAND.md (Royal Blue, Light Cream, Instrument Serif / Archivo / Inter).
Fonts ship in halio/fonts (SIL OFL) so the card looks the same on every server.
"""

from __future__ import annotations

import io
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SIZE = 1080
PAD = 80
FONT_DIR = Path(__file__).resolve().parent / "fonts"

BLUE, CREAM, INK, MUTED, LINE, SUN = "#014BAA", "#F8F3F0", "#0E1726", "#5B6475", "#E7E1DC", "#FFC83D"
THEME = {
    "terbukti_salah": ("#B42318", "TERBUKTI SALAH"),
    "tidak_yakin": ("#B54708", "HALIO TIDAK YAKIN"),
    "belum_ada_pemeriksaan": ("#475467", "BELUM ADA PEMERIKSAAN"),
}

_FILES = {
    "serif": "InstrumentSerif-Regular.ttf",
    "display": "Archivo-SemiExpanded-ExtraBold.ttf",
    "regular": "Inter-Regular.ttf",
    "medium": "Inter-Medium.ttf",
    "semibold": "Inter-SemiBold.ttf",
    "bold": "Inter-Bold.ttf",
}
_FALLBACK = ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "C:/Windows/Fonts/arial.ttf"]


@lru_cache(maxsize=64)
def font(role: str, size: int) -> ImageFont.FreeTypeFont:
    path = FONT_DIR / _FILES[role]
    if path.exists():
        return ImageFont.truetype(str(path), size)
    for p in _FALLBACK:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size=size)


def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Kept for scripts/make_thumbnail.py."""
    return font("bold" if bold else "medium", size)


def _wrap(draw: ImageDraw.ImageDraw, text: str, f, width: int, max_lines: int) -> list[str]:
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=f) <= width or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(" .,") + "…"
    return lines


def _block(draw, y: int, text: str, f, fill: str, max_lines: int, leading: float = 1.22) -> int:
    for line in _wrap(draw, text, f, SIZE - 2 * PAD, max_lines):
        draw.text((PAD, y), line, font=f, fill=fill)
        y += int(f.size * leading)
    return y


def _label(draw, y: int, text: str) -> int:
    f = font("semibold", 22)
    x = PAD
    for ch in text.upper():  # letter-spaced micro label
        draw.text((x, y), ch, font=f, fill=MUTED)
        x += draw.textlength(ch, font=f) + 3
    return y + 40


def draw_mark(img: Image.Image, x: int, y: int, s: int) -> None:
    """The Halio mark (video/assets/halio-mark.svg) drawn with primitives, s = side in px."""
    k = s / 128
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([x, y, x + s, y + s], radius=int(36 * k), fill=BLUE)
    d.ellipse([x + 24 * k, y + 25 * k, x + 104 * k, y + 94 * k], fill=CREAM)
    d.polygon([(x + 40 * k, y + 80 * k), (x + 33 * k, y + 103 * k), (x + 58 * k, y + 91 * k)], fill=CREAM)
    for cx in (50, 78):
        d.ellipse([x + (cx - 5.5) * k, y + 44.5 * k, x + (cx + 5.5) * k, y + 55.5 * k], fill=BLUE)
    d.line([(x + 47 * k, y + 65 * k), (x + 58 * k, y + 75 * k), (x + 81 * k, y + 56 * k)], fill=BLUE,
           width=max(2, int(8.5 * k)), joint="curve")
    d.ellipse([x + 92 * k, y + 14 * k, x + 114 * k, y + 36 * k], fill=SUN)


def render(result: dict) -> bytes:
    color, title = THEME[result["status"]]
    img = Image.new("RGB", (SIZE, SIZE), CREAM)
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, SIZE, 210], fill=color)
    size = 64
    while size > 36 and d.textlength(title, font=font("display", size)) > SIZE - 2 * PAD:
        size -= 2
    d.text((PAD, 52 + (64 - size) // 2), title, font=font("display", size), fill=CREAM)
    d.text((PAD, 138), "Dicek dengan Halio", font=font("medium", 30), fill="#F3E6E1")

    y = _label(d, 262, "Pesan yang beredar")
    y = _block(d, y, f"“{result['claim']}”", font("serif", 46), INK, max_lines=4, leading=1.12) + 30

    match = result.get("match")
    if match:
        y = _label(d, y, "Faktanya")
        y = _block(d, y, match["sederhana"], font("semibold", 38), INK, max_lines=5) + 26
        src = match["sumber"][0]
        y = _label(d, y, "Sumber")
        y = _block(d, y, src["nama"], font("medium", 28), INK, max_lines=2)
        domain = src["url"].split("//")[-1].split("/")[0].removeprefix("www.")
        d.text((PAD, y + 2), domain, font=font("regular", 26), fill=BLUE)
    else:
        msg = (
            "Belum ada pemeriksa fakta yang memeriksa pesan ini. Halio tidak menebak. Tahan dulu, jangan diteruskan."
            if result["status"] == "belum_ada_pemeriksaan"
            else "Ini lebih mirip pendapat atau salam, bukan kabar yang bisa dicek. Halio tidak menilai pendapat."
        )
        y = _label(d, y, "Kata Halio")
        _block(d, y, msg, font("semibold", 40), INK, max_lines=6)

    d.line([PAD, SIZE - 140, SIZE - PAD, SIZE - 140], fill=LINE, width=3)
    d.text((PAD, SIZE - 98), f"{result['created'][:10]}  ·  Bukan vonis Halio: cek sumbernya.", font=font("regular", 24), fill=MUTED)
    wf = font("serif", 52)
    word_w = d.textlength("halio", font=wf)
    dot_w = d.textlength(".", font=wf)
    wx = SIZE - PAD - word_w - dot_w
    d.text((wx, SIZE - 118), "halio", font=wf, fill=INK)
    d.text((wx + word_w, SIZE - 118), ".", font=wf, fill=BLUE)
    draw_mark(img, int(wx - 70), SIZE - 112, 54)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
