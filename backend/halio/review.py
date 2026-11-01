from __future__ import annotations

import httpx

from .config import settings


def send_reply(item: dict, response: str) -> None:
    origin = item.get("reporter") or ""
    if item.get("channel") == "telegram" and origin.startswith("tg:"):
        if not settings.telegram_token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN belum diatur; tiket belum ditutup")
        reply = httpx.post(
            f"https://api.telegram.org/bot{settings.telegram_token}/sendMessage",
            json={"chat_id": int(origin[3:]), "text": response},
            timeout=20,
        )
        reply.raise_for_status()
        if not reply.json().get("ok"):
            raise RuntimeError("Telegram menolak balasan; tiket belum ditutup")
    elif item.get("channel") == "whatsapp" and origin.startswith("wa:"):
        if not (settings.wa_token and settings.wa_phone_id):
            raise RuntimeError("WhatsApp belum dikonfigurasi; tiket belum ditutup")
        reply = httpx.post(
            f"https://graph.facebook.com/v21.0/{settings.wa_phone_id}/messages",
            headers={"Authorization": f"Bearer {settings.wa_token}"},
            json={"messaging_product": "whatsapp", "to": origin[3:], "type": "text", "text": {"body": response}},
            timeout=20,
        )
        reply.raise_for_status()
    else:
        raise RuntimeError("Kanal tidak mendukung balasan otomatis; berikan nomor tiket dan jawaban melalui kanal asal")
