"""Download the on-device runtime + model into the extension (not committed to git).

    python scripts/fetch_models.py

Chrome MV3 forbids remotely hosted code, so onnxruntime-web is bundled locally
and the NudeNet weights are packaged as data. Check licences in docs/THIRD_PARTY.md.
URLs were not verified at the time of writing (plan task B-4); if one 404s, find
the current asset on the project's release page and update it here.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
EXT = ROOT / "extension"
ORT_VERSION = "1.20.1"
ORT = f"https://cdn.jsdelivr.net/npm/onnxruntime-web@{ORT_VERSION}/dist"

FILES = {
    EXT / "vendor" / "ort.min.js": f"{ORT}/ort.min.js",
    EXT / "vendor" / "ort-wasm-simd-threaded.wasm": f"{ORT}/ort-wasm-simd-threaded.wasm",
    EXT / "vendor" / "ort-wasm-simd-threaded.mjs": f"{ORT}/ort-wasm-simd-threaded.mjs",
    EXT / "models" / "320n.onnx": "https://github.com/notAI-tech/NudeNet/releases/download/v3.4-weights/320n.onnx",
}


def main() -> int:
    failed = 0
    with httpx.Client(follow_redirects=True, timeout=120) as client:
        for dest, url in FILES.items():
            dest.parent.mkdir(parents=True, exist_ok=True)
            print(f"-> {dest.relative_to(ROOT)}")
            try:
                resp = client.get(url)
                resp.raise_for_status()
            except httpx.HTTPError as exc:
                print(f"   FAILED: {exc}")
                failed += 1
                continue
            dest.write_bytes(resp.content)
            print(f"   {len(resp.content) / 1e6:.1f} MB  sha256={hashlib.sha256(resp.content).hexdigest()[:16]}")
    print("Done." if not failed else f"{failed} download(s) failed; see docstring.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
