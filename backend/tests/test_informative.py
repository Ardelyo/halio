"""Answers must say what the thing IS, not 'belum ada pemeriksaan, jangan diteruskan' for everything."""

from dataclasses import replace

import pytest

from halio import google_agent, link_check, outlets, pipeline, reading
from halio.channels import telegram as t
from halio.channels.format import reply_text
from halio.config import Settings

CFG = Settings(google_factcheck_key=None, llm_enabled=True, llm_provider="google", link_check_enabled=True)

DETIK = ("Pertamina Dukung Pembinaan Pembalap Muda Lewat Mandalika Racing Series\n\n"
         "Baca artikel detiknews, \"Pertamina Dukung Pembinaan Pembalap Muda Lewat Mandalika Racing Series\" selengkapnya "
         "https://news.detik.com/berita/d-8741715/pertamina-dukung-pembinaan-pembalap-muda-lewat-mandalika-racing-series.\n\n"
         "Download Apps Detikcom Sekarang https://apps.detik.com/detik/")


def page(host, title, outlet="", site_name="", published="", description="", state="terbuka", **extra):
    return {"url": f"https://{host}/x", "host": host, "ok": state == "terbuka", "state": state, "final_url": f"https://{host}/x",
            "final_host": host, "status": 200, "title": title, "kind": "media" if outlet else "", "shortener": False, "note": "",
            "site_name": site_name, "description": description, "published": published, "outlet": outlet,
            "outlet_group": "Trans Media" if outlet else "", **extra}


@pytest.fixture
def offline(monkeypatch):
    """No network, and the web agent must not even be called for plain articles."""
    def agent(*a, **k):
        raise AssertionError("the web agent should not run for this message")

    monkeypatch.setattr(google_agent, "investigate", agent)
    return monkeypatch


def stub_links(monkeypatch, *pages):
    monkeypatch.setattr(link_check, "check_links", lambda text: list(pages))


NEWS_PAGE = page("news.detik.com", "Pertamina Dukung Pembinaan Pembalap Muda Lewat Mandalika Racing Series - detikNews",
                 outlet="detikNews", site_name="detiknews", published="2026-11-05T09:12:00+07:00",
                 description="Pertamina mendukung pembinaan pembalap muda lewat Mandalika Racing Series.")
APPS_PAGE = page("apps.detik.com", "Unduh Aplikasi Detikcom", outlet="detikNews")


def test_article_from_known_outlet_is_described_not_treated_as_a_rumour(offline):
    stub_links(offline, NEWS_PAGE, APPS_PAGE)
    r = pipeline.check(DETIK, CFG)
    assert r["kind"] == "berita_media" and r["reason"] == "berita_media_dikenal"
    assert r["info"]["penerbit"] == "detikNews" and r["info"]["judul"].startswith("Pertamina Dukung Pembinaan")
    assert r["info"]["terbit"] == "2026-11-05"
    assert r["links"]["warnings"] == []          # no "bukan situs pemerintah" noise for a news site
    assert r["offer_human_review"] is False
    out = reply_text(r, html=False)
    assert "BERITA DARI MEDIA DIKENAL" in out and "5 Nov 2026" in out and "detikNews" in out
    assert "jangan diteruskan" not in out.lower() and "tidak mau menebak" not in out.lower()
    assert out.count("bandingkan dengan satu atau dua media lain") == 1      # said once, not three times
    assert "apps.detik.com" not in out                                       # an app-download promo is not part of the answer
    assert "2026-11-05" not in out


def test_pushy_message_with_an_outlet_link_is_still_judged_as_a_message(offline, monkeypatch):
    monkeypatch.setattr(google_agent, "investigate", lambda *a, **k: None)   # the agent may run here
    stub_links(offline, NEWS_PAGE)
    r = pipeline.check("SEGERA SEBARKAN!! Klaim hadiah gratis Rp5 juta sekarang juga https://news.detik.com/berita/d-1 dan transfer biaya admin", CFG)
    assert r["kind"] == "pesan"


def test_unknown_site_keeps_its_caution(offline):
    stub_links(offline, page("promo-bansos-cair.xyz", "Daftar bansos"))
    r = pipeline.check("Daftar bansos di https://promo-bansos-cair.xyz/daftar sekarang", replace(CFG, llm_enabled=False))
    assert r["kind"] == "pesan" and any("bukan situs pemerintah" in w for w in r["links"]["warnings"])


def test_screenshot_of_several_headlines_is_not_one_claim(offline):
    stub_links(offline)
    r = pipeline.check("Istana Waspadai Musuh\nSiap-siap, Rekrutmen\ndalam Selimut Sekitar\nCPNS 2026 Dibuka\nPrabowo: Bersih-Bersih", CFG)
    assert r["kind"] == "kumpulan_judul" and r["reason"] == "kumpulan_judul"
    out = reply_text(r, html=False)
    assert "1. Istana Waspadai Musuh" in out and "satu judul atau satu berita per pesan" in out


def test_ai_rejection_is_explained_in_plain_words(offline):
    stub_links(offline)
    r = {"status": "belum_ada_pemeriksaan", "status_label": "Belum ada pemeriksaan", "reason": "tidak_ada_bantahan", "kind": "pesan",
         "method": "lokal+gemini_search", "match": None, "manipulation": {"techniques": []}, "links": {"warnings": [], "checked": []},
         "voice_script": "x", "offer_human_review": True, "reading": {"items": []},
         "llm": {"sumber_ditemukan": 2, "sumber_terverifikasi": 0,
                 "sumber_ditolak": [{"url": "u", "alasan": "domain_bukan_sumber_primer"}, {"url": "v", "alasan": "kutipan_tidak_ada_di_halaman"}]}}
    out = reply_text(r, html=False)
    assert "Tidak dipakai karena" in out and "media biasa" in out


