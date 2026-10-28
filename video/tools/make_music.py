"""Generate a calm ambient bed for the video (original, procedurally synthesised, no samples).

    python video/tools/make_music.py <seconds>   ->  video/out/music.wav (48 kHz stereo)

Kept quiet (around -24 dBFS RMS) so a voice-over recorded later sits clearly on top.
A gentle low-pass is applied by ffmpeg when the video is assembled (video/tools/render_all.py).
"""

from __future__ import annotations

import sys
import wave
from pathlib import Path

import numpy as np

SR = 48000
OUT = Path(__file__).resolve().parents[1] / "out" / "music.wav"


def midi(n: float) -> float:
    return 440.0 * 2 ** ((n - 69) / 12)


# Fmaj9 - Am7 - Dm9 - Bbmaj7(#11): warm, hopeful, unresolved enough to loop.
CHORDS = [
    [41, 53, 57, 60, 64, 67],
    [45, 52, 55, 60, 64, 67],
    [38, 50, 53, 57, 60, 64],
    [46, 53, 57, 62, 64, 69],
]
CHORD_S = 8.0


def env(n: int, attack: float, release: float) -> np.ndarray:
    a, r = int(attack * SR), int(release * SR)
    e = np.ones(n, np.float32)
    e[:a] = np.linspace(0, 1, a) ** 2
    e[-r:] *= np.linspace(1, 0, r) ** 1.5
    return e


def pad_note(freq: float, dur: float, seed: int) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    rng = np.random.default_rng(seed)
    out = np.zeros((n, 2), np.float32)
    for det, pan in ((-0.0035, 0.25), (0.0035, 0.75), (0.0, 0.5)):
        f = freq * (1 + det)
        ph = rng.random() * 6.28
        vib = 0.0015 * np.sin(2 * np.pi * 0.21 * t + ph)
        sig = np.sin(2 * np.pi * f * t * (1 + vib) + ph) + 0.18 * np.sin(4 * np.pi * f * t + ph) + 0.05 * np.sin(6 * np.pi * f * t)
        out[:, 0] += sig * (1 - pan)
        out[:, 1] += sig * pan
    return out * env(n, 2.2, 3.0)[:, None]


def pluck(freq: float, dur: float = 2.5) -> np.ndarray:
    n = int(dur * SR)
    t = np.arange(n) / SR
    sig = (np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t)) * np.exp(-t * 2.6)
    sig *= env(n, 0.005, 0.4)
    return np.stack([sig * 0.6, sig * 0.4], 1).astype(np.float32)


def build(seconds: float) -> np.ndarray:
    n = int(seconds * SR)
    mix = np.zeros((n + SR * 8, 2), np.float32)
    k = 0
    t = 0.0
    while t < seconds:
        chord = CHORDS[k % len(CHORDS)]
        for i, m in enumerate(chord):
            note = pad_note(midi(m), CHORD_S + 3.0, seed=k * 10 + i) * (0.55 if i == 0 else 0.32)
            s = int(t * SR)
            mix[s:s + len(note)] += note[: len(mix) - s]
        # sparse plucks on upper chord tones, two per beat-pair, gives gentle movement
        for j, m in enumerate([chord[3] + 12, chord[4] + 12, chord[5], chord[4] + 12]):
            s = int((t + 0.5 + j * 2.0) * SR)
            if s < n:
                p = pluck(midi(m)) * 0.12
                mix[s:s + len(p)] += p[: len(mix) - s]
        t += CHORD_S
        k += 1
    mix = mix[:n]
    # simple stereo echo for space
    d = int(0.37 * SR)
    echo = np.zeros_like(mix)
    echo[d:, 0] = mix[:-d, 1] * 0.28
    echo[d:, 1] = mix[:-d, 0] * 0.28
    mix += echo
    fade_in, fade_out = int(2.5 * SR), int(5 * SR)
    mix[:fade_in] *= np.linspace(0, 1, fade_in)[:, None]
    mix[-fade_out:] *= np.linspace(1, 0, fade_out)[:, None] ** 1.5
    rms = np.sqrt(np.mean(mix ** 2))
    mix *= (10 ** (-24 / 20)) / max(rms, 1e-9)
    peak = np.abs(mix).max()
    if peak > 0.89:
        mix *= 0.89 / peak
    return mix


def main() -> None:
    seconds = float(sys.argv[1]) if len(sys.argv) > 1 else 230.0
    audio = build(seconds)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pcm = (np.clip(audio, -1, 1) * 32767).astype("<i2")
    with wave.open(str(OUT), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())
    print(f"wrote {OUT} ({seconds:.1f} s)")


if __name__ == "__main__":
    main()
