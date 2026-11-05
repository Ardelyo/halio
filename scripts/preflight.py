"""Is Halio ready to be used (and filmed) right now? Prints PASS / WARN / FAIL for each thing a demo depends on.

    python scripts/preflight.py                      # API on http://localhost:8000, token from TELEGRAM_BOT_TOKEN
    HALIO_API_URL=https://halio.example.com python scripts/preflight.py

Exit code 1 if anything FAILs. Needs only the Python standard library.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

API = os.getenv("HALIO_API_URL", "http://localhost:8000").rstrip("/")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
KEY = os.getenv("HALIO_CHANNEL_KEY", "")
failed = False


def say(level: str, what: str, detail: str = "") -> None:
    global failed
    failed = failed or level == "FAIL"
    print(f"[{level:<4}] {what}" + (f"  ({detail})" if detail else ""))


def call(url: str, data: dict | None = None, headers: dict | None = None, timeout: int = 20):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json", **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read(), r.headers


def main() -> None:
    print(f"Halio preflight, API = {API}\n")
    # 1. API alive
    try:
        _, body, _ = call(f"{API}/health")
        health = json.loads(body)
        say("PASS", "API hidup", f"versi {health.get('version')}, LLM {'on' if health.get('llm') else 'off (jawaban dari korpus saja)'}")
    except Exception as exc:
        say("FAIL", "API tidak bisa dihubungi", f"{exc}; jalankan: cd backend && uvicorn halio.api:app --port 8000")
        sys.exit(1)

    # 2. a real check, with the bot's channel key
    probe = "Bapak ibu, ada video Presiden bagi-bagi bantuan tunai, bayar biaya admin 150rb lewat WA. SEBARKAN!!"
    try:
        _, body, _ = call(f"{API}/api/check", {"text": probe, "channel": "telegram", "reporter": "tg:0"},
                          {"x-halio-channel-key": KEY} if KEY else {})
        res = json.loads(body)
        ok = res["status"] == "terbukti_salah"
        say("PASS" if ok else "FAIL", "Cek pesan hoaks contoh", f"status {res['status']}")
    except Exception as exc:
        say("FAIL", "Cek pesan gagal", str(exc))
        res = None

    if res:
        for name, url_key, kind in (("Kartu Halio (PNG)", "card_url", b"\x89PNG"), ("Suara (MP3)", "voice_url", None)):
            try:
                _, content, _ = call(API + res[url_key], timeout=40)
                good = content[:4] == kind if kind else len(content) > 1000
                say("PASS" if good else "FAIL", name, f"{len(content)} byte")
            except urllib.error.HTTPError as exc:
                say("WARN" if url_key == "voice_url" else "FAIL", name, f"HTTP {exc.code}; suara server butuh internet (gTTS), suara di perangkat tetap jalan di web")
            except Exception as exc:
                say("WARN" if url_key == "voice_url" else "FAIL", name, str(exc))

    # 3. Telegram
    if not TOKEN:
        say("FAIL", "TELEGRAM_BOT_TOKEN kosong", "isi dari @BotFather")
    else:
        try:
            _, body, _ = call(f"https://api.telegram.org/bot{TOKEN}/getMe")
            me = json.loads(body)["result"]
            say("PASS", "Token Telegram valid", f"@{me['username']}")
            _, body, _ = call(f"https://api.telegram.org/bot{TOKEN}/getWebhookInfo")
            hook = json.loads(body)["result"].get("url")
            say("WARN" if hook else "PASS", "Webhook Telegram", f"ada webhook ({hook}); bot ini polling dan akan menghapusnya saat start" if hook else "tidak ada (benar untuk polling)")
        except Exception as exc:
            say("FAIL", "Telegram tidak bisa dicek", str(exc))
    say("PASS" if KEY else "WARN", "HALIO_CHANNEL_KEY", "terisi" if KEY else "kosong: tombol 'Tanya pemeriksa manusia' tidak bisa membalas dan semua pengguna Telegram terhitung satu pelapor")

    # 4. Radar protection
    try:
        call(f"{API}/api/radar")
        say("WARN", "Radar terbuka tanpa token", "aman bila hanya di laptop Anda; isi RADAR_TOKEN sebelum dipublikasikan")
    except urllib.error.HTTPError as exc:
        say("PASS" if exc.code == 401 else "WARN", "Radar menolak tanpa token" if exc.code == 401 else "Radar", f"HTTP {exc.code}")
    except Exception as exc:
        say("WARN", "Radar", str(exc))

    print("\nSiap." if not failed else "\nAda yang GAGAL; perbaiki dulu sebelum merekam.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
