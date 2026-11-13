"""Bukti jalur T1 (tanpa AI) bener-bener jalan tanpa jaringan.

Semua akses keluar (socket, DNS, httpx) dibikin gagal keras. Kalo ada kode di jalur T1 yg diam-diam
nyentuh internet, tes ini langsung pecah, jadi klaim "tanpa jaringan" di docs/PROFIL_PENERAPAN.md ada buktinya.
"""

from __future__ import annotations

import importlib.util
import socket
import time
from dataclasses import replace
from pathlib import Path

import httpx
import pytest

from halio import pipeline
from halio.config import Settings

ROOT = Path(__file__).resolve().parents[2]
CFG = replace(Settings(), google_factcheck_key=None, llm_enabled=False, link_check_enabled=False)


def _load_run_eval():
    # eval/ bukan package python, jadi dimuat langsung dari path-nya
    spec = importlib.util.spec_from_file_location("halio_run_eval", ROOT / "eval" / "run_eval.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def no_network(monkeypatch):
    attempts: list[str] = []

    def boom(*args, **kwargs):
        attempts.append(repr(args[:2]))
        raise AssertionError(f"akses jaringan terdeteksi di jalur T1: {args[:2]}")

    monkeypatch.setattr(socket.socket, "connect", boom)
    monkeypatch.setattr(socket.socket, "connect_ex", boom)
    monkeypatch.setattr(socket, "getaddrinfo", boom)
    monkeypatch.setattr(socket, "create_connection", boom)
    monkeypatch.setattr(httpx.Client, "send", boom)
    monkeypatch.setattr(httpx.AsyncClient, "send", boom)
    yield attempts
    assert attempts == []


@pytest.mark.parametrize("name", ["dev", "holdout"])
def test_eval_sets_run_without_network(no_network, name):
    run_eval = _load_run_eval()
    items = run_eval.load(name)
    m = run_eval.evaluate(CFG, items)
    # angka yg paling krusial tetap 0 walau jaringan mati
    assert m["false_hoax"] == 0
    assert m["wrong_debunk"] == 0
    assert m["n"] == len(items) > 0


def test_every_status_comes_from_local_code_only(no_network):
    for text in (
        "Ada video Presiden bagi-bagi bantuan tunai, daftar lewat WA dan bayar biaya admin Rp150 ribu. SEBARKAN!!",
        "Selamat pagi semua, semoga hari ini menyenangkan.",
        "Besok Jakarta akan diguyur hujan es sebesar bola tenis.",
    ):
        r = pipeline.check(text, CFG)
        assert r["status"] in {"terbukti_salah", "tidak_yakin", "belum_ada_pemeriksaan"}
        assert r["method"] == "lokal"
        assert r["links"]["checked"] == []


def test_local_latency_budget(no_network):
    pipeline.check("pemanasan index", CFG)
    samples = []
    for _ in range(30):
        t0 = time.perf_counter()
        pipeline.check("Video Presiden bagi-bagi bantuan tunai, bayar biaya admin lewat WhatsApp", CFG)
        samples.append((time.perf_counter() - t0) * 1000)
    samples.sort()
    # batas longgar biar ga flaky di CI; angka sungguhan diukur & dicatat di docs
    assert samples[len(samples) // 2] < 50
