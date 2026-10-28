"""Procedural grass-field backdrops for the Halio video (no stock photos; all generated).

    python video/tools/make_fields.py   ->  video/assets/field-*.jpg
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

OUT = Path(__file__).resolve().parents[1] / "assets"
W, H = 1920, 1080
rng = np.random.default_rng(7)


def noise(w: int, h: int, cell: int, seed: int) -> np.ndarray:
    r = np.random.default_rng(seed)
    gw, gh = max(2, w // cell + 2), max(2, h // cell + 2)
    g = Image.fromarray((r.random((gh, gw)) * 255).astype(np.uint8))
    return np.asarray(g.resize((w, h), Image.BICUBIC), dtype=np.float32) / 255.0


def fbm(w, h, base, octaves, seed):
    out, amp, tot = np.zeros((h, w), np.float32), 1.0, 0.0
    for o in range(octaves):
        out += amp * noise(w, h, max(2, base >> o), seed + o)
        tot += amp
        amp *= 0.55
    return out / tot


def lerp(a, b, t):
    return a + (b - a) * t[..., None]


def grade(img: np.ndarray, warm=0.03, grain=0.05, vignette=0.35, seed=1) -> Image.Image:
    h, w, _ = img.shape
    yy, xx = np.mgrid[0:h, 0:w]
    d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
    img = img * (1 - vignette * np.clip(d - 0.35, 0, 1)[..., None] ** 1.4)
    img[..., 0] += warm
    img[..., 2] -= warm * 0.6
    img = 0.92 * img + 0.06  # lifted blacks: film look
    img += (np.random.default_rng(seed).normal(0, grain, (h, w, 1))).astype(np.float32)
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))


def _texture(size: int, seed: int) -> np.ndarray:
    """Tileable-ish grass texture: fine vertical blades over mid-scale clumps."""
    r = np.random.default_rng(seed)
    blades = r.random((size // 6, size)).astype(np.float32)          # tall cells -> vertical streaks
    blades = np.asarray(Image.fromarray((blades * 255).astype(np.uint8)).resize((size, size), Image.BILINEAR), np.float32) / 255
    clumps = fbm(size, size, 24, 4, seed + 1)
    return 0.55 * blades + 0.45 * clumps


def field_layer(h_top: int, top_rgb, bottom_rgb, seed: int, streak=True, vscale: float = 900.0) -> np.ndarray:
    """Grass from the horizon (row h_top) down, sampled through a perspective projection."""
    rows = H - h_top
    y = np.linspace(0, 1, rows, dtype=np.float32)[:, None]
    base = lerp(np.array(top_rgb, np.float32), np.array(bottom_rgb, np.float32), np.repeat(y, W, 1))
    size = 1024
    tex = _texture(size, seed)
    yy = np.arange(rows, dtype=np.float32)[:, None] + 6.0          # distance below horizon in px
    depth = 420.0 / yy                                               # far rows -> large depth
    xx = (np.arange(W, dtype=np.float32)[None, :] - W / 2)
    u = (xx * depth * 1.4).astype(np.int64) % size
    v = (depth * vscale).astype(np.int64) % size
    detail = tex[v, u]
    # distant rows alias: fade their contrast toward the mean (cheap mip-mapping)
    fade = np.clip(yy / 160.0, 0.0, 1.0) ** 0.8
    detail = (detail - 0.5) * fade
    mottled = fbm(W, rows, 260, 3, seed + 5) - 0.5                 # large lighter/darker patches
    img = base * (1 + detail[..., None] * 0.9 + mottled[..., None] * 0.35)
    # atmospheric haze right at the horizon
    haze = np.clip(1 - yy / 70.0, 0, 1)[..., None] * 0.35
    img = img * (1 - haze) + np.array([0.62, 0.72, 0.62], np.float32) * haze
    return img


def sky(h: int, top, bottom, clouds: float, seed: int, cloud_rgb=(1, 1, 1)) -> np.ndarray:
    y = np.linspace(0, 1, h, dtype=np.float32)[:, None]
    img = lerp(np.array(top, np.float32), np.array(bottom, np.float32), np.repeat(y ** 0.8, W, 1))
    if clouds:
        c = fbm(W, h, 300, 5, seed)
        c = np.clip((c - 0.52) * 4.0, 0, 1) * clouds * (0.4 + 0.6 * y)
        img = img * (1 - c[..., None]) + np.array(cloud_rgb, np.float32) * c[..., None]
    return img


def hills(img: np.ndarray, horizon: int, rgb, height: int, seed: int, haze=0.25, rough=0.0) -> None:
    ridge = horizon - height * (0.35 + 0.65 * fbm(W, 1, 380, 4, seed)[0])
    if rough:
        ridge -= rough * fbm(W, 1, 6, 3, seed + 7)[0]
    ridge = np.asarray(Image.fromarray(ridge[None].astype(np.float32)).resize((W, 1)), np.float32)[0]
    yy = np.arange(H)[:, None]
    mask = (yy >= ridge[None, :]) & (yy < horizon + 4)
    col = np.array(rgb, np.float32) * (1 - haze) + img[max(0, horizon - height - 5), W // 2] * haze
    tex = fbm(W, H, 14, 4, seed + 3)[..., None]
    shade = np.clip((yy - ridge[None, :]) / max(8, height), 0, 1)[..., None]   # lit ridge, darker base
    img[mask] = (col * (1.12 - 0.25 * shade) * (0.85 + 0.3 * tex))[mask]


def make_day() -> Image.Image:
    horizon = 560
    img = np.zeros((H, W, 3), np.float32)
    img[:horizon] = sky(horizon, (0.42, 0.62, 0.86), (0.86, 0.92, 0.96), 0.9, 3)
    hills(img, horizon, (0.24, 0.36, 0.46), 190, 11, haze=0.5)    # far blue mountains
    hills(img, horizon, (0.17, 0.30, 0.36), 110, 12, haze=0.3)    # nearer ridge
    hills(img, horizon, (0.08, 0.20, 0.09), 40, 21, haze=0.0, rough=26)   # tree line
    img[horizon:] = field_layer(horizon, (0.30, 0.52, 0.16), (0.16, 0.42, 0.10), 31)
    return grade(img, warm=0.02, grain=0.035, seed=1)


def make_dusk() -> Image.Image:
    horizon = 610
    img = np.zeros((H, W, 3), np.float32)
    img[:horizon] = sky(horizon, (0.36, 0.42, 0.78), (0.98, 0.66, 0.72), 0.55, 8, cloud_rgb=(1.0, 0.78, 0.82))
    hills(img, horizon, (0.22, 0.45, 0.16), 120, 41, haze=0.0, rough=10)
    img[horizon:] = field_layer(horizon, (0.34, 0.58, 0.18), (0.20, 0.46, 0.12), 51)
    return grade(img, warm=0.03, grain=0.03, seed=2)


def make_meadow() -> Image.Image:
    """Ground only (top-down-ish), like a lawn filling the frame."""
    global H
    full, H = H, H + 260                       # horizon just above the frame
    img = field_layer(0, (0.30, 0.48, 0.20), (0.22, 0.42, 0.13), 61, vscale=5200.0)[260:]
    H = full
    return grade(img, warm=0.03, grain=0.04, vignette=0.45, seed=3).filter(ImageFilter.GaussianBlur(0.4))


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in [("day", make_day), ("dusk", make_dusk), ("meadow", make_meadow)]:
        fn().save(OUT / f"field-{name}.jpg", quality=92)
        print("wrote", OUT / f"field-{name}.jpg")
