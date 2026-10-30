"""Regression tests for the Oct 2026 audit: false accusations, abuse limits, injection, privacy gaps."""

import hashlib
import hmac
import json
import os
import subprocess
import sys
import tempfile
from dataclasses import replace
from pathlib import Path

import pytest

os.environ.setdefault("HALIO_DB", os.path.join(tempfile.mkdtemp(), "hardening.db"))
os.environ.pop("RADAR_TOKEN", None)

from fastapi.testclient import TestClient  # noqa: E402

from halio import api, manipulation, pipeline  # noqa: E402
from halio.channels.format import reply_text  # noqa: E402
from halio.config import Settings  # noqa: E402
from halio.netguard import RateLimiter, network_of  # noqa: E402
from halio.pii import extract_domains, scrub  # noqa: E402
from halio.retrieval import is_correction  # noqa: E402

CFG = Settings(google_factcheck_key=None, llm_enabled=False)
ROOT = Path(__file__).resolve().parents[2]
client = TestClient(api.app)


# --- false accusations -------------------------------------------------------------------------

@pytest.mark.parametrize("text", [
    "Pendaftaran Bintara TNI AD 2026 dibuka tanggal 5 Januari melalui penerimaan.tniad.mil.id, biaya gratis",
    "Telkomsel memberi bonus kuota gratis 5GB untuk pelanggan setia yang mengisi pulsa Rp100 ribu",
    "Hati-hati penculikan anak, polisi sudah menangkap pelakunya di Bekasi, warga diminta tetap waspada",
    "Dokter menyarankan minum air kelapa dan jeruk nipis saat flu, tapi tetap minum obat dari dokter",
    "Presiden Prabowo membagikan bantuan sembako kepada warga, daftar penerima sudah diumumkan kelurahan",
])
def test_true_same_topic_statements_are_not_called_hoax(text):
    assert pipeline.check(text, CFG)["status"] != "terbukti_salah"


@pytest.mark.parametrize("text", [
    "Pesan prediksi gempa besar minggu depan itu hoaks, BMKG sudah membantahnya",
    "Jasa Marga membantah membagikan saldo e-toll gratis lewat link, itu penipuan",
    "Tidak ada bukti air kelapa dan garam menyembuhkan covid, kata Kementerian Kesehatan",
])
def test_forwarded_corrections_are_recognised(text):
    r = pipeline.check(text, CFG)
    assert r["status"] == "tidak_yakin" and r["reason"] == "tampak_meluruskan"
    assert "memperingatkan" in r["voice_script"]


def test_hoax_that_denies_being_a_hoax_is_still_caught():
    assert not is_correction("Ini bukan hoaks! BMKG memprediksi gempa M9 akan terjadi minggu depan, sebarkan")
    r = pipeline.check("Ini bukan hoaks! BMKG memprediksi gempa M9 akan terjadi minggu depan, sebarkan", CFG)
    assert r["status"] == "terbukti_salah"


def test_llm_cannot_lift_past_the_guard(monkeypatch):
    from halio import llm_verdict

    def always_same(claim, candidates, model):
        d = candidates[0].debunk
        return llm_verdict.LlmJudgement("sama", d.id, d.fakta[:30], "x", True)

    monkeypatch.setattr(llm_verdict, "judge", always_same)
    cfg = replace(CFG, llm_enabled=True)
    # Core negated ("tidak dipungut biaya"): the LLM saying "sama" must not turn it into a hoax.
    r = pipeline.check("Rekrutmen tamtama TNI AD tidak dipungut biaya, daftar resmi lewat situs", cfg)
    assert r["status"] != "terbukti_salah"
    r = pipeline.check("Pesan prediksi gempa besar minggu depan itu hoaks, BMKG sudah membantahnya", cfg)
    assert r["status"] != "terbukti_salah"
    # A "mirip" paraphrase whose core is present may still be confirmed with a quote.
    r = pipeline.check("bisa bantu masuk bintara TNI lwt kenalan perwira, ada uang pelicin dikit", cfg)
    assert r["status"] == "terbukti_salah" and r["reason"] == "cocok_dikonfirmasi_llm"


def test_holdout_eval_has_no_false_hoax():
    sys.path.insert(0, str(ROOT / "eval"))
    import run_eval

    for name in run_eval.SETS:
        m = run_eval.evaluate(CFG, run_eval.load(name))
        assert m["false_hoax"] == 0, name
        assert m["wrong_debunk"] == 0, name


# --- privacy and links -------------------------------------------------------------------------

