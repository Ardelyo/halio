"""Investigation jobs: queued, run in a small thread pool, progress and report kept in SQLite (survive a restart).

Limits: HALIO_AGENT_DAILY_CAP investigations per day in total, HALIO_AGENT_PER_REPORTER per reporter per day.
Privacy: the reporter is stored only as a pseudonym keyed by today's salt (store.daily_salt), enough to count today's runs,
unlinkable once the salt is gone. Finished jobs are deleted after HALIO_RETENTION_DAYS (default 30).
A job interrupted by a restart is marked 'gagal' on startup; the user can start it again.
"""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
from typing import Callable

from ..config import Settings
from ..store import WIB, daily_salt

log = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS investigations (
    id TEXT PRIMARY KEY, created TEXT NOT NULL, day TEXT NOT NULL, reporter TEXT, channel TEXT,
    status TEXT NOT NULL, stage TEXT, progress TEXT, report TEXT, error TEXT, claim TEXT
);
CREATE INDEX IF NOT EXISTS idx_inv_day ON investigations (day);
"""


class LimitReached(Exception):
    pass


class Jobs:
    def __init__(self, cfg: Settings, runner: Callable | None = None, workers: int = 2):
        self.cfg, self.path = cfg, str(cfg.db_path)
        self._runner = runner
        self._pool = ThreadPoolExecutor(max_workers=workers, thread_name_prefix="telusur")
        self._lock = threading.Lock()
        self._last_write: dict[str, float] = {}
        self._last_prune = ""
        with self._conn() as c:
            c.executescript(SCHEMA)
            # job yg nyangkut gara2 server sempat restart langsung tandain gagal biar user ga nungguin selamanya
            c.execute("UPDATE investigations SET status='gagal', error='terhenti karena server dimulai ulang' "
                      "WHERE status IN ('antre','berjalan')")

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path, check_same_thread=False, timeout=10)
        conn.row_factory = sqlite3.Row
        return conn

    def _run(self, text: str, progress: Callable, image=None) -> dict:
        if self._runner:
            return self._runner(text, progress)
        from . import run

        return run(text, self.cfg, progress=progress, image=image)

    def prune(self) -> None:
        """Delete finished or failed investigations older than the retention window. Queued and running jobs stay."""
        cutoff = (datetime.now(WIB).date() - timedelta(days=self.cfg.retention_days)).isoformat()
        with self._conn() as c:
            c.execute("DELETE FROM investigations WHERE day<? AND status NOT IN ('antre','berjalan')", (cutoff,))

    @staticmethod
    def _pseudonym(c: sqlite3.Connection, day: str, reporter: str | None) -> str | None:
        # samarin id pelapor pake salt harian: cukup buat ngitung jatah hari ini tp ga bisa dilacak besoknya
        if not reporter:
            return None
        return hashlib.sha256(f"{daily_salt(c, day)}|telusur|{reporter}".encode()).hexdigest()[:16]

    def submit(self, text: str, reporter: str | None, channel: str, image: tuple[bytes, str] | None = None) -> str:
        """The image (if any) stays in memory for the run only; it is never written to the database."""
        day = datetime.now(WIB).date().isoformat()
        if self._last_prune != day:
            self.prune()
            self._last_prune = day
        with self._lock, self._conn() as c:
            reporter = self._pseudonym(c, day, reporter)
            # cek jatah harian total server sm jatah per orang dulu sblm masukin antrean
            total = c.execute("SELECT COUNT(*) FROM investigations WHERE day=?", (day,)).fetchone()[0]
            if total >= self.cfg.agent_daily_cap:
                raise LimitReached("Batas investigasi harian server sudah tercapai. Coba lagi besok.")
            if reporter:
                mine = c.execute("SELECT COUNT(*) FROM investigations WHERE day=? AND reporter=?", (day, reporter)).fetchone()[0]
                if mine >= self.cfg.agent_per_reporter:
                    raise LimitReached(f"Anda sudah memakai {mine} investigasi hari ini (batas {self.cfg.agent_per_reporter}).")
            job_id = uuid.uuid4().hex
            c.execute("INSERT INTO investigations (id, created, day, reporter, channel, status, stage, progress) VALUES (?,?,?,?,?,?,?,?)",
                      (job_id, datetime.now(WIB).isoformat(timespec="seconds"), day, reporter, channel, "antre", "antre", "{}"))
        self._pool.submit(self._work, job_id, text, image)
        return job_id

    def _progress(self, job_id: str) -> Callable:
        def say(stage: str = "", **counts):
            now = time.monotonic()
            if now - self._last_write.get(job_id, 0) < 1.0 and stage != "menyusun":
                return  # batesin tulis progres ke sqlite maks sekali sedetik biar db ga ke-lock terus
            self._last_write[job_id] = now
            with self._conn() as c:
                c.execute("UPDATE investigations SET stage=?, progress=? WHERE id=?", (stage, json.dumps(counts), job_id))
        return say

    def _work(self, job_id: str, text: str, image=None) -> None:
        with self._conn() as c:
            c.execute("UPDATE investigations SET status='berjalan' WHERE id=?", (job_id,))
        try:
            report = self._run(text, self._progress(job_id), image)
            with self._conn() as c:
                c.execute("UPDATE investigations SET status='selesai', stage='selesai', report=?, claim=? WHERE id=?",
                          (json.dumps(report, ensure_ascii=False, default=str), report.get("klaim", ""), job_id))
        except Exception as exc:  # jgn smpe job gagal diem2 tanpa jejak di db
            log.exception("investigation %s failed", job_id)
            with self._conn() as c:
                c.execute("UPDATE investigations SET status='gagal', error=? WHERE id=?", (type(exc).__name__, job_id))

    def get(self, job_id: str) -> dict | None:
        with self._conn() as c:
            row = c.execute("SELECT * FROM investigations WHERE id=?", (job_id,)).fetchone()
        if not row:
            return None
        return {"id": row["id"], "dibuat": row["created"], "status": row["status"], "tahap": row["stage"],
                "progres": json.loads(row["progress"] or "{}"), "laporan": json.loads(row["report"]) if row["report"] else None,
                "galat": row["error"]}

    def wait(self, job_id: str, timeout: float = 5.0) -> dict | None:
        """For tests and the bot: poll until the job is no longer running (or the timeout)."""
        # helper polling singkat buat nungguin job kelar di unit test sm bot telegram
        end = time.monotonic() + timeout
        while time.monotonic() < end:
            job = self.get(job_id)
            if job and job["status"] in ("selesai", "gagal"):
                return job
            time.sleep(0.05)
        return self.get(job_id)
