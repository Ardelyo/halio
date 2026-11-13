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

# set db sementra dulu sblm import modul api biar aman dr db lokal
os.environ.setdefault("HALIO_DB", os.path.join(tempfile.mkdtemp(), "hardening.db"))
os.environ.pop("RADAR_TOKEN", None)

from fastapi.testclient import TestClient  # noqa: E402

from halio import api, manipulation, pipeline  # noqa: E402
from halio.channels.format import reply_text  # noqa: E402
from halio.config import Settings  # noqa: E402
from halio.netguard import network_of  # noqa: E402
from halio.security import RateLimiter  # noqa: E402
from halio.pii import extract_domains, scrub  # noqa: E402
from halio.retrieval import is_correction  # noqa: E402

CFG = Settings(google_factcheck_key=None, llm_enabled=False)
ROOT = Path(__file__).resolve().parents[2]
client = TestClient(api.app)


# --- cegah tuduhan hoaks salah sasaran ---------------------------------------------------------

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
    # temuan dr stress test jelang kumpul (Nov 2026): dua pesan imbauan ini tadinya sempet kecap hoaks
    "Hati-hati penipuan bansos memakai video palsu Presiden. Bantuan resmi tidak pernah meminta biaya administrasi. Cek di situs resmi Kemensos.",
    "Kodam XV Pattimura menangkap calo penerimaan prajurit. Masyarakat diminta melapor bila ada yang meminta uang. Seleksi TNI AD tidak dipungut biaya.",
    "Jangan percaya calo yang menjanjikan lulus masuk TNI AD dengan bayar uang, semua tes resmi gratis",
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
    cfg = replace(CFG, llm_enabled=True, llm_provider="anthropic")
    # inti klaimnya dibalik ("tidak dipungut biaya"): biarpun LLM ngotot bilang "sama", tetep ga boleh jadi hoaks
    r = pipeline.check("Rekrutmen tamtama TNI AD tidak dipungut biaya, daftar resmi lewat situs", cfg)
    assert r["status"] != "terbukti_salah"
    r = pipeline.check("Pesan prediksi gempa besar minggu depan itu hoaks, BMKG sudah membantahnya", cfg)
    assert r["status"] != "terbukti_salah"
    # parafrase "mirip" yg intinya masih utuh tetep boleh dikonfirmasi pake kutipan
    r = pipeline.check("bisa bantu masuk bintara TNI lwt kenalan perwira, ada uang pelicin dikit", cfg)
    assert r["status"] == "terbukti_salah" and r["reason"] == "cocok_dikonfirmasi_llm"


def test_holdout_eval_has_no_false_hoax():
    sys.path.insert(0, str(ROOT / "eval"))
    import run_eval

    for name in run_eval.SETS:
        m = run_eval.evaluate(CFG, run_eval.load(name))
        assert m["false_hoax"] == 0, name
        assert m["wrong_debunk"] == 0, name


# --- sensor data pribadi & pengecekkan tautan --------------------------------------------------

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
    # skrg pipeline beneran ngebuka link; matiin fitur buka link di sini biar murni ngetes parsing host secara offline
    r = pipeline.check("daftar di https://kemensos.go.id.bansos-cair.xyz/form dan https://cekbansos.kemensos.go.id", replace(CFG, link_check_enabled=False))
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
    # pastin kamus kata di ekstensi browser tetep sinkron sm sumber python-nya
    subprocess.run([sys.executable, str(ROOT / "scripts" / "sync_lexicon.py"), "--check"], check=True)


# --- batas anti-spam & penyalahgunaan API ------------------------------------------------------

def test_long_input_is_truncated_not_rejected():
    r = client.post("/api/check", json={"text": "Waspada gempa besar diprediksi minggu depan. " + "x " * 5000})
    assert r.status_code == 200


def test_rate_limit_returns_429(monkeypatch):
    monkeypatch.setattr(api, "limiter", RateLimiter(2))
    codes = [client.post("/api/check", json={"text": "Harga cabai naik di pasar"}).status_code for _ in range(3)]
    assert codes == [200, 200, 429]


def test_rate_limit_keys_on_forwarded_address_only_when_proxy_trusted(monkeypatch):
    seen = []
    monkeypatch.setattr(api, "limiter", type("L", (), {"allow": lambda self, key: seen.append(key) or True})())
    hdr = {"x-forwarded-for": "6.6.6.6, 203.0.113.9"}
    client.post("/api/check", json={"text": "Harga cabai naik di pasar"}, headers=hdr)
    monkeypatch.setattr(api, "settings", replace(api.settings, trust_proxy=True))
    client.post("/api/check", json={"text": "Harga cabai naik di pasar"}, headers=hdr)
    assert seen[0].startswith("testclient:") and seen[1].startswith("203.0.113.9:")


def test_forged_reporters_count_once():
    # lima "device" karangan dr satu subnet jaringan yg sama tetep diitung satu pelapor buat k-anonymity
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


# --- webhook WhatsApp --------------------------------------------------------------------------

def _signed(body: bytes, secret: str) -> dict:
    return {"x-hub-signature-256": "sha256=" + hmac.new(secret.encode(), body, hashlib.sha256).hexdigest(),
            "content-type": "application/json"}


