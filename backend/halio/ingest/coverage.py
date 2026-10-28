"""Coverage report: for every registered source, is it alive, how fast, and what we do not see.

The point of this module is honesty. "Semua berita" is not achievable; what can be
shown is which sources Halio watches, how fresh each one is, and which parts of the
information space are blind spots (docs/ARCHITECTURE_SENSOR.md §2).
"""

from __future__ import annotations

import statistics
from datetime import datetime, timedelta

from .sources import BLIND_SPOTS, KIND_LABEL, SOURCES, Source
from .store import SensorStore, iso

WINDOW_H = 24
STATUS_ORDER = ("hidup", "basi", "tertunda", "mati", "belum")
FAIL_LIMIT = 3


def _age_s(stamp: str | None, now: datetime) -> float | None:
    return None if not stamp else max(0.0, (now - datetime.fromisoformat(stamp)).total_seconds())


def _median(xs: list[float] | list[int]) -> float | None:
    return round(statistics.median(xs), 1) if xs else None


def classify(source: Source, state: dict | None, stats: dict | None, now: datetime) -> str:
    """hidup = fresh and answering; basi = answers but nothing new for too long;
    tertunda = we stopped polling it; mati = repeated failures; belum = not polled yet."""
    if not state or not state.get("last_attempt"):
        return "belum"
    if state["fails"] >= FAIL_LIMIT:
        return "mati"
    if not state.get("last_success"):
        return "belum"
    since_ok = _age_s(state["last_success"], now) or 0.0
    if since_ok > max(5 * source.cadence_s, 120):
        return "tertunda"
    stats = stats or {}
    # Feeds without publish dates are judged by when we first saw their newest item.
    newest = stats.get("newest_pub") or stats.get("newest_seen")
    quiet = _age_s(newest, now)
    if quiet is None:
        quiet = _age_s(state.get("first_success"), now)  # nothing new since we started watching
    if quiet is not None and quiet > source.max_quiet_s:
        return "basi"
    return "hidup"


def build(store: SensorStore, now: datetime, sources: tuple[Source, ...] | list[Source] = SOURCES) -> dict:
    since = now - timedelta(hours=WINDOW_H)
    states, stats = store.states(), store.item_stats(since)
    lat, delays = store.latencies(since), store.seen_delays(since)

    rows = []
    for s in sources:
        st, it = states.get(s.id), stats.get(s.id)
        status = classify(s, st, it, now)
        observed_h = None
        if st and st.get("first_success"):
            observed_h = min(WINDOW_H, (_age_s(st["first_success"], now) or 0) / 3600)
        rate = round(it["n_window"] / observed_h, 1) if it and observed_h and observed_h >= 1 else None
        newest = (it or {}).get("newest_pub") or (it or {}).get("newest_seen")
        rows.append({
            "id": s.id, "name": s.name, "kind": s.kind, "kind_label": KIND_LABEL[s.kind], "url": s.url,
            "status": status, "cadence_s": s.cadence_s, "fails": (st or {}).get("fails", 0),
            "last_success": (st or {}).get("last_success"), "last_error": (st or {}).get("last_error"),
            "newest_item_age_s": _age_s(newest, now), "items_per_hour": rate,
            "latency_ms_median": _median(lat.get(s.id, [])), "seen_delay_s_median": _median(delays.get(s.id, [])),
            "items_total": (it or {}).get("total", 0), "notes": s.notes,
        })

    counts = {k: sum(r["status"] == k for r in rows) for k in STATUS_ORDER}
    by_kind = {}
    for r in rows:
        k = by_kind.setdefault(r["kind"], {"label": r["kind_label"], "total": 0, "hidup": 0})
        k["total"] += 1
        k["hidup"] += r["status"] == "hidup"
    delay_medians = [r["seen_delay_s_median"] for r in rows if r["seen_delay_s_median"] is not None]
    return {
        "generated": iso(now),
        "window_hours": WINDOW_H,
        "sources_total": len(rows),
        "counts": counts,
        "live_share": round(counts["hidup"] / len(rows), 2) if rows else 0.0,
        "by_kind": by_kind,
        "seen_delay_s_median": _median(delay_medians),
        "sources": rows,
        "blind_spots": [{"id": b.id, "name": b.name, "tier": b.tier, "reason": b.reason} for b in BLIND_SPOTS],
        "disclaimer": (
            "Cakupan adalah daftar sumber terbuka yang kami pasang, bukan seluruh ruang informasi. "
            "Tertulis 'hidup' berarti feed menjawab dan masih ada isi baru; bukan berarti semua berita terlihat."
        ),
    }
