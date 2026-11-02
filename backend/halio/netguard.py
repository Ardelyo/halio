"""Who is asking, for rate limiting and for counting distinct reporters.

A client-chosen reporter id is free to forge: one script could invent 5 "devices" and push any rumour
past the Radar's k-anonymity gate. So for counting we use the network prefix (/24 IPv4, /48 IPv6)
the request came from, which a single attacker cannot multiply cheaply. Only our own bots, which
present HALIO_CHANNEL_KEY, may name the reporter (the Telegram chat or WhatsApp sender).
The prefix is hashed with the daily salt in store.py like every other pseudonym and never stored raw.
"""

from __future__ import annotations

import hmac
import ipaddress

from fastapi import Request

from .config import Settings


def client_ip(request: Request, cfg: Settings) -> str:
    if cfg.trust_proxy:
        # The proxy appends the address it saw; earlier entries are whatever the client sent.
        fwd = request.headers.get("x-forwarded-for", "")
        if fwd:
            return fwd.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"


def network_of(ip: str) -> str:
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return ip
    prefix = 24 if addr.version == 4 else 48
    return str(ipaddress.ip_network(f"{addr}/{prefix}", strict=False))


def trusted_channel(request: Request, cfg: Settings) -> bool:
    key = request.headers.get("x-halio-channel-key", "")
    return bool(cfg.channel_key) and hmac.compare_digest(key, cfg.channel_key)


def reporter_for(request: Request, cfg: Settings, claimed: str | None) -> str:
    if claimed and trusted_channel(request, cfg):
        return claimed
    return "net:" + network_of(client_ip(request, cfg))
