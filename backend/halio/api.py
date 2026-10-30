"""HTTP API + static web app.  Run:  uvicorn halio.api:app --reload  (from backend/)."""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from . import __version__, card, pipeline, voice
from .channels import whatsapp
from .config import settings
from .ingest import coverage
from .ingest.fetcher import Poller
from .ingest.store import SensorStore, utcnow
from .netguard import RateLimiter, client_ip, network_of, reporter_for
from .store import ResultCache, Store

logging.basicConfig(level=logging.INFO)

cache = ResultCache()
store = Store(settings.db_path, k_anonymity=settings.k_anonymity)
sensor = SensorStore(settings.db_path)
limiter = RateLimiter(settings.rate_per_minute)
log = logging.getLogger("halio.api")


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
    # Long forwards are cut, not rejected: the claim is almost always in the first lines.
    text: str = Field(min_length=3, max_length=100_000)
    channel: str = Field(default="web", pattern="^(web|telegram|whatsapp|extension|demo)$")
    sapaan: str = Field(default="Bapak, Ibu", max_length=30)
    reporter: str | None = Field(default=None, max_length=128, description="Trusted only from our own bots (HALIO_CHANNEL_KEY)")

    @field_validator("text")
    @classmethod
    def _cut(cls, v: str) -> str:
        return v[: settings.max_input_chars]


class AppealIn(BaseModel):
    check_id: str
    reason: str = Field(default="", max_length=500)


class EscalateIn(BaseModel):
    check_id: str


def run_check(body: CheckIn, reporter: str | None) -> dict:
    result = pipeline.check(body.text, settings, sapaan=body.sapaan)
    result["card_url"] = f"/api/card/{result['id']}.png"
    result["voice_url"] = f"/api/voice/{result['id']}.mp3"
    cache.put(result["id"], result)
    store.record(result, body.channel, reporter)
    return result


def _limit(request: Request, bucket: str) -> None:
    limiter.check(f"{bucket}:{network_of(client_ip(request, settings))}")


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
def api_check(body: CheckIn, request: Request) -> dict:
    _limit(request, "check")
    return run_check(body, reporter_for(request, settings, body.reporter))


@app.get("/api/check/{check_id}")
def api_get(check_id: str) -> dict:
    return _cached(check_id)


@app.get("/api/card/{check_id}.png")
def api_card(check_id: str) -> Response:
    return Response(card.render(_cached(check_id)), media_type="image/png")


@app.get("/api/voice/{check_id}.mp3")
def api_voice(check_id: str, request: Request) -> Response:
    result = _cached(check_id)
    _limit(request, "voice")
    try:
        audio = voice.synthesize(result["voice_script"])
    except voice.VoiceUnavailable as exc:
        raise HTTPException(501, f"Suara server tidak tersedia: {exc}") from exc
    return Response(audio, media_type="audio/mpeg")


@app.post("/api/appeal")
def api_appeal(body: AppealIn, request: Request) -> dict:
    _limit(request, "appeal")
    result = cache.get(body.check_id) or {}
    debunk_id = (result.get("match") or {}).get("debunk_id")
    return {"ok": True, "appeal_id": store.add_appeal(body.check_id, debunk_id, body.reason)}


@app.post("/api/escalate")
def api_escalate(body: EscalateIn, request: Request) -> dict:
    _limit(request, "appeal")
    result = _cached(body.check_id)
    return {
        "ok": True,
        "ticket": store.add_escalation(body.check_id, result["claim"]),
        "message": "Terima kasih. Pertanyaan Anda diteruskan ke pemeriksa manusia. Jawaban akan dikirim lewat kanal yang sama.",
    }


def _require_radar_token(authorization: str | None, request: Request) -> None:
    if settings.radar_token:
        if not hmac.compare_digest(authorization or "", f"Bearer {settings.radar_token}"):
            raise HTTPException(401, "Radar memerlukan token")
    elif not settings.radar_public and client_ip(request, settings) not in ("127.0.0.1", "::1", "testclient"):
        raise HTTPException(401, "Radar tertutup: set RADAR_TOKEN, atau HALIO_RADAR_PUBLIC=1 untuk demo publik")


@app.get("/api/radar")
def api_radar(request: Request, days: int = 14, authorization: str | None = Header(default=None)) -> dict:
    _require_radar_token(authorization, request)
    return store.radar(days=max(1, min(days, 90)))


@app.get("/api/sensor/coverage")
def api_sensor_coverage(request: Request, authorization: str | None = Header(default=None)) -> dict:
    """Which sources the sensor watches, how fresh each is, and the declared blind spots."""
    _require_radar_token(authorization, request)
    report = coverage.build(sensor, utcnow())
    report["polling"] = settings.sensor_enabled
    return report


@app.get("/api/sensor/items")
def api_sensor_items(request: Request, limit: int = 50, source: str | None = None, authorization: str | None = Header(default=None)) -> dict:
    """Newest headline metadata seen since polling started (public media only)."""
    _require_radar_token(authorization, request)
    return {"items": sensor.recent_items(limit=limit, source_id=source)}


# --- WhatsApp Cloud API webhook (see channels/whatsapp.py; access unverified) ---
@app.get("/webhook/whatsapp")
def wa_verify(request: Request) -> PlainTextResponse:
    p = request.query_params
    if p.get("hub.mode") == "subscribe" and settings.wa_verify_token and p.get("hub.verify_token") == settings.wa_verify_token:
        return PlainTextResponse(p.get("hub.challenge", ""))
    raise HTTPException(403)


def _wa_signature_ok(raw: bytes, header: str | None) -> bool:
    if not settings.wa_app_secret or not header or not header.startswith("sha256="):
        return False
    expected = hmac.new(settings.wa_app_secret.encode(), raw, hashlib.sha256).hexdigest()
    return hmac.compare_digest(header.removeprefix("sha256="), expected)


def _wa_process(payload: dict) -> None:
    for sender, text in whatsapp.incoming_texts(payload):
        try:
            if len(text.strip()) < 3:
                continue
            result = run_check(CheckIn(text=text, channel="whatsapp"), reporter=f"wa:{sender}")
            whatsapp.reply(sender, result, settings)
        except Exception:  # one bad message must not drop the rest of the batch
            log.exception("WhatsApp message failed")


@app.post("/webhook/whatsapp")
async def wa_receive(request: Request, background: BackgroundTasks) -> dict:
    raw = await request.body()
    if not _wa_signature_ok(raw, request.headers.get("x-hub-signature-256")):
        raise HTTPException(401, "Tanda tangan webhook tidak valid")
    try:
        payload = json.loads(raw)
    except ValueError:
        return {"ok": True}  # signed but unreadable: acknowledge so Meta does not retry forever
    # Answer Meta at once; the checks (and the blocking HTTP replies) run after the response.
    background.add_task(_wa_process, payload if isinstance(payload, dict) else {})
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
