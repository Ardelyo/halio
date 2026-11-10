"""Runtime settings, read once from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    corpus_path: Path = field(
        default_factory=lambda: Path(os.getenv("HALIO_CORPUS", REPO_ROOT / "data" / "debunks.json"))
    )
    db_path: Path = field(
        default_factory=lambda: Path(os.getenv("HALIO_DB", REPO_ROOT / "halio.db"))
    )
    web_dir: Path = field(default_factory=lambda: REPO_ROOT / "web")
    public_base_url: str = field(default_factory=lambda: os.getenv("PUBLIC_BASE_URL", "http://localhost:8000"))
    cors_origins: tuple[str, ...] = field(
        default_factory=lambda: tuple(x.strip() for x in os.getenv("HALIO_CORS_ORIGINS", "").split(",") if x.strip())
    )
    rate_limit_per_minute: int = field(default_factory=lambda: int(os.getenv("HALIO_RATE_LIMIT", "60")))

    # Retrieval thresholds, calibrated with eval/run_eval.py. Re-run the eval after changing.
    match_threshold: float = field(default_factory=lambda: float(os.getenv("HALIO_MATCH_THRESHOLD", "0.40")))
    unsure_threshold: float = field(default_factory=lambda: float(os.getenv("HALIO_UNSURE_THRESHOLD", "0.26")))

    # T1: Google Fact Check Tools (ClaimReview). Optional.
    google_factcheck_key: str | None = field(default_factory=lambda: os.getenv("GOOGLE_FACTCHECK_API_KEY") or None)

    # T2: grounded model verdict and web evidence. Optional, off by default.
    llm_enabled: bool = field(default_factory=lambda: _bool("HALIO_LLM"))
    # "v2" = numbered passages picked by code + tier policy (halio/evidence.py); "v1" = the earlier quote-matching agent.
    evidence_engine: str = field(default_factory=lambda: os.getenv("HALIO_ENGINE", "v2"))
    llm_provider: str = field(default_factory=lambda: os.getenv("HALIO_LLM_PROVIDER", "google"))
    llm_model: str = field(
        default_factory=lambda: os.getenv(
            "HALIO_LLM_MODEL",
            "claude-haiku-5-5" if os.getenv("HALIO_LLM_PROVIDER", "google") == "anthropic" else "gemini-3.5-flash-lite",
        )
    )
    google_cloud_project: str = field(default_factory=lambda: os.getenv("GOOGLE_CLOUD_PROJECT", "gemma4good-494311"))
    # Gemini 3.5 Flash-Lite is served from "global" (and the us/eu multi-regions), not us-central1.
    google_cloud_location: str = field(default_factory=lambda: os.getenv("GOOGLE_CLOUD_LOCATION", "global"))
    agent_timeout_s: float = field(default_factory=lambda: float(os.getenv("HALIO_AGENT_TIMEOUT", "45")))

    # Photos and voice notes: Gemini reads them into text (halio/media.py). Independent of HALIO_LLM so verdicts stay stable.
    media_enabled: bool = field(default_factory=lambda: _bool("HALIO_MEDIA"))
    # Halio Telusur (investigation agent): needs HALIO_LLM=1. Each run costs real model calls; these are hard daily caps.
    agent_daily_cap: int = field(default_factory=lambda: int(os.getenv("HALIO_AGENT_DAILY_CAP", "60")))
    agent_per_reporter: int = field(default_factory=lambda: int(os.getenv("HALIO_AGENT_PER_REPORTER", "8")))
    # Cost guards for /api/check and /api/check-media, per process per day. 0 = no limit (the default keeps today's behaviour).
    # Past the LLM cap a check answers from the curated corpus only (labelled); past the media cap photos/voice get a 429.
    llm_daily_cap: int = field(default_factory=lambda: int(os.getenv("HALIO_LLM_DAILY_CAP", "0")))
    media_daily_cap: int = field(default_factory=lambda: int(os.getenv("HALIO_MEDIA_DAILY_CAP", "0")))
    # Requests with a larger Content-Length are refused with 413 before the body is read.
    max_body_mb: int = field(default_factory=lambda: int(os.getenv("HALIO_MAX_BODY_MB", "16")))
    # Content-Security-Policy: enforce (default), report (report-only, for debugging a page) or off.
    csp_mode: str = field(default_factory=lambda: os.getenv("HALIO_CSP", "enforce").strip().lower())
    # Daily analyst brief (investigate/brief.py): built each morning from 06:00 WIB when on; needs the sensor and HALIO_LLM=1.
    brief_enabled: bool = field(default_factory=lambda: _bool("HALIO_BRIEF"))
    media_model: str = field(default_factory=lambda: os.getenv("HALIO_MEDIA_MODEL", "gemini-3.5-flash-lite"))
    # Open the links users forward and report what is there (halio/link_check.py).
    link_check_enabled: bool = field(default_factory=lambda: os.getenv("HALIO_LINK_CHECK", "1") != "0")

    # Radar (aggregate dashboard) privacy knobs.
    radar_token: str | None = field(default_factory=lambda: os.getenv("RADAR_TOKEN") or None)
    # Without a token the Radar answers only localhost, unless this is set (public demo; data is aggregate).
    radar_public: bool = field(default_factory=lambda: _bool("HALIO_RADAR_PUBLIC"))
    k_anonymity: int = field(default_factory=lambda: int(os.getenv("HALIO_K_ANON", "5")))
    # Days kept for unknown claims, appeals, closed tickets, review audit and investigations (docs/PRIVACY.md).
    retention_days: int = field(default_factory=lambda: max(1, int(os.getenv("HALIO_RETENTION_DAYS", "30"))))

    # Sensor: polls public news / fact-check feeds (docs/ARCHITECTURE_SENSOR.md). Off by default.
    sensor_enabled: bool = field(default_factory=lambda: _bool("HALIO_SENSOR"))
    sensor_workers: int = field(default_factory=lambda: int(os.getenv("HALIO_SENSOR_WORKERS", "8")))
    sensor_tick_s: float = field(default_factory=lambda: float(os.getenv("HALIO_SENSOR_TICK", "15")))
    sensor_user_agent: str = field(
        default_factory=lambda: os.getenv("HALIO_SENSOR_UA", "HalioSensor/0.1 (riset anti-disinformasi; hanya feed publik)")
    )

    # Abuse limits and trust (halio/netguard.py). The per-minute limit is rate_limit_per_minute above.
    # Behind a reverse proxy every client shares the proxy's address; enable this to read X-Forwarded-For.
    trust_proxy: bool = field(default_factory=lambda: _bool("HALIO_TRUST_PROXY"))
    max_input_chars: int = field(default_factory=lambda: int(os.getenv("HALIO_MAX_INPUT", "4000")))
    # Shared secret our own bots send so their reporter ids are trusted.
    channel_key: str | None = field(default_factory=lambda: os.getenv("HALIO_CHANNEL_KEY") or None)

    # Channels.
    telegram_token: str | None = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN") or None)
    wa_token: str | None = field(default_factory=lambda: os.getenv("WHATSAPP_TOKEN") or None)
    wa_phone_id: str | None = field(default_factory=lambda: os.getenv("WHATSAPP_PHONE_NUMBER_ID") or None)
    wa_verify_token: str | None = field(default_factory=lambda: os.getenv("WHATSAPP_VERIFY_TOKEN") or None)
    # Meta signs each webhook POST with the app secret (X-Hub-Signature-256). Required to accept them.
    wa_app_secret: str | None = field(default_factory=lambda: os.getenv("WHATSAPP_APP_SECRET") or None)


settings = Settings()
