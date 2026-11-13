"""Fetch model-discovered sources and verify their exact quoted evidence."""

from __future__ import annotations

import ipaddress
import re
import socket
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Protocol
from urllib.parse import urljoin, urlparse

import httpx

from .safefetch import PinnedTransport

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


@dataclass
class Page:
    text: str
    final_url: str
    title: str = ""
    published: str = ""
    site_name: str = ""
    archived: str = ""      # tanggal salinan Internet Archive kl baca dari arsip (kosong kl langsung dari situs asli)


_META = {
    "og:site_name": "site_name", "article:published_time": "published", "og:article:published_time": "published",
    "pubdate": "published", "publishdate": "published", "parsely-pub-date": "published", "date": "published",
}


class _Head(HTMLParser):
    """Title and the few meta tags that say who published a page and when."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title, self.meta, self._in_title = "", {}, False

    def handle_starttag(self, tag, attrs):
        self._in_title = tag == "title"
        if tag == "meta":
            a = {k.lower(): (v or "") for k, v in attrs}
            key = _META.get((a.get("property") or a.get("name") or "").lower())
            if key and a.get("content") and key not in self.meta:
                self.meta[key] = " ".join(a["content"].split())[:200]

    def handle_data(self, data):
        if self._in_title and len(self.title) < 200:
            self.title += data


class _VisibleText(HTMLParser):
    # saring tag script/style dkk biar yg keambil cuma teks artikel yg beneran tampil di layar
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


def best_passage(claim: str, page_text: str) -> str | None:
    """The sentence of the page that overlaps the claim most, copied from the page by code (so it is always verbatim).

    None unless at least half of the claim's content words appear in it: a page that merely shares a topic does not count.
    """
    from .textnorm import tokens

    want = set(tokens(claim))
    if len(want) < 3:
        return None
    best, best_score = None, 0.0
    for sentence in re.split(r"(?<=[.!?])\s+|\s\|\s", page_text):
        sentence = sentence.strip()
        if not 40 <= len(sentence) <= 600:
            continue
        score = len(want & set(tokens(sentence))) / len(want)
        if score > best_score:
            best, best_score = sentence, score
    return best if best_score >= 0.5 else None


def source_kind(url: str) -> str:
    # kenalin apakah URL ini milik instansi resmi (.go.id/.mil.id/WHO) atau redaksi pemeriksa fakta
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


BLOCKED = {"http_403", "http_429", "http_451", "http_503", "http_202"}


def fetch_page(url: str, transport: httpx.BaseTransport | None = None, max_redirects: int = 4, wayback: bool = True) -> Page:
    """Live page first; when the site refuses a program (403 and similar), the Internet Archive's copy of the SAME url.

    We never disguise ourselves as a browser. The archived copy is labelled (Page.archived) so a report can say "read from
    an archive copy dated X"; the page's own publication date is still taken from its content."""
    try:
        return _fetch_live(url, transport, max_redirects)
    except SourceError as exc:
        if not wayback or str(exc) not in BLOCKED or transport is not None:
            raise
    return _fetch_wayback(url)


def _wayback_snapshot(url: str) -> tuple[str, str]:
    """(archive url, timestamp) of a capture, or ("", ""). The availability endpoint sometimes answers empty for pages that
    are archived, so the CDX index (reliable, one row per capture) is the second opinion."""
    headers = {"User-Agent": "HalioEvidence/0.1 (verifikasi kutipan sumber publik)"}
    try:
        meta = httpx.get("https://archive.org/wayback/available", params={"url": url}, timeout=10, headers=headers).json()
        snap = (meta.get("archived_snapshots") or {}).get("closest") or {}
        if snap.get("available") and str(snap.get("url", "")).startswith(("http://web.archive.org/", "https://web.archive.org/")):
            return snap["url"].replace("http://", "https://", 1), str(snap.get("timestamp", ""))
    except (httpx.HTTPError, ValueError):
        pass
    # kl API availability zonk, cek cadangan langsung ke indeks CDX Wayback
    try:
        rows = httpx.get("https://web.archive.org/cdx/search/cdx", timeout=12, headers=headers,
                         params={"url": url, "output": "json", "limit": -1, "fl": "timestamp", "filter": "statuscode:200"}).json()
        stamps = [r[0] for r in rows[1:] if r and str(r[0]).isdigit()]
        if stamps:
            return f"https://web.archive.org/web/{stamps[0]}/{url}", stamps[0]
    except (httpx.HTTPError, ValueError, IndexError, TypeError, KeyError):
        pass
    return "", ""


def _fetch_wayback(url: str) -> Page:
    copy_url, ts = _wayback_snapshot(url)
    if not copy_url:
        raise SourceError("diblokir_dan_tidak_ada_salinan_arsip")
    # sisipin id_ di path Wayback biar dapet HTML murni aslinya tanpa suntikan banner arsip
    copy_url = re.sub(r"/web/(\d+)/", r"/web/\1id_/", copy_url, count=1)
    page = _fetch_live(copy_url, None, 4)
    day = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]}" if len(ts) >= 8 else ""
    return Page(page.text, url, page.title, page.published, page.site_name, archived=day)


def _fetch_live(url: str, transport: httpx.BaseTransport | None = None, max_redirects: int = 4) -> Page:
    """Public https pages only, no scripts, size-capped; redirects are followed by hand and each hop is re-checked."""
    current = url
    with httpx.Client(
        timeout=httpx.Timeout(12.0, connect=6.0),
        follow_redirects=False,
        headers={"User-Agent": "HalioEvidence/0.1 (verifikasi kutipan sumber publik)"},
        # kunci koneksi ke IP publik yg udah lolos cek ensure_public_url, jgn biarin lookup DNS kedua belok sendiri
        transport=transport or PinnedTransport(),
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
                html = bytes(body).decode(response.encoding or "utf-8", errors="replace")
                head = _Head()
                try:
                    head.feed(html[:200_000])
                except Exception:  # tag head yg agak rusak jgn smpe bikin teks halaman utamanya gagal kebaca
                    pass
                return Page(visible_text(html), current, " ".join(head.title.split())[:200],
                            head.meta.get("published", ""), head.meta.get("site_name", ""))
    raise SourceError("terlalu_banyak_redirect")


def fetch_text(url: str, transport: httpx.BaseTransport | None = None, max_redirects: int = 4) -> tuple[str, str]:
    page = fetch_page(url, transport, max_redirects)
    return page.text, page.final_url


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
    # jgn smpe link awalnya keliatan resmi tp pas di-redirect malah nyasar ke domain biasa
    if not final_kind:
        return Verification(False, "redirect_ke_domain_lain", evidence, final_url=final_url)
    if not quote_present(evidence.quote, text):
        return Verification(
            False, "kutipan_tidak_ada_di_halaman", evidence,
            final_url=final_url, source_kind=final_kind, page_text=text,
        )
    return Verification(True, "terverifikasi", evidence, final_url=final_url, source_kind=final_kind)
