"""Parse RSS 2.0 / Atom feeds into minimal item metadata.

Only a title, link, optional publish time and a short snippet are kept. Full article
text is never stored: the sensor needs to know a narrative exists, not to republish it.
"""

from __future__ import annotations

import hashlib
import html
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from ..textnorm import normalized

MAX_FEED_BYTES = 3_000_000
SNIPPET_CHARS = 200

_TAG = re.compile(r"<[^>]+>")
_SPACE = re.compile(r"\s+")


class FeedError(ValueError):
    pass


@dataclass(frozen=True)
class Item:
    guid: str
    title: str
    url: str
    published: str | None   # ISO 8601 UTC, None when the feed gives no usable date
    snippet: str
    fingerprint: str        # hash of the normalised title, for near-duplicate grouping


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _text(el: ET.Element | None) -> str:
    return (el.text or "").strip() if el is not None else ""


def _child(parent: ET.Element, *names: str) -> ET.Element | None:
    for ch in parent:
        if _local(ch.tag) in names:
            return ch
    return None


def clean(raw: str, limit: int | None = None) -> str:
    out = _SPACE.sub(" ", html.unescape(_TAG.sub(" ", html.unescape(raw)))).strip()
    return out[:limit].rstrip() if limit else out


def parse_date(raw: str) -> str | None:
    raw = raw.strip()
    if not raw:
        return None
    try:
        dt = parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        try:
            dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


def fingerprint(title: str) -> str:
    return hashlib.sha256(normalized(title).encode()).hexdigest()[:16]


def parse_feed(data: bytes) -> list[Item]:
    if len(data) > MAX_FEED_BYTES:
        raise FeedError("feed terlalu besar")
    # Stdlib ElementTree expands entities; refuse any feed that declares them (billion-laughs).
    if b"<!ENTITY" in data:
        raise FeedError("feed memuat deklarasi entity")
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise FeedError(f"XML tidak valid: {exc}") from exc

    nodes = [e for e in root.iter() if _local(e.tag) in ("item", "entry")]
    items: list[Item] = []
    for n in nodes:
        title = clean(_text(_child(n, "title")))
        link_el = _child(n, "link")
        url = (link_el.get("href") or _text(link_el)) if link_el is not None else ""
        url = url.strip()
        if not title or not url:
            continue
        guid = _text(_child(n, "guid", "id")) or url
        published = parse_date(_text(_child(n, "pubDate", "published", "updated", "date")))
        snippet = clean(_text(_child(n, "description", "summary")), SNIPPET_CHARS)
        items.append(Item(guid, title, url, published, snippet, fingerprint(title)))
    return items
