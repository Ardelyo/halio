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
        # ambil alamat paling kanan yg ditempel proxy kita, soalnya entri di depannya bebas dipalsuin client
        fwd = request.headers.get("x-forwarded-for", "")
        if fwd:
            return fwd.split(",")[-1].strip()
    return request.client.host if request.client else "unknown"


def network_of(ip: str) -> str:
    # kelompokin per blok subnet (/24 IPv4, /48 IPv6) biar satu skrip iseng ga bisa ngakalin k-anonymity Radar
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return ip
    prefix = 24 if addr.version == 4 else 48
    return str(ipaddress.ip_network(f"{addr}/{prefix}", strict=False))


def trusted_channel(request: Request, cfg: Settings) -> bool:
    # cek shared key dari bot internal pake compare_digest biar aman
    key = request.headers.get("x-halio-channel-key", "")
    return bool(cfg.channel_key) and hmac.compare_digest(key, cfg.channel_key)


def reporter_for(request: Request, cfg: Settings, claimed: str | None) -> str:
    # id pelapor kiriman request cuma dipercaya kl bawa kunci bot resmi kita
    if claimed and trusted_channel(request, cfg):
        return claimed
    return "net:" + network_of(client_ip(request, cfg))


_PROXY_HEADERS = ("x-forwarded-for", "forwarded", "cf-connecting-ip", "x-real-ip", "true-client-ip", "x-forwarded-host")


def is_direct_local(request: Request, cfg: Settings) -> bool:
    """True only for a developer on the same machine talking to the app directly.

    A reverse proxy or tunnel (nginx, Cloudflare Tunnel) on the same host also connects from 127.0.0.1,
    so a loopback peer alone proves nothing. Any proxy header, or HALIO_TRUST_PROXY, means the request came
    from the network and must carry the token.
    """
    # kl lewat nginx/Cloudflare Tunnel di mesin yg sama peer-nya tetep 127.0.0.1, jadi wajib tolak kl ada header proxy
    if cfg.trust_proxy or any(h in request.headers for h in _PROXY_HEADERS):
        return False
    peer = request.client.host if request.client else ""
    return peer in ("127.0.0.1", "::1", "testclient")
