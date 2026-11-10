"""HTTP API + static web app. Run from backend/ with uvicorn halio.api:app."""

from __future__ import annotations

import hmac
import json
import logging
import threading
from contextlib import asynccontextmanager

from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, field_validator

from . import BUILD, __version__, card, pipeline, review, voice
from .channels import whatsapp
from .config import settings
from .ingest import coverage
from .ingest.fetcher import Poller
from .ingest.store import SensorStore, utcnow
from .netguard import client_ip, is_direct_local, reporter_for
from .security import RateLimiter, valid_meta_signature
from .store import ResultCache, Store

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("halio.api")

cache = ResultCache()
seen_wa_messages = ResultCache(max_items=10000, ttl=86400)
store = Store(settings.db_path, k_anonymity=settings.k_anonymity, retention_days=settings.retention_days)
sensor = SensorStore(settings.db_path)
limiter = RateLimiter(settings.rate_limit_per_minute)


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.telegram_token and not settings.channel_key:
        # Without the shared key the Telegram bot's per-chat id is not trusted, so escalation replies
        # cannot be routed back and every Telegram user counts as one reporter for the Radar.
        log.warning("TELEGRAM_BOT_TOKEN is set but HALIO_CHANNEL_KEY is not: set the same value on the API and the bot")
    poller = None
    if settings.sensor_enabled:
        poller = Poller(sensor, settings.sensor_user_agent, settings.sensor_tick_s, settings.sensor_workers)
        poller.start()
    stop = threading.Event()
    if settings.brief_enabled and settings.llm_enabled:
        threading.Thread(target=_brief_loop, args=(stop,), daemon=True, name="brief").start()
    yield
    stop.set()
    if poller:
        poller.stop()


def _brief_loop(stop: threading.Event) -> None:
    """Every 30 minutes: after 06:00 WIB, build today's brief for each topic once."""
    from datetime import datetime

    from .investigate.brief import TOPICS, Briefs
    from .store import WIB

    briefs = Briefs(settings)
    while not stop.wait(30 if not stop.is_set() else 0):
        if datetime.now(WIB).hour < 6:
            stop.wait(1800)
            continue
        for topic in TOPICS:
            try:
                if not briefs.has_today(topic):
                    briefs.build(topic, jobs())
                    log.info("brief built: %s", topic)
            except Exception:
                log.exception("brief %s failed", topic)
        stop.wait(1800)


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
        client = client_ip(request, settings)
        if not limiter.allow(f"{client}:{request.url.path}"):
            return JSONResponse({"detail": "Terlalu banyak permintaan. Coba lagi satu menit lagi."}, status_code=429)
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    return response


class CheckIn(BaseModel):
    # Long forwards are cut, not rejected: the claim is almost always in the first lines.
    text: str = Field(min_length=3, max_length=100_000)
    channel: str = Field(default="web", pattern="^(web|telegram|whatsapp|extension|demo)$")
    sapaan: str = Field(default="Bapak, Ibu", max_length=30)
    reporter: str | None = Field(default=None, max_length=128, description="Trusted only from our own bots (HALIO_CHANNEL_KEY)")
    mode: str = Field(default="penuh", pattern="^(penuh|tanpa_ai)$", description="tanpa_ai: this request never calls a model (demo of the fallback)")

    @field_validator("text")
    @classmethod
    def _cut(cls, v: str) -> str:
        return v[: settings.max_input_chars]


class MediaIn(BaseModel):
    data_b64: str = Field(min_length=100, max_length=12_000_000)
    mime: str = Field(max_length=40)
    channel: str = Field(default="web", pattern="^(web|telegram|whatsapp|extension|demo)$")
    sapaan: str = Field(default="Bapak, Ibu", max_length=30)
    reporter: str | None = Field(default=None, max_length=128)


class AppealIn(BaseModel):
    check_id: str = Field(min_length=32, max_length=32)
    reason: str = Field(default="", max_length=500)


class EscalateIn(BaseModel):
    check_id: str = Field(min_length=32, max_length=32)


class ReviewResolveIn(BaseModel):
    response: str = Field(min_length=1, max_length=2000)
    send: bool = True


def _public(result: dict) -> dict:
    return {k: v for k, v in result.items() if not k.startswith("_")}


