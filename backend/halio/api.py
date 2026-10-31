"""HTTP API + static web app. Run from backend/ with uvicorn halio.api:app."""

from __future__ import annotations

import json
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import __version__, card, pipeline, voice
from .channels import whatsapp
from .config import settings
from .ingest import coverage
from .ingest.fetcher import Poller
from .ingest.store import SensorStore, utcnow
from .security import RateLimiter, valid_meta_signature
from .store import ResultCache, Store

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("halio.api")

cache = ResultCache()
seen_wa_messages = ResultCache(max_items=10000, ttl=86400)
store = Store(settings.db_path, k_anonymity=settings.k_anonymity)
sensor = SensorStore(settings.db_path)
limiter = RateLimiter(settings.rate_limit_per_minute)


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
if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=list(settings.cors_origins),
        allow_methods=["GET", "POST"],
        allow_headers=["Authorization", "Content-Type"],
    )


@app.middleware("http")
async def protect(request: Request, call_next):
    if request.url.path.startswith(("/api/", "/webhook/")):
        client = request.client.host if request.client else "unknown"
        if not limiter.allow(f"{client}:{request.url.path}"):
            return JSONResponse({"detail": "Terlalu banyak permintaan. Coba lagi satu menit lagi."}, status_code=429)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


class CheckIn(BaseModel):
    text: str = Field(min_length=3, max_length=4000)
    channel: str = Field(default="web", pattern="^(web|telegram|whatsapp|extension|demo)$")
    sapaan: str = Field(default="Bapak, Ibu", max_length=30)
    reporter: str | None = Field(default=None, max_length=128, description="Opaque per-device id; hashed with a daily salt")


class AppealIn(BaseModel):
    check_id: str = Field(min_length=32, max_length=32)
    reason: str = Field(default="", max_length=500)


class EscalateIn(BaseModel):
    check_id: str = Field(min_length=32, max_length=32)


def _public(result: dict) -> dict:
    return {k: v for k, v in result.items() if not k.startswith("_")}


def run_check(body: CheckIn) -> dict:
    result = pipeline.check(body.text, settings, sapaan=body.sapaan)
    result["card_url"] = f"/api/card/{result['id']}.png"
    result["voice_url"] = f"/api/voice/{result['id']}.mp3"
    cached = {**result, "_channel": body.channel, "_reporter": body.reporter}
    cache.put(result["id"], cached)
    store.record(result, body.channel, body.reporter)
    return result


def _cached(check_id: str) -> dict:
    result = cache.get(check_id)
    if not result:
        raise HTTPException(404, "Hasil cek sudah kedaluwarsa (disimpan maksimal 1 jam). Silakan cek ulang.")
    return result


@app.get("/health")
def health() -> dict:
    return {"ok": True, "version": __version__, "claimreview": bool(settings.google_factcheck_key), "llm": settings.llm_enabled}


@app.get("/ready")
def ready() -> dict:
    with store._conn() as c:
        c.execute("SELECT 1").fetchone()
    return {"ok": True}


@app.post("/api/check")
def api_check(body: CheckIn) -> dict:
    return run_check(body)


@app.get("/api/check/{check_id}")
def api_get(check_id: str) -> dict:
    return _public(_cached(check_id))


@app.get("/api/card/{check_id}.png")
def api_card(check_id: str) -> Response:
    return Response(card.render(_cached(check_id)), media_type="image/png")


@app.get("/api/voice/{check_id}.mp3")
def api_voice(check_id: str) -> Response:
    result = _cached(check_id)
    try:
        audio = voice.synthesize(result["voice_script"])
    except voice.VoiceUnavailable as exc:
        log.warning("Voice unavailable: %s", type(exc).__name__)
        raise HTTPException(501, "Suara server tidak tersedia. Coba fitur suara di perangkat Anda.") from exc
    return Response(audio, media_type="audio/mpeg")


@app.post("/api/appeal")
def api_appeal(body: AppealIn) -> dict:
    result = _cached(body.check_id)
    debunk_id = (result.get("match") or {}).get("debunk_id")
    return {"ok": True, "appeal_id": store.add_appeal(body.check_id, debunk_id, body.reason)}


@app.post("/api/escalate")
def api_escalate(body: EscalateIn) -> dict:
    result = _cached(body.check_id)
    ticket = store.add_escalation(body.check_id, result["claim"], result["_channel"], result["_reporter"])
    return {
        "ok": True,
        "ticket": ticket,
        "message": "Pertanyaan Anda masuk antrean pemeriksa. Simpan nomor tiket ini; balasan dikirim bila kanal mendukungnya.",
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
    _require_radar_token(authorization)
    report = coverage.build(sensor, utcnow())
    report["polling"] = settings.sensor_enabled
    return report


@app.get("/api/sensor/items")
def api_sensor_items(limit: int = 50, source: str | None = None, authorization: str | None = Header(default=None)) -> dict:
    _require_radar_token(authorization)
    return {"items": sensor.recent_items(limit=limit, source_id=source)}


@app.get("/webhook/whatsapp")
def wa_verify(request: Request) -> PlainTextResponse:
    p = request.query_params
    if p.get("hub.mode") == "subscribe" and settings.wa_verify_token and p.get("hub.verify_token") == settings.wa_verify_token:
        return PlainTextResponse(p.get("hub.challenge", ""))
    raise HTTPException(403)


@app.post("/webhook/whatsapp")
async def wa_receive(request: Request) -> dict:
    body = await request.body()
    if not valid_meta_signature(body, request.headers.get("X-Hub-Signature-256"), settings.wa_app_secret):
        raise HTTPException(403, "Signature webhook tidak valid")
    try:
        payload = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise HTTPException(400, "Payload webhook tidak valid") from exc
    for message_id, sender, text in whatsapp.incoming_texts(payload):
        if seen_wa_messages.get(message_id):
            continue
        seen_wa_messages.put(message_id, {"seen": True})
        result = run_check(CheckIn(text=text, channel="whatsapp", reporter=f"wa:{sender}"))
        whatsapp.reply(sender, result, settings)
    return {"ok": True}


@app.get("/radar")
def radar_page() -> FileResponse:
    return FileResponse(settings.web_dir / "radar.html")


@app.get("/coverage")
def coverage_page() -> FileResponse:
    return FileResponse(settings.web_dir / "coverage.html")


if settings.web_dir.exists():
    app.mount("/", StaticFiles(directory=settings.web_dir, html=True), name="web")
