"""Timeline, earliest appearance and wording variants. Pure code over what was really found; no model.

"Earliest" always means earliest that Halio FOUND on the open web, never "the origin": closed groups and platforms are invisible.
"""

from __future__ import annotations

import re
from datetime import date

from ..textnorm import tokens

KIND_LABEL = {"A": "Sumber resmi", "B": "Pemeriksa fakta", "C": "Media", "D": "Situs lain"}


_YMD = re.compile(r"(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})")
_DMY = re.compile(r"(\d{1,2})[-/.](\d{1,2})[-/.](\d{4})")


def iso_date(raw: str) -> str:
    """'2012/12/18', '2025-01-24T10:00', '18/12/2012' -> '2012-12-18'; anything else -> ''. Mixed formats would misorder the timeline."""
    raw = (raw or "").strip()
    m = _YMD.search(raw[:25])
    if m:
        y, mo, d = m.groups()
    else:
        m = _DMY.search(raw[:25])
        if not m:
            return ""
        d, mo, y = m.groups()
    try:
        return date(int(y), int(mo), int(d)).isoformat()
    except ValueError:
        return ""


def _jaccard(a: set[str], b: set[str]) -> float:
    return len(a & b) / len(a | b) if a and b else 0.0


def timeline(events: list[dict], limit: int = 25) -> list[dict]:
    """events: {tanggal (ISO or ''), judul, url, penerbit, tingkat, asal (google|sensor|gdelt|claimreview|wayback), catatan}.
    Dated events in date order, one per URL (its earliest date); undated ones are dropped from the timeline."""
    best: dict[str, dict] = {}
    for e in events:
        d = iso_date(e.get("tanggal") or "")
        if not d or d > date.today().isoformat() or d < "1995-01-01":   # bad page metadata, not history
            continue
        cur = best.get(e["url"])
        if cur is None or d < cur["tanggal"]:
            best[e["url"]] = {**e, "tanggal": d}
    return sorted(best.values(), key=lambda e: (e["tanggal"], e["url"]))[:limit]


def earliest(line: list[dict]) -> dict | None:
    """The first dated appearance, and separately the first by a fact-checker or official source (who reacted first)."""
    if not line:
        return None
    first = line[0]
    reaction = next((e for e in line if e.get("tingkat") in ("A", "B")), None)
    return {
        "pertama": first,
        "tanggapan_pertama": reaction,
        "catatan": "Kemunculan paling awal yang DITEMUKAN Halio di web terbuka, bukan pasti asal-usulnya: grup WhatsApp, "
                   "Telegram privat, dan platform media sosial tidak bisa ditelusuri.",
    }


def variants(passages: list[dict], threshold: float = 0.55, limit: int = 6) -> list[dict]:
    """Group near-identical sentences across sites (one wording = one cluster). Shows how a claim mutates or is copied."""
    clusters: list[dict] = []
    for p in passages:
        toks = set(tokens(p["kutipan"]))
        if len(toks) < 4:
            continue
        home = next((c for c in clusters if _jaccard(toks, c["_tok"]) >= threshold), None)
        if home is None:
            clusters.append({"_tok": toks, "contoh": p["kutipan"], "situs": [p["host"]], "tanggal": [p.get("tanggal") or ""]})
        else:
            if p["host"] not in home["situs"]:
                home["situs"].append(p["host"])
            home["tanggal"].append(p.get("tanggal") or "")
    out = []
    for c in sorted(clusters, key=lambda c: -len(c["situs"]))[:limit]:
        dates = sorted(d for d in c["tanggal"] if d)
        out.append({"contoh": c["contoh"], "jumlah_situs": len(c["situs"]), "situs": c["situs"][:6], "paling_awal": dates[0] if dates else ""})
    return out


def coverage(passages: list[dict]) -> dict:
    """How many distinct voices per tier (outlets of one group or one wire copy count once)."""
    out = {}
    for tier in "ABCD":
        groups = {p["grup"] for p in passages if p["tingkat"] == tier}
        out[tier] = {"label": KIND_LABEL[tier], "suara": len(groups)}
    return out
