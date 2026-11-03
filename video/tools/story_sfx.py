"""Sound design for the 9:16 story teaser: every effect is synthesised here (no sample packs).

    python video/tools/story_sfx.py   ->  video/out/story-sfx.wav (48 kHz stereo, 25 s)

Cue times mirror the cuts in video/story/story.js (beat = 0.4 s, bar hits at 0.41 + 1.6k s).
"""

from __future__ import annotations

import wave
from pathlib import Path

import numpy as np

SR = 48000
DUR = 25.0
OUT = Path(__file__).resolve().parents[1] / "out" / "story-sfx.wav"
RNG = np.random.default_rng(2026)
D = lambda k: 0.41 + 1.6 * k  # noqa: E731

mix = np.zeros((int(SR * (DUR + 3)), 2), np.float32)


def put(t: float, sig: np.ndarray, gain: float = 1.0, pan: float = 0.0) -> None:
    """Add a mono or stereo signal at time t; pan -1 (left) .. 1 (right)."""
    if sig.ndim == 1:
        l, r = np.sqrt((1 - pan) / 2), np.sqrt((1 + pan) / 2)
        sig = np.stack([sig * l, sig * r], 1)
    s = int(t * SR)
    if s >= len(mix):
        return
    n = min(len(sig), len(mix) - s)
    mix[s:s + n] += sig[:n] * gain


def tvec(dur: float) -> np.ndarray:
    return np.arange(int(dur * SR)) / SR


def band_noise(dur: float, f0: float, f1: float, width: float = 0.35) -> np.ndarray:
    """White noise through a band-pass whose centre glides from f0 to f1 (log), via STFT masking."""
    n = int(dur * SR)
    N, hop = 2048, 512
    x = RNG.standard_normal(n + N).astype(np.float32)
    win = np.hanning(N).astype(np.float32)
    freqs = np.fft.rfftfreq(N, 1 / SR)
    out = np.zeros(n + N, np.float32)
    norm = np.zeros(n + N, np.float32)
    frames = max(1, (n) // hop)
    for i in range(frames + 1):
        a = i * hop
        p = min(1.0, a / max(1, n))
        fc = np.exp(np.log(f0) + (np.log(f1) - np.log(f0)) * p)
        mask = np.exp(-0.5 * (np.log(np.maximum(freqs, 1) / fc) / width) ** 2)
        spec = np.fft.rfft(x[a:a + N] * win) * mask
        out[a:a + N] += np.fft.irfft(spec, N).astype(np.float32) * win
        norm[a:a + N] += win ** 2
    y = out[:n] / np.maximum(norm[:n], 1e-3)
    return y / (np.abs(y).max() + 1e-9)


def env_ar(n: int, attack: float, release: float, curve: float = 2.0) -> np.ndarray:
    a = max(1, int(attack * SR))
    e = np.ones(n, np.float32)
    e[:a] = np.linspace(0, 1, a) ** curve
    r = max(1, int(release * SR))
    e[-r:] *= np.linspace(1, 0, r) ** curve
    return e


def reverb(sig: np.ndarray, length: float = 1.2, mix_: float = 0.25) -> np.ndarray:
    ir_n = int(length * SR)
    ir = RNG.standard_normal(ir_n).astype(np.float32) * np.exp(-np.arange(ir_n) / SR * (6.0 / length))
    ir /= np.sqrt((ir ** 2).sum())
    wet = np.fft.irfft(np.fft.rfft(sig, len(sig) + ir_n) * np.fft.rfft(ir, len(sig) + ir_n))[: len(sig) + ir_n]
    dry = np.concatenate([sig, np.zeros(ir_n, np.float32)])
    return (dry * (1 - mix_) + wet.astype(np.float32) * mix_ * 3).astype(np.float32)


# ---------- instruments ----------
def whoosh(dur: float, up: bool = True, bright: float = 1.0) -> np.ndarray:
    f0, f1 = (350, 5200 * bright) if up else (5200 * bright, 300)
    y = band_noise(dur, f0, f1, 0.45)
    n = len(y)
    e = np.minimum(np.linspace(0, 1, n) / 0.7, 1) ** 2 * np.minimum(np.linspace(1, 0, n) / 0.3, 1)
    return y * e


def impact(power: float = 1.0, tail: float = 0.9) -> np.ndarray:
    t = tvec(tail)
    f = 38 + 50 * np.exp(-t * 18)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4.5)
    body = band_noise(tail, 260, 120, 0.6) * np.exp(-t * 22) * 0.6
    click = np.zeros_like(t)
    click[: int(0.004 * SR)] = RNG.standard_normal(int(0.004 * SR)) * 0.8
    sig = (sub * 0.9 + body + click) * power
    return reverb(sig.astype(np.float32), 0.8, 0.18)


