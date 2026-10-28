"""Render the whole Halio demo video.

    python video/tools/render_all.py [--workers 4]

Steps: narration timeline -> app data -> frames (parallel Chromium workers) -> concat ->
music -> three deliverables in video/out/:

  halio-demo.mp4                 subtitles burned in + music   (upload this one)
  halio-demo-tanpa-musik.mp4     subtitles burned in, silent   (play this while recording the voice-over)
  halio-demo-tanpa-subtitle.mp4  music only                    (upload with halio-demo.srt as YouTube captions)
"""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
OUT = ROOT / "out"
SEG = OUT / "segments"
FONTS = REPO / "backend" / "halio" / "fonts"


def run(cmd: list[str], **kw) -> None:
    subprocess.run(cmd, check=True, **kw)


def node_env() -> dict:
    root = subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip()
    return dict(os.environ, NODE_PATH=root)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()

    run([sys.executable, str(ROOT / "tools" / "build_timeline.py")])
    run([sys.executable, str(ROOT / "tools" / "make_data.py")])
    tl = json.loads((ROOT / "src" / "timeline.js").read_text(encoding="utf-8").split("=", 1)[1].strip().rstrip(";"))
    total = math.ceil(tl["duration"] * tl["fps"])
    SEG.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    per = math.ceil(total / args.workers)
    procs, parts = [], []
    for i in range(args.workers):
        a, b = i * per, min(total, (i + 1) * per)
        if a >= b:
            break
        part = SEG / f"part{i}.mp4"
        parts.append(part)
        procs.append(subprocess.Popen(["node", str(ROOT / "tools" / "render.js"), "frames", str(part), str(a), str(b)], env=node_env()))
    if any(p.wait() for p in procs):
        raise SystemExit("a render worker failed")
    print(f"frames rendered in {time.time() - t0:.0f} s")

    lst = SEG / "list.txt"
    lst.write_text("".join(f"file '{p.name}'\n" for p in parts))
    master = OUT / "master-silent.mp4"
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", str(master)])

    run([sys.executable, str(ROOT / "tools" / "make_music.py"), str(tl["duration"])])
    music = OUT / "music.wav"
    ass = OUT / "halio-demo.ass"
    subs = f"subtitles={ass}:fontsdir={FONTS}"
    audio = ["-filter_complex", "[1:a]lowpass=f=2600,afade=t=in:d=1.5[a]", "-map", "0:v", "-map", "[a]", "-c:a", "aac", "-b:a", "192k", "-shortest"]
    enc = ["-c:v", "libx264", "-preset", "slow", "-crf", "21", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]

    run(["ffmpeg", "-v", "error", "-y", "-i", str(master), "-i", str(music), "-vf", subs, *enc, *audio, str(OUT / "halio-demo.mp4")])
    run(["ffmpeg", "-v", "error", "-y", "-i", str(master), "-vf", subs, *enc, "-an", str(OUT / "halio-demo-tanpa-musik.mp4")])
    run(["ffmpeg", "-v", "error", "-y", "-i", str(master), "-i", str(music), *enc, *audio, str(OUT / "halio-demo-tanpa-subtitle.mp4")])
    for f in ("halio-demo.mp4", "halio-demo-tanpa-musik.mp4", "halio-demo-tanpa-subtitle.mp4"):
        p = OUT / f
        print(f"{f}: {p.stat().st_size / 1e6:.1f} MB")
    print(f"done in {time.time() - t0:.0f} s")


if __name__ == "__main__":
    main()
