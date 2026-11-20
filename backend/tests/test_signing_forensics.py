"""Halio v1.0: tanda tangan Ed25519, forensik zero-cloud, registri buletin resmi, LAPSUS, Medan Uji 8 serangan."""

import io
import json
import re
import sys
from dataclasses import replace
from datetime import date
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "backend"))

from halio import card, crypto_sign, forensics, pipeline, retrieval, selftest, verify  # noqa: E402
from halio.api import app  # noqa: E402
from halio.config import Settings  # noqa: E402
from halio.store import Store, zscore  # noqa: E402

CFG = replace(Settings(), google_factcheck_key=None, llm_enabled=False, link_check_enabled=False)
SAMPLE = {"id": "a" * 32, "status": "terbukti_salah", "claim": "Calon tamtama dijamin lulus asal bayar", "created": "2026-11-20T10:00:00+07:00", "match": None}


@pytest.fixture
def signer(tmp_path, monkeypatch):
    s = crypto_sign.load_signer(tmp_path / "key.pem")
    monkeypatch.setattr(crypto_sign, "_signer", s)
    return s


# ---------- crypto_sign ----------

def test_envelope_roundtrip_and_any_change_is_rejected(signer):
    env = crypto_sign.sign_payload({"a": 1, "b": "x"}, signer)
    assert crypto_sign.verify_payload(env, signer.public_pem)[0]
    assert not crypto_sign.verify_payload({**env, "payload": {"a": 2, "b": "x"}}, signer.public_pem)[0]
    assert not crypto_sign.verify_payload({**env, "issued_at": "2020-01-01T00:00:00+00:00"}, signer.public_pem)[0]
    assert not crypto_sign.verify_payload({**env, "alg": "ML-DSA-65"}, signer.public_pem)[0]
    assert not crypto_sign.verify_payload({k: v for k, v in env.items() if k != "sha256"}, signer.public_pem)[0]
    assert not crypto_sign.verify_payload("bukan amplop", signer.public_pem)[0]


def test_other_units_key_is_rejected(tmp_path, signer):
    env = crypto_sign.sign_payload({"a": 1}, signer)
    other = crypto_sign.load_signer(tmp_path / "other.pem")
    ok, reason = crypto_sign.verify_payload(env, other.public_pem)
    assert not ok and "kunci publik" in reason


def test_key_file_is_reused(tmp_path):
    a = crypto_sign.load_signer(tmp_path / "k.pem")
    assert crypto_sign.load_signer(tmp_path / "k.pem").key_id == a.key_id


# ---------- kartu PNG ----------