def run_check(body: CheckIn, reporter: str | None) -> dict:
    from dataclasses import replace

    # "tanpa_ai" turns the model off for THIS request only: the answer then comes from the curated corpus and the archive alone.
    cfg = replace(settings, llm_enabled=False) if body.mode == "tanpa_ai" else settings
    result = pipeline.check(body.text, cfg, sapaan=body.sapaan)
    result["mode"] = body.mode
    result["card_url"] = f"/api/card/{result['id']}.png"
    result["voice_url"] = f"/api/voice/{result['id']}.mp3"
    cached = {**result, "_channel": body.channel, "_reporter": reporter}
    cache.put(result["id"], cached)
    store.record(result, body.channel, reporter)
    return result


def _cached(check_id: str) -> dict:
    result = cache.get(check_id)
    if not result:
        raise HTTPException(404, "Hasil cek sudah kedaluwarsa (disimpan maksimal 1 jam). Silakan cek ulang.")
    return result


@app.get("/health")
def health() -> dict:
    return {"ok": True, "version": __version__, "claimreview": bool(settings.google_factcheck_key), "llm": settings.llm_enabled, "media": settings.media_enabled, "build": BUILD}


@app.get("/ready")
def ready() -> dict:
    with store._conn() as c:
        c.execute("SELECT 1").fetchone()
    return {"ok": True}


@app.post("/api/check")
def api_check(body: CheckIn, request: Request) -> dict:
    # A client-chosen reporter id is free to forge; only our own bots may name one (netguard.py).
    return run_check(body, reporter_for(request, settings, body.reporter))


@app.post("/api/check-media")
def api_check_media(body: MediaIn, request: Request) -> dict:
    """Photo or voice note -> text (Gemini reads it) -> the normal check. Never judges the picture itself."""
    import base64

    from . import media

    if not media.supported(body.mime):
        raise HTTPException(415, "Jenis berkas ini belum didukung. Kirim foto (JPG/PNG/WebP) atau pesan suara.")
    try:
        data = base64.b64decode(body.data_b64, validate=True)
    except ValueError:
        raise HTTPException(400, "Berkas rusak.")
    reading = media.read_media(data, body.mime, settings)
    if reading is None:
        raise HTTPException(503, "Halio belum bisa membaca foto atau suara sekarang. Tolong ketik atau salin teksnya.")
    if not reading.readable or len(reading.text.strip()) < 3:
        return {"readable": False, "media": reading.model_dump(),
                "message": "Halio tidak menemukan tulisan atau ucapan yang bisa dicek. Coba foto yang lebih jelas, atau salin teksnya."}
    result = run_check(CheckIn(text=reading.text, channel=body.channel, sapaan=body.sapaan),
                       reporter_for(request, settings, body.reporter))
    result["readable"] = True
    result["media"] = {**reading.model_dump(), "authenticity_checked": False}
    return result


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


_uji_cache: dict[str, tuple[float, dict]] = {}


@app.post("/api/uji/{nama}")
def api_uji(nama: str) -> dict:
    """Run one live safety test (halio/selftest.py). Cached for five minutes: the injection test calls the real model."""
    import time as _t

    from . import selftest

    if nama not in selftest.TESTS:
        raise HTTPException(404, "Uji tidak dikenal.")
    hit = _uji_cache.get(nama)
    if hit and _t.monotonic() - hit[0] < 300:
        return {**hit[1], "dari_cache": True}
    title, fn = selftest.TESTS[nama]
    result = {"nama": nama, "judul": title, **fn(settings)}
    if result["lulus"] is not None:
        _uji_cache[nama] = (_t.monotonic(), result)
    return result


@app.get("/api/uji")
def api_uji_list() -> list[dict]:
    from . import selftest

    return [{"nama": k, "judul": v[0]} for k, v in selftest.TESTS.items()]


class InvestigateIn(BaseModel):
    text: str = Field(min_length=10, max_length=100_000)
    channel: str = Field(default="web", pattern="^(web|telegram|whatsapp|extension|demo)$")
    reporter: str | None = Field(default=None, max_length=128)
    check_id: str | None = Field(default=None, min_length=32, max_length=32)
    image_b64: str | None = Field(default=None, max_length=12_000_000)
    mime: str | None = Field(default=None, max_length=40)

    @field_validator("text")
    @classmethod
    def _cut(cls, v: str) -> str:
        return v[: settings.max_input_chars]


