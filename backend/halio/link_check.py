"""Open the links a user forwarded (safely) and report what is really there.

Never executes anything: plain GET with a size cap, no JavaScript, public addresses only, redirects followed by hand
so each hop is re-checked. The result is a fact about the link ("404", "redirects to another domain", "government site"),
not a verdict on the claim.
"""

from __future__ import annotations

import ipaddress
import re
import socket
from concurrent.futures import ThreadPoolExecutor
from html.parser import HTMLParser
from urllib.parse import urljoin, urlparse

import httpx

from . import outlets
from .source_verifier import source_kind

URL_RE = re.compile(r"https?://[^\s<>\"')\]]+", re.I)
SHORTENERS = {"bit.ly", "s.id", "cutt.ly", "tinyurl.com", "shorturl.at", "rb.gy", "t.ly", "linktr.ee", "wa.me", "is.gd", "ow.ly"}
OFFICIAL = (".go.id", ".mil.id")
MAX_BYTES = 300_000
MAX_LINKS = 3


def extract_urls(text: str) -> list[str]:
    seen: list[str] = []
    for raw in URL_RE.findall(text):
        url = raw.rstrip(".,;:!?")
        if url not in seen:
            seen.append(url)
    return seen[:MAX_LINKS]


def _is_public(host: str) -> bool:
    try:
        infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except socket.gaierror:
        return False
    return bool(infos) and all(ipaddress.ip_address(i[4][0]).is_global for i in infos)


_META_KEYS = {
    "og:site_name": "site_name", "og:title": "og_title", "og:description": "description", "description": "description",
    "article:published_time": "published", "og:article:published_time": "published", "date": "published",
    "pubdate": "published", "publishdate": "published", "parsely-pub-date": "published",
}


class _Title(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.in_title, self.title, self.meta = False, "", {}

    def handle_starttag(self, tag, attrs):
        self.in_title = tag == "title"
        if tag == "meta":
            a = {k.lower(): (v or "") for k, v in attrs}
            key = _META_KEYS.get((a.get("property") or a.get("name") or "").lower())
            if key and a.get("content") and key not in self.meta:
                self.meta[key] = " ".join(a["content"].split())[:300]

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title and len(self.title) < 200:
            self.title += data


def check_link(url: str, transport: httpx.BaseTransport | None = None) -> dict:
    """Return {url, ok, state, final_url, final_host, status, title, kind, note}. Never raises."""
    host = (urlparse(url).hostname or "").lower()
    out = {"url": url, "host": host, "ok": False, "state": "tidak_diperiksa", "final_url": url, "final_host": host,
           "status": None, "title": "", "kind": "", "shortener": host in SHORTENERS, "note": "",
           "site_name": "", "description": "", "published": "", "outlet": "", "outlet_group": ""}
    current, hops = url, 0
    try:
        with httpx.Client(timeout=httpx.Timeout(10.0, connect=5.0), follow_redirects=False, transport=transport,
                          headers={"User-Agent": "Mozilla/5.0 (compatible; HalioLinkCheck/0.1; +cek tautan, tanpa menjalankan skrip)"}) as client:
            while hops <= 5:
                parsed = urlparse(current)
                if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username:
                    out.update(state="tidak_aman", note="Alamat tautan tidak wajar.")
                    return out
                if transport is None and not _is_public(parsed.hostname):
                    out.update(state="tidak_ditemukan", note="Nama situs ini tidak ada atau tidak bisa dijangkau.")
                    return out
                with client.stream("GET", current) as r:
                    out["status"] = r.status_code
                    if r.status_code in (301, 302, 303, 307, 308) and r.headers.get("location"):
                        current = urljoin(current, r.headers["location"])
                        hops += 1
                        continue
                    out["final_url"], out["final_host"] = current, (urlparse(current).hostname or "").lower()
                    if r.status_code >= 400:
                        out.update(state="rusak", note=f"Tautan tidak bisa dibuka (kode {r.status_code}).")
                        return out
                    body = bytearray()
                    for chunk in r.iter_bytes():
                        body.extend(chunk)
                        if len(body) > MAX_BYTES:
                            break
                    if "html" in r.headers.get("content-type", "").lower():
                        t = _Title()
                        t.feed(bytes(body).decode(r.encoding or "utf-8", errors="replace"))
                        out["title"] = " ".join(t.title.split())[:160]
                        out["site_name"] = t.meta.get("site_name", "")
                        out["description"] = t.meta.get("description", "")
                        out["published"] = t.meta.get("published", "")[:40]
                        if not out["title"]:
                            out["title"] = t.meta.get("og_title", "")[:160]
                    if re.search(r"^\s*(error\s*)?404\b|\b404\s*[-:|]|tidak ditemukan|not found|halaman tidak (ada|tersedia)", out["title"], re.I):
                        out.update(state="rusak", note="Halaman ini menampilkan 'tidak ditemukan'.")
                        return out
                    out["ok"] = True
                    out["state"] = "terbuka"
                    out["kind"] = "resmi" if out["final_host"].endswith(OFFICIAL) else (source_kind(current) or "")
                    known = outlets.lookup(current)
                    if known:
                        out["outlet"], out["outlet_group"] = known.name, known.group
                        out["kind"] = out["kind"] or "media"
                    if out["final_host"] != host and not out["final_host"].endswith("." + host.removeprefix("www.")):
                        out["note"] = f"Tautan ini dialihkan ke {out['final_host']}."
                    return out
        out.update(state="terlalu_banyak_alihan", note="Tautan dialihkan berkali-kali.")
    except httpx.HTTPError:
        out.update(state="tidak_bisa_dijangkau", note="Situs tidak merespons.")
    return out


def check_links(text: str) -> list[dict]:
    urls = extract_urls(text)
    if not urls:
        return []
    with ThreadPoolExecutor(max_workers=len(urls)) as pool:
        return list(pool.map(check_link, urls))


def warning_for(c: dict) -> str | None:
    """One plain Indonesian sentence per link, or None when the link looks ordinary and official."""
    host = c["final_host"] or c["host"]
    if c["state"] in ("rusak", "tidak_ditemukan", "tidak_bisa_dijangkau"):
        return f"Tautan {c['host']}: {c['note']} Jangan diandalkan sebagai bukti."
    if c["state"] != "terbuka":
        return f"Tautan {c['host']}: {c['note']}"
    if c.get("outlet") and not c["shortener"]:
        return None  # an ordinary article from a known outlet: nothing to warn about, the answer describes it
    if c["shortener"]:
        return f"Tautan pendek ini ternyata menuju {host}. {'Situs pemerintah.' if c['kind'] == 'resmi' else 'Bukan situs pemerintah, hati-hati bila diminta data.'}"
    if c["note"] and c["kind"] != "resmi":
        return f"{c['note']} Pastikan Anda mengenali situs tujuannya."
    if c["kind"] == "resmi":
        return None
    return f"Tautan {host} bukan situs pemerintah (.go.id). Hati-hati bila diminta mengisi data."
