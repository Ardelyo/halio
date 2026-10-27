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

    # Retrieval thresholds, calibrated with eval/run_eval.py. Re-run the eval after changing.
    match_threshold: float = field(default_factory=lambda: float(os.getenv("HALIO_MATCH_THRESHOLD", "0.40")))
    unsure_threshold: float = field(default_factory=lambda: float(os.getenv("HALIO_UNSURE_THRESHOLD", "0.26")))

    # T1: Google Fact Check Tools (ClaimReview). Optional.
    google_factcheck_key: str | None = field(default_factory=lambda: os.getenv("GOOGLE_FACTCHECK_API_KEY") or None)

    # T2: LLM verdict over retrieved sources. Optional, off by default.
    llm_enabled: bool = field(default_factory=lambda: _bool("HALIO_LLM"))
    llm_model: str = field(default_factory=lambda: os.getenv("HALIO_LLM_MODEL", "claude-opus-5-5"))

    # Radar (aggregate dashboard) privacy knobs.
    radar_token: str | None = field(default_factory=lambda: os.getenv("RADAR_TOKEN") or None)
    k_anonymity: int = field(default_factory=lambda: int(os.getenv("HALIO_K_ANON", "5")))

    # Channels.
    telegram_token: str | None = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN") or None)
    wa_token: str | None = field(default_factory=lambda: os.getenv("WHATSAPP_TOKEN") or None)
    wa_phone_id: str | None = field(default_factory=lambda: os.getenv("WHATSAPP_PHONE_NUMBER_ID") or None)
    wa_verify_token: str | None = field(default_factory=lambda: os.getenv("WHATSAPP_VERIFY_TOKEN") or None)


settings = Settings()