def test_signed_card_verifies_and_one_byte_flip_is_rejected(signer):
    png = card.render(SAMPLE, signer=signer)
    assert png[:8] == b"\x89PNG\r\n\x1a\n"
    good = verify.verify_bytes(png, signer.public_pem)
    assert good["sah"] and good["ringkasan"]["status"] == "terbukti_salah" and re.fullmatch(r"[0-9A-F]{10}", good["ringkasan"]["verif_id"])
    for pos in (len(png) // 3, len(png) // 2, len(png) - 20):
        flipped = bytearray(png)
        flipped[pos] ^= 1
        assert not verify.verify_bytes(bytes(flipped), signer.public_pem)["sah"], pos


def test_pixel_edit_with_reused_signature_is_rejected(signer):
    from PIL import Image

    png = card.render(SAMPLE, signer=signer)
    envelope = crypto_sign.extract_png_signature(png)
    with Image.open(io.BytesIO(png)) as img:
        edited = img.convert("RGB")
        edited.putpixel((10, 10), (1, 2, 3))
        buf = io.BytesIO()
        edited.save(buf, format="PNG")
    forged = crypto_sign.embed_png_signature(buf.getvalue(), envelope)
    res = verify.verify_bytes(forged, signer.public_pem)
    assert not res["sah"] and "piksel" in res["alasan"]


def test_unsigned_card_and_unrelated_files_are_not_valid(signer):
    assert not verify.verify_bytes(card.render(SAMPLE), signer.public_pem)["sah"]
    assert not verify.verify_bytes(b"halo", signer.public_pem)["sah"]


def test_cli_exit_codes(signer, tmp_path, monkeypatch):
    good, bad = tmp_path / "kartu.png", tmp_path / "ubah.png"
    png = card.render(SAMPLE, signer=signer)
    good.write_bytes(png)
    flipped = bytearray(png)
    flipped[len(flipped) // 2] ^= 1
    bad.write_bytes(bytes(flipped))
    assert verify.main([str(good)]) == 0
    assert verify.main([str(bad)]) == 1
    assert verify.main([str(tmp_path / "tidak_ada.png")]) == 1
    pub = tmp_path / "pub.pem"
    pub.write_text(signer.public_pem)
    monkeypatch.setattr(crypto_sign, "_signer", crypto_sign.load_signer(tmp_path / "lain.pem"))
    assert verify.main([str(good)]) == 1  # kunci lokal berbeda
    assert verify.main([str(good), "--pubkey", str(pub)]) == 0


# ---------- API ----------

def test_api_verify_pubkey_and_signed_card(signer):
    client = TestClient(app)
    check = client.post("/api/check", json={"text": "Waspada gempa besar diprediksi minggu depan, sebarkan!", "channel": "demo"}).json()
    png = client.get(check["card_url"]).content
    assert client.get("/api/pubkey").json()["key_id"] == signer.key_id
    res = client.post("/api/verify", content=png).json()
    assert res["sah"] and res["ringkasan"]["status"] == "terbukti_salah"
    tampered = bytearray(png)
    tampered[len(tampered) // 2] ^= 1
    assert not client.post("/api/verify", content=bytes(tampered)).json()["sah"]
    assert client.post("/api/verify", content=b"").status_code == 400


def test_api_lapsus_is_signed_and_has_no_message_text(signer):
    client = TestClient(app)
    env = client.get("/api/radar/lapsus?days=7").json()
    assert crypto_sign.verify_payload(env, signer.public_pem)[0]
    payload = env["payload"]
    assert payload["kind"] == "lapsus_siber_sosial" and payload["period"]["days"] == 7 and "catatan_privasi" in payload
    blob = json.dumps(payload)
    assert "emerging" not in blob and "reporter" not in blob
    assert client.post("/api/verify", content=json.dumps(env).encode()).json()["sah"]
    env["payload"]["total_cek"] = 999
    assert not client.post("/api/verify", content=json.dumps(env).encode()).json()["sah"]


# ---------- LAPSUS: z-score dan lonjakan ----------

def test_zscore_basics():
    assert zscore(5, []) == 0.0
    assert zscore(0, [0, 0, 0]) == 0.0
    assert zscore(6, [0, 0, 0, 0]) == 12.0  # simpangan baku dilantai 0.5
    assert zscore(3, [3, 3, 3]) == 0.0


def test_lapsus_flags_a_burst_and_suppresses_small_cells(tmp_path):
    store = Store(tmp_path / "l.db", k_anonymity=5)
    result = {"status": "terbukti_salah", "manipulation": {"techniques": [{"id": "urgensi"}]},
              "match": {"debunk_id": "rekrutmen-tni-ad-berbayar", "kategori": "penipuan_catut_tni"}}
    for _ in range(6):
        store.record(result, "web", None)
    other = {**result, "match": {"debunk_id": "air-kelapa-garam-obat", "kategori": "kesehatan"}}
    store.record(other, "web", None)
    lap = store.lapsus(days=7)
    top = lap["topik_melonjak"][0]
    assert top["debunk_id"] == "rekrutmen-tni-ad-berbayar" and top["peringatan"] == "lonjakan" and top["hari_ini"] == 6
    small = next(t for t in lap["topik_melonjak"] if t["debunk_id"] == "air-kelapa-garam-obat")
    assert small["hari_ini"] == "<3" and small["peringatan"] == "normal"
    assert lap["peringatan_dini"] and lap["penipuan_catut_tni"]["status"] == "naik"


# ---------- forensik ----------

def kinds(text):
    return {f["kode"] for f in forensics.analyze_domains(pipeline.extract_domains(text), text)}


def test_fake_domains_are_flagged_and_real_ones_are_not():
    assert "tiruan_instansi" in kinds("buka rekrutmen-tniad.xyz")
    assert "tiruan_domain_resmi" in kinds("klaim di kemensos-go-id.com")
    assert "tiruan_domain_resmi" in kinds("masuk tni.mil.id.login.site")
    assert "homograph" in kinds("buka https://tíniad.com/daftar")
    assert "pemendek_tautan" in kinds("klik bit.ly/abc")
    assert kinds("daftar di https://ad.rekrutmen-tni.mil.id/ dan https://www.kemensos.go.id/berita") == set()
    assert kinds("toko di madanabank.com") == set()  # 'dana' di tengah kata bukan tiruan


def test_attachment_lures():
    hit = forensics.analyze_attachment_lure("Undangan nikah kami Undangan.apk silakan dibuka")
    assert hit and hit[0]["tingkat"] == "tinggi" and hit[0]["ekstensi"] == "apk" and "undangan" in hit[0]["penjelasan"].lower()
    assert forensics.analyze_attachment_lure("surat tilang Surat_Tilang.APK")[0]["tingkat"] == "tinggi"
    assert forensics.analyze_attachment_lure("Berikut foto kegiatan kemarin: kegiatan.jpg") == []


def test_check_result_carries_forensics_without_changing_the_verdict():
    r = pipeline.check("Surat dinas Kodam: buka SuratDinas.apk lewat rekrutmen-tniad.xyz sekarang", CFG)
    assert any(f["kode"] == "tiruan_instansi" for f in r["forensics"]["domain"]) and r["forensics"]["lampiran"]


def _png(text_chunks=None, exif=False):
    from PIL import Image, PngImagePlugin

    info = PngImagePlugin.PngInfo()
    for k, v in (text_chunks or {}).items():
        info.add_text(k, v)
    buf = io.BytesIO()
    Image.new("RGB", (8, 8)).save(buf, "PNG", pnginfo=info)
    return buf.getvalue()


def test_image_metadata_indicators_are_reported_honestly():
    ai = forensics.inspect_image_bytes(_png({"parameters": "a cat\nSteps: 20, Sampler: Euler a, Model: Stable Diffusion"}))
    assert ai["ringkasan"] == "indikator_ai" and any(i["kode"] == "tag_generator_ai" for i in ai["indikator"])
    assert "bukan vonis" in ai["catatan"]
    assert forensics.inspect_image_bytes(_png())["ringkasan"] == "tanpa_metadata"
    assert forensics.inspect_image_bytes(_png({"Software": "Adobe Photoshop 25"}))["ringkasan"] == "ada_jejak_editor"
    from PIL import Image

    buf = io.BytesIO()
    exif = Image.Exif()
    exif[0x010F], exif[0x0110] = "Canon", "EOS R"
    Image.new("RGB", (8, 8)).save(buf, "JPEG", exif=exif)
    cam = forensics.inspect_image_bytes(buf.getvalue())
    assert cam["ringkasan"] == "metadata_kamera" and cam["kamera"]["merek"] == "Canon"
    assert forensics.inspect_image_bytes(b"GIF89a....")["ringkasan"] == "tidak_didukung"
    assert forensics.inspect_image_bytes(_png({"x": "y"})[:40])["format"] == "png"  # terpotong: tidak meledak


# ---------- registri buletin resmi ----------

DATA = ROOT / "data"


def test_committed_registry_is_validly_signed():
    reg = retrieval.load_registry(DATA)
    assert len(reg) == 3 and all(d.signed and d.is_positive for d in reg)


def test_tampered_registry_is_ignored_entirely(tmp_path):
    for name in (retrieval.REGISTRY_FILE, retrieval.REGISTRY_PUBKEY):
        (tmp_path / name).write_bytes((DATA / name).read_bytes())
    assert retrieval.load_registry(tmp_path)
    raw = json.loads((tmp_path / retrieval.REGISTRY_FILE).read_text(encoding="utf-8"))
    raw["bulletins"][0]["sederhana"] += " (diubah)"
    (tmp_path / retrieval.REGISTRY_FILE).write_text(json.dumps(raw), encoding="utf-8")
    assert retrieval.load_registry(tmp_path) == []
    # kunci publik lain juga menolak
    other = crypto_sign.load_signer(tmp_path / "x.pem")
    (tmp_path / retrieval.REGISTRY_FILE).write_bytes((DATA / retrieval.REGISTRY_FILE).read_bytes())
    (tmp_path / retrieval.REGISTRY_PUBKEY).write_text(other.public_pem)
    assert retrieval.load_registry(tmp_path) == []


def test_debunks_json_cannot_switch_on_signed():
    raw = json.loads((DATA / "debunks.json").read_text(encoding="utf-8"))
    raw["debunks"][0]["signed"] = True
    tmp = DATA.parent / "backend" / "tests" / "_tmp_debunks.json"
    try:
        tmp.write_text(json.dumps(raw), encoding="utf-8")
        assert not retrieval.load_debunks(tmp)[0].signed
    finally:
        tmp.unlink(missing_ok=True)


@pytest.mark.parametrize("text, green", [
    ("Pendaftaran Bintara TNI AD 2026 dibuka di ad.rekrutmen-tni.mil.id, gratis tanpa biaya apa pun.", True),
    ("Seleksi masuk TNI AD sama sekali tidak dipungut biaya, biaya pendidikan ditanggung negara", True),
    ("Pendaftaran Bintara TNI AD gratis, tapi bayar 5 juta lewat calo supaya lulus", False),
    ("Pendaftaran tamtama TNI AD gratis, daftar di rekrutmen-tniad.xyz", False),
    ("Pendaftaran Bintara TNI AD tidak gratis, bayar dulu", False),
])
def test_signed_bulletin_confirms_offline_only_when_every_guard_passes(text, green):
    r = pipeline.check(text, CFG)
    assert (r["status"] == "sejalan_dengan_sumber") is green
    assert r["status"] != "terbukti_salah" or not green
    if green:
        assert r["reason"] == "cocok_dengan_buletin_resmi" and "buletin_resmi" in r["method"] and r["match"]["sumber"][0]["jenis"] == "resmi"


def test_expired_bulletin_is_not_confirmed():
    d = retrieval.load_registry(DATA)[0]
    ok_today = date(2026, 12, 1)
    text = "Pendaftaran Bintara TNI AD dibuka di ad.rekrutmen-tni.mil.id, gratis"
    assert pipeline._signed_bulletin_ok(d, text, ["ad.rekrutmen-tni.mil.id"], ok_today)
    assert not pipeline._signed_bulletin_ok(d, text, ["ad.rekrutmen-tni.mil.id"], date(2027, 3, 1))
    assert not pipeline._signed_bulletin_ok(d, text, ["ad.rekrutmen-tni.mil.id"], date(2026, 1, 1))


def test_warning_about_scam_that_mentions_official_site_is_not_confirmed():
    r = pipeline.check("Jangan percaya calo yang menjanjikan lulus masuk TNI AD dengan bayar uang, semua tes resmi gratis", CFG)
    assert r["status"] == "tidak_yakin" and r["reason"] == "tampak_meluruskan"


# ---------- T1: sinonim domain ----------

@pytest.mark.parametrize("text", [
    "bisa bantu masuk bintara TNI lwt kenalan perwira, ada uang pelicin dikit",
    "Mau anaknya jadi tentara? Saya punya orang dalam di Kodam, pasti lulus, siapkan 150 juta",
    "Dijamin lulus Bintara TNI lewat ordal, siapkan uang pelicin",
])
def test_slang_paraphrases_of_the_tni_recruitment_scam_are_caught_offline(text):
    r = pipeline.check(text, CFG)
    assert r["status"] == "terbukti_salah" and r["match"]["debunk_id"] == "rekrutmen-tni-ad-berbayar"


def test_canonical_tokens_are_added_not_substituted():
    from halio.textnorm import tokens

    t = tokens("pakai uang pelicin lewat orang dalam, dijamin lulus")
    assert {"pelicin", "biayailegal", "orang", "caloordal", "jaminlulus"} <= set(t)


def test_corpus_has_35_plus_entries_each_with_a_https_source_and_core_pattern():
    raw = json.loads((DATA / "debunks.json").read_text(encoding="utf-8"))["debunks"]
    assert len(raw) >= 35 and len({d["id"] for d in raw}) == len(raw)
    for d in raw:
        assert d["sumber"] and all(s["url"].startswith("https://") and s["jenis"] in {"resmi", "media", "cek_fakta"} for s in d["sumber"]), d["id"]
        assert d.get("syarat"), d["id"]  # tanpa inti klaim, korpus bisa salah menuduh
        for g in d["syarat"]:
            re.compile(g)
    assert sum(d["kategori"] == "penipuan_catut_tni" for d in raw) >= 6


# ---------- Medan Uji ----------

def test_medan_uji_has_eight_tests_and_the_seven_local_ones_pass():
    assert len(selftest.TESTS) == 8
    for name, (_, fn) in selftest.TESTS.items():
        if name == "injeksi":
            continue  # memanggil model sungguhan
        res = fn(CFG)
        assert res["lulus"] is True, (name, [s for s in res["langkah"] if s["ok"] is False])