@pytest.mark.parametrize("text,leak", [
    ("hubungi +62 812-3456-7890", "812"), ("telp (0812) 3456 7890", "3456"),
    ("wa 0812 345 678 90", "345"), ("NIK 32 01 23 456789 0001", "456789"),
    ("buka bit.ly/abc?x=1 sekarang", "bit.ly"),
])
def test_scrub_gaps_closed(text, leak):
    assert leak not in scrub(text)


def test_link_host_is_parsed_not_suffix_matched():
    assert extract_domains("https://kemensos.go.id.bansos-cair.xyz/?a=.go.id") == ["kemensos.go.id.bansos-cair.xyz"]
    assert extract_domains("klik bit.ly/abc atau s.id/daftar") == ["bit.ly", "s.id"]
    r = pipeline.check("daftar di https://kemensos.go.id.bansos-cair.xyz/form dan https://cekbansos.kemensos.go.id", CFG)
    warned = " ".join(r["links"]["warnings"])
    assert "bansos-cair.xyz" in warned and "cekbansos.kemensos.go.id" not in warned


def test_school_domains_are_not_official():
    r = pipeline.check("isi data di https://smkn9.sch.id/bansos", CFG)
    assert r["links"]["warnings"]


def test_judol_rule_ignores_everyday_words():
    assert not manipulation.is_judol("Slot parkir penuh, cek situs resmi Kemensos")
    assert manipulation.is_judol("SLOT GACOR maxwin hari ini")
    assert manipulation.is_judol("link alternatif, jackpot scatter")


def test_extension_lexicon_is_generated_from_python():
    subprocess.run([sys.executable, str(ROOT / "scripts" / "sync_lexicon.py"), "--check"], check=True)


# --- API abuse limits --------------------------------------------------------------------------

def test_long_input_is_truncated_not_rejected():
    r = client.post("/api/check", json={"text": "Waspada gempa besar diprediksi minggu depan. " + "x " * 5000})
    assert r.status_code == 200


def test_rate_limit_returns_429(monkeypatch):
    monkeypatch.setattr(api, "limiter", RateLimiter(2))
    codes = [client.post("/api/check", json={"text": "Harga cabai naik di pasar"}).status_code for _ in range(3)]
    assert codes == [200, 200, 429]


def test_forged_reporters_count_once():
    # Five invented "devices" from one network are one reporter for k-anonymity.
    for i in range(6):
        client.post("/api/check", json={"text": "Jembatan Ampera ditutup total tiga hari mulai besok pagi", "reporter": f"fake{i}"})
    texts = [r.get("text") for r in api.store.radar(days=1)["emerging_rumours"]]
    assert not any(t and "Ampera" in t for t in texts)
    assert network_of("203.0.113.77") == network_of("203.0.113.9") != network_of("203.0.114.9")


def test_radar_closed_to_remote_clients_without_token(monkeypatch):
    remote = TestClient(api.app, client=("198.51.100.4", 5000))
    assert remote.get("/api/radar").status_code == 401
    monkeypatch.setattr(api, "settings", replace(api.settings, radar_public=True))
    assert remote.get("/api/radar").status_code == 200


# --- WhatsApp webhook --------------------------------------------------------------------------

def _signed(body: bytes, secret: str) -> dict:
    return {"x-hub-signature-256": "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest(),
            "content-type": "application/json"}


def test_whatsapp_rejects_unsigned_and_accepts_signed(monkeypatch):
    monkeypatch.setattr(api, "settings", replace(api.settings, wa_app_secret="s3cret"))
    seen = []
    monkeypatch.setattr(api.whatsapp, "reply", lambda to, result, cfg: seen.append((to, result["status"])))
    body = json.dumps({"entry": [{"changes": [{"value": {"messages": [
        {"from": "628111", "type": "text", "text": {"body": "Waspada gempa besar diprediksi minggu depan, sebarkan!"}},
        {"from": "628222", "type": "image"}, {"type": "text"},
    ]}}]}]}).encode()
    assert client.post("/webhook/whatsapp", content=body, headers={"content-type": "application/json"}).status_code == 401
    assert client.post("/webhook/whatsapp", content=body, headers=_signed(body, "wrong")).status_code == 401
    assert client.post("/webhook/whatsapp", content=body, headers=_signed(body, "s3cret")).status_code == 200
    assert seen == [("628111", "terbukti_salah")]
    junk = b"not json"
    assert client.post("/webhook/whatsapp", content=junk, headers=_signed(junk, "s3cret")).status_code == 200


# --- Telegram HTML -----------------------------------------------------------------------------

def test_telegram_reply_escapes_user_text():
    r = pipeline.check("Jembatan <b>Suramadu</b> ditutup, cek http://a<script>.xyz", CFG, sapaan="<i>Bu</i>")
    out = reply_text(r, html=True)
    assert "<i>" not in out and "<script>" not in out
