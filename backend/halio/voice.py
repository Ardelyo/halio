"""Halio Suara: turn the voice script into an MP3 voice note.

First choice: Google Cloud Text-to-Speech (official API, Chirp 3 HD Indonesian voices) with the VM's own credentials. If that is
unavailable (API off, quota, no credentials) it falls back to gTTS, and if that also fails the API answers 501 and the web app
uses the browser's own Indonesian speech synthesis. HALIO_TTS_VOICE picks the voice (default: a warm female Chirp 3 HD voice).
"""

from __future__ import annotations

import io
import logging
import os

import httpx

log = logging.getLogger(__name__)

ENDPOINT = "https://texttospeech.googleapis.com/v1/text:synthesize"
VOICE = os.getenv("HALIO_TTS_VOICE", "id-ID-Chirp3-HD-Aoede")
PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "gemma4good-494311")
MAX_CHARS = 1500   # voice note cukup ringkas aja biar enak didengerin orang tua, ga usah sepanjang artikel


class VoiceUnavailable(RuntimeError):
    pass


def _token() -> str:
    import google.auth
    from google.auth.transport.requests import Request

    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(Request())
    return creds.token


def _cloud(script: str, token=_token, transport: httpx.BaseTransport | None = None) -> bytes:
    import base64

    with httpx.Client(timeout=25, transport=transport) as client:
        # speakingRate 0.95 biar temponya agak pelan dikit & artikulasinya jelas buat bapak/ibu
        resp = client.post(ENDPOINT, headers={"Authorization": f"Bearer {token()}", "x-goog-user-project": PROJECT}, json={
            "input": {"text": script[:MAX_CHARS]},
            "voice": {"languageCode": "id-ID", "name": VOICE},
            "audioConfig": {"audioEncoding": "MP3", "speakingRate": 0.95},
        })
    if resp.status_code != 200:
        raise VoiceUnavailable(f"cloud_tts_http_{resp.status_code}")
    return base64.b64decode(resp.json()["audioContent"])


def _gtts(script: str) -> bytes:
    try:
        from gtts import gTTS
    except ImportError as exc:
        raise VoiceUnavailable("gTTS not installed (pip install gTTS)") from exc
    buf = io.BytesIO()
    try:
        gTTS(script, lang="id", slow=False).write_to_fp(buf)
    except Exception as exc:  # gTTS suka ngelempar error sendiri kl koneksi lagi bermasalah
        log.warning("TTS failed: %s", exc)
        raise VoiceUnavailable(str(exc)) from exc
    return buf.getvalue()


def synthesize(script: str) -> bytes:
    # coba pake suara Chirp 3 HD di Cloud TTS dulu, kl gagal otomatis turun ke gTTS
    try:
        return _cloud(script)
    except Exception as exc:   # kredensial blm ada, kuota abis, atau jaringan gangguan: jgn smpe voice note batal dibuat
        log.info("Cloud TTS unavailable, falling back to gTTS: %s", type(exc).__name__)
        return _gtts(script)
