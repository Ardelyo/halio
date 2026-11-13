"""The "already checked" layer: claims that a fact-checker has already written about.

Most misinformation circulating in Indonesian family groups has already been debunked by someone (roughly a third of the viral
chain messages in one study of private groups). So before the expensive web investigation, match the message against the
archive of fact-check headlines. A hit is only a LEAD: its URL goes to the evidence engine, which opens the page and copies the
quote itself. An archive match never produces a verdict on its own.

Sources of entries
  - the sensor database: headlines of fact-check feeds (TurnBackHoax, CekFakta, Liputan6 Cek Fakta, Mafindo), backfill included
  - data/arsip.jsonl (optional, not committed): one JSON object per line {klaim, url, penerbit, tanggal, label}, produced by
    scripts/import_arsip.py from a dataset you are licensed to use
Only headlines that say the claim is FALSE are kept: [BENAR] / [FAKTA] / "valid" items are dropped.
"""

from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path
from urllib.parse import urlparse

from .config import Settings
from .retrieval import Debunk, Index, Match
from .textnorm import tokens

log = logging.getLogger(__name__)

# pola kata di judul cek fakta buat misahin mana yg beneran bantahan hoaks vs berita valid
_FALSE_LABEL = re.compile(r"\b(hoa[xk]s?|salah|disinformasi|misinformasi|penipuan|palsu|keliru|menyesatkan|tidak benar|bohong|klarifikasi)\b", re.I)
_TRUE_LABEL = re.compile(r"^\s*\[?\s*(benar|fakta|valid|terbukti benar)\b|\bterbukti benar\b|\bkabar benar\b", re.I)
_PREFIX = re.compile(r"^\s*(\[[^\]]{2,24}\]|hoa[xk]s?!?:?|cek fakta:?|fakta atau hoa[xk]s:?|klarifikasi:?)\s*", re.I)
_MIN_TOKENS = 4
_cache: dict[str, tuple[float, Index | None, int]] = {}
TTL = 600.0


def says_false(title: str) -> bool:
    """True when a fact-check headline calls the claim false. Unlabelled or [BENAR]/[FAKTA] headlines are not debunks."""
    return bool(_FALSE_LABEL.search(title)) and not _TRUE_LABEL.search(title)


def claim_of(title: str) -> str:
    # buang embel-embel "[SALAH]" atau "CEK FAKTA:" di depan judul biar bersih pas dicocokin
    return " ".join(_PREFIX.sub("", title).split())


def _entry(i: int, title: str, url: str, publisher: str, date: str, origin: str) -> Debunk | None:
    claim = claim_of(title)
    # kl kata kuncinya kedikitan atau bukan https, skip aja drpd salah cocok
    if len(set(tokens(claim))) < _MIN_TOKENS or not url.startswith("https://"):
        return None
    return Debunk(
        id=f"arsip-{origin}-{i}", kategori="arsip", klaim=claim, varian=[],
        fakta=f"{publisher} menerbitkan pemeriksaan: {title}", sederhana=f"{publisher} sudah memeriksa kabar ini.",
        sumber=[{"nama": publisher, "url": url, "jenis": "cek_fakta", "tanggal": date}],
    )


def from_sensor(cfg: Settings, limit: int = 20000) -> list[Debunk]:
    from .ingest.sources import SOURCES
    from .ingest.store import SensorStore

    names = {s.id: s.name for s in SOURCES if s.kind == "cek_fakta"}
    if not names:
        return []
    try:
        store = SensorStore(cfg.db_path)
        with store._conn() as c:
            marks = ",".join("?" for _ in names)
            rows = [dict(r) for r in c.execute(
                f"SELECT source_id, title, url, published, first_seen FROM sensor_items WHERE source_id IN ({marks}) "
                "ORDER BY first_seen DESC LIMIT ?", [*names, limit])]
    except Exception as exc:
        log.info("sensor archive unavailable: %s", type(exc).__name__)
        return []
    out = []
    for i, r in enumerate(rows):
        if says_false(r["title"]):
            e = _entry(i, r["title"], r["url"], names[r["source_id"]], (r["published"] or r["first_seen"] or "")[:10], "sensor")
            if e:
                out.append(e)
    return out


def from_file(path: Path) -> list[Debunk]:
    if not path.exists():
        return []
    out = []
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines()):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        label = str(d.get("label", "")).lower()
        if label and not re.search(r"salah|hoa[xk]|fake|false|disinfo|misinfo|penipuan|palsu|1", label):
            continue   # baris berita valid/benar di dataset campuran jgn dimasukin sbg bantahan
        e = _entry(i, d.get("klaim", ""), d.get("url", ""), d.get("penerbit", "Pemeriksa fakta"), str(d.get("tanggal", ""))[:10], "berkas")
        if e:
            out.append(e)
    return out


def index_for(cfg: Settings) -> tuple[Index | None, int]:
    # simpen index arsip sementra di memori (10 menit) biar ga bolak-balik baca db tiap request
    key = str(cfg.db_path)
    hit = _cache.get(key)
    if hit and time.monotonic() - hit[0] < TTL:
        return hit[1], hit[2]
    entries = from_sensor(cfg) + from_file(cfg.corpus_path.parent / "arsip.jsonl")
    seen, unique = set(), []
    for d in entries:   # cukup satu entri aja per URL biar ga dobel
        if d.sumber[0]["url"] not in seen:
            seen.add(d.sumber[0]["url"])
            unique.append(d)
    idx = Index(unique) if unique else None
    _cache[key] = (time.monotonic(), idx, len(unique))
    return idx, len(unique)


def search(claim: str, cfg: Settings, k: int = 5, floor: float = 0.30) -> list[Match]:
    """Best archive entries for the claim, strongest first. Only leads: the caller must open the page."""
    idx, _ = index_for(cfg)
    if idx is None or len(set(tokens(claim))) < 3:
        return []
    return [m for m in idx.search(claim, k=k) if m.score >= floor]


def size(cfg: Settings) -> int:
    return index_for(cfg)[1]