def test_whatsapp_rejects_unsigned_and_accepts_signed(monkeypatch):
    monkeypatch.setattr(api, "settings", replace(api.settings, wa_app_secret="s3cret"))
    seen = []
    monkeypatch.setattr(api.whatsapp, "reply", lambda to, result, cfg: seen.append((to, result["status"])))
    body = json.dumps({"entry": [{"changes": [{"value": {"messages": [
        {"id": "wamid.1", "from": "628111", "type": "text", "text": {"body": "Waspada gempa besar diprediksi minggu depan, sebarkan!"}},
        {"id": "wamid.2", "from": "628222", "type": "image"}, {"type": "text"},
    ]}}]}]}).encode()
    assert client.post("/webhook/whatsapp", content=body, headers={"content-type": "application/json"}).status_code == 403
    assert client.post("/webhook/whatsapp", content=body, headers=_signed(body, "wrong")).status_code == 403
    assert client.post("/webhook/whatsapp", content=body, headers=_signed(body, "s3cret")).status_code == 200
    assert seen == [("628111", "terbukti_salah")]
    # Meta kadang kirim ulang wamid yg sama: jgn sampe kekirim balasan dobel ke user
    assert client.post("/webhook/whatsapp", content=body, headers=_signed(body, "s3cret")).status_code == 200
    assert seen == [("628111", "terbukti_salah")]
    junk = b"not json"
    assert client.post("/webhook/whatsapp", content=junk, headers=_signed(junk, "s3cret")).status_code == 400


# --- keamanan HTML Telegram --------------------------------------------------------------------

def test_telegram_reply_escapes_user_text():
    r = pipeline.check("Jembatan <b>Suramadu</b> ditutup, cek http://a<script>.xyz", CFG, sapaan="<i>Bu</i>")
    out = reply_text(r, html=True)
    assert "<i>" not in out and "<script>" not in out


def test_bot_reporter_is_kept_only_with_the_channel_key(monkeypatch):
    monkeypatch.setattr(api, "settings", replace(api.settings, channel_key="k3y"))
    body = {"text": "Jembatan Ampera ditutup total tiga hari mulai besok pagi", "channel": "telegram", "reporter": "tg:42"}
    forged = client.post("/api/check", json=body).json()
    real = client.post("/api/check", json=body, headers={"x-halio-channel-key": "k3y"}).json()
    assert api.cache.get(forged["id"])["_reporter"].startswith("net:")
    assert api.cache.get(real["id"])["_reporter"] == "tg:42"  # id ini dipake buat ngerutein balasn tiket eskalasi


def test_web_agent_cannot_turn_a_correction_into_a_hoax(monkeypatch):
    from halio import google_agent

    def refutes(claim, cfg, seed_urls=()):
        match = pipeline.get_index(cfg.corpus_path).search(claim, k=1)[0]
        return google_agent.AgentResult("terbukti_salah", "cocok_dengan_bantahan_web", match, None, {"penjelasan": "x"})

    monkeypatch.setattr(google_agent, "investigate", refutes)
    cfg = replace(CFG, llm_enabled=True, llm_provider="google")
    r = pipeline.check("Pesan prediksi gempa besar minggu depan itu hoaks, BMKG sudah membantahnya", cfg)
    assert r["status"] == "tidak_yakin" and r["reason"] == "tampak_meluruskan"
    r = pipeline.check("Waspada gempa besar diprediksi terjadi minggu depan, sebarkan ke keluarga", cfg)
    assert r["status"] == "terbukti_salah"


def test_gemini_defaults(monkeypatch):
    for k in ("HALIO_LLM_MODEL", "HALIO_LLM_PROVIDER", "GOOGLE_CLOUD_LOCATION"):
        monkeypatch.delenv(k, raising=False)
    cfg = Settings()
    assert (cfg.llm_provider, cfg.llm_model, cfg.google_cloud_location) == ("google", "gemini-3.5-flash-lite", "global")
    monkeypatch.setenv("HALIO_LLM_PROVIDER", "anthropic")
    assert Settings().llm_model == "claude-haiku-5-5"


def test_radar_stays_closed_behind_a_same_host_proxy():
    # nginx / Cloudflare Tunnel masuk dr 127.0.0.1; cek header proxy buat nangkep IP pengakses luarnya
    proxied = TestClient(api.app, client=("127.0.0.1", 5000))
    for path in ("/api/radar", "/api/review/escalations", "/api/sensor/coverage"):
        for hdr in ({"x-forwarded-for": "203.0.113.9"}, {"cf-connecting-ip": "203.0.113.9"}, {"forwarded": "for=203.0.113.9"}):
            assert proxied.get(path, headers=hdr).status_code == 401, (path, hdr)
    assert proxied.get("/api/radar").status_code == 200  # kl diakses dev lokal langsung tanpa header proxy tetep jalan


# --- penjaga kuota biaya & beban server (jelang kumpul, Nov 2026) ------------------------------

