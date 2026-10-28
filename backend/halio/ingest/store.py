"""SQLite persistence for the sensor: per-source fetch state, item metadata, fetch log.

Retention is short by design (docs/ARCHITECTURE_SENSOR.md §5): item metadata 30 days,
fetch log 7 days. Items are public media headlines; no citizen accounts are stored.
"""

from __future__ import annotations

import sqlite3
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path

from .parse import Item
from .sources import Source

SCHEMA = """
CREATE TABLE IF NOT EXISTS sensor_state (
    source_id TEXT PRIMARY KEY, etag TEXT, last_modified TEXT,
    last_attempt TEXT, last_success TEXT, first_success TEXT,
    fails INTEGER NOT NULL DEFAULT 0, last_status TEXT, last_latency_ms INTEGER,
    last_error TEXT, next_due TEXT
);
CREATE TABLE IF NOT EXISTS sensor_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT, source_id TEXT NOT NULL, guid TEXT NOT NULL,
    title TEXT NOT NULL, url TEXT NOT NULL, published TEXT, snippet TEXT,
    fingerprint TEXT NOT NULL, first_seen TEXT NOT NULL, backfill INTEGER NOT NULL DEFAULT 0,
    UNIQUE (source_id, guid)
);
CREATE INDEX IF NOT EXISTS idx_items_seen ON sensor_items (first_seen);
CREATE INDEX IF NOT EXISTS idx_items_fp ON sensor_items (fingerprint);
CREATE TABLE IF NOT EXISTS sensor_log (
    ts TEXT NOT NULL, source_id TEXT NOT NULL, status TEXT NOT NULL,
    latency_ms INTEGER, new_items INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_log_ts ON sensor_log (ts);
"""

MAX_BACKOFF_S = 3600
MAX_ITEMS_PER_FETCH = 200


def iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class SensorStore:
    def __init__(self, path: Path | str):
        self.path = str(path)
        self._lock = threading.Lock()
        with self._conn() as c:
            c.executescript(SCHEMA)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    # --- scheduling -----------------------------------------------------
    def due(self, sources: tuple[Source, ...] | list[Source], now: datetime) -> list[Source]:
        with self._conn() as c:
            rows = {r["source_id"]: r["next_due"] for r in c.execute("SELECT source_id, next_due FROM sensor_state")}
        stamp = iso(now)
        return [s for s in sources if rows.get(s.id) is None or rows[s.id] <= stamp]

    def state(self, source_id: str) -> dict | None:
        with self._conn() as c:
            row = c.execute("SELECT * FROM sensor_state WHERE source_id=?", (source_id,)).fetchone()
        return dict(row) if row else None

    # --- writes ---------------------------------------------------------
    def record_fetch(
        self, source: Source, now: datetime, *, status: str, latency_ms: int | None,
        error: str | None = None, items: list[Item] | None = None,
        etag: str | None = None, last_modified: str | None = None,
    ) -> int:
        """Store one fetch attempt. `status` is "ok", "304" or "error". Returns the number of new items."""
        stamp = iso(now)
        with self._lock, self._conn() as c:
            prev = c.execute("SELECT * FROM sensor_state WHERE source_id=?", (source.id,)).fetchone()
            first_success = prev["first_success"] if prev else None
            ok = status in ("ok", "304")
            fails = 0 if ok else (prev["fails"] if prev else 0) + 1
            delay = source.cadence_s if ok else min(source.cadence_s * 2 ** min(fails, 6), MAX_BACKOFF_S)

            new = 0
            if status == "ok" and items:
                # Items found on a source's very first successful poll are history, not news:
                # flagged so they never count toward rate or latency statistics.
                backfill = 0 if first_success else 1
                for it in items[:MAX_ITEMS_PER_FETCH]:
                    cur = c.execute(
                        "INSERT OR IGNORE INTO sensor_items "
                        "(source_id, guid, title, url, published, snippet, fingerprint, first_seen, backfill) "
                        "VALUES (?,?,?,?,?,?,?,?,?)",
                        (source.id, it.guid, it.title, it.url, it.published, it.snippet, it.fingerprint, stamp, backfill),
                    )
                    new += cur.rowcount
            c.execute(
                "INSERT INTO sensor_state (source_id, etag, last_modified, last_attempt, last_success, first_success, "
                "fails, last_status, last_latency_ms, last_error, next_due) VALUES (?,?,?,?,?,?,?,?,?,?,?) "
                "ON CONFLICT(source_id) DO UPDATE SET etag=excluded.etag, last_modified=excluded.last_modified, "
                "last_attempt=excluded.last_attempt, last_success=excluded.last_success, first_success=excluded.first_success, "
                "fails=excluded.fails, last_status=excluded.last_status, last_latency_ms=excluded.last_latency_ms, "
                "last_error=excluded.last_error, next_due=excluded.next_due",
                (
                    source.id,
                    etag if ok else (prev["etag"] if prev else None),
                    last_modified if ok else (prev["last_modified"] if prev else None),
                    stamp,
                    stamp if ok else (prev["last_success"] if prev else None),
                    first_success or (stamp if ok else None),
                    fails, status, latency_ms, error, iso(now + timedelta(seconds=delay)),
                ),
            )
            c.execute("INSERT INTO sensor_log VALUES (?,?,?,?,?)", (stamp, source.id, status, latency_ms, new))
        return new

    def prune(self, now: datetime, item_days: int = 30, log_days: int = 7) -> None:
        with self._lock, self._conn() as c:
            c.execute("DELETE FROM sensor_items WHERE first_seen < ?", (iso(now - timedelta(days=item_days)),))
            c.execute("DELETE FROM sensor_log WHERE ts < ?", (iso(now - timedelta(days=log_days)),))

    # --- reads for coverage + UI ----------------------------------------
    def states(self) -> dict[str, dict]:
        with self._conn() as c:
            return {r["source_id"]: dict(r) for r in c.execute("SELECT * FROM sensor_state")}

    def item_stats(self, since: datetime) -> dict[str, dict]:
        with self._conn() as c:
            rows = c.execute(
                "SELECT source_id, MAX(published) newest_pub, "
                "MAX(CASE WHEN backfill=0 THEN first_seen END) newest_seen, "
                "SUM(CASE WHEN backfill=0 AND first_seen>=? THEN 1 ELSE 0 END) n_window, COUNT(*) total "
                "FROM sensor_items GROUP BY source_id", (iso(since),),
            ).fetchall()
        return {r["source_id"]: dict(r) for r in rows}

    def latencies(self, since: datetime) -> dict[str, list[int]]:
        out: dict[str, list[int]] = {}
        with self._conn() as c:
            for r in c.execute(
                "SELECT source_id, latency_ms FROM sensor_log WHERE ts>=? AND status IN ('ok','304') AND latency_ms IS NOT NULL",
                (iso(since),),
            ):
                out.setdefault(r["source_id"], []).append(r["latency_ms"])
        return out

    def seen_delays(self, since: datetime) -> dict[str, list[float]]:
        """Seconds between an article's own publish time and the moment Halio first saw it."""
        out: dict[str, list[float]] = {}
        with self._conn() as c:
            rows = c.execute(
                "SELECT source_id, published, first_seen FROM sensor_items "
                "WHERE backfill=0 AND published IS NOT NULL AND first_seen>=?", (iso(since),),
            ).fetchall()
        for r in rows:
            d = (datetime.fromisoformat(r["first_seen"]) - datetime.fromisoformat(r["published"])).total_seconds()
            if d >= 0:  # clock skew in a feed can put "published" in the future; ignore those
                out.setdefault(r["source_id"], []).append(d)
        return out

    def recent_items(self, limit: int = 50, source_id: str | None = None) -> list[dict]:
        sql = "SELECT source_id, title, url, published, first_seen FROM sensor_items WHERE backfill=0"
        args: list = []
        if source_id:
            sql += " AND source_id=?"
            args.append(source_id)
        sql += " ORDER BY first_seen DESC, id DESC LIMIT ?"
        args.append(max(1, min(limit, 200)))
        with self._conn() as c:
            return [dict(r) for r in c.execute(sql, args)]
