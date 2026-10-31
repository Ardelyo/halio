"""WhatsApp Cloud API adapter (webhook lives in halio/api.py).

STATUS: written against Meta's documented Cloud API shape but NOT yet tested
end-to-end. Access (test number, recipient allow-list, Business verification)
is plan task C-1. If it is not live by 3 Nov, demo with Telegram and say so.
"""

from __future__ import annotations

import logging
import os
from collections.abc import Iterator

import httpx

from ..config import Settings
from .format import reply_text

log = logging.getLogger(__name__)
GRAPH_VERSION = os.getenv("WHATSAPP_GRAPH_VERSION", "v21.0")


def incoming_texts(payload: dict) -> Iterator[tuple[str, str, str]]:
    if not isinstance(payload, dict):
        return
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            for msg in change.get("value", {}).get("messages", []):
                if msg.get("type") == "text" and msg.get("id") and msg.get("from"):
                    body = msg.get("text", {}).get("body", "")
                    if isinstance(body, str) and 3 <= len(body) <= 4000:
                        yield msg["id"], msg["from"], body


def _send(cfg: Settings, body: dict) -> None:
    if not (cfg.wa_token and cfg.wa_phone_id):
        log.warning("WhatsApp not configured; skipping reply")
        return
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{cfg.wa_phone_id}/messages"
    resp = httpx.post(url, json={"messaging_product": "whatsapp", **body},
                      headers={"Authorization": f"Bearer {cfg.wa_token}"}, timeout=15)
    if resp.status_code >= 400:
        log.warning("WhatsApp send failed %s: %s", resp.status_code, resp.text[:300])


def reply(to: str, result: dict, cfg: Settings) -> None:
    base = cfg.public_base_url.rstrip("/")
    _send(cfg, {"to": to, "type": "text", "text": {"body": reply_text(result), "preview_url": False}})
    # Media by link requires PUBLIC_BASE_URL to be reachable by Meta (e.g. the deployed demo).
    _send(cfg, {"to": to, "type": "image", "image": {"link": base + result["card_url"]}})
    _send(cfg, {"to": to, "type": "audio", "audio": {"link": base + result["voice_url"]}})
