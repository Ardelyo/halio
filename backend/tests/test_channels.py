"""Telegram/WhatsApp logic tested without touching the real services."""

from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient

from halio.api import app
from halio.channels import format as fmt
from halio.channels import telegram, whatsapp

client = TestClient(app)


class FakeHttpx:
    """Routes the bot's HTTP calls to the in-process API via TestClient."""

    HTTPError = httpx.HTTPError

    def __init__(self, fail=False):
        self.fail = fail

    def _path(self, url):
        return url.replace(telegram.API_URL, "")

    def post(self, url, timeout=None, headers=None, json=None):
        if self.fail:
            raise httpx.ConnectError("API down")
        return client.post(self._path(url), json=json, headers=headers or {})

    def get(self, url, timeout=None, params=None):
        return client.get(self._path(url))


@pytest.fixture
def bot(monkeypatch):
    sent = []

    def fake_tg(method, **kwargs):
        sent.append((method, kwargs))
        return {"ok": True}

    monkeypatch.setattr(telegram, "tg", fake_tg)
    monkeypatch.setattr(telegram, "httpx", FakeHttpx())
    telegram.sapaan_by_chat.clear()
    return sent


def msg(text, chat_id=42):
    return {"chat": {"id": chat_id}, "text": text}


def test_parse_command():
    assert telegram.parse_command("/sapaan@HalioBot Bu") == ("sapaan", "Bu")
    assert telegram.parse_command("/START") == ("start", "")
    assert telegram.parse_command("halo") == (None, "halo")


def test_start_and_privacy(bot):
    telegram.handle_message(msg("/start"))
    telegram.handle_message(msg("/privasi@HalioBot"))
    assert [m for m, _ in bot] == ["sendMessage", "sendMessage"]
    assert "Halio" in bot[0][1]["json"]["text"]
    assert "Privasi" in bot[1][1]["json"]["text"]


def test_sapaan_in_group_strips_bot_name(bot):
    telegram.handle_message(msg("/sapaan@HalioBot Mbah"))
    assert telegram.sapaan_by_chat[42] == "Mbah"


def test_forward_hoax_sends_text_card_and_keyboard(bot):
    telegram.handle_message(msg("WASPADA!!! BMKG memprediksi gempa besar dan tsunami tanggal 12 bulan depan, sebarkan!"))
    methods = [m for m, _ in bot]
    assert methods[:3] == ["sendChatAction", "sendMessage", "sendPhoto"]
    text = bot[1][1]["json"]["text"]
    assert "Terbukti salah" in text and "bmkg.go.id" in text
    keyboard = bot[1][1]["json"]["reply_markup"]["inline_keyboard"]
    assert any(b["callback_data"].startswith("app:") for row in keyboard for b in row)
    photo = bot[2][1]["files"]["photo"]
    assert photo[1][:8] == b"\x89PNG\r\n\x1a\n"


def test_unknown_offers_human_and_escalates(bot):
    telegram.handle_message(msg("Jembatan Suramadu akan ditutup total selama seminggu mulai besok"))
    payload = next(k for m, k in bot if m == "sendMessage")["json"]
    assert "Belum ada pemeriksaan" in payload["text"]
    esc = next(b for row in payload["reply_markup"]["inline_keyboard"] for b in row if b["callback_data"].startswith("esc:"))

    bot.clear()
    telegram.handle_callback({"id": "cb1", "data": esc["callback_data"], "message": {"chat": {"id": 42}}})
    assert bot[0][0] == "answerCallbackQuery"
    assert "pemeriksa manusia" in bot[1][1]["json"]["text"]


def test_trik_callback_lists_lessons(bot):
    telegram.handle_message(msg("SEGERA transfer biaya administrasi untuk bantuan tunai gratis, sebarkan!"))
    kb = next(k for m, k in bot if m == "sendMessage")["json"]["reply_markup"]["inline_keyboard"]
    trik = next(b for row in kb for b in row if b["callback_data"].startswith("trik:"))
    bot.clear()
    telegram.handle_callback({"id": "cb2", "data": trik["callback_data"], "message": {"chat": {"id": 42}}})
    assert "Meminta data atau uang" in bot[1][1]["json"]["text"]


def test_expired_callback_is_polite(bot):
    telegram.handle_callback({"id": "cb3", "data": "esc:doesnotexist", "message": {"chat": {"id": 42}}})
    assert "kedaluwarsa" in bot[1][1]["json"]["text"]


def test_sticker_or_empty_message(bot):
    telegram.handle_message({"chat": {"id": 1}, "sticker": {}})
    assert "baru bisa membaca teks" in bot[0][1]["json"]["text"]


def test_unknown_command(bot):
    telegram.handle_message(msg("/hapus"))
    assert "tidak dikenal" in bot[0][1]["json"]["text"]


def test_api_down_sends_apology(bot, monkeypatch):
    monkeypatch.setattr(telegram, "httpx", FakeHttpx(fail=True))
    telegram.handle_message(msg("Harga BBM naik besok pagi jam 6"))
    assert bot[-1][1]["json"]["text"] == telegram.SORRY


def test_very_long_message_is_truncated_not_rejected(bot):
    telegram.handle_message(msg("Bank akan memblokir rekening tidak aktif. " * 300))
    assert any(m == "sendMessage" and "text" in k["json"] and k["json"]["text"] != telegram.SORRY for m, k in bot)


def test_html_reply_escapes_user_controlled_text():
    result = {
        "status": "belum_ada_pemeriksaan", "status_label": "Belum ada pemeriksaan", "match": None,
        "voice_script": "a < b & c", "manipulation": {"techniques": []},
        "links": {"warnings": ["Tautan x.com<b>bad</b> bukan situs pemerintah"]}, "offer_human_review": True,
    }
    out = fmt.reply_text(result, html=True)
    assert "<b>bad</b>" not in out and "&lt;b&gt;bad&lt;/b&gt;" in out and "a &lt; b &amp; c" in out


def test_whatsapp_incoming_parsing():
    payload = {"entry": [{"changes": [{"value": {"messages": [
        {"from": "6281200000000", "type": "text", "text": {"body": "halo"}},
        {"from": "6281200000001", "type": "image", "image": {}},
    ]}}]}]}
    assert list(whatsapp.incoming_texts(payload)) == [("6281200000000", "halo")]


def test_whatsapp_reply_skips_when_unconfigured(monkeypatch):
    calls = []
    monkeypatch.setattr(whatsapp.httpx, "post", lambda *a, **k: calls.append(a))
    cfg = SimpleNamespace(wa_token=None, wa_phone_id=None, public_base_url="http://x")
    whatsapp.reply("62", {"status": "tidak_yakin", "status_label": "x", "match": None, "voice_script": "v",
                          "manipulation": {"techniques": []}, "links": {"warnings": []},
                          "offer_human_review": False, "card_url": "/c", "voice_url": "/v"}, cfg)
    assert calls == []


def test_whatsapp_webhook_verification():
    assert client.get("/webhook/whatsapp", params={"hub.mode": "subscribe", "hub.verify_token": "wrong"}).status_code == 403
