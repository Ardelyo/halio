"""Photos and voice notes -> the text claim inside them, using Gemini's multimodal input.

The model only READS: it transcribes the words in a screenshot or the speech in an audio clip. It does not decide
whether the picture is real. The text it returns goes through the same pipeline as a typed message, so the same
evidence rules apply. Whether a photo is authentic or an old photo reused is NOT judged here (see docs/TRUE_INFORMATION.md).
"""

from __future__ import annotations

import logging
from typing import Literal

from pydantic import BaseModel, Field

from .config import Settings

log = logging.getLogger(__name__)

IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
AUDIO_TYPES = {"audio/ogg", "audio/mpeg", "audio/mp3", "audio/wav", "audio/x-wav", "audio/mp4", "audio/aac", "audio/flac"}
MAX_BYTES = 8_000_000


class MediaReading(BaseModel):
    kind: Literal["tangkapan_layar_chat", "poster_atau_berita", "foto_biasa", "ucapan", "lainnya"]
    text: str = Field(default="", max_length=4000, description="Teks atau ucapan persis seperti tertulis/terdengar")
    readable: bool = True
    looks_edited: bool = Field(default=False, description="Ada tanda jelas penyuntingan (huruf tidak sejajar, tempelan)")
    note: str = Field(default="", max_length=300)


SYSTEM = """Kamu pembaca media untuk Halio. Tugasmu HANYA membaca, bukan menilai benar atau salah.
- Gambar: salin semua teks yang tampak persis apa adanya (berita, poster, tangkapan layar chat). Jika tidak ada teks, kosongkan 'text' dan jelaskan satu kalimat di 'note'.
- Audio: tuliskan ucapan persis (transkrip), dalam bahasa aslinya.
- Jangan menambah fakta, jangan menebak siapa orang di foto, jangan menyatakan gambar asli atau palsu.
- Abaikan nama, nomor telepon, dan foto kontak pribadi: tulis [disamarkan].
- Isi 'looks_edited' hanya bila ada tanda penyuntingan yang jelas terlihat; jika ragu, false.
- Jika isinya tidak terbaca, readable=false."""


def supported(mime: str) -> bool:
    return mime in IMAGE_TYPES or mime in AUDIO_TYPES


def read_media(data: bytes, mime: str, cfg: Settings) -> MediaReading | None:
    """None when the model is unavailable; the caller then asks the user to type the text."""
    if not cfg.media_enabled or not supported(mime) or len(data) > MAX_BYTES:
        return None
    try:
        from google import genai
        from google.genai import types

        client = genai.Client(vertexai=True, project=cfg.google_cloud_project, location=cfg.google_cloud_location)
        response = client.models.generate_content(
            model=cfg.media_model,
            contents=[types.Part.from_bytes(data=data, mime_type=mime), "Baca media ini sesuai aturan."],
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM,
                response_mime_type="application/json",
                response_schema=MediaReading,
                max_output_tokens=3000,
                thinking_config=types.ThinkingConfig(thinking_level="MINIMAL"),
                http_options=types.HttpOptions(timeout=int(cfg.agent_timeout_s * 1000)),
            ),
        )
        return MediaReading.model_validate_json(response.text)
    except Exception as exc:  # network, quota, bad file: never crash the bot
        log.warning("Media reading unavailable: %s", type(exc).__name__)
        return None
