"""Jaga mesin luring di browser (web/engine) tetep sama persis dgn jalur T1 python.

Tiga lapis: data.js & parity_vectors.json ga boleh basi, dan uji paritas node harus 0 perbedaan.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]


def _run(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, timeout=300)


def test_engine_data_is_not_stale():
    r = _run(sys.executable, "scripts/build_engine_data.py", "--check")
    assert r.returncode == 0, r.stdout + r.stderr


def test_parity_vectors_are_not_stale():
    r = _run(sys.executable, "scripts/gen_parity_vectors.py", "--check")
    assert r.returncode == 0, r.stdout + r.stderr


@pytest.mark.skipif(shutil.which("node") is None, reason="node tidak terpasang")
def test_js_engine_matches_python():
    r = _run("node", "web/engine/parity.test.mjs")
    assert r.returncode == 0, r.stdout + r.stderr
    assert " 0 perbedaan" in r.stdout
