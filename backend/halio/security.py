from __future__ import annotations

import hashlib
import hmac
import threading
import time
from collections import deque


def valid_meta_signature(body: bytes, signature: str | None, app_secret: str | None) -> bool:
    if not app_secret or not signature or not signature.startswith("sha256="):
        return False
    expected = hmac.new(app_secret.encode(), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature[7:], expected)


class RateLimiter:
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
