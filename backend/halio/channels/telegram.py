"""Telegram bot (primary chat channel for the prototype).

Talks to the Halio HTTP API so the bot can run anywhere:
    set TELEGRAM_BOT_TOKEN=...   HALIO_API_URL=http://localhost:8000
    python -m halio.channels.telegram
"""

from __future__ import annotations

import html
import json
import logging
import os
import time

import httpx

from .format import reply_text

log = logging.getLogger("halio.telegram")

API_URL = os.getenv("HALIO_API_URL", "http://localhost:8000").rstrip("/")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TG = f"https://api.telegram.org/bot{TOKEN}"

WELCOME = (
    "Halo! Saya <b>Halio</b>, teman cek pesan keluarga.\n\n"
    "Teruskan (forward) pesan yang meragukan ke sini. Saya akan menjawab dengan bahasa sederhana, "
    "kartu yang bisa dibagikan ke grup keluarga, dan pesan suara.\n\n"
    "Saya hanya membaca pesan yang Anda kirim ke sini. Saya tidak membuat vonis sendiri: "
    "jawaban selalu dari pemeriksa fakta atau sumber resmi, dan kalau belum ada, saya bilang terus terang.\n\n"
    "Perintah: /sapaan Bu  (cara saya memanggil Anda), /privasi"
)
PRIVACY = (
    "🔒 <b>Privasi Halio</b>\n"
    "• Nomor telepon, NIK, email, dan tautan dihapus sebelum diproses.\n"
    "• Hasil cek disimpan di memori paling lama 1 jam untuk kartu dan suara.\n"
    "• Statistik hanya berupa jumlah per kategori, tanpa isi pesan dan tanpa identitas.\n"
    "• Isi kabar yang belum dikenal baru dicatat bila sudah dikirim banyak orang berbeda (k-anonimitas)."
)

sapaan_by_chat: dict[int, str] = {}  # in memory only; families set it once


def tg(method: str, **kwargs) -> dict:
    resp = httpx.post(f"{TG}/{method}", timeout=40, **kwargs)
    data = resp.json()
    if not data.get("ok"):
        log.warning("Telegram %s failed: %s", method, data)
    return data


def send_result(chat_id: int, result: dict) -> None:
    keyboard = [[{"text": "🧠 Kenali triknya", "callback_data": f"trik:{result['id']}"}]]
    if result["offer_human_review"]:
        keyboard.insert(0, [{"text": "🙋 Tanya pemeriksa manusia", "callback_data": f"esc:{result['id']}"}])
    else:
        keyboard.append([{"text": "⚖️ Ajukan banding", "callback_data": f"app:{result['id']}"}])

    tg("sendMessage", json={
        "chat_id": chat_id, "text": reply_text(result, html=True), "parse_mode": "HTML",
        "disable_web_page_preview": True, "reply_markup": {"inline_keyboard": keyboard},
    })
    card = httpx.get(f"{API_URL}{result['card_url']}", timeout=20)
    if card.status_code == 200:
        tg("sendPhoto", data={"chat_id": chat_id, "caption": "Kartu Halio: bagikan ke grup keluarga untuk meluruskan."},
           files={"photo": ("kartu-halio.png", card.content, "image/png")})
    audio = httpx.get(f"{API_URL}{result['voice_url']}", timeout=30)
    if audio.status_code == 200:
        tg("sendAudio", data={"chat_id": chat_id, "title": "Halio Suara", "performer": "Halio"},
           files={"audio": ("halio-suara.mp3", audio.content, "audio/mpeg")})


def handle_message(msg: dict) -> None:
    chat_id = msg["chat"]["id"]
    text = msg.get("text") or msg.get("caption") or ""
    if text.startswith("/start"):
        tg("sendMessage", json={"chat_id": chat_id, "text": WELCOME, "parse_mode": "HTML"})
        return
    if text.startswith("/privasi"):
        tg("sendMessage", json={"chat_id": chat_id, "text": PRIVACY, "parse_mode": "HTML"})
        return
    if text.startswith("/sapaan"):
        value = text.removeprefix("/sapaan").strip()[:30] or "Bapak, Ibu"
        sapaan_by_chat[chat_id] = value
        tg("sendMessage", json={"chat_id": chat_id, "text": f"Baik, saya akan memanggil Anda “{html.escape(value)}”."})
        return
    if len(text.strip()) < 3:
        tg("sendMessage", json={"chat_id": chat_id, "text": "Untuk sekarang saya baru bisa membaca teks. Teruskan pesan tulisannya, ya."})
        return

    tg("sendChatAction", json={"chat_id": chat_id, "action": "typing"})
    resp = httpx.post(f"{API_URL}/api/check", timeout=30, json={
        "text": text, "channel": "telegram", "reporter": f"tg:{chat_id}",
        "sapaan": sapaan_by_chat.get(chat_id, "Bapak, Ibu"),
    })
    resp.raise_for_status()
    send_result(chat_id, resp.json())


def handle_callback(cb: dict) -> None:
    action, _, check_id = cb.get("data", "").partition(":")
    chat_id = cb["message"]["chat"]["id"]
    tg("answerCallbackQuery", json={"callback_query_id": cb["id"]})
    if action == "esc":
        r = httpx.post(f"{API_URL}/api/escalate", json={"check_id": check_id}, timeout=10)
        text = r.json().get("message") if r.status_code == 200 else "Maaf, hasil cek sudah kedaluwarsa. Kirim ulang pesannya, ya."
    elif action == "app":
        httpx.post(f"{API_URL}/api/appeal", json={"check_id": check_id, "reason": "banding dari telegram"}, timeout=10)
        text = "Banding dicatat. Tim akan meninjau ulang sumbernya. Terima kasih sudah kritis!"
    elif action == "trik":
        r = httpx.get(f"{API_URL}/api/check/{check_id}", timeout=10)
        techs = r.json()["manipulation"]["techniques"] if r.status_code == 200 else []
        text = "\n\n".join(f"<b>{t['label']}</b>\n{t['lesson']}" for t in techs) or (
            "Pesan ini tidak memakai trik manipulasi yang umum. Tetap cek sumbernya sebelum meneruskan, ya.")
    else:
        return
    tg("sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})


def main() -> None:
    if not TOKEN:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN (dari @BotFather) terlebih dahulu.")
    logging.basicConfig(level=logging.INFO)
    log.info("Halio Telegram bot started, API=%s", API_URL)
    offset = 0
    while True:
        try:
            updates = httpx.get(f"{TG}/getUpdates", params={"timeout": 30, "offset": offset}, timeout=40).json()
            for upd in updates.get("result", []):
                offset = upd["update_id"] + 1
                try:
                    if "message" in upd:
                        handle_message(upd["message"])
                    elif "callback_query" in upd:
                        handle_callback(upd["callback_query"])
                except (httpx.HTTPError, KeyError, json.JSONDecodeError) as exc:
                    log.exception("Failed to handle update: %s", exc)
        except httpx.HTTPError as exc:
            log.warning("Polling error: %s; retrying in 3s", exc)
            time.sleep(3)


if __name__ == "__main__":
    main()
