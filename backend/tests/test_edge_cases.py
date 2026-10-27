import json
import sys
import types
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from halio import api, card, factcheck_api, llm_verdict, pipeline
from halio.config import Settings
from halio.pii import scrub
from halio.retrieval import get_index

CFG = Settings(google_factcheck_key=None, llm_enabled=False)
client = TestClient(api.app)


@pytest.mark.parametrize("raw", [
    "+62 812 3456 7890", "+62-812-3456-7890", "6281234567890", "0812 3456 7890", "0812.3456.7890", "081234567890",
])
def test_phone_formats_scrubbed(raw):
    out = scrub(f"hubungi {raw} sekarang")
    assert not any(ch.isdigit() for ch in out), out


@pytest.mark.parametrize("raw", ["3201234567890001", "3201 2345 6789 0001", "320123.456789.0001", "320123-456789-0001"])
def test_nik_formats_scrubbed(raw):
    assert "[NIK]" in scrub(f"NIK saya {raw}")


def test_ordinary_numbers_survive_scrub():
    out = scrub("Gempa magnitudo 5,1 terjadi pukul 06.30, bantuan Rp 150.000 untuk 20 provinsi")
    assert "5,1" in out and "150.000" in out and "20" in out


def test_link_only_message_is_not_called_opinion():
    r = pipeline.check("https://bit.ly/abc123", CFG)
    assert r["reason"] == "terlalu_pendek"
    assert "tautan" in r["voice_script"]
    assert r["links"]["warnings"]


def test_emoji_heavy_message_still_matches_and_renders():
    r = pipeline.check("🚨🚨 WASPADA!!! 😱 BMKG prediksi gempa besar tanggal 12 bulan depan 🙏🙏 sebarkan 👇", CFG)
    assert r["status"] == "terbukti_salah"
    png = card.render(r)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    assert "🚨" not in card._printable(r["claim"])


@pytest.mark.parametrize("status_text", [
    "Harga cabai naik dua kali lipat karena musim hujan",
    "Selamat pagi keluarga, semoga sehat",
    "https://s.id/x",
])
def test_card_renders_for_every_state(status_text):
    assert card.render(pipeline.check(status_text, CFG))[:4] == b"\x89PNG"


def test_unsafe_source_urls_are_dropped():
    deb = get_index(CFG.corpus_path).debunks[0]
    original = deb.sumber
    try:
        deb.sumber = [{"nama": "x", "url": "javascript:alert(1)"}, *original]
        r = pipeline.check("Presiden bagi bantuan tunai daftar lewat nomor whatsapp transfer biaya admin", CFG)
        assert all(s["url"].startswith("http") for s in r["match"]["sumber"])
    finally:
        deb.sumber = original


def test_validation_rejects_bad_input():
    assert client.post("/api/check", json={"text": "hi"}).status_code == 422
    assert client.post("/api/check", json={"text": "x" * 5000}).status_code == 422
    assert client.post("/api/check", json={"text": "kabar apa", "channel": "evil"}).status_code == 422


def test_rate_limit(monkeypatch):
    monkeypatch.setattr(api, "limiter", api.RateLimiter(2))
    body = {"text": "Harga BBM naik besok pagi jam 6"}
    assert client.post("/api/check", json=body).status_code == 200
    assert client.post("/api/check", json=body).status_code == 200
    assert client.post("/api/check", json=body).status_code == 429


def test_trusted_channel_is_limited_per_chat(monkeypatch):
    monkeypatch.setattr(api, "limiter", api.RateLimiter(1))
    monkeypatch.setattr(api, "settings", Settings(channel_key="s3cret", rate_limit_per_min=1))
    h = {"X-Halio-Channel-Key": "s3cret"}
    for chat in ("tg:1", "tg:2", "tg:3"):
        assert client.post("/api/check", headers=h, json={"text": "Harga BBM naik besok", "reporter": chat}).status_code == 200
    assert client.post("/api/check", headers=h, json={"text": "Harga BBM naik besok", "reporter": "tg:1"}).status_code == 429


def test_radar_token(monkeypatch):
    monkeypatch.setattr(api, "settings", Settings(radar_token="t0k"))
    assert client.get("/api/radar").status_code == 401
    assert client.get("/api/radar", headers={"Authorization": "Bearer t0k"}).status_code == 200


def test_voice_unavailable_returns_501(monkeypatch):
    def boom(_):
        raise api.voice.VoiceUnavailable("offline")
    monkeypatch.setattr(api.voice, "synthesize", boom)
    r = client.post("/api/check", json={"text": "Harga BBM naik besok pagi jam 6"}).json()
    assert client.get(r["voice_url"]).status_code == 501


