"""HTTP API + static web app.  Run:  uvicorn halio.api:app --reload  (from backend/)."""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import __version__, card, pipeline, voice
from .channels import whatsapp
from .config import settings
from .ingest import coverage
from .ingest.fetcher import Poller
from .ingest.store import SensorStore, utcnow
from .store import ResultCache, Store

logging.basicConfig(level=logging.INFO)

cache = ResultCache()
store = Store(settings.db_path, k_anonymity=settings.k_anonymity)
sensor = SensorStore(settings.db_path)


@asynccontextmanager
async def lifespan(_: FastAPI):
    poller = None
    if settings.sensor_enabled:
        poller = Poller(sensor, settings.sensor_user_agent, settings.sensor_tick_s, settings.sensor_workers)
        poller.start()
    yield
    if poller:
        poller.stop()


app = FastAPI(title="Halio API", version=__version__, lifespan=lifespan)
# The extension calls from page origins; only scrubbed claim text is accepted.
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"])


class CheckIn(BaseModel):
    text: str = Field(min_length=3, max_length=4000)
    channel: str = Field(default="web", pattern="^(web|telegram|whatsapp|extension|demo)$")
    sapaan: str = Field(default="Bapak, Ibu", max_length=30)
    reporter: str | None = Field(default=None, max_length=128, description="Opaque per-device id; hashed with a daily salt")


class AppealIn(BaseModel):
    check_id: str
    reason: str = Field(default="", max_length=500)


class EscalateIn(BaseModel):
    check_id: str


def run_check(body: CheckIn) -> dict:
    result = pipeline.check(body.text, settings, sapaan=body.sapaan)
    result["card_url"] = f"/api/card/{result['id']}.png"
    result["voice_url"] = f"/api/voice/{result['id']}.mp3"
    cache.put(result["id"], result)
    store.record(result, body.channel, body.reporter)
    return result


def _cached(check_id: str) -> dict:
    result = cache.get(check_id)
    if not result:
        raise HTTPException(404, "Hasil cek sudah kedaluwarsa (disimpan maksimal 1 jam). Silakan cek ulang.")
    return result


@app.get("/health")
def health() -> dict:
    return {
        "ok": True, "version": __version__,
        "claimreview": bool(settings.google_factcheck_key), "llm": settings.llm_enabled,
    }


@app.post("/api/check")
def api_check(body: CheckIn) -> dict:
    return run_check(body)


@app.get("/api/check/{check_id}")
def api_get(check_id: str) -> dict:
    return _cached(check_id)


@app.get("/api/card/{check_id}.png")
def api_card(check_id: str) -> Response:
    return Response(card.render(_cached(check_id)), media_type="image/png")


@app.get("/api/voice/{check_id}.mp3")
def api_voice(check_id: str) -> Response:
    result = _cached(check_id)
    try:
        audio = voice.synthesize(result["voice_script"])
    except voice.VoiceUnavailable as exc:
        raise HTTPException(501, f"Suara server tidak tersedia: {exc}") from exc
    return Response(audio, media_type="audio/mpeg")


@app.post("/api/appeal")
def api_appeal(body: AppealIn) -> dict:
    result = cache.get(body.check_id) or {}
    debunk_id = (result.get("match") or {}).get("debunk_id")
    return {"ok": True, "appeal_id": store.add_appeal(body.check_id, debunk_id, body.reason)}


@app.post("/api/escalate")
def api_escalate(body: EscalateIn) -> dict:
    result = _cached(body.check_id)
    return {
        "ok": True,
        "ticket": store.add_escalation(body.check_id, result["claim"]),
        "message": "Terima kasih. Pertanyaan Anda diteruskan ke pemeriksa manusia. Jawaban akan dikirim lewat kanal yang sama.",
    }


def _require_radar_token(authorization: str | None) -> None:
    if settings.radar_token and authorization != f"Bearer {settings.radar_token}":
        raise HTTPException(401, "Radar memerlukan token")


@app.get("/api/radar")
def api_radar(days: int = 14, authorization: str | None = Header(default=None)) -> dict:
    _require_radar_token(authorization)
    return store.radar(days=max(1, min(days, 90)))


@app.get("/api/sensor/coverage")
def api_sensor_coverage(authorization: str | None = Header(default=None)) -> dict:
    """Which sources the sensor watches, how fresh each is, and the declared blind spots."""
    _require_radar_token(authorization)
    report = coverage.build(sensor, utcnow())
    report["polling"] = settings.sensor_enabled
    return report


@app.get("/api/sensor/items")
def api_sensor_items(limit: int = 50, source: str | None = None, authorization: str | None = Header(default=None)) -> dict:
    """Newest headline metadata seen since polling started (public media only)."""
    _require_radar_token(authorization)
    return {"items": sensor.recent_items(limit=limit, source_id=source)}


# --- WhatsApp Cloud API webhook (see channels/whatsapp.py; access unverified) ---
@app.get("/webhook/whatsapp")
def wa_verify(request: Request) -> PlainTextResponse:
    p = request.query_params
    if p.get("hub.mode") == "subscribe" and settings.wa_verify_token and p.get("hub.verify_token") == settings.wa_verify_token:
        return PlainTextResponse(p.get("hub.challenge", ""))
    raise HTTPException(403)


@app.post("/webhook/whatsapp")
async def wa_receive(request: Request) -> dict:
    payload = await request.json()
    for sender, text in whatsapp.incoming_texts(payload):
        result = run_check(CheckIn(text=text, channel="whatsapp", reporter=f"wa:{sender}"))
        whatsapp.reply(sender, result, settings)
    return {"ok": True}


# --- Static web app (PWA + Radar) ---
@app.get("/radar")
def radar_page() -> FileResponse:
    return FileResponse(settings.web_dir / "radar.html")


@app.get("/coverage")
def coverage_page() -> FileResponse:
    return FileResponse(settings.web_dir / "coverage.html")


if settings.web_dir.exists():
    app.mount("/", StaticFiles(directory=settings.web_dir, html=True), name="web")
