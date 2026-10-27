"""Kartu Halio: a 1080x1080 correction card sized for WhatsApp family groups."""

from __future__ import annotations

import io
import re
import textwrap
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SIZE = 1080
PAD = 72
THEME = {
    "terbukti_salah": ("#B42318", "TERBUKTI SALAH"),
    "tidak_yakin": ("#B54708", "HALIO TIDAK YAKIN"),
    "belum_ada_pemeriksaan": ("#475467", "BELUM ADA PEMERIKSAAN"),
}
INK, MUTED, PAPER = "#101828", "#475467", "#FFFFFF"

_FONT_CANDIDATES = [
    "C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/System/Library/Fonts/Supplemental/Arial.ttf",
]
_BOLD_CANDIDATES = [
    "C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
]


@lru_cache(maxsize=32)
def _font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    for p in _BOLD_CANDIDATES if bold else _FONT_CANDIDATES:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default(size=size)


_NO_GLYPH = re.compile("[\U00010000-\U0010FFFF☀-➿⬀-⯿️‍⃣]")


def _printable(text: str) -> str:
    """Drop emoji and symbols the card fonts cannot draw (they would render as boxes)."""
    return re.sub(r"\s{2,}", " ", _NO_GLYPH.sub("", text)).strip()


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, width: int, max_lines: int) -> list[str]:
    text = _printable(text)
    avg = max(1, int(draw.textlength("abcdefghij", font=font) / 10))
    lines = textwrap.wrap(text, width=max(10, int(width * 0.9) // avg))
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(" .,") + "…"
    return lines


def _block(draw, y: int, text: str, font, fill: str, max_lines: int, gap: int = 10) -> int:
    for line in _wrap(draw, text, font, SIZE - 2 * PAD, max_lines):
        draw.text((PAD, y), line, font=font, fill=fill)
        y += font.size + gap
    return y


def render(result: dict) -> bytes:
    color, title = THEME[result["status"]]
    img = Image.new("RGB", (SIZE, SIZE), PAPER)
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, SIZE, 190], fill=color)
    d.text((PAD, 48), title, font=_font(64, bold=True), fill=PAPER)
    d.text((PAD, 128), "Dicek dengan Halio", font=_font(30), fill=PAPER)

    y = 240
    d.text((PAD, y), "Pesan yang beredar:", font=_font(30, bold=True), fill=MUTED)
    y = _block(d, y + 46, f"“{result['claim']}”", _font(36), INK, max_lines=4) + 24

    match = result.get("match")
    if match:
        d.text((PAD, y), "Faktanya:", font=_font(30, bold=True), fill=MUTED)
        y = _block(d, y + 46, match["sederhana"], _font(40, bold=True), INK, max_lines=5) + 24
        src = match["sumber"][0]
        d.text((PAD, y), "Sumber:", font=_font(28, bold=True), fill=MUTED)
        y = _block(d, y + 40, src["nama"], _font(28), INK, max_lines=2, gap=6)
        domain = src["url"].split("//")[-1].split("/")[0].removeprefix("www.")
        d.text((PAD, y + 4), domain, font=_font(26), fill=MUTED)
    else:
        if result["status"] == "belum_ada_pemeriksaan":
            msg = "Belum ada pemeriksa fakta yang memeriksa pesan ini. Halio tidak menebak. Tahan dulu, jangan diteruskan."
        elif result.get("reason") == "terlalu_pendek":
            msg = "Pesan terlalu pendek atau hanya tautan, jadi belum bisa dicek. Jangan klik tautan yang tidak jelas."
        else:
            msg = "Ini lebih mirip pendapat atau salam, bukan kabar yang bisa dicek. Halio tidak menilai pendapat."
        y = _block(d, y, msg, _font(40, bold=True), INK, max_lines=6)

    d.line([PAD, SIZE - 130, SIZE - PAD, SIZE - 130], fill="#EAECF0", width=3)
    d.text((PAD, SIZE - 105), f"{result['created'][:10]}  ·  Bukan vonis Halio: cek sumbernya.", font=_font(26), fill=MUTED)

    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    return buf.getvalue()
