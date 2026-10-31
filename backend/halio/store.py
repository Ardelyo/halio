"""Short-lived check cache and privacy-conscious SQLite persistence."""

from __future__ import annotations

import hashlib
import json
import secrets
import sqlite3
import threading
import time
from collections import OrderedDict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

from .textnorm import tokens

WIB = timezone(timedelta(hours=7))

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    day TEXT NOT NULL, status TEXT NOT NULL, debunk_id TEXT, kategori TEXT,
    techniques TEXT, channel TEXT
);
CREATE TABLE IF NOT EXISTS unknown_claims (
    hash TEXT PRIMARY KEY, first_seen TEXT NOT NULL, last_seen TEXT NOT NULL,
    reporters TEXT NOT NULL, count INTEGER NOT NULL, text TEXT
);
CREATE TABLE IF NOT EXISTS daily_salt (day TEXT PRIMARY KEY, salt TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS appeals (
    id INTEGER PRIMARY KEY AUTOINCREMENT, created TEXT NOT NULL, check_id TEXT,
    debunk_id TEXT, reason TEXT, status TEXT NOT NULL DEFAULT 'baru'
);
CREATE TABLE IF NOT EXISTS escalations (
    id INTEGER PRIMARY KEY AUTOINCREMENT, created TEXT NOT NULL, check_id TEXT,
    claim TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'menunggu',
    channel TEXT, reporter TEXT
);
CREATE TABLE IF NOT EXISTS review_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT, created TEXT NOT NULL,
    item_type TEXT NOT NULL, item_id INTEGER NOT NULL, action TEXT NOT NULL,
    response TEXT
);
"""


def today() -> str:
    return datetime.now(WIB).date().isoformat()


def now_iso() -> str:
    return datetime.now(WIB).isoformat(timespec="seconds")


def claim_hash(text: str) -> str:
    key = " ".join(sorted(set(tokens(text))))
    return hashlib.sha256(key.encode()).hexdigest()[:16]


class ResultCache:
    def __init__(self, max_items: int = 2000, ttl: float = 3600):
        self._data: OrderedDict[str, tuple[float, dict]] = OrderedDict()
        self._lock = threading.Lock()
        self.max_items, self.ttl = max_items, ttl

    def put(self, key: str, value: dict) -> None:
        with self._lock:
            self._data[key] = (time.time(), value)
            self._data.move_to_end(key)
            while len(self._data) > self.max_items:
                self._data.popitem(last=False)

    def get(self, key: str) -> dict | None:
        with self._lock:
            item = self._data.get(key)
            if not item or time.time() - item[0] > self.ttl:
                self._data.pop(key, None)
                return None
            return item[1]


class Store:
    def __init__(self, path: Path, k_anonymity: int = 5, min_cell: int = 3):
        self.path = str(path)
        self.k = k_anonymity
        self.min_cell = min_cell
        self._lock = threading.Lock()
        self._last_prune = ""
        with self._conn() as c:
            c.executescript(SCHEMA)
            columns = {r["name"] for r in c.execute("PRAGMA table_info(escalations)")}
            if "channel" not in columns:
                c.execute("ALTER TABLE escalations ADD COLUMN channel TEXT")
            if "reporter" not in columns:
                c.execute("ALTER TABLE escalations ADD COLUMN reporter TEXT")

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, check_same_thread=False, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def _salt(self, c: sqlite3.Connection, day: str) -> str:
        row = c.execute("SELECT salt FROM daily_salt WHERE day=?", (day,)).fetchone()
        if row:
            return row["salt"]
        salt = secrets.token_hex(16)
        c.execute("DELETE FROM daily_salt WHERE day<>?", (day,))
        c.execute("INSERT INTO daily_salt VALUES (?,?)", (day, salt))
        return salt

    def prune(self, retention_days: int = 30) -> None:
        cutoff = (datetime.now(WIB) - timedelta(days=retention_days)).isoformat(timespec="seconds")
        day_cutoff = (date.fromisoformat(today()) - timedelta(days=retention_days)).isoformat()
        with self._lock, self._conn() as c:
            c.execute("DELETE FROM unknown_claims WHERE last_seen<?", (day_cutoff,))
            c.execute("DELETE FROM appeals WHERE created<?", (cutoff,))
            c.execute("DELETE FROM escalations WHERE created<? AND status<>'menunggu'", (cutoff,))
            c.execute("DELETE FROM review_events WHERE created<?", (cutoff,))

    def record(self, result: dict, channel: str, reporter: str | None, day: str | None = None) -> None:
        day = day if day and channel == "demo" else today()
        match = result.get("match") or {}
        techniques = ",".join(t["id"] for t in result["manipulation"]["techniques"])
        with self._lock, self._conn() as c:
            c.execute(
                "INSERT INTO events VALUES (?,?,?,?,?,?)",
                (day, result["status"], match.get("debunk_id"), match.get("kategori"), techniques, channel),
            )
            if result["status"] == "belum_ada_pemeriksaan" and reporter and result["claim"]:
                self._count_unknown(c, day, result["claim"], reporter)
        if self._last_prune != day:
            self.prune()
            self._last_prune = day

    def _count_unknown(self, c: sqlite3.Connection, day: str, claim: str, reporter: str) -> None:
        h = claim_hash(claim)
        pseudo = hashlib.sha256((self._salt(c, day) + reporter).encode()).hexdigest()[:12]
        row = c.execute("SELECT * FROM unknown_claims WHERE hash=?", (h,)).fetchone()
        if row is None:
            c.execute("INSERT INTO unknown_claims VALUES (?,?,?,?,?,NULL)", (h, day, day, json.dumps([pseudo]), 1))
            return
        reporters = json.loads(row["reporters"]) if row["last_seen"] == day else []
        is_new = pseudo not in reporters and len(reporters) < self.k
        if is_new:
            reporters.append(pseudo)
        count = row["count"] + int(is_new)
        text = row["text"] or (claim if len(reporters) >= self.k else None)
        c.execute(
            "UPDATE unknown_claims SET last_seen=?, reporters=?, count=?, text=? WHERE hash=?",
            (day, json.dumps(reporters), count, text, h),
        )

    def add_appeal(self, check_id: str, debunk_id: str | None, reason: str) -> int:
        with self._lock, self._conn() as c:
            cur = c.execute(
                "INSERT INTO appeals (created, check_id, debunk_id, reason) VALUES (?,?,?,?)",
                (now_iso(), check_id, debunk_id, reason[:500]),
            )
            return cur.lastrowid

    def add_escalation(self, check_id: str, claim: str, channel: str, reporter: str | None) -> int:
        with self._lock, self._conn() as c:
            cur = c.execute(
                "INSERT INTO escalations (created, check_id, claim, channel, reporter) VALUES (?,?,?,?,?)",
                (now_iso(), check_id, claim, channel, reporter),
            )
            return cur.lastrowid

    def review_items(self, item_type: str, open_only: bool = True) -> list[dict]:
        if item_type not in ("appeals", "escalations"):
            raise ValueError("item_type must be appeals or escalations")
        pending = "baru" if item_type == "appeals" else "menunggu"
        where = " WHERE status=?" if open_only else ""
        args = (pending,) if open_only else ()
        with self._conn() as c:
            return [dict(r) for r in c.execute(f"SELECT * FROM {item_type}{where} ORDER BY id", args)]

    def resolve_review(self, item_type: str, item_id: int, response: str) -> dict:
        if item_type not in ("appeals", "escalations"):
            raise ValueError("item_type must be appeals or escalations")
        done = "selesai"
        with self._lock, self._conn() as c:
            row = c.execute(f"SELECT * FROM {item_type} WHERE id=?", (item_id,)).fetchone()
            if not row:
                raise KeyError(item_id)
            c.execute(f"UPDATE {item_type} SET status=? WHERE id=?", (done, item_id))
            c.execute(
                "INSERT INTO review_events (created,item_type,item_id,action,response) VALUES (?,?,?,?,?)",
                (now_iso(), item_type, item_id, "resolved", response[:2000]),
            )
            return dict(row)

    def _suppress(self, n: int) -> int | str:
        return n if n >= self.min_cell else f"<{self.min_cell}"

    def radar(self, days: int = 14) -> dict:
        since = (date.fromisoformat(today()) - timedelta(days=days - 1)).isoformat()
        with self._conn() as c:
            q = lambda sql, *a: c.execute(sql, (since, *a)).fetchall()  # noqa: E731
            by_status = q("SELECT status, COUNT(*) n FROM events WHERE day>=? GROUP BY status")
            by_kategori = q("SELECT kategori, COUNT(*) n FROM events WHERE day>=? AND kategori IS NOT NULL GROUP BY kategori ORDER BY n DESC")
            top_debunks = q("SELECT debunk_id, kategori, COUNT(*) n FROM events WHERE day>=? AND debunk_id IS NOT NULL GROUP BY debunk_id ORDER BY n DESC LIMIT 10")
            daily = q("SELECT day, status, COUNT(*) n FROM events WHERE day>=? GROUP BY day, status ORDER BY day")
            tech_rows = q("SELECT techniques FROM events WHERE day>=? AND techniques<>''")
            emerging = q("SELECT hash, first_seen, last_seen, count, text FROM unknown_claims WHERE last_seen>=? AND text IS NOT NULL ORDER BY count DESC LIMIT 10")
            demo = q("SELECT COUNT(*) n FROM events WHERE day>=? AND channel='demo'")[0]["n"]
            pending = c.execute("SELECT COUNT(*) n FROM unknown_claims WHERE text IS NULL").fetchone()["n"]
            appeals = c.execute("SELECT COUNT(*) n FROM appeals WHERE status='baru'").fetchone()["n"]
            escalations = c.execute("SELECT COUNT(*) n FROM escalations WHERE status='menunggu'").fetchone()["n"]

        techniques: dict[str, int] = {}
        for row in tech_rows:
            for t in row["techniques"].split(","):
                techniques[t] = techniques.get(t, 0) + 1

        total = sum(r["n"] for r in by_status)
        return {
            "window_days": days,
            "since": since,
            "total_checks": total,
            "demo_events": demo,
            "by_status": {r["status"]: r["n"] for r in by_status},
            "by_kategori": [{"kategori": r["kategori"], "n": self._suppress(r["n"])} for r in by_kategori],
            "top_debunks": [{"debunk_id": r["debunk_id"], "kategori": r["kategori"], "n": self._suppress(r["n"])} for r in top_debunks],
            "daily": [dict(r) for r in daily],
            "techniques": dict(sorted(techniques.items(), key=lambda kv: -kv[1])),
            "emerging_rumours": [dict(r) for r in emerging],
            "rumours_below_k": pending,
            "k_anonymity": self.k,
            "open_appeals": appeals,
            "open_escalations": escalations,
        }
