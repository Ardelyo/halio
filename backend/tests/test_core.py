from dataclasses import replace

from halio import claims, manipulation, pipeline
from halio.config import Settings
from halio.pii import extract_domains, scrub

CFG = Settings(google_factcheck_key=None, llm_enabled=False)


def test_scrub_removes_personal_data():
    text = "Hubungi 0812-3456-7890 atau +6281234567890, NIK 3201234567890001, email a.b@mail.com, cek https://bit.ly/xyz @budi"
    out = scrub(text)
    for leaked in ("0812", "6281", "3201234567890001", "a.b@mail.com", "bit.ly", "@budi"):
        assert leaked not in out
    assert "[NOMOR]" in out and "[NIK]" in out and "[TAUTAN]" in out


def test_scrub_truncates_to_300_chars():
    assert len(scrub("kata " * 200)) <= 300


def test_extract_domains():
    assert extract_domains("daftar di https://bit.ly/abc dan www.tni-ad.mil.id/rekrutmen.") == ["bit.ly", "tni-ad.mil.id"]


def test_opinion_is_not_factual():
    assert not claims.extract("Selamat pagi keluarga, semoga sehat selalu. Amin").is_factual
    assert claims.extract("BMKG memprediksi gempa magnitudo 9 akan terjadi tanggal 12 November").is_factual


def test_manipulation_flags_techniques():
    r = manipulation.analyze("SEGERA SEBARKAN!!! Bantuan tunai gratis, transfer biaya administrasi dulu")
    ids = {t["id"] for t in r["techniques"]}
    assert {"ajakan_sebar", "urgensi", "iming_iming", "minta_data_uang"} <= ids
    assert r["needs_check"]


def test_known_hoax_is_terbukti_salah_with_source():
    r = pipeline.check("Jalur khusus masuk TNI AD dijamin lulus, bayar ke orang dalam 50 juta", CFG)
    assert r["status"] == "terbukti_salah"
    assert r["match"]["debunk_id"] == "rekrutmen-tni-ad-berbayar"
    assert r["match"]["sumber"][0]["url"].startswith("https://")
    assert not r["offer_human_review"]


def test_negated_core_is_not_labelled_hoax():
    # True statement on the same topic must never be called a hoax.
    r = pipeline.check("Rekrutmen TNI AD dibuka, tidak dipungut biaya dan tanpa calo", CFG)
    assert r["status"] != "terbukti_salah"


def test_unknown_claim_abstains_and_offers_human():
    r = pipeline.check("Jembatan Suramadu akan ditutup total selama seminggu mulai besok", CFG)
    assert r["status"] == "belum_ada_pemeriksaan"
    assert r["match"] is None
    assert r["offer_human_review"]
    assert "tidak mau menebak" in r["voice_script"]


def test_sapaan_used_in_voice_script():
    r = pipeline.check("air kelapa garam jeruk nipis menyembuhkan covid", CFG, sapaan="Mbah")
    assert r["voice_script"].startswith("Mbah,")


def test_thresholds_are_respected():
    strict = replace(CFG, match_threshold=0.99, unsure_threshold=0.98)
    r = pipeline.check("air kelapa garam jeruk nipis menyembuhkan covid", strict)
    assert r["status"] == "belum_ada_pemeriksaan"
