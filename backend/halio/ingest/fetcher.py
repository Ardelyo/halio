"""Poll one feed with conditional GET, and run all due sources concurrently."""

from __future__ import annotations

import logging
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from datetime import datetime

import httpx

from .parse import FeedError, Item, parse_feed
from .sources import SOURCES, Source
from .store import SensorStore, utcnow

log = logging.getLogger(__name__)

DEFAULT_UA = "HalioSensor/0.1 (riset anti-disinformasi; hanya feed publik)"


@dataclass
class Outcome:
    source: Source
    status: str                      # "ok" | "304" | "error"
    latency_ms: int | None
    error: str | None = None
    items: list[Item] | None = None
    etag: str | None = None
    last_modified: str | None = None


def fetch(source: Source, client: httpx.Client, prev_state: dict | None) -> Outcome:
    headers = {}
    if prev_state:
        if prev_state.get("etag"):
            headers["If-None-Match"] = prev_state["etag"]
        if prev_state.get("last_modified"):
            headers["If-Modified-Since"] = prev_state["last_modified"]
    t0 = time.perf_counter()
    try:
        resp = client.get(source.url, headers=headers)
    except httpx.HTTPError as exc:
        return Outcome(source, "error", None, error=type(exc).__name__)
    ms = int((time.perf_counter() - t0) * 1000)
    if resp.status_code == 304:
        return Outcome(source, "304", ms, etag=headers.get("If-None-Match"), last_modified=headers.get("If-Modified-Since"))
    if resp.status_code != 200:
        return Outcome(source, "error", ms, error=f"HTTP {resp.status_code}")
    try:
        items = parse_feed(resp.content)
    except FeedError as exc:
        return Outcome(source, "error", ms, error=str(exc)[:120])
    return Outcome(source, "ok", ms, items=items, etag=resp.headers.get("etag"), last_modified=resp.headers.get("last-modified"))


def make_client(user_agent: str = DEFAULT_UA, transport: httpx.BaseTransport | None = None) -> httpx.Client:
    return httpx.Client(
        headers={"User-Agent": user_agent, "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*"},
        timeout=httpx.Timeout(15.0, connect=8.0), follow_redirects=True, transport=transport,
    )


def run_once(
    store: SensorStore, client: httpx.Client, sources: tuple[Source, ...] | list[Source] = SOURCES,
    now: datetime | None = None, workers: int = 8,
) -> dict:
    """Poll every due source. Network work is threaded; database writes stay on the calling thread."""
    now = now or utcnow()
    due = store.due(sources, now)
    if not due:
        return {"polled": 0, "ok": 0, "errors": 0, "new_items": 0}
    with ThreadPoolExecutor(max_workers=max(1, min(workers, len(due)))) as pool:
        outcomes = list(pool.map(lambda s: fetch(s, client, store.state(s.id)), due))
    ok = errors = new_items = 0
    for o in outcomes:
        new_items += store.record_fetch(
            o.source, now, status=o.status, latency_ms=o.latency_ms, error=o.error,
            items=o.items, etag=o.etag, last_modified=o.last_modified,
        )
        if o.status == "error":
            errors += 1
            log.warning("sensor: %s gagal (%s)", o.source.id, o.error)
        else:
            ok += 1
    return {"polled": len(due), "ok": ok, "errors": errors, "new_items": new_items}


class Poller:
    """Background thread that keeps calling run_once. Off unless HALIO_SENSOR=1."""

    def __init__(self, store: SensorStore, user_agent: str = DEFAULT_UA, tick_s: float = 15.0, workers: int = 8):
        self.store, self.tick_s, self.workers = store, tick_s, workers
        self._client = make_client(user_agent)
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, name="halio-sensor", daemon=True)
        self._last_prune = 0.0

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._client.close()

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                summary = run_once(self.store, self._client, workers=self.workers)
                if summary["polled"]:
                    log.info("sensor: %s", summary)
                if time.monotonic() - self._last_prune > 3600:
                    self.store.prune(utcnow())
                    self._last_prune = time.monotonic()
            except Exception:  # keep the sensor alive; the coverage panel will show what stopped working
                log.exception("sensor loop error")
            self._stop.wait(self.tick_s)