def test_daily_budget_zero_means_unlimited_and_resets_each_day():
    from halio.security import DailyBudget

    unlimited = DailyBudget(0)
    assert all(unlimited.take() for _ in range(1000))
    b = DailyBudget(2)
    assert b.take(day="2026-11-16") and b.take(day="2026-11-16") and not b.take(day="2026-11-16")
    assert b.take(day="2026-11-17")


def test_llm_daily_cap_falls_back_to_local_answer_with_a_label(monkeypatch):
    from halio.security import DailyBudget

    seen = []
    real_check = pipeline.check

    def spy(text, cfg, sapaan="Bapak, Ibu"):
        seen.append(cfg.llm_enabled)
        return real_check(text, replace(cfg, llm_enabled=False, google_factcheck_key=None), sapaan=sapaan)

    monkeypatch.setattr(api, "settings", replace(api.settings, llm_enabled=True))
    monkeypatch.setattr(api, "llm_budget", DailyBudget(1))
    monkeypatch.setattr(api.pipeline, "check", spy)
    text = "Jalur khusus masuk tentara, pasti lulus, bayar ke orang dalam"
    first = client.post("/api/check", json={"text": text}).json()
    second = client.post("/api/check", json={"text": text}).json()
    assert seen == [True, False]
    assert first["mode"] == "penuh" and second["mode"] == "tanpa_ai" and second.get("batas_ai_harian")
    assert second["status"] == first["status"] == "terbukti_salah"   # basis data kurasi lokal tetep bisa ngejawab


def test_media_daily_cap_answers_429_with_plain_advice(monkeypatch):
    from halio.security import DailyBudget

    monkeypatch.setattr(api, "media_budget", DailyBudget(1))
    assert api.media_budget.take()
    r = client.post("/api/check-media", json={"data_b64": "A" * 200, "mime": "image/png"})
    assert r.status_code == 429 and "ketik" in r.json()["detail"]


def test_oversized_body_is_refused_before_parsing(monkeypatch):
    monkeypatch.setattr(api, "MAX_BODY_BYTES", 1000)
    r = client.post("/api/check", content=b"x" * 2000, headers={"Content-Type": "application/json"})
    assert r.status_code == 413
    ok = client.post("/api/check", json={"text": "Halo apa kabar semuanya"})
    assert ok.status_code == 200


def test_pages_get_csp_and_frame_denial_and_the_inline_script_hash_matches():
    import base64
    import re

    r = client.get("/cek.html")
    assert r.headers["X-Frame-Options"] == "DENY"
    csp = r.headers["Content-Security-Policy"]
    assert "frame-ancestors 'none'" in csp and "object-src 'none'" in csp and "'unsafe-eval'" not in csp
    # semua <script> inline di web/*.html wajib cocok hash sha256-nya di CSP; tes rewel dikit gpp drpd jebol pas didemoin ke juri
    for page in (ROOT / "web").glob("*.html"):
        for body in re.findall(r"<script>(.*?)</script>", page.read_text(encoding="utf-8"), re.S):
            digest = "sha256-" + base64.b64encode(hashlib.sha256(body.encode()).digest()).decode()
            assert digest in csp, f"{page.name}: inline script not allowed by the CSP ({digest})"


def test_scam_line_followed_by_a_call_to_action_is_still_recognised():
    """The TNI AD recruitment scam with a trailing 'call Pak Budi' line fell just under the threshold (0.398) before."""
    text = ("Info penting! Ada jalur titipan masuk TNI AD 2026, dijamin lulus Tamtama, cukup transfer 75 juta ke orang dalam Kodam. "
            "Hubungi Pak Budi segera, kuota terbatas.")
    r = pipeline.check(text, CFG)
    assert r["status"] == "terbukti_salah" and r["match"]["debunk_id"] == "rekrutmen-tni-ad-berbayar"


def test_a_known_hoax_written_in_two_sentences_is_not_split_into_two_weak_claims():
    text = "Pak Prabowo bagi-bagi uang tunai 10 juta lewat video resmi! Daftar di WhatsApp, bayar admin 300 ribu dulu. Buruan sebelum ditutup."
    r = pipeline.check(text, CFG)
    assert r["status"] == "terbukti_salah" and r["reason"] == "cocok_dengan_bantahan" and not r.get("claims")


def test_genuinely_different_claims_are_still_split():
    text = ("BMKG memprediksi gempa magnitudo 9 akan terjadi tanggal 3 Desember di Jawa. "
            "Pemerintah membuka pendaftaran beasiswa kuliah gratis 2026 untuk seluruh siswa SMA di Indonesia.")
    assert pipeline.check(text, CFG)["reason"] == "beberapa_klaim"


def test_true_message_on_a_hoax_topic_is_not_told_to_be_held_back():
    text = "Pendaftaran Tamtama TNI AD 2026 dilakukan secara online melalui situs resmi penerimaan TNI AD dan seluruh tahapannya tidak dipungut biaya."
    r = pipeline.check(text, CFG)
    assert r["status"] == "tidak_yakin" and r["reason"] == "inti_klaim_tidak_ada"
    assert "tidak memuat bagian yang bohong" in r["voice_script"] and "ditahan" not in r["voice_script"]