_jobs = None


def jobs():
    global _jobs
    if _jobs is None:
        from .investigate.jobs import Jobs

        _jobs = Jobs(settings)
    return _jobs


@app.post("/api/investigate", status_code=202)
def api_investigate(body: InvestigateIn, request: Request) -> dict:
    """Start a deep investigation (1-3 minutes). Poll GET /api/investigate/{id} for progress and the report."""
    from .investigate.jobs import LimitReached

    if not (settings.llm_enabled and settings.llm_provider == "google"):
        raise HTTPException(503, "Penelusuran mendalam membutuhkan AI (HALIO_LLM=1) dan sedang tidak aktif di server ini.")
    text = body.text
    if body.check_id:  # "investigate this answer": reuse the text the user already sent
        text = _cached(body.check_id).get("claim") or text
    image = None
    if body.image_b64:
        import base64

        if (body.mime or "") not in ("image/jpeg", "image/png", "image/webp"):
            raise HTTPException(415, "Foto harus JPG, PNG, atau WebP.")
        try:
            image = (base64.b64decode(body.image_b64, validate=True), body.mime)
        except ValueError:
            raise HTTPException(400, "Berkas foto rusak.")
    try:
        job_id = jobs().submit(text, reporter_for(request, settings, body.reporter), body.channel, image=image)
    except LimitReached as exc:
        raise HTTPException(429, str(exc))
    return {"id": job_id, "url": f"/laporan.html?id={job_id}", "status": "antre"}


@app.get("/api/investigate/{job_id}")
def api_investigate_get(job_id: str) -> dict:
    if len(job_id) != 32 or not job_id.isalnum():
        raise HTTPException(404, "Laporan tidak ditemukan.")
    job = jobs().get(job_id)
    if not job:
        raise HTTPException(404, "Laporan tidak ditemukan.")
    return job


@app.get("/api/brief")
def api_brief(request: Request, topic: str = "tni", authorization: str | None = Header(default=None)) -> dict:
    _require_radar_token(authorization, request)
    from .investigate.brief import TOPICS, Briefs

    if topic not in TOPICS:
        raise HTTPException(404, "Topik tidak dikenal.")
    brief = Briefs(settings).latest(topic, jobs())
    return {"topik": topic, "label": TOPICS[topic][0], "brief": brief, "otomatis": settings.brief_enabled,
            "topik_tersedia": {k: v[0] for k, v in TOPICS.items()}}


@app.post("/api/brief/run")
def api_brief_run(request: Request, topic: str = "tni", authorization: str | None = Header(default=None)) -> dict:
    _require_radar_token(authorization, request)
    from .investigate.brief import TOPICS, Briefs

    if topic not in TOPICS:
        raise HTTPException(404, "Topik tidak dikenal.")
    use_jobs = jobs() if settings.llm_enabled and settings.llm_provider == "google" else None
    brief = Briefs(settings).build(topic, use_jobs)
    return {"ok": True, "id": brief["id"], "narasi": len(brief["narasi"])}


def _require_radar_token(authorization: str | None, request: Request) -> None:
    if settings.radar_token:
        if not hmac.compare_digest(authorization or "", f"Bearer {settings.radar_token}"):
            raise HTTPException(401, "Radar memerlukan token")
    elif not settings.radar_public and not is_direct_local(request, settings):
        raise HTTPException(401, "Radar tertutup: set RADAR_TOKEN, atau HALIO_RADAR_PUBLIC=1 untuk demo publik")


def _validate_review_type(item_type: str) -> None:
    if item_type not in ("appeals", "escalations"):
        raise HTTPException(404, "Jenis antrean tidak dikenal")


@app.get("/api/review/{item_type}")
def api_review_items(request: Request, item_type: str, open_only: bool = True, authorization: str | None = Header(default=None)) -> dict:
    _require_radar_token(authorization, request)
    _validate_review_type(item_type)
    return {"items": store.review_items(item_type, open_only), "events": store.review_events(item_type)}