def test_reading_list_drops_search_engines_and_names_the_publisher(monkeypatch):
    pages = {
        "https://vertexaisearch.cloud.google.com/r/1": page("www.google.com", "google.com"),
        "https://news.detik.com/a": NEWS_PAGE,
    }
    monkeypatch.setattr(reading, "check_link", lambda url: pages[url])
    out = reading.build([{"title": "google.com", "uri": u} for u in pages])
    assert [i["host"] for i in out["items"]] == ["news.detik.com"]
    assert out["items"][0]["kind_label"] == "detikNews"


@pytest.mark.parametrize("host,expected", [("news.detik.com", "detikNews"), ("www.kompas.com", "Kompas.com"), ("m.cnnindonesia.com", "CNN Indonesia")])
def test_outlet_lookup(host, expected):
    assert outlets.lookup(host).name == expected


def test_same_group_outlets_are_one_voice():
    assert outlets.lookup("detik.com").group == outlets.lookup("cnnindonesia.com").group
    assert outlets.lookup("kompas.com").group != outlets.lookup("tempo.co").group


# --- Telegram -------------------------------------------------------------------------------------------------

class Resp:
    def __init__(self, status=200, data=None):
        self.status_code, self._d = status, data or {}

    def json(self):
        return self._d

    def raise_for_status(self):
        if self.status_code >= 400:
            raise t.httpx.HTTPStatusError("x", request=None, response=self)


def test_news_answer_has_no_card_voice_or_banding_button(monkeypatch):
    calls = []
    monkeypatch.setattr(t, "tg", lambda m, **kw: calls.append((m, kw)))
    monkeypatch.setattr(t.httpx, "get", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no card or voice expected")))
    result = {"id": "a" * 32, "status": "belum_ada_pemeriksaan", "status_label": "Belum ada pemeriksaan", "reason": "berita_media_dikenal",
              "kind": "berita_media", "info": {"judul": "J", "penerbit": "detikNews", "terbit": "2026-11-05", "ringkasan": ""},
              "match": None, "manipulation": {"techniques": []}, "links": {"warnings": [], "checked": []}, "voice_script": "v",
              "offer_human_review": False, "reading": {"items": []}, "method": "lokal"}
    t.send_result(1, result, reply_to=77)
    assert [m for m, _ in calls] == ["sendMessage"]
    body = calls[0][1]["json"]
    assert body["reply_to_message_id"] == 77 and body["reply_markup"]["inline_keyboard"] == []


def test_button_recovers_after_a_restart_using_the_replied_message(monkeypatch):
    sent, posts = [], []
    monkeypatch.setattr(t, "tg", lambda m, **kw: sent.append((m, kw)))

    def get(url, **k):
        return Resp(404) if "/api/check/old" in url else Resp(200, {"manipulation": {"techniques": []}})

    def post(url, **k):
        posts.append(url)
        return Resp(200, {"id": "newid", "message": "Tiket 5"}) 

    monkeypatch.setattr(t.httpx, "get", get)
    monkeypatch.setattr(t.httpx, "post", post)
    cb = {"id": "c", "data": "esc:old", "message": {"chat": {"id": 9}, "reply_to_message": {"text": "Jembatan ditutup total besok pagi"}}}
    t.handle_callback(cb)
    assert any(u.endswith("/api/check") for u in posts) and any(u.endswith("/api/escalate") for u in posts)
    assert sent[-1][1]["json"]["text"] == "Tiket 5"


def test_button_without_recoverable_text_says_so_plainly(monkeypatch):
    sent = []
    monkeypatch.setattr(t, "tg", lambda m, **kw: sent.append((m, kw)))
    monkeypatch.setattr(t.httpx, "get", lambda *a, **k: Resp(404))
    t.handle_callback({"id": "c", "data": "esc:old", "message": {"chat": {"id": 9}}})
    assert "kedaluwarsa" in sent[-1][1]["json"]["text"]


def test_a_hoax_chain_written_in_short_lines_is_not_mistaken_for_headlines(offline, monkeypatch):
    monkeypatch.setattr(google_agent, "investigate", lambda *a, **k: None)
    stub_links(offline)
    chain = "Hati-hati\nAda penculik anak\nnaik mobil putih\nkeliling sekolah\nSebarkan ke semua grup"
    r = pipeline.check(chain, CFG)
    assert r["kind"] == "pesan"


def test_article_that_is_itself_a_known_hoax_is_still_judged(offline, monkeypatch):
    monkeypatch.setattr(google_agent, "investigate", lambda *a, **k: None)
    stub_links(offline, page("www.liputan6.com", "Cek Fakta: Hoaks Video Menkeu Bagi Bantuan Tunai Lewat WhatsApp", outlet="Liputan6"))
    r = pipeline.check("Presiden Prabowo dan Menteri Keuangan membagikan bantuan tunai, daftar lewat nomor WhatsApp dan bayar biaya admin "
                       "https://www.liputan6.com/cek-fakta/read/1", CFG)
    assert r["status"] == "terbukti_salah"
