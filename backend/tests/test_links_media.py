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
