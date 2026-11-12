"""Tests for the green (sejalan dengan sumber) gate: current official evidence plus a verified quote, otherwise never."""

import json
from dataclasses import replace

import pytest

from halio import pipeline
from halio.config import Settings
from halio.llm_verdict import LlmJudgement

CLAIM = "BMKG menyatakan gempa bumi belum dapat diprediksi secara pasti"
QUOTE = "BMKG menyatakan bahwa gempa bumi belum dapat diprediksi secara pasti dan akurat."


def entry(**changes):
    value = {
        "id": "bmkg-prediksi-gempa",
        "kategori": "bencana",
        "klaim": CLAIM,
        "varian": ["Belum ada teknologi yang dapat memprediksi gempa secara pasti"],
        "fakta": QUOTE,
        "sederhana": "BMKG memang menyatakan bahwa gempa belum dapat diprediksi secara pasti.",
        "sumber": [{"nama": "BMKG", "url": "https://www.bmkg.go.id/siaran-pers/contoh", "jenis": "resmi"}],
        "jenis": "verifikasi_positif",
        "kutipan_sumber": QUOTE,
        "valid_from": "2020-01-01",
        "valid_until": "2099-12-31",
        "wilayah": "Indonesia",
    }
    value.update(changes)
    return value


def config(tmp_path, entries):
    path = tmp_path / "positive.json"
    path.write_text(json.dumps({"debunks": entries}), encoding="utf-8")
    return Settings(corpus_path=path, google_factcheck_key=None, llm_enabled=True, llm_provider="anthropic")


def ground_positive(monkeypatch, quote=QUOTE, grounded=True):
    judgement = LlmJudgement("sama", "bmkg-prediksi-gempa", quote, "Sesuai keterangan BMKG.", grounded)
    monkeypatch.setattr(pipeline.llm_verdict, "judge", lambda *args: judgement)


def test_grounded_current_official_evidence_is_green(tmp_path, monkeypatch):
    ground_positive(monkeypatch)
    result = pipeline.check(CLAIM, config(tmp_path, [entry()]))
    assert result["status"] == "sejalan_dengan_sumber"
    assert result["reason"] == "cocok_dengan_sumber_resmi"
    assert result["match"]["jenis"] == "verifikasi_positif"
    assert result["match"]["valid_until"] == "2099-12-31"
    assert not result["offer_human_review"]


def test_positive_match_never_turns_green_from_retrieval_alone(tmp_path):
    result = pipeline.check(CLAIM, replace(config(tmp_path, [entry()]), llm_enabled=False))
    assert result["status"] == "tidak_yakin"
    assert result["reason"] == "memerlukan_verifikasi_ai"
    assert result["offer_human_review"]


@pytest.mark.parametrize(
    ("dates", "reason"),
    [
        ({"valid_until": "2020-01-02"}, "sumber_kedaluwarsa"),
        ({"valid_from": "2099-01-01"}, "sumber_belum_berlaku"),
        ({"valid_from": None}, "sumber_kedaluwarsa"),
    ],
)
def test_expired_or_future_evidence_cannot_turn_green(tmp_path, monkeypatch, dates, reason):
    ground_positive(monkeypatch)
    result = pipeline.check(CLAIM, config(tmp_path, [entry(**dates)]))
    assert result["status"] == "tidak_yakin"
    assert result["reason"] == reason


def test_competing_candidate_blocks_green_result(tmp_path, monkeypatch):
    ground_positive(monkeypatch)
    competing = entry(id="sumber-lain", klaim=CLAIM)
    result = pipeline.check(CLAIM, config(tmp_path, [entry(), competing]))
    assert result["status"] == "tidak_yakin"
    assert result["reason"] == "bukti_bertentangan"


@pytest.mark.parametrize(
    ("changes", "quote", "grounded", "reason"),
    [
        ({"sumber": [{"nama": "Blog", "url": "https://blog.example/artikel", "jenis": "media"}]}, QUOTE, True, "sumber_bukan_resmi"),
        ({"kutipan_sumber": "Kutipan lain"}, QUOTE, True, "kutipan_sumber_tidak_cocok"),
        ({}, "Kutipan karangan", True, "kutipan_sumber_tidak_cocok"),
        ({}, QUOTE, False, "llm_tidak_dapat_membuktikan"),
    ],
)
def test_source_and_quote_gates_fail_closed(tmp_path, monkeypatch, changes, quote, grounded, reason):
    ground_positive(monkeypatch, quote=quote, grounded=grounded)
    result = pipeline.check(CLAIM, config(tmp_path, [entry(**changes)]))
    assert result["status"] == "tidak_yakin"
    assert result["reason"] == reason
