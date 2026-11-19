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


def _mark_down(name: str, seconds: float = COOLDOWN_S) -> None:
    with _lock:
        _down[name] = time.monotonic() + seconds


def thinking(model: str, level: str):
    """ThinkingConfig yg cocok buat modelnya. Seri gemini-4 menolak level MINIMAL (400) dan thinking defaultnya menghabiskan
    batas token (hasil pencarian kosong), jadi MINIMAL dinaikkan jadi LOW."""
    from google.genai import types

    if model.startswith("gemini-4") and level.upper() == "MINIMAL":
        level = "LOW"
    return types.ThinkingConfig(thinking_level=level)


def _is_quota(exc: Exception) -> bool:
    text = f"{getattr(exc, 'code', '')} {getattr(exc, 'status', '')} {exc}"
    return "429" in text or "RESOURCE_EXHAUSTED" in text


def model_chain(primary: str, fallbacks: tuple[str, ...] = ()) -> list[str]:
    """Model utama diikuti cadangan, tanpa duplikat, urutan terjaga."""
    out: list[str] = []
    for m in (primary, *fallbacks):
        if m and m not in out:
            out.append(m)
    return out


def run_genai(cfg: Settings, call: Callable[[object, str], T], label: str, *, models: tuple[str, ...] | None = None) -> T:
    """Jalanin call(client, model). Urutan: tiap model (utama lalu cadangan) x tiap jalur (Vertex lalu key Gemini API).

    Pasangan (jalur, model) yg gagal diistirahatkan 60 detik. Lempar error terakhir kalau semuanya gagal."""
    from google import genai

    providers: list[tuple[str, Callable[[], object]]] = [
        ("vertex", lambda: genai.Client(vertexai=True, project=cfg.google_cloud_project, location=cfg.google_cloud_location)),
    ]
    if cfg.gemini_api_key:
        providers.append(("gemini_key", lambda: genai.Client(api_key=cfg.gemini_api_key)))
    chain = models if models is not None else tuple(model_chain(cfg.llm_model, cfg.llm_fallback_models))
    attempts = [(f"{pname}:{model}", make, model) for model in chain for pname, make in providers]

    last: Exception | None = None
    for i, (name, make, model) in enumerate(attempts):
        # pasangan yg lagi diistirahatkan dilompati, kecuali tinggal dia satu-satunya yg belum dicoba
        if _is_down(name) and i < len(attempts) - 1:
            continue
        try:
            try:
                return call(make(), model)
            except Exception as exc:
                if not _is_quota(exc):
                    raise
                time.sleep(1.5)   # kuota/laju sesaat (429): coba sekali lagi di model & jalur yg sama sblm pindah
                return call(make(), model)
        except Exception as exc:
            last = exc
            _mark_down(name, 15.0 if _is_quota(exc) else COOLDOWN_S)
            log.warning("%s: %s gagal (%s)%s", label, name, type(exc).__name__, ", coba cadangan" if i < len(attempts) - 1 else "")
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

def _search_mughu(cfg: Settings, query: str) -> list[dict]:
    r = httpx.get(f"{cfg.mughu_base_url}/web-search-api", params={"q": query}, headers={"x-api-key": cfg.mughu_api_key or ""}, timeout=20)
    r.raise_for_status()
    data = r.json()
    if not data.get("ok", True):  # mis. kuota harian habis / key dicabut
        raise RuntimeError("mughu_" + str(data.get("error", "gagal")))
    return [{"uri": x["url"], "title": x.get("title") or ""} for x in data.get("results", []) if x.get("url")]


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


def _search_claude(cfg: Settings, query: str) -> list[dict]:
    """Claude + tool web_search lewat endpoint Anthropic ON Token. Cuma mengambil daftar URL dari blok web_search_tool_result."""
    if not cfg.ontoken_api_key:
        raise RuntimeError("ontoken_belum_dikonfigurasi")
    r = httpx.post(
        f"{cfg.ontoken_base_url}/messages",
        headers={"x-api-key": cfg.ontoken_api_key, "anthropic-version": "2023-06-01"},
        json={
            "model": cfg.ontoken_search_model, "max_tokens": 700,
            "tools": [{"type": "web_search_20250305", "name": "web_search", "max_uses": 2}],
            "system": "Gunakan web_search untuk menemukan halaman pemeriksa fakta atau situs resmi Indonesia yang membahas klaim pengguna. "
                      "Jawab satu kalimat saja; daftar tautan diambil dari hasil pencarian.",
            "messages": [{"role": "user", "content": f"Klaim: {query}"}],
        },
        timeout=max(cfg.agent_timeout_s, 60.0),
    )
    r.raise_for_status()
    out = []
    for block in r.json().get("content", []):
        content = block.get("content") if block.get("type") == "web_search_tool_result" else None
        for x in content if isinstance(content, list) else []:
            if x.get("url"):
                out.append({"uri": x["url"], "title": x.get("title") or ""})
    return out[:10]


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


def _key(url: str) -> str:
    from urllib.parse import urlparse

    u = urlparse(url)
    return (u.hostname or "") + u.path.rstrip("/")


def web_search(cfg: Settings, claim: str, sources: int = 2) -> tuple[list[dict], list[str]]:
    """(kandidat halaman, kueri yg dijalankan) dari penyedia pencarian alternatif. Lempar error kalau semuanya gagal/kosong.

    Hasil dari sampai `sources` penyedia yg berhasil digabung selang-seling (peringkat 1 Mughu, peringkat 1 Tavily, ...) dan
    dideduplikasi: sebagian halaman cek fakta gagal dibuka dari IP server, jadi kandidat dari dua mesin memperbesar peluang.
    """
    query = f"{claim.strip()[:180]} hoaks cek fakta"
    providers = []
    if cfg.mughu_api_key:
        providers.append(("mughu", _search_mughu))
    if cfg.tavily_api_key:
        providers.append(("tavily", _search_tavily))
    if cfg.serper_api_key:
        providers.append(("serper", _search_serper))
    if cfg.ontoken_api_key:
        providers.append(("claude", _search_claude))
    providers.append(("duckduckgo", _search_ddg))
    last: Exception | None = None
    batches: list[list[dict]] = []
    for name, fn in providers:
        if len(batches) >= sources:
            break
        # Claude (berbayar) dan DDG (tak stabil) cuma pilihan terakhir: dilewati kalau mesin lain sudah memberi hasil
        if _is_down(name) or (name in ("claude", "duckduckgo") and batches):
            continue
        try:
            found = fn(cfg, query)
            if found:
                batches.append(found)
        except Exception as exc:
            last = exc
            # kuota harian habis (429) ga akan pulih dalam semenit: istirahatkan lebih lama biar ga buang waktu tiap request
            quota = getattr(getattr(exc, "response", None), "status_code", None) in (402, 429) or "quota" in str(exc).lower()
            _mark_down(name, 900.0 if quota else COOLDOWN_S)
            log.warning("pencarian %s gagal (%s)", name, type(exc).__name__)
    if not batches:
        raise last or RuntimeError("pencarian_alternatif_kosong")
    merged, seen = [], set()
    for rank in range(max(len(b) for b in batches)):
        for b in batches:
            if rank < len(b) and _key(b[rank]["uri"]) not in seen:
                seen.add(_key(b[rank]["uri"]))
                merged.append(b[rank])
    return merged, [query]
