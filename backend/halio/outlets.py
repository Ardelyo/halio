"""Known news outlets: who published a page, and whether two outlets are really independent of each other.

This is a working list, not a certification. It exists so Halio can say "this is an article from detikNews"
instead of "this link is not a government site", and so that two reports from the same group are not counted
as two independent confirmations. Review it against the Dewan Pers verified-media list before relying on it
(docs/ARCHITECTURE_AGENT.md). Membership means "an established outlet that publishes under an editorial team",
which says nothing about whether one particular article is accurate.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class Outlet:
    name: str
    group: str  # outlets of one group are one voice when counting independent reports
    kind: str   # "media" | "kantor_berita_negara"


# (registrable domain, display name, group). Groups are only merged where common ownership is public knowledge.
_ROWS = [
    ("detik.com", "detikNews", "Trans Media"),
    ("cnnindonesia.com", "CNN Indonesia", "Trans Media"),
    ("cnbcindonesia.com", "CNBC Indonesia", "Trans Media"),
    ("kompas.com", "Kompas.com", "Kompas Gramedia"),
    ("kompas.id", "Kompas.id", "Kompas Gramedia"),
    ("kompas.tv", "Kompas TV", "Kompas Gramedia"),
    ("tribunnews.com", "Tribunnews", "Kompas Gramedia"),
    ("liputan6.com", "Liputan6", "Emtek"),
    ("antaranews.com", "ANTARA", "ANTARA"),
    ("tempo.co", "Tempo", "Tempo"),
    ("tirto.id", "Tirto", "Tirto"),
    ("republika.co.id", "Republika", "Republika"),
    ("mediaindonesia.com", "Media Indonesia", "Media Group"),
    ("metrotvnews.com", "Metro TV", "Media Group"),
    ("bbc.com", "BBC", "BBC"),
    ("bbc.co.uk", "BBC", "BBC"),
    ("kontan.co.id", "Kontan", "Kontan"),
    ("bisnis.com", "Bisnis.com", "Bisnis Indonesia"),
    ("suara.com", "Suara.com", "Suara"),
    ("jawapos.com", "Jawa Pos", "Jawa Pos"),
    ("merdeka.com", "Merdeka.com", "Merdeka"),
    ("okezone.com", "Okezone", "MNC"),
    ("sindonews.com", "SINDOnews", "MNC"),
    ("viva.co.id", "VIVA", "VIVA"),
    ("rri.co.id", "RRI", "Lembaga negara"),
    ("beritasatu.com", "Berita Satu", "Berita Satu"),
    ("thejakartapost.com", "The Jakarta Post", "The Jakarta Post"),
    ("reuters.com", "Reuters", "Reuters"),
    ("apnews.com", "Associated Press", "Associated Press"),
    ("afp.com", "AFP", "AFP"),
]
OUTLETS: dict[str, Outlet] = {d: Outlet(n, g, "kantor_berita_negara" if g == "ANTARA" else "media") for d, n, g in _ROWS}

# Search engines, redirectors and app stores are never a source: they only point at one.
NOT_A_SOURCE = (
    "google.com", "google.co.id", "vertexaisearch.cloud.google.com", "bing.com", "duckduckgo.com", "yahoo.com",
    "facebook.com", "instagram.com", "twitter.com", "x.com", "tiktok.com", "youtube.com", "t.me", "wa.me",
    "apps.apple.com", "play.google.com", "apps.detik.com",
)


def _registrable(host: str) -> list[str]:
    host = host.lower().rstrip(".").removeprefix("www.")
    parts = host.split(".")
    # "news.detik.com" -> ["news.detik.com", "detik.com", "com"]; ".co.id" style domains are covered by the table itself.
    return [".".join(parts[i:]) for i in range(len(parts) - 1)]


def lookup(url_or_host: str) -> Outlet | None:
    host = urlparse(url_or_host).hostname if "//" in url_or_host else url_or_host
    for candidate in _registrable(host or ""):
        if candidate in OUTLETS:
            return OUTLETS[candidate]
    return None


def is_not_a_source(url_or_host: str) -> bool:
    host = urlparse(url_or_host).hostname if "//" in url_or_host else url_or_host
    return any(c in NOT_A_SOURCE for c in _registrable(host or ""))