def boom() -> np.ndarray:
    t = tvec(2.6)
    f = 30 + 45 * np.exp(-t * 6)
    sub = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.6)
    crack = band_noise(2.6, 3000, 200, 0.7) * np.exp(-t * 7) * 0.7
    return reverb(((sub + crack) * 1.4).astype(np.float32), 2.4, 0.35)


def riser(dur: float) -> np.ndarray:
    t = tvec(dur)
    noise = band_noise(dur, 300, 9000, 0.4)
    f = 180 * (8 ** (t / dur))
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35
    trem = 0.6 + 0.4 * np.sin(2 * np.pi * np.cumsum(4 + 22 * (t / dur) ** 2) / SR)
    e = (t / dur) ** 2.2
    return ((noise * 0.8 + tone) * trem * e).astype(np.float32)


def swell(dur: float) -> np.ndarray:
    """Reverse-cymbal style swell that ends exactly on the next hit."""
    t = tvec(dur)
    y = band_noise(dur, 7000, 5000, 0.5) * (t / dur) ** 3
    return y.astype(np.float32)


def pop(freq: float = 700, dur: float = 0.12) -> np.ndarray:
    t = tvec(dur)
    f = freq * (1 + 0.6 * np.exp(-t * 60))
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40)).astype(np.float32)


def chime() -> np.ndarray:
    a, b = pop(1320, 0.35), pop(1760, 0.45)
    out = np.zeros(int(0.6 * SR), np.float32)
    out[: len(a)] += a * 0.7
    s = int(0.09 * SR)
    out[s:s + len(b)] += b * 0.6
    return reverb(out, 0.6, 0.3)


def tick() -> np.ndarray:
    n = int(0.006 * SR)
    return (RNG.standard_normal(n) * np.exp(-np.arange(n) / n * 5)).astype(np.float32) * 0.6


def shutter() -> np.ndarray:
    out = np.zeros(int(0.15 * SR), np.float32)
    for off in (0.0, 0.045):
        c = band_noise(0.03, 3500, 2500, 0.5) * np.exp(-tvec(0.03) * 120)
        s = int(off * SR)
        out[s:s + len(c)] += c
    return out


def glitch(dur: float = 0.16) -> np.ndarray:
    t = tvec(dur)
    sq = np.sign(np.sin(2 * np.pi * (220 + 900 * RNG.random()) * t))
    gate = (np.floor(t * 60) % 2).astype(np.float32)
    crushed = np.round(band_noise(dur, 1500, 4000, 0.8) * 4) / 4
    return ((sq * 0.4 + crushed * 0.6) * gate * env_ar(len(t), 0.002, 0.03)).astype(np.float32)


def shimmer(dur: float = 2.0, base: float = 1760) -> np.ndarray:
    t = tvec(dur)
    out = np.zeros((len(t), 2), np.float32)
    for i, ratio in enumerate([1, 1.25, 1.5, 2, 2.5, 3]):
        ph = RNG.random() * 6.28
        s = np.sin(2 * np.pi * base * ratio * t * (1 + 0.003 * np.sin(2 * np.pi * 5 * t + ph)) + ph) * np.exp(-t * (1.2 + i * 0.3))
        pan = (i % 2) * 2 - 1
        out[:, 0] += s * (0.6 - 0.3 * pan) / 6
        out[:, 1] += s * (0.6 + 0.3 * pan) / 6
    return out * env_ar(len(t), 0.02, 0.3)[:, None]


def heartbeat() -> np.ndarray:
    out = np.zeros(int(0.6 * SR), np.float32)
    for off, g in ((0.0, 1.0), (0.17, 0.7)):
        t = tvec(0.25)
        th = np.sin(2 * np.pi * (55 + 30 * np.exp(-t * 30)) * t) * np.exp(-t * 18) * g
        s = int(off * SR)
        out[s:s + len(th)] += th
    return out


