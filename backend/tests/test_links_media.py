"""Link checking and photo/voice reading: facts about the link, never a verdict on the picture."""

import base64

import httpx
import pytest
from fastapi.testclient import TestClient

from halio import api, link_check, media
from halio.channels import telegram as t
from halio.config import Settings


def transport(handler):
    return httpx.MockTransport(handler)


def test_extract_urls_strips_punctuation_and_caps():
    urls = link_check.extract_urls("Lihat https://a.go.id/x. dan http://b.com/y, https://c.id https://d.id https://e.id")
    assert urls[0] == "https://a.go.id/x" and len(urls) == 3


def test_dead_link_is_reported_not_trusted():
    out = link_check.check_link("https://berita.example/x", transport(lambda r: httpx.Response(404)))
    assert out["state"] == "rusak" and out["status"] == 404
    assert "tidak bisa dibuka" in link_check.warning_for(out)


def test_redirect_to_other_domain_is_named():
    # kl link pemendek belok ke domain aneh, buka kedok domain tujuan aslinya di peringatan
    def handler(req):
        if req.url.host == "bit.ly":
            return httpx.Response(302, headers={"location": "https://bansos-cair.xyz/daftar"})
        return httpx.Response(200, headers={"content-type": "text/html"}, text="<title>Daftar Bansos</title>")

    out = link_check.check_link("https://bit.ly/abc", transport(handler))
    assert out["state"] == "terbuka" and out["final_host"] == "bansos-cair.xyz" and out["shortener"]
    assert out["title"] == "Daftar Bansos"
    assert "bansos-cair.xyz" in link_check.warning_for(out)


def test_official_site_has_no_warning():
    out = link_check.check_link("https://www.bmkg.go.id/", transport(lambda r: httpx.Response(200, headers={"content-type": "text/html"}, text="<title>BMKG</title>")))
    assert out["kind"] == "resmi" and link_check.warning_for(out) is None


def test_private_address_is_refused_without_fetch():
    # alamat lokal / privat langsung ditolak tanpa sempet nembak koneksi
    out = link_check.check_link("http://127.0.0.1:8000/api/radar")
    assert out["state"] == "tidak_ditemukan" and out["status"] is None


def test_media_off_by_default(monkeypatch):
    monkeypatch.delenv("HALIO_MEDIA", raising=False)
    assert media.read_media(b"x" * 10, "image/png", Settings()) is None


def test_media_rejects_unsupported_type():
    assert not media.supported("application/x-msdownload")


@pytest.fixture
def client():
    return TestClient(api.app)


def test_check_media_returns_503_when_reader_down(client, monkeypatch):
    monkeypatch.setattr(media, "read_media", lambda *a: None)
    r = client.post("/api/check-media", json={"data_b64": base64.b64encode(b"x" * 200).decode(), "mime": "image/png"})
    assert r.status_code == 503


def test_check_media_runs_text_through_pipeline_and_never_claims_authenticity(client, monkeypatch):
    # teks di dlm poster lanjut dicek ke pipeline, tp jujur bilang blm ngecek keaslian foto/deepfake
    reading = media.MediaReading(kind="poster_atau_berita", text="Bapak ibu, ada video Presiden bagi-bagi bantuan tunai, bayar biaya admin 150rb lewat WA. SEBARKAN!!")
    monkeypatch.setattr(media, "read_media", lambda *a: reading)
    r = client.post("/api/check-media", json={"data_b64": base64.b64encode(b"x" * 200).decode(), "mime": "image/png"})
    body = r.json()
    assert r.status_code == 200 and body["status"] == "terbukti_salah"
    assert body["media"]["authenticity_checked"] is False


def test_check_media_unreadable(client, monkeypatch):
    monkeypatch.setattr(media, "read_media", lambda *a: media.MediaReading(kind="foto_biasa", text="", readable=False))
    r = client.post("/api/check-media", json={"data_b64": base64.b64encode(b"x" * 200).decode(), "mime": "image/png"})
    assert r.json()["readable"] is False


def test_check_media_bad_type(client):
    r = client.post("/api/check-media", json={"data_b64": base64.b64encode(b"x" * 200).decode(), "mime": "text/html"})
    assert r.status_code == 415


def test_telegram_media_detection():
    assert t._media_of({"photo": [{"file_id": "s"}, {"file_id": "big"}]}) == ("big", "image/jpeg")
    assert t._media_of({"voice": {"file_id": "v"}}) == ("v", "audio/ogg")
    assert t._media_of({"document": {"file_id": "d", "mime_type": "application/zip"}}) is None
    assert t._media_of({"text": "hai"}) is None


def test_versi_and_bantuan_commands_answer(monkeypatch):
    calls = []
    monkeypatch.setattr(t, "tg", lambda method, **kw: calls.append((method, kw)) or {"ok": True})
    monkeypatch.setattr(t, "_status_line", lambda: "API: aktif")
    t.handle_message({"chat": {"id": 7}, "text": "/versi"})
    t.handle_message({"chat": {"id": 7}, "text": "/bantuan"})
    t.handle_message({"chat": {"id": 7}, "text": "/start"})
    texts = [kw["json"]["text"] for _, kw in calls]
    assert "Halio v" in texts[0] and "API: aktif" in texts[0]
    assert "Bantuan" in texts[1]
    assert "Halio v" in texts[2] and "Cara pakai" in texts[2]


