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

    # batas skor pencocokan korpus, udah dikalibrasi pake eval/run_eval.py (jangan lupa jalanin eval lagi kl diubah)
    match_threshold: float = field(default_factory=lambda: float(os.getenv("HALIO_MATCH_THRESHOLD", "0.40")))
    unsure_threshold: float = field(default_factory=lambda: float(os.getenv("HALIO_UNSURE_THRESHOLD", "0.26")))

    # lapis 1: Google Fact Check Tools API (ClaimReview), opsional kl ada API key-nya
    google_factcheck_key: str | None = field(default_factory=lambda: os.getenv("GOOGLE_FACTCHECK_API_KEY") or None)

    # lapis 2: penelusuran bukti web & model AI, opsional dan default-nya mati biar aman biaya
    llm_enabled: bool = field(default_factory=lambda: _bool("HALIO_LLM"))
    # "v2" = kutipan bernomor dipilih kode + kebijakan tier (evidence.py); "v1" = versi agen pencocok kutipan lama
    evidence_engine: str = field(default_factory=lambda: os.getenv("HALIO_ENGINE", "v2"))
    llm_provider: str = field(default_factory=lambda: os.getenv("HALIO_LLM_PROVIDER", "google"))
    llm_model: str = field(
        default_factory=lambda: os.getenv(
            "HALIO_LLM_MODEL",
            "claude-haiku-5-5" if os.getenv("HALIO_LLM_PROVIDER", "google") == "anthropic" else "gemini-3.5-flash-lite",
        )
    )
    google_cloud_project: str = field(default_factory=lambda: os.getenv("GOOGLE_CLOUD_PROJECT", "gemma4good-494311"))
    # Gemini 3.5 Flash-Lite adanya di endpoint "global" (atau multi-region us/eu), bukan di us-central1
    google_cloud_location: str = field(default_factory=lambda: os.getenv("GOOGLE_CLOUD_LOCATION", "global"))
    agent_timeout_s: float = field(default_factory=lambda: float(os.getenv("HALIO_AGENT_TIMEOUT", "45")))

    # baca foto & voice note jadi teks pake Gemini (media.py), dipisah dari HALIO_LLM biar logika vonis tetep stabil
    media_enabled: bool = field(default_factory=lambda: _bool("HALIO_MEDIA"))
    # Halio Telusur (agen investigasi mendalam): butuh HALIO_LLM=1, dibatasin ketat per hari krn lumayan makan kuota model
    agent_daily_cap: int = field(default_factory=lambda: int(os.getenv("HALIO_AGENT_DAILY_CAP", "60")))
    agent_per_reporter: int = field(default_factory=lambda: int(os.getenv("HALIO_AGENT_PER_REPORTER", "8")))
    # pengaman biaya harian buat /api/check dan /api/check-media (0 = ga dibatasin).
    # kl kuota LLM abis tetep jawab dari korpus kurasi aja; kl kuota media abis bakal balikin 429.
    llm_daily_cap: int = field(default_factory=lambda: int(os.getenv("HALIO_LLM_DAILY_CAP", "0")))
    media_daily_cap: int = field(default_factory=lambda: int(os.getenv("HALIO_MEDIA_DAILY_CAP", "0")))
    # tolak request yg ukuran Content-Length-nya kelewat gede pake 413 sebelum body-nya dibaca penuh
    max_body_mb: int = field(default_factory=lambda: int(os.getenv("HALIO_MAX_BODY_MB", "16")))
    # mode CSP: enforce (default), report (buat nge-debug tampilan halaman), atau off
    csp_mode: str = field(default_factory=lambda: os.getenv("HALIO_CSP", "enforce").strip().lower())
    # rangkuman pagi analis (investigate/brief.py): jalan tiap lewat jam 06:00 WIB kl dinyalain (butuh sensor + HALIO_LLM=1)
    brief_enabled: bool = field(default_factory=lambda: _bool("HALIO_BRIEF"))
    media_model: str = field(default_factory=lambda: os.getenv("HALIO_MEDIA_MODEL", "gemini-3.5-flash-lite"))
    # intip isi link yg diterusin user biar ketauan beneran situs resmi atau jebakan (link_check.py)
    link_check_enabled: bool = field(default_factory=lambda: os.getenv("HALIO_LINK_CHECK", "1") != "0")

    # konfigrasi privasi buat halaman dashboard agregat Radar
    radar_token: str | None = field(default_factory=lambda: os.getenv("RADAR_TOKEN") or None)
    # tanpa token, Radar cuma bisa dibuka dari localhost kecuali flag ini dinyalain buat demo publik
    radar_public: bool = field(default_factory=lambda: _bool("HALIO_RADAR_PUBLIC"))
    k_anonymity: int = field(default_factory=lambda: int(os.getenv("HALIO_K_ANON", "5")))
    # batas hari nyimpen klaim belum dikenal, sanggahan, tiket selesai, sama riwayat audit
    retention_days: int = field(default_factory=lambda: max(1, int(os.getenv("HALIO_RETENTION_DAYS", "30"))))

    # sensor pemantau RSS berita & cek fakta publik, default mati biar hemat resource kl ga dipake
    sensor_enabled: bool = field(default_factory=lambda: _bool("HALIO_SENSOR"))
    sensor_workers: int = field(default_factory=lambda: int(os.getenv("HALIO_SENSOR_WORKERS", "8")))
    sensor_tick_s: float = field(default_factory=lambda: float(os.getenv("HALIO_SENSOR_TICK", "15")))
    sensor_user_agent: str = field(
        default_factory=lambda: os.getenv("HALIO_SENSOR_UA", "HalioSensor/0.1 (riset anti-disinformasi; hanya feed publik)")
    )

    # batas anti-spam & kepercayaan jaringan (netguard.py)
    # kl di belakang reverse proxy semua user bakal keliatan satu IP, nyalain ini biar baca X-Forwarded-For
    trust_proxy: bool = field(default_factory=lambda: _bool("HALIO_TRUST_PROXY"))
    max_input_chars: int = field(default_factory=lambda: int(os.getenv("HALIO_MAX_INPUT", "4000")))
    # kunci rahasia bareng biar id pelapor dari bot internal kita bisa dipercaya server
    channel_key: str | None = field(default_factory=lambda: os.getenv("HALIO_CHANNEL_KEY") or None)

    # kredensial kanal bot (Telegram & WhatsApp)
    telegram_token: str | None = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN") or None)
    wa_token: str | None = field(default_factory=lambda: os.getenv("WHATSAPP_TOKEN") or None)
    wa_phone_id: str | None = field(default_factory=lambda: os.getenv("WHATSAPP_PHONE_NUMBER_ID") or None)
    wa_verify_token: str | None = field(default_factory=lambda: os.getenv("WHATSAPP_VERIFY_TOKEN") or None)
    # Meta ngasih tanda tangan HMAC (X-Hub-Signature-256) pake app secret ini di tiap POST webhook, wajib ada
    wa_app_secret: str | None = field(default_factory=lambda: os.getenv("WHATSAPP_APP_SECRET") or None)


settings = Settings()
