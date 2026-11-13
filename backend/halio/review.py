"""Deliver a human reviewer's answer back to the channel the ticket came from (Telegram or WhatsApp).

A ticket is closed only after delivery succeeds; failures raise so the caller keeps it open.
"""

from __future__ import annotations

import httpx

from .config import settings


def send_reply(item: dict, response: str) -> None:
    """Send `response` to the ticket's origin. Raises RuntimeError when the channel cannot reply or the API refuses."""
    # terusin jawaban pemeriksa manusia balik ke chat tempat tiket awalnya dibuat
    origin = item.get("reporter") or ""
    if item.get("channel") == "telegram" and origin.startswith("tg:"):
        if not settings.telegram_token:
            raise RuntimeError("TELEGRAM_BOT_TOKEN belum diatur; tiket belum ditutup")
        # kl pengiriman gagal sengaja lempar error biar tiketnya tetep kebuka di antrean
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
        # tembak ke WhatsApp Cloud API pake nomor pengirim yg tersimpan di field reporter
        reply = httpx.post(
            f"https://graph.facebook.com/v21.0/{settings.wa_phone_id}/messages",
            headers={"Authorization": f"Bearer {settings.wa_token}"},
            json={"messaging_product": "whatsapp", "to": origin[3:], "type": "text", "text": {"body": response}},
            timeout=20,
        )
        reply.raise_for_status()
    else:
        # kanal web/ekstensi ga nyimpen kontak user, jadi cuma bisa ditutup manual tanpa kirim pesan balik
        raise RuntimeError("Kanal tidak mendukung balasan otomatis; berikan nomor tiket dan jawaban melalui kanal asal")