def test_reply_shows_how_halio_checked_and_version():
    from halio import pipeline
    from halio.channels.format import reply_text

    out = reply_text(pipeline.check("Jembatan Suramadu akan ditutup total selama seminggu mulai besok.", Settings()), html=True)
    assert "Cara Halio memeriksa" in out and "Sebaiknya" in out and "Halio v" in out


def test_soft_404_page_is_not_a_good_link():
    # tes kasus pojok soft-404: balikin HTTP 200 tp judulnya halaman ga ketemu, jgn ketukar sm berita "Rp 404 juta" wkwk
    html = "<title>404 - Halaman tidak ditemukan</title>"
    out = link_check.check_link("https://x.example/a", transport(lambda r: httpx.Response(200, headers={"content-type": "text/html"}, text=html)))
    assert out["state"] == "rusak"
    ok = link_check.check_link("https://x.example/b", transport(lambda r: httpx.Response(200, headers={"content-type": "text/html"}, text="<title>Rp 404 juta dibagikan</title>")))
    assert ok["state"] == "terbuka"


def test_best_passage_is_verbatim_and_needs_real_overlap():
    from halio.source_verifier import best_passage, quote_present

    page = "Beranda. Video Presiden Prabowo membagikan bantuan tunai lewat WhatsApp adalah hoaks dan hasil rekayasa teknologi. Lihat juga berita olahraga."
    p = best_passage("Presiden Prabowo membagikan bantuan tunai lewat WhatsApp", page)
    assert p and quote_present(p, page)
    assert best_passage("Jembatan Suramadu ditutup total seminggu", page) is None


def test_reading_list_filters_dead_pages(monkeypatch):
    # saring keluar link yg udah mati dr daftar bacaan lanjutan
    from halio import reading

    def fake(url):
        dead = "mati" in url
        return {"state": "rusak" if dead else "terbuka", "final_url": url, "final_host": "x", "title": "T", "kind": "resmi" if "go.id" in url else ""}

    monkeypatch.setattr(reading, "check_link", fake)
    out = reading.build([{"title": "a", "uri": "https://a.com/mati"}, {"title": "b", "uri": "https://b.go.id/x"}, {"title": "c", "uri": "https://c.com/y"}])
    assert [i["url"] for i in out["items"]] == ["https://b.go.id/x", "https://c.com/y"] and out["disaring"] == 1


def test_reading_list_keeps_only_pages_about_the_claim():
    from halio import evidence
    from halio.source_verifier import Page

    claim = "Anak Jakarta juara satu di Harvard sebagai orang terbodoh"
    off = Page(text="Empat tips menghindari berita hoax penculikan anak di sekolah.", final_url="https://rri.co.id/a", title="Tips hoax penculikan anak")
    on = Page(text="Seorang anak Jakarta disebut juara satu di Harvard sebagai orang terbodoh, ini penjelasannya.", final_url="https://www.kompas.com/b", title="Anak Jakarta Harvard")
    out = evidence.reading_list(claim, [off, on], [], [], [])
    assert [i["url"] for i in out["items"]] == ["https://www.kompas.com/b"]


def test_empty_result_gives_next_steps_and_plain_sentence():
    from halio.channels.format import reply_text
    from halio import pipeline

    r = pipeline.check("Seorang anak jakarta berhasil meraih juara 1 di harvard sebagai orang terbodoh", Settings())
    assert r["status"] == "belum_ada_pemeriksaan" and len(r["cari_sendiri"]) == 3
    out = reply_text(r, html=True)
    assert "Cari sendiri" in out and "turnbackhoax.id/?s=" in out


def test_green_is_lowered_when_a_factchecker_covers_the_topic_as_hoax():
    # kl ada situs cek fakta yg bahas isu serupa sbg hoaks, rem dulu jgn dikasih hijau
    from halio import pipeline

    assert pipeline._factcheck_warns({"items": [{"kind": "cek_fakta", "title": "[HOAKS] Pendaftaran CPNS 2026 Sudah Dibuka"}]})
    assert not pipeline._factcheck_warns({"items": [{"kind": "media", "title": "Hoaks CPNS"}]})
    assert not pipeline._factcheck_warns({"items": [{"kind": "cek_fakta", "title": "Cek Fakta: BMKG jelaskan gempa hari ini"}]})


def test_attribution_mismatch_is_flagged_but_content_verdict_kept():
    # kl pesan nyatut nama lembaga yg beda dr sumber bantahan (PMI vs BMKG), vonis isinya tetep tp kasih catatan jelas
    from halio import pipeline
    from halio.channels.format import reply_text

    r = pipeline.check("WASPADA!!! Menurut PMI akan terjadi gempa besar dan tsunami tanggal 12 bulan depan. Segera siapkan tas siaga!", Settings())
    assert r["status"] == "terbukti_salah"
    assert r["attribution"] and "PMI" in r["attribution"]["pesan"] and "BMKG" in r["attribution"]["bantahan"]
    assert "Sumber yang disebut berbeda" in reply_text(r, html=True)


def test_no_attribution_note_when_same_agency_or_none():
    from halio import pipeline

    same = pipeline.check("Menurut BMKG akan terjadi gempa besar dan tsunami tanggal 12 bulan depan, segera siapkan tas siaga!", Settings())
    none = pipeline.check("Akan terjadi gempa besar dan tsunami tanggal 12 bulan depan, segera siapkan tas siaga!", Settings())
    assert same["attribution"] is None and none["attribution"] is None
