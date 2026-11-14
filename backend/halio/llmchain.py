"""Rantai cadangan model: Vertex (proyek GCP) -> key Gemini API -> ON Token.

Dipakai evidence.py dan media.py. Model mana pun yang jawab, verifikasi kutipan dan vonis tetap dikerjakan kode Halio,
jadi model cadangan yang lebih murah ga bisa mengubah vonis sendirian.

Kalau satu penyedia gagal (403/429/timeout/dll) dia "diistirahatkan" 60 detik biar request berikutnya ga nunggu dia lagi.
"""

from __future__ import annotations

import json
import logging
import re
import threading
import time
from typing import Callable, TypeVar

import httpx

from .config import Settings

log = logging.getLogger(__name__)
T = TypeVar("T")

COOLDOWN_S = 60.0
_down: dict[str, float] = {}
_lock = threading.Lock()


def reset() -> None:
    """Kosongkan catatan penyedia yg lagi diistirahatkan (buat tes)."""
    with _lock:
        _down.clear()


def _is_down(name: str) -> bool:
    with _lock:
        return _down.get(name, 0.0) > time.monotonic()


def _mark_down(name: str) -> None:
    with _lock:
        _down[name] = time.monotonic() + COOLDOWN_S


def run_genai(cfg: Settings, call: Callable[[object], T], label: str) -> T:
    """Jalanin call(client) ke Vertex dulu, lalu ke key Gemini API. Lempar error terakhir kalau semuanya gagal."""
    from google import genai

    makers: list[tuple[str, Callable[[], object]]] = [
        ("vertex", lambda: genai.Client(vertexai=True, project=cfg.google_cloud_project, location=cfg.google_cloud_location)),
    ]
    if cfg.gemini_api_key:
        makers.append(("gemini_key", lambda: genai.Client(api_key=cfg.gemini_api_key)))

    last: Exception | None = None
    for i, (name, make) in enumerate(makers):
        # penyedia yg lagi diistirahatkan dilompati, kecuali tinggal dia satu-satunya yg belum dicoba
        if _is_down(name) and i < len(makers) - 1:
            continue
        try:
            return call(make())
        except Exception as exc:
            last = exc
            _mark_down(name)
            log.warning("%s: %s gagal (%s)%s", label, name, type(exc).__name__, ", coba cadangan" if i < len(makers) - 1 else "")
    assert last is not None
    raise last


_FENCE = re.compile(r"^```(?:json)?\s*|\s*```$", re.I)


def ontoken_json(cfg: Settings, system: str, user: str, max_tokens: int = 1500) -> dict:
    """Satu panggilan chat ke ON Token yang mengembalikan objek JSON. Lempar error kalau ga dikonfigurasi atau gagal."""
    if not cfg.ontoken_api_key:
        raise RuntimeError("ontoken_belum_dikonfigurasi")
    if _is_down("ontoken"):
        raise RuntimeError("ontoken_diistirahatkan")
    try:
        resp = httpx.post(
            f"{cfg.ontoken_base_url}/chat/completions",
            headers={"Authorization": f"Bearer {cfg.ontoken_api_key}"},
            json={
                "model": cfg.ontoken_model,
                "max_tokens": max_tokens,
                "temperature": 0,
                "response_format": {"type": "json_object"},
                "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            },
            timeout=cfg.agent_timeout_s,
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"] or ""
        return json.loads(_FENCE.sub("", text.strip()))
    except Exception as exc:
        _mark_down("ontoken")
        log.warning("ON Token gagal (%s)", type(exc).__name__)
        raise


# ---- pencarian web alternatif (dipakai kalau pencarian Google lewat Gemini gagal) -----------------------------------

def _search_tavily(cfg: Settings, query: str) -> list[dict]:
    r = httpx.post("https://api.tavily.com/search", headers={"Authorization": f"Bearer {cfg.tavily_api_key}"},
                   json={"query": query, "max_results": 8, "search_depth": "basic", "country": "indonesia"}, timeout=20)
    r.raise_for_status()
    return [{"uri": x["url"], "title": x.get("title") or ""} for x in r.json().get("results", []) if x.get("url")]


def _search_serper(cfg: Settings, query: str) -> list[dict]:
    r = httpx.post("https://google.serper.dev/search", headers={"X-API-KEY": cfg.serper_api_key or ""},
                   json={"q": query, "gl": "id", "hl": "id", "num": 8}, timeout=20)
    r.raise_for_status()
    return [{"uri": x["link"], "title": x.get("title") or ""} for x in r.json().get("organic", []) if x.get("link")]


_DDG_LINK = re.compile(r'class="result__a"[^>]*href="([^"]+)"')


def _search_ddg(cfg: Settings, query: str) -> list[dict]:
    from urllib.parse import parse_qs, unquote, urlparse

    r = httpx.get("https://html.duckduckgo.com/html/", params={"q": query}, headers={"User-Agent": "Mozilla/5.0"}, timeout=15,
                  follow_redirects=True)
    r.raise_for_status()
    out = []
    for href in _DDG_LINK.findall(r.text):
        url = parse_qs(urlparse(href).query).get("uddg", [href])[0]
        if url.startswith("http"):
            out.append({"uri": unquote(url), "title": ""})
    return out[:8]


def web_search(cfg: Settings, claim: str) -> tuple[list[dict], list[str]]:
    """(kandidat halaman, kueri yg dijalankan) dari penyedia pencarian alternatif. Lempar error kalau semuanya gagal/kosong."""
    query = f"{claim.strip()[:180]} hoaks cek fakta"
    providers = []
    if cfg.tavily_api_key:
        providers.append(("tavily", _search_tavily))
    if cfg.serper_api_key:
        providers.append(("serper", _search_serper))
    providers.append(("duckduckgo", _search_ddg))
    last: Exception | None = None
    for name, fn in providers:
        if _is_down(name):
            continue
        try:
            found = fn(cfg, query)
            if found:
                return found, [query]
        except Exception as exc:
            last = exc
            _mark_down(name)
            log.warning("pencarian %s gagal (%s)", name, type(exc).__name__)
    raise last or RuntimeError("pencarian_alternatif_kosong")
