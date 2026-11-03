"""Render the 9:16 "segera hadir" story teaser.

    python video/tools/render_story.py --music path/to/backsound.mp3 [--workers 4]

Frames are rendered at 60 fps and folded to 30 fps with a 2-frame blend, which gives
real motion blur on the fast camera moves. Outputs in video/out/:

  halio-story-segera-hadir.mp4         music + sound effects, -14 LUFS (Instagram)
  halio-story-segera-hadir-sfx.mp4     sound effects only (if Instagram mutes the music)

The backing track is not committed to the repository; pass it with --music.
"""

from __future__ import annotations

import argparse
import math
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "out"
SEG = OUT / "story-segments"
FPS_RENDER, DUR = 60, 25.0


def run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--music", required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--mux-only", action="store_true", help="reuse rendered frames, redo audio + encode")
    args = ap.parse_args()

    run([sys.executable, str(ROOT / "tools" / "story_sfx.py")])
    master = OUT / "story-master-60.mp4"
    t0 = time.time()
    if not args.mux_only:
        render_frames(args.workers, master)
    mux(master, args.music)
    print(f"done in {time.time() - t0:.0f} s")


def render_frames(workers: int, master: Path) -> None:
    SEG.mkdir(parents=True, exist_ok=True)
    total = int(DUR * FPS_RENDER)
    per = math.ceil(total / workers)
    env = dict(os.environ, NODE_PATH=subprocess.run(["npm", "root", "-g"], capture_output=True, text=True).stdout.strip())
    t0 = time.time()
    procs, parts = [], []
    for i in range(workers):
        a, b = i * per, min(total, (i + 1) * per)
        part = SEG / f"part{i}.mp4"
        parts.append(part)
        procs.append(subprocess.Popen(["node", str(ROOT / "tools" / "render_story.js"), "frames", str(part), str(a), str(b), str(FPS_RENDER)], env=env))
    if any(p.wait() for p in procs):
        raise SystemExit("a render worker failed")
    print(f"frames rendered in {time.time() - t0:.0f} s")
    (SEG / "list.txt").write_text("".join(f"file '{p.name}'\n" for p in parts))
    run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(SEG / "list.txt"), "-c", "copy", str(master)])



def mux(master: Path, music: str) -> None:
    vf = "tmix=frames=2:weights='1 1',fps=30"
    enc = ["-c:v", "libx264", "-preset", "slow", "-crf", "18", "-profile:v", "high", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    sfx = OUT / "story-sfx.wav"
    full = ("[1:a]aresample=48000,volume=0.8,afade=t=out:st=24.4:d=0.6[m];[2:a]volume=1.0[s];"
            "[m][s]amix=inputs=2:normalize=0,loudnorm=I=-14:TP=-1.0:LRA=11,aresample=48000[a]")
    run(["ffmpeg", "-v", "error", "-y", "-i", str(master), "-i", music, "-i", str(sfx), "-filter_complex", f"[0:v]{vf}[v];{full}",
         "-map", "[v]", "-map", "[a]", *enc, "-c:a", "aac", "-b:a", "192k", "-t", str(DUR), str(OUT / "halio-story-segera-hadir.mp4")])
    run(["ffmpeg", "-v", "error", "-y", "-i", str(master), "-i", str(sfx), "-filter_complex", f"[0:v]{vf}[v];[1:a]loudnorm=I=-16:TP=-1.0,aresample=48000[a]",
         "-map", "[v]", "-map", "[a]", *enc, "-c:a", "aac", "-b:a", "192k", "-t", str(DUR), str(OUT / "halio-story-segera-hadir-sfx.mp4")])
    for f in ("halio-story-segera-hadir.mp4", "halio-story-segera-hadir-sfx.mp4"):
        print(f, f"{(OUT / f).stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
