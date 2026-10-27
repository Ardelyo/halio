"""Halio Suara: turn the voice script into an MP3 voice note.

Uses gTTS when installed (needs internet). Without it the API returns 501 and
the web app falls back to the browser's own Indonesian speech synthesis. For
the recorded demo, pre-render the five demo claims (scripts/prerender_voice.py).
"""

from __future__ import annotations

import io
import logging

log = logging.getLogger(__name__)


class VoiceUnavailable(RuntimeError):
    pass


def synthesize(script: str) -> bytes:
    try:
        from gtts import gTTS
    except ImportError as exc:
        raise VoiceUnavailable("gTTS not installed (pip install gTTS)") from exc
    buf = io.BytesIO()
    try:
        gTTS(script, lang="id", slow=False).write_to_fp(buf)
    except Exception as exc:  # gTTS raises its own error types on network failure
        log.warning("TTS failed: %s", exc)
        raise VoiceUnavailable(str(exc)) from exc
    return buf.getvalue()