def test_health_and_static_pages():
    assert client.get("/health").json()["ok"]
    for path in ("/", "/radar", "/demo-feed.html", "/manifest.webmanifest", "/sw.js", "/app.js"):
        assert client.get(path).status_code == 200, path


# ---- T2 grounded LLM, with a stubbed SDK (no network, no cost) ----------------

def _stub_anthropic(monkeypatch, payload, stop_reason="end_turn"):
    mod = types.ModuleType("anthropic")
    for name in ("RateLimitError", "APIStatusError", "APIConnectionError"):
        setattr(mod, name, type(name, (Exception,), {}))
    calls = []

    class Messages:
        def create(self, **kwargs):
            calls.append(kwargs)
            return SimpleNamespace(stop_reason=stop_reason, content=[SimpleNamespace(type="text", text=json.dumps(payload))])

    mod.Anthropic = lambda: SimpleNamespace(beta=SimpleNamespace(messages=Messages()))
    monkeypatch.setitem(sys.modules, "anthropic", mod)
    return calls


def _candidates():
    return get_index(CFG.corpus_path).search("air kelapa garam jeruk nipis menyembuhkan covid", k=3)


def test_llm_grounded_quote_confirms(monkeypatch):
    cands = _candidates()
    quote = cands[0].debunk.fakta.split(".")[0]
    calls = _stub_anthropic(monkeypatch, {"relasi": "sama", "kandidat_id": cands[0].debunk.id, "kutipan": quote, "penjelasan": "x"})
    j = llm_verdict.judge("air kelapa sembuhkan covid", cands, "claude-opus-5-5")
    assert j.grounded and j.relation == "sama"
    assert calls[0]["output_config"]["format"]["type"] == "json_schema"


def test_llm_invented_quote_is_rejected(monkeypatch):
    cands = _candidates()
    _stub_anthropic(monkeypatch, {"relasi": "sama", "kandidat_id": cands[0].debunk.id, "kutipan": "WHO menyatakan ini hoaks", "penjelasan": "x"})
    j = llm_verdict.judge("air kelapa sembuhkan covid", cands, "claude-opus-5-5")
    assert not j.grounded and j.relation == "tidak_cukup_bukti"


def test_llm_cannot_upgrade_unsure_without_quote(monkeypatch):
    _stub_anthropic(monkeypatch, {"relasi": "sama", "kandidat_id": "air-kelapa-garam-obat", "kutipan": "dibuat-buat", "penjelasan": "x"})
    r = pipeline.check("Air kelapa mengandung elektrolit seperti kalium", Settings(llm_enabled=True))
    assert r["status"] != "terbukti_salah"


def test_llm_refusal_falls_back(monkeypatch):
    _stub_anthropic(monkeypatch, {}, stop_reason="refusal")
    assert llm_verdict.judge("x", _candidates(), "claude-opus-5-5") is None


def test_llm_missing_sdk_falls_back(monkeypatch):
    monkeypatch.setitem(sys.modules, "anthropic", None)
    assert llm_verdict.judge("x", _candidates(), "claude-opus-5-5") is None


# ---- T1 ClaimReview, with a mocked HTTP response --------------------------------

def test_claimreview_parsing_and_threshold(monkeypatch):
    data = {"claims": [
        {"text": "Minum air rebusan daun sirsak menyembuhkan kanker stadium akhir",
         "claimReview": [{"publisher": {"name": "Cek Fakta X"}, "url": "https://example.org/a", "title": "Sirsak bukan obat kanker", "textualRating": "Salah"}]},
        {"text": "Klaim benar", "claimReview": [{"publisher": {"name": "Y"}, "url": "https://e.org", "textualRating": "Benar"}]},
    ]}
    monkeypatch.setattr(factcheck_api.httpx, "get", lambda *a, **k: SimpleNamespace(raise_for_status=lambda: None, json=lambda: data))
    matches = factcheck_api.search("rebusan daun sirsak menyembuhkan kanker", "KEY")
    assert len(matches) == 1 and matches[0].debunk.sumber[0]["nama"] == "Cek Fakta X"

    r = pipeline.check("Minum air rebusan daun sirsak setiap hari bisa menyembuhkan kanker stadium akhir", Settings(google_factcheck_key="KEY"))
    assert r["status"] == "terbukti_salah" and "claimreview" in r["method"]


def test_claimreview_network_error_is_silent(monkeypatch):
    def boom(*a, **k):
        raise factcheck_api.httpx.ConnectError("down")
    monkeypatch.setattr(factcheck_api.httpx, "get", boom)
    assert factcheck_api.search("apa saja", "KEY") == []
