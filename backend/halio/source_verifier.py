"""Fetch model-discovered sources and verify their exact quoted evidence."""

from __future__ import annotations

import ipaddress
import socket
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Protocol
from urllib.parse import urljoin, urlparse

import httpx

MAX_BYTES = 2_000_000
OFFICIAL_DOMAINS = (".go.id", ".mil.id", ".who.int")


class EvidenceLike(Protocol):
    url: str
    quote: str


@dataclass
class Verification:
    ok: bool
    reason: str
    evidence: EvidenceLike
    final_url: str = ""
    source_kind: str = ""
    page_text: str = ""


class SourceError(ValueError):
    pass


class _VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []
        self.hidden = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "svg", "template"}:
            self.hidden += 1
        elif not self.hidden:
            self.parts.append(" ")

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg", "template"} and self.hidden:
            self.hidden -= 1
        elif not self.hidden:
            self.parts.append(" ")

    def handle_data(self, data):
        if not self.hidden:
            self.parts.append(data)


def compact(text: str) -> str:
    return " ".join(text.split())


def visible_text(html: str) -> str:
    parser = _VisibleText()
    parser.feed(html)
    return compact("".join(parser.parts))


def quote_present(quote: str, page_text: str) -> bool:
    normalized = compact(quote)
    return 40 <= len(normalized) <= 1500 and normalized in compact(page_text)


def source_kind(url: str) -> str:
    host = (urlparse(url).hostname or "").lower().rstrip(".")
    path = urlparse(url).path.lower()
    if any(host.endswith(suffix) for suffix in OFFICIAL_DOMAINS):
        return "resmi"
    if host == "turnbackhoax.id" or host.endswith(".turnbackhoax.id"):
        return "cek_fakta"
    if host == "cekfakta.com" or host.endswith(".cekfakta.com"):
        return "cek_fakta"
    if (host == "kompas.com" or host.endswith(".kompas.com")) and "/cekfakta" in path:
        return "cek_fakta"
    if (host == "liputan6.com" or host.endswith(".liputan6.com")) and "/cek-fakta/" in path:
        return "cek_fakta"
    if (host == "afp.com" or host.endswith(".afp.com")) and "fact-check" in path:
        return "cek_fakta"
    return ""


def ensure_public_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise SourceError("url_tidak_aman")
    if parsed.port not in (None, 443):
        raise SourceError("port_tidak_diizinkan")
    try:
        addresses = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise SourceError("domain_tidak_ditemukan") from exc
    if not addresses or any(not ipaddress.ip_address(item[4][0]).is_global for item in addresses):
        raise SourceError("alamat_jaringan_tidak_publik")


def fetch_text(url: str, transport: httpx.BaseTransport | None = None, max_redirects: int = 4) -> tuple[str, str]:
    current = url
    with httpx.Client(
        timeout=httpx.Timeout(12.0, connect=6.0),
        follow_redirects=False,
        headers={"User-Agent": "HalioEvidence/0.1 (verifikasi kutipan sumber publik)"},
        transport=transport,
    ) as client:
        for _ in range(max_redirects + 1):
            ensure_public_url(current)
            with client.stream("GET", current) as response:
                if response.status_code in {301, 302, 303, 307, 308}:
                    if not response.headers.get("location"):
                        raise SourceError("redirect_tanpa_tujuan")
                    current = urljoin(current, response.headers["location"])
                    continue
                if response.status_code != 200:
                    raise SourceError(f"http_{response.status_code}")
                content_type = response.headers.get("content-type", "").lower()
                if not any(kind in content_type for kind in ("text/html", "application/xhtml", "text/plain")):
                    raise SourceError("jenis_konten_tidak_didukung")
                body = bytearray()
                for chunk in response.iter_bytes():
                    body.extend(chunk)
                    if len(body) > MAX_BYTES:
                        raise SourceError("halaman_terlalu_besar")
                encoding = response.encoding or "utf-8"
                return visible_text(body.decode(encoding, errors="replace")), current
    raise SourceError("terlalu_banyak_redirect")


def verify_source(evidence: EvidenceLike, transport: httpx.BaseTransport | None = None) -> Verification:
    host = (urlparse(evidence.url).hostname or "").lower()
    grounding_url = host == "vertexaisearch.cloud.google.com"
    if not source_kind(evidence.url) and not grounding_url:
        return Verification(False, "domain_bukan_sumber_primer", evidence)
    try:
        text, final_url = fetch_text(evidence.url, transport=transport)
    except (httpx.HTTPError, SourceError, UnicodeError) as exc:
        reason = str(exc) if isinstance(exc, SourceError) else "sumber_tidak_dapat_diakses"
        return Verification(False, reason, evidence)
    final_kind = source_kind(final_url)
    if not final_kind:
        return Verification(False, "redirect_ke_domain_lain", evidence, final_url=final_url)
    if not quote_present(evidence.quote, text):
        return Verification(
            False, "kutipan_tidak_ada_di_halaman", evidence,
            final_url=final_url, source_kind=final_kind, page_text=text,
        )
    return Verification(True, "terverifikasi", evidence, final_url=final_url, source_kind=final_kind)