@app.post("/api/review/{item_type}/{item_id}/resolve")
def api_resolve_review(request: Request, item_type: str, item_id: int, body: ReviewResolveIn, authorization: str | None = Header(default=None)) -> dict:
    _require_radar_token(authorization, request)
    _validate_review_type(item_type)
    if item_id < 1:
        raise HTTPException(422, "ID tiket tidak valid")
    if not body.response.strip():
        raise HTTPException(422, "Respons pemeriksa tidak boleh kosong")
    items = {item["id"]: item for item in store.review_items(item_type, open_only=False)}
    item = items.get(item_id)
    if not item:
        raise HTTPException(404, "Tiket tidak ditemukan")
    if item["status"] == "selesai":
        raise HTTPException(409, "Tiket sudah diselesaikan")
    sent = False
    if item_type == "escalations" and body.send:
        try:
            review.send_reply(item, body.response)
            sent = True
        except Exception as exc:
            log.warning("Balasan tiket %s gagal: %s", item_id, type(exc).__name__)
            detail = str(exc) if isinstance(exc, RuntimeError) else "Kanal tujuan menolak balasan; tiket belum ditutup"
            raise HTTPException(502, detail) from exc
    try:
        store.resolve_review(item_type, item_id, body.response)
    except PermissionError as exc:
        raise HTTPException(409, str(exc)) from exc
    message = "Balasan terkirim dan tiket ditutup." if sent else "Respons dicatat dan tiket ditutup. Tindak lanjut manual tetap diperlukan bila kanal tidak mendukung balasan."
    return {"ok": True, "sent": sent, "recorded": True, "message": message}


@app.get("/api/radar")
def api_radar(request: Request, days: int = 14, authorization: str | None = Header(default=None)) -> dict:
    _require_radar_token(authorization, request)
    return store.radar(days=max(1, min(days, 90)))


@app.get("/api/sensor/coverage")
def api_sensor_coverage(request: Request, authorization: str | None = Header(default=None)) -> dict:
    _require_radar_token(authorization, request)
    report = coverage.build(sensor, utcnow())
    report["polling"] = settings.sensor_enabled
    return report


@app.get("/api/sensor/items")
def api_sensor_items(request: Request, limit: int = 50, source: str | None = None, authorization: str | None = Header(default=None)) -> dict:
    _require_radar_token(authorization, request)
    return {"items": sensor.recent_items(limit=limit, source_id=source)}


@app.get("/webhook/whatsapp")
def wa_verify(request: Request) -> PlainTextResponse:
    p = request.query_params
    if p.get("hub.mode") == "subscribe" and settings.wa_verify_token and p.get("hub.verify_token") == settings.wa_verify_token:
        return PlainTextResponse(p.get("hub.challenge", ""))
    raise HTTPException(403)


def _wa_process(payload: dict) -> None:
    for message_id, sender, text in whatsapp.incoming_texts(payload):
        if seen_wa_messages.get(message_id):
            continue
        seen_wa_messages.put(message_id, {"seen": True})
        try:
            result = run_check(CheckIn(text=text, channel="whatsapp"), reporter=f"wa:{sender}")
            whatsapp.reply(sender, result, settings)
        except Exception:  # one bad message must not drop the rest of the batch
            log.exception("WhatsApp message failed")


@app.post("/webhook/whatsapp")
async def wa_receive(request: Request, background: BackgroundTasks) -> dict:
    body = await request.body()
    if not valid_meta_signature(body, request.headers.get("X-Hub-Signature-256"), settings.wa_app_secret):
        raise HTTPException(403, "Signature webhook tidak valid")
    try:
        payload = json.loads(body)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise HTTPException(400, "Payload webhook tidak valid") from exc
    # Answer Meta at once; the checks (and the blocking HTTP replies) run after the response.
    background.add_task(_wa_process, payload if isinstance(payload, dict) else {})
    return {"ok": True}


@app.get("/radar")
def radar_page() -> FileResponse:
    return FileResponse(settings.web_dir / "radar.html")


@app.get("/coverage")
def coverage_page() -> FileResponse:
    return FileResponse(settings.web_dir / "coverage.html")


if settings.web_dir.exists():
    app.mount("/", StaticFiles(directory=settings.web_dir, html=True), name="web")
