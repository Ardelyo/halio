"""Request-level safeguards: WhatsApp webhook signature check, per-key rate limit, daily budget for paid calls."""

from __future__ import annotations

import hashlib
import hmac
import threading
import time
from collections import deque


def valid_meta_signature(body: bytes, signature: str | None, app_secret: str | None) -> bool:
    """True only if `signature` is the HMAC-SHA256 of the exact raw body under the app secret. No secret means reject."""
    if not app_secret or not signature or not signature.startswith("sha256="):
        return False
    expected = hmac.new(app_secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature[7:], expected)


class RateLimiter:
    """Sliding one-minute window per key (user or IP). Bounded memory: stale keys are dropped past 10,000 entries."""

    def __init__(self, per_minute: int):
        self.limit = max(1, per_minute)
        self._hits: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def allow(self, key: str, now: float | None = None) -> bool:
        now = time.monotonic() if now is None else now
        with self._lock:
            hits = self._hits.setdefault(key, deque())
            while hits and now - hits[0] >= 60:
                hits.popleft()
            if len(hits) >= self.limit:
                if not hits:
                    self._hits.pop(key, None)
                return False
            hits.append(now)
            if len(self._hits) > 10000:
                self._hits = {k: v for k, v in self._hits.items() if v and now - v[-1] < 60}
            return True


class DailyBudget:
    """A per-process daily counter for calls that cost money (model, media). cap <= 0 means no limit.

    Resets at midnight WIB. Per process only: with several workers each one has its own budget (docs/LAUNCH_READINESS.md).
    """

    def __init__(self, cap: int):
        self.cap = cap
        self._day = ""
        self._used = 0
        self._lock = threading.Lock()

    def take(self, day: str | None = None) -> bool:
        if self.cap <= 0:
            return True
        if day is None:
            from datetime import datetime

            from .store import WIB

            day = datetime.now(WIB).date().isoformat()
        with self._lock:
            if day != self._day:
                self._day, self._used = day, 0
            if self._used >= self.cap:
                return False
            self._used += 1
            return True