def drone(dur: float) -> np.ndarray:
    t = tvec(dur)
    y = np.sin(2 * np.pi * 55 * t) * 0.6 + np.sin(2 * np.pi * 110.4 * t) * 0.3 + band_noise(dur, 200, 600, 0.5) * 0.15
    return (y * env_ar(len(t), 0.3, 0.5)).astype(np.float32)


# ---------- the cue sheet (mirrors story.js) ----------
def build() -> np.ndarray:
    put(0.0, glitch(0.12), 0.25)
    put(0.0, swell(0.41), 0.35)
    for k, t in enumerate([0.41, 0.81, 1.21]):
        put(t, chime(), 0.45, pan=[-0.4, 0.4, 0.0][k])
    put(0.41, impact(0.5), 0.6)
    put(1.61, pop(1100), 0.35)

    put(2.01, whoosh(0.42, True, 1.2), 0.9, pan=-0.2)
    put(2.41, impact(1.0), 0.9)
    put(2.81, pop(520, 0.2), 0.7)
    put(2.81, impact(0.7), 0.7)

    for i, t in enumerate([3.61, 4.01, 4.41, 4.81]):
        put(t - 0.12, whoosh(0.14, True, 1.4), 0.5, pan=0.5 if i % 2 else -0.5)
        put(t, impact(0.85), 0.85)
    put(4.81, glitch(0.2), 0.45)

    put(5.21, riser(1.6), 0.55)
    for i in range(7):
        put(5.35 + i * 0.2, whoosh(0.25, i % 2 == 0, 1.3), 0.45, pan=(-1) ** i * 0.7)
    put(6.81, impact(0.6), 0.7)
    put(6.81, whoosh(0.9, False, 0.8), 0.6)
    for t in (7.06, 7.56):
        put(t, tick(), 0.4)

    put(8.41, impact(0.55, 1.2), 0.7)
    for ring, t in enumerate([8.81, 9.21, 9.61]):
        for j in range(4 + ring * 3):
            put(t + j * 0.02, pop(600 + ring * 220 + j * 25, 0.09), 0.16, pan=np.sin(j * 1.7) * 0.8)

    put(10.01, impact(0.75), 0.75)
    put(10.01, whoosh(1.1, True, 0.9), 0.55, pan=0.3)

    for i, t in enumerate([11.61, 12.01, 12.41, 12.81]):
        put(t, shutter(), 0.6, pan=(-1) ** i * 0.3)
        put(t - 0.1, whoosh(0.12, True, 1.5), 0.45)
        put(t, impact(0.5), 0.55)

    put(13.21, impact(0.35, 1.4), 0.5)
    put(13.21, shimmer(1.4, 1320), 0.3)

    put(14.81, drone(1.6), 0.45)
    put(15.01, shimmer(1.4, 2093), 0.45)
    put(15.0, whoosh(1.2, True, 0.7), 0.25)

    for i, t in enumerate([16.41, 16.81, 17.21, 17.61]):
        put(t - 0.12, whoosh(0.14, True, 1.4), 0.5, pan=0.5 if i % 2 else -0.5)
        put(t, impact(0.9), 0.9)
    put(17.61, glitch(0.22), 0.5)

    put(18.01, whoosh(1.4, True, 0.8), 0.5, pan=-0.3)
    put(18.4, shimmer(1.2, 1568), 0.2)

    put(19.61, riser(1.6), 0.75)
    put(21.21, impact(1.0, 1.4), 1.0)
    for t in (21.21, 21.61, 22.01, 22.21):
        put(t, heartbeat(), 0.9)
    full = "untuk keluarga Indonesia."
    for i in range(len(full)):
        put(21.51 + i * 0.9 / len(full), tick(), 0.3, pan=np.sin(i) * 0.3)
    put(21.91, swell(0.9), 0.7)

    put(22.81, boom(), 1.0)
    put(22.81, whoosh(0.65, False, 1.2), 0.6)
    put(22.85, shimmer(2.2, 1760), 0.5)
    put(23.21, whoosh(0.4, True, 1.0), 0.3)
    put(23.61, tick(), 0.3)
    put(24.41, impact(1.0), 0.95)
    put(24.41, pop(880, 0.18), 0.4)

    out = mix[: int(DUR * SR)]
    return out / (np.abs(out).max() + 1e-9) * 0.7


def main() -> None:
    y = build()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUT), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(y, -1, 1) * 32767).astype("<i2").tobytes())
    print("wrote", OUT)


if __name__ == "__main__":
    main()
