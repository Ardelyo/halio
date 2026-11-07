"""Telegram bot (primary chat channel for the prototype).

Talks to the Halio HTTP API so the bot can run anywhere:
    set TELEGRAM_BOT_TOKEN=...   HALIO_API_URL=http://localhost:8000
    python -m halio.channels.telegram
"""

from __future__ import annotations

import html
import json
import logging
import os
import threading
import time

import httpx

from .. import version_line
from .format import reply_text

log = logging.getLogger("halio.telegram")

API_URL = os.getenv("HALIO_API_URL", "http://localhost:8000").rstrip("/")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
# Lets the API trust our per-chat reporter id (halio/netguard.py). Same value as the server's.
CHANNEL_HEADERS = {"x-halio-channel-key": os.getenv("HALIO_CHANNEL_KEY", "")}
TG = f"https://api.telegram.org/bot{TOKEN}"

WELCOME = (
    "Halo! Saya <b>Halio</b>, teman cek pesan keluarga.\n\n"
    "Teruskan (forward) pesan yang meragukan ke sini. Saya akan menjawab dengan bahasa sederhana, "
    "kartu yang bisa dibagikan ke grup keluarga, dan pesan suara.\n\n"
    "Saya hanya membaca pesan yang Anda kirim ke sini. Saya tidak membuat vonis sendiri: "
    "jawaban selalu dari pemeriksa fakta atau sumber resmi, dan kalau belum ada, saya bilang terus terang.\n\n"
    "<b>Cara pakai</b>\n"
    "1️⃣ Teruskan pesan, atau kirim foto/pesan suara\n"
    "2️⃣ Tunggu sebentar (kadang sampai 30 detik, AI sedang mencari sumber)\n"
    "3️⃣ Baca vonis berwarna: 🔴 salah · 🟢 sejalan dengan sumber · 🔵 dilaporkan media · 🟠 tidak yakin · ⚪ belum ada pemeriksaan\n\n"
    "Perintah: /bantuan · /sapaan Bu · /privasi · /versi"
)
HELP = (
    "🆘 <b>Bantuan</b>\n"
    "• Kirim pesan yang meragukan, atau foto/suara yang berisi kabar itu.\n"
    "• Kirim tautan: Halio membukanya dan memberi tahu bila rusak, dialihkan, atau bukan situs resmi.\n"
    "• 🔴 terbukti salah · 🟢 sejalan dengan sumber resmi · 🔵 dilaporkan beberapa media (bukan pemeriksaan fakta) · 🟠 tidak yakin · ⚪ belum ada yang memeriksa\n"
    "• Halio tidak menilai pendapat, dan tidak menilai apakah sebuah foto asli.\n"
    "• /sapaan Nenek mengatur cara Halio memanggil Anda."
)
PRIVACY = (
    "🔒 <b>Privasi Halio</b>\n"
    "• Nomor telepon, NIK, email, dan tautan dihapus sebelum diproses.\n"
    "• Hasil cek disimpan di memori paling lama 1 jam untuk kartu dan suara.\n"
    "• Statistik hanya berupa jumlah per kategori, tanpa isi pesan dan tanpa identitas.\n"
    "• Isi kabar yang belum dikenal baru dicatat bila sudah dikirim banyak orang berbeda (k-anonimitas)."
)

CARD_CAPTION = {
    "terbukti_salah": "Kartu Halio: bagikan ke grup keluarga untuk meluruskan.",
    "sejalan_dengan_sumber": "Kartu Halio: sumbernya bisa dibuka, cek tanggal dan konteksnya.",
    "dilaporkan_media": "Kartu Halio: dilaporkan media, bukan pemeriksaan fakta. Sebut sumbernya bila dibagikan.",
    "tidak_yakin": "Kartu Halio: Halio belum yakin, sebaiknya ditahan dulu.",
    "belum_ada_pemeriksaan": "Kartu Halio: belum ada pemeriksaan, jangan diteruskan dulu.",
}
BUSY = "Maaf, Halio sedang tidak bisa memeriksa pesan ini. Coba kirim lagi sebentar lagi, ya."
NOT_TEXT = "Untuk sekarang saya baru bisa membaca teks. Teruskan pesan tulisannya, ya."

sapaan_by_chat: dict[int, str] = {}  # in memory only; families set it once


def tg(method: str, **kwargs) -> dict:
    resp = httpx.post(f"{TG}/{method}", timeout=40, **kwargs)
    data = resp.json()
    if not data.get("ok"):
        log.warning("Telegram %s failed: %s", method, data)
    return data


def keyboard_for(result: dict) -> list[list[dict]]:
    """Only buttons that mean something for this answer."""
    rows: list[list[dict]] = []
    if result["offer_human_review"]:
        rows.append([{"text": "🙋 Tanya pemeriksa manusia", "callback_data": f"esc:{result['id']}"}])
    if result["manipulation"]["techniques"]:
        rows.append([{"text": "🧠 Kenali triknya", "callback_data": f"trik:{result['id']}"}])
    if result["status"] in ("terbukti_salah", "sejalan_dengan_sumber"):
        rows.append([{"text": "⚖️ Ajukan banding", "callback_data": f"app:{result['id']}"}])
    if result.get("_photo_key"):
        rows.append([{"text": "🔬 Telusuri mendalam + cari asal foto", "callback_data": f"teli:{result['_photo_key']}"}])
    elif result.get("kind", "pesan") == "pesan":
        rows.append([{"text": "🔬 Telusuri mendalam (laporan lengkap)", "callback_data": f"tel:{result['id']}"}])
    return rows


PUBLIC_URL = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")
STAGE_LABEL = {
    "antre": "menunggu giliran", "merencanakan": "merencanakan kueri", "mencari": "mencari di web dan arsip",
    "membuka": "membuka halaman dan menyalin kutipan", "menilai": "AI menilai kutipan bernomor",
    "menelusuri_asal": "menelusuri asal-usul", "menyusun": "menyusun laporan", "selesai": "selesai",
}


def _report_link(job_id: str) -> str:
    return f"{PUBLIC_URL}/laporan.html?id={job_id}" if PUBLIC_URL.startswith("https://") else ""


def investigation_summary(rep: dict, job_id: str, sapaan: str = "Bapak, Ibu") -> str:
    """Family first: plain words with the user's form of address. The analyst detail is one tap away (report link)."""
    e = lambda s: html.escape(str(s), quote=False)  # noqa: E731
    icon = {"terbukti_salah": "🔴", "sejalan_dengan_sumber": "🟢", "dilaporkan_media": "🔵", "tidak_yakin": "🟠"}.get(rep["status"], "⚪")
    fam = rep.get("keluarga") or {}
    m = rep.get("metode", {})
    lines = [f"🔬 <b>Hasil penelusuran Halio</b>", "", f"{icon} <b>{e(sapaan)}, {e(fam.get('judul') or rep['status_label'])}</b>", "",
             f"Kabar yang diperiksa: “{e(rep['klaim'][:200])}”"]
    points = fam.get("poin") or [s["teks"] for s in (rep.get("laporan") or {}).get("ringkasan", [])]
    if points:
        lines += ["", "<b>Yang perlu diketahui:</b>"] + [f"• {e(p[:280])}" for p in points[:3]]
    if fam.get("sejak"):
        lines += ["", f"🕰 {e(fam['sejak'])}"]
    refs = [b for b in rep.get("bukti", []) if b["hubungan"] in ("refutes", "claimreview")][:3]
    if refs:
        lines += ["", "🛡 <b>Yang sudah membantah:</b> " + ", ".join(f'<a href="{html.escape(b["url"])}">{e(b["penerbit"])}</a>' for b in refs)]
    if rep.get("gambar"):
        g = rep["gambar"]
        first = g.get("paling_awal")
        lines += ["", f"🖼 Foto yang sama ditemukan di {g['halaman_sama'] + g['halaman_mirip']} halaman"
                      + (f"; paling awal {e(first['tanggal'])} di {e(first['host'])}." if first else ".")]
    lines += ["", f"👉 <b>Sebaiknya:</b> {e(fam.get('saran', ''))}", "",
              f"<i>Halio membuka {m.get('dibuka', 0)} halaman dari {m.get('kandidat', 0)} kandidat dalam {m.get('detik', 0)} detik.</i>"]
    url = _report_link(job_id)
    lines.append(f'📄 <a href="{html.escape(url)}">Laporan lengkap</a> (semua bukti, linimasa, asal-usul; untuk yang ingin tahu rinciannya)' if url else
                 "Laporan lengkap tersedia di situs Halio.")
    return "\n".join(lines)


def _follow_job(chat_id: int, job_id: str, message_id: int | None) -> None:
    """Edit one progress message while the job runs, then send the summary. Runs in its own thread."""
    last = ""
    for _ in range(150):
        time.sleep(3)
        try:
            job = httpx.get(f"{API_URL}/api/investigate/{job_id}", timeout=10).json()
        except (httpx.HTTPError, ValueError):
            continue
        if job.get("status") == "selesai" and job.get("laporan"):
            tg("sendMessage", json={"chat_id": chat_id, "text": investigation_summary(job["laporan"], job_id, sapaan_by_chat.get(chat_id, "Bapak, Ibu")), "parse_mode": "HTML",
                                    "disable_web_page_preview": True})
            return
        if job.get("status") == "gagal":
            tg("sendMessage", json={"chat_id": chat_id, "text": "Maaf, penelusuran berhenti di tengah jalan. Coba lagi sebentar lagi."})
            return
        p = job.get("progres") or {}
        now = (f"🔬 Menelusuri… <b>{STAGE_LABEL.get(job.get('tahap'), job.get('tahap'))}</b>\n"
               f"{p.get('kueri', 0)} kueri · {p.get('kandidat', 0)} kandidat · {p.get('dibuka', 0)} halaman · {p.get('kutipan', 0)} kutipan")
        if message_id and now != last:
            tg("editMessageText", json={"chat_id": chat_id, "message_id": message_id, "text": now, "parse_mode": "HTML"})
            last = now
    tg("sendMessage", json={"chat_id": chat_id, "text": "Penelusuran terlalu lama. Buka laporannya nanti: " + (_report_link(job_id) or "situs Halio")})


photo_refs: dict[str, tuple[str, str, str]] = {}   # short key -> (Telegram file_id, mime, text read from the photo)
PHOTO_ONLY = "Foto tanpa tulisan yang diteruskan pengguna"


def _remember_photo(file_id: str, mime: str, text: str) -> str:
    import uuid

    if len(photo_refs) > 500:
        photo_refs.pop(next(iter(photo_refs)))
    key = uuid.uuid4().hex[:12]
    photo_refs[key] = (file_id, mime, text)
    return key


def start_investigation(chat_id: int, text: str = "", check_id: str | None = None, image: tuple[bytes, str] | None = None) -> None:
    import base64

    body = {"text": text or "x" * 10, "channel": "telegram", "reporter": f"tg:{chat_id}"}
    if check_id:
        body["check_id"] = check_id
    if image:
        body["image_b64"], body["mime"] = base64.b64encode(image[0]).decode(), image[1]
    try:
        r = httpx.post(f"{API_URL}/api/investigate", json=body, headers=CHANNEL_HEADERS, timeout=15)
    except httpx.HTTPError:
        tg("sendMessage", json={"chat_id": chat_id, "text": BUSY})
        return
    if r.status_code != 202:
        detail = (r.json() if r.headers.get("content-type", "").startswith("application/json") else {}).get("detail") or BUSY
        tg("sendMessage", json={"chat_id": chat_id, "text": str(detail)})
        return
    job_id = r.json()["id"]
    sent = tg("sendMessage", json={"chat_id": chat_id, "parse_mode": "HTML",
                                   "text": "🔬 Mulai menelusuri. Halio akan mencari puluhan sumber dan menyusun laporan (1–3 menit)."})
    message_id = (sent.get("result") or {}).get("message_id")
    threading.Thread(target=_follow_job, args=(chat_id, job_id, message_id), daemon=True).start()


def send_result(chat_id: int, result: dict, reply_to: int | None = None) -> None:
    body = {
        "chat_id": chat_id, "text": reply_text(result, html=True), "parse_mode": "HTML",
        "disable_web_page_preview": True, "reply_markup": {"inline_keyboard": keyboard_for(result)},
    }
    if reply_to:
        # Replying to the user's message lets the buttons recover the original text after a restart (see handle_callback).
        body["reply_to_message_id"] = reply_to
        body["allow_sending_without_reply"] = True
    tg("sendMessage", json=body)
    if result.get("reason") in ("berita_media_dikenal", "kumpulan_judul"):
        return  # an article link or a list of headlines needs the text answer only, not a correction card or a voice note
    # The card and the voice note are extras: if either fails the text answer above has already been delivered.
    try:
        card = httpx.get(f"{API_URL}{result['card_url']}", timeout=20)
        if card.status_code == 200:
            tg("sendPhoto", data={"chat_id": chat_id, "caption": CARD_CAPTION.get(result["status"], CARD_CAPTION["tidak_yakin"])},
               files={"photo": ("kartu-halio.png", card.content, "image/png")})
    except httpx.HTTPError as exc:
        log.warning("Card skipped: %s", exc)
    try:
        audio = httpx.get(f"{API_URL}{result['voice_url']}", timeout=30)
        if audio.status_code == 200:
            tg("sendAudio", data={"chat_id": chat_id, "title": "Halio Suara", "performer": "Halio"},
               files={"audio": ("halio-suara.mp3", audio.content, "audio/mpeg")})
    except httpx.HTTPError as exc:
        log.warning("Voice skipped: %s", exc)


def _status_line() -> str:
    try:
        h = httpx.get(f"{API_URL}/health", timeout=8).json()
        return f"API: aktif · AI pencarian web: {'ya' if h.get('llm') else 'tidak'} · baca foto/suara: {'ya' if h.get('media') else 'tidak'}"
    except (httpx.HTTPError, ValueError):
        return "API: tidak merespons"


def _media_of(msg: dict) -> tuple[str, str] | None:
    """(file_id, mime) of a photo, voice note, audio or image document, else None."""
    if msg.get("photo"):
        return msg["photo"][-1]["file_id"], "image/jpeg"  # Telegram lists sizes small to large
    for key, default in (("voice", "audio/ogg"), ("audio", "audio/mpeg"), ("document", "")):
        item = msg.get(key)
        if item and (item.get("mime_type") or default):
            mime = item.get("mime_type") or default
            if key != "document" or mime.startswith(("image/", "audio/")):
                return item["file_id"], mime
    return None


def handle_media(chat_id: int, ref: tuple[str, str], reply_to: int | None = None) -> None:
    import base64

    file_id, mime = ref
    tg("sendChatAction", json={"chat_id": chat_id, "action": "typing"})
    try:
        info = tg("getFile", json={"file_id": file_id})["result"]
        if info.get("file_size", 0) > 8_000_000:
            tg("sendMessage", json={"chat_id": chat_id, "text": "Berkasnya terlalu besar. Kirim yang lebih kecil, atau salin teksnya, ya."})
            return
        raw = httpx.get(f"https://api.telegram.org/file/bot{TOKEN}/{info['file_path']}", timeout=40).content
        resp = httpx.post(f"{API_URL}/api/check-media", timeout=90, headers=CHANNEL_HEADERS, json={
            "data_b64": base64.b64encode(raw).decode(), "mime": mime, "channel": "telegram",
            "reporter": f"tg:{chat_id}", "sapaan": sapaan_by_chat.get(chat_id, "Bapak, Ibu"),
        })
        if resp.status_code == 503:
            tg("sendMessage", json={"chat_id": chat_id, "text": NOT_TEXT})
            return
        resp.raise_for_status()
        result = resp.json()
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as exc:
        log.warning("Media check failed for chat %s: %s", chat_id, type(exc).__name__)
        tg("sendMessage", json={"chat_id": chat_id, "text": BUSY})
        return
    photo = mime.startswith("image/")
    if not result.get("readable", True):
        markup = {"inline_keyboard": [[{"text": "🔬 Cari asal foto ini di internet", "callback_data": f"teli:{_remember_photo(file_id, mime, '')}"}]]} if photo else None
        tg("sendMessage", json={"chat_id": chat_id, "text": result["message"] + ("\nHalio tetap bisa mencari di mana foto ini pernah muncul." if photo else ""),
                                **({"reply_markup": markup} if markup else {})})
        return
    if photo:
        result["_photo_key"] = _remember_photo(file_id, mime, result.get("claim", ""))
    note = "Halio membaca tulisan/ucapan di berkas Anda. Halio <b>tidak menilai apakah fotonya asli</b>, hanya isinya."
    if result["media"].get("looks_edited"):
        note += "\n⚠️ Ada tanda foto ini sudah disunting."
    tg("sendMessage", json={"chat_id": chat_id, "text": note, "parse_mode": "HTML"})
    send_result(chat_id, result, reply_to=reply_to)


def handle_message(msg: dict) -> None:
    chat_id = msg["chat"]["id"]
    text = msg.get("text") or msg.get("caption") or ""
    if text.startswith("/start"):
        tg("sendMessage", json={"chat_id": chat_id, "text": WELCOME + f"\n\n<i>{html.escape(version_line())}</i>", "parse_mode": "HTML"})
        return
    if text.startswith(("/versi", "/version")):
        tg("sendMessage", json={"chat_id": chat_id, "text": f"🤖 <b>{html.escape(version_line())}</b>\n{_status_line()}", "parse_mode": "HTML"})
        return
    if text.startswith("/bantuan"):
        tg("sendMessage", json={"chat_id": chat_id, "text": HELP, "parse_mode": "HTML"})
        return
    if text.startswith("/telusur"):
        claim = text.removeprefix("/telusur").strip()
        if len(claim) < 10:
            tg("sendMessage", json={"chat_id": chat_id, "text": "Tulis klaimnya setelah perintah, contoh:\n/telusur Video Presiden bagi-bagi bantuan tunai lewat WhatsApp"})
            return
        start_investigation(chat_id, text=claim)
        return
    if text.startswith("/privasi"):
        tg("sendMessage", json={"chat_id": chat_id, "text": PRIVACY, "parse_mode": "HTML"})
        return
    if text.startswith("/sapaan"):
        value = text.removeprefix("/sapaan").strip()[:30] or "Bapak, Ibu"
        sapaan_by_chat[chat_id] = value
        tg("sendMessage", json={"chat_id": chat_id, "text": f"Baik, saya akan memanggil Anda “{html.escape(value)}”."})
        return
    media_ref = _media_of(msg)
    if media_ref and len(text.strip()) < 3:
        handle_media(chat_id, media_ref, reply_to=msg.get("message_id"))
        return
    if len(text.strip()) < 3:
        tg("sendMessage", json={"chat_id": chat_id, "text": NOT_TEXT})
        return

    tg("sendChatAction", json={"chat_id": chat_id, "action": "typing"})
    try:
        resp = httpx.post(f"{API_URL}/api/check", timeout=80, headers=CHANNEL_HEADERS, json={
            "text": text, "channel": "telegram", "reporter": f"tg:{chat_id}",
            "sapaan": sapaan_by_chat.get(chat_id, "Bapak, Ibu"),
        })
        if resp.status_code == 429:
            tg("sendMessage", json={"chat_id": chat_id, "text": "Terlalu banyak pesan dalam waktu singkat. Tunggu sebentar, lalu kirim lagi, ya."})
            return
        resp.raise_for_status()
        result = resp.json()
    except (httpx.HTTPError, ValueError) as exc:
        log.warning("Check failed for chat %s: %s", chat_id, exc)
        tg("sendMessage", json={"chat_id": chat_id, "text": BUSY})
        return
    send_result(chat_id, result, reply_to=msg.get("message_id"))


def _recover(cb: dict, chat_id: int) -> str | None:
    """A result lives in memory for an hour and not across a restart. The bot's answer is a reply to the user's own message,
    and Telegram sends that message back with the button press, so the check can be redone without storing anything."""
    original = (cb["message"].get("reply_to_message") or {})
    text = original.get("text") or original.get("caption") or ""
    if len(text.strip()) < 3:
        return None
    try:
        r = httpx.post(f"{API_URL}/api/check", timeout=80, headers=CHANNEL_HEADERS, json={
            "text": text, "channel": "telegram", "reporter": f"tg:{chat_id}", "sapaan": sapaan_by_chat.get(chat_id, "Bapak, Ibu"),
        })
        r.raise_for_status()
        return r.json()["id"]
    except (httpx.HTTPError, ValueError, KeyError):
        return None


def handle_callback(cb: dict) -> None:
    action, _, check_id = cb.get("data", "").partition(":")
    chat_id = cb["message"]["chat"]["id"]
    tg("answerCallbackQuery", json={"callback_query_id": cb["id"]})
    expired = "Maaf, hasil cek ini sudah kedaluwarsa dan pesan aslinya tidak bisa dibaca lagi. Kirim ulang pesannya, ya."
    if action in ("esc", "trik", "app", "tel") and httpx.get(f"{API_URL}/api/check/{check_id}", timeout=10).status_code == 404:
        check_id = _recover(cb, chat_id) or ""
        if not check_id:
            tg("sendMessage", json={"chat_id": chat_id, "text": expired})
            return
    if action == "esc":
        r = httpx.post(f"{API_URL}/api/escalate", json={"check_id": check_id}, timeout=10)
        text = r.json().get("message") if r.status_code == 200 else expired
    elif action == "app":
        httpx.post(f"{API_URL}/api/appeal", json={"check_id": check_id, "reason": "banding dari telegram"}, timeout=10)
        text = "Banding dicatat. Tim akan meninjau ulang sumbernya. Terima kasih sudah kritis!"
    elif action == "tel":
        start_investigation(chat_id, check_id=check_id)
        return
    elif action == "teli":
        ref = photo_refs.get(check_id)
        if not ref:
            tg("sendMessage", json={"chat_id": chat_id, "text": "Fotonya sudah tidak tersimpan. Kirim ulang fotonya, ya."})
            return
        try:
            info = tg("getFile", json={"file_id": ref[0]})["result"]
            raw = httpx.get(f"https://api.telegram.org/file/bot{TOKEN}/{info['file_path']}", timeout=40).content
        except (httpx.HTTPError, KeyError, TypeError):
            tg("sendMessage", json={"chat_id": chat_id, "text": BUSY})
            return
        start_investigation(chat_id, text=ref[2] if len(ref[2]) >= 10 else PHOTO_ONLY, image=(raw, ref[1]))
        return
    elif action == "trik":
        r = httpx.get(f"{API_URL}/api/check/{check_id}", timeout=10)
        techs = r.json()["manipulation"]["techniques"] if r.status_code == 200 else []
        text = "\n\n".join(f"<b>{html.escape(t['label'])}</b>\n{html.escape(t['lesson'])}" for t in techs) or (
            "Pesan ini tidak memakai trik manipulasi yang umum. Tetap cek sumbernya sebelum meneruskan, ya.")
    else:
        return
    tg("sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})


def _chat_of(upd: dict) -> int | None:
    m = upd.get("message") or (upd.get("callback_query") or {}).get("message") or {}
    return (m.get("chat") or {}).get("id")


def startup_checks() -> None:
    """Fail loudly on a bad token; warn about the settings that silently break features."""
    me = httpx.get(f"{TG}/getMe", timeout=15).json()
    if not me.get("ok"):
        raise SystemExit(f"Token Telegram ditolak: {me.get('description', 'tidak dikenal')}. Periksa TELEGRAM_BOT_TOKEN.")
    log.info("Logged in as @%s", me["result"].get("username"))
    # A leftover webhook makes getUpdates fail with 409; this bot polls.
    httpx.post(f"{TG}/deleteWebhook", json={"drop_pending_updates": False}, timeout=15)
    try:
        health = httpx.get(f"{API_URL}/health", timeout=10).json()
        log.info("API reachable: version %s, llm=%s", health.get("version"), health.get("llm"))
    except (httpx.HTTPError, ValueError):
        log.warning("API %s belum bisa dihubungi; bot tetap berjalan dan akan membalas permintaan maaf sampai API hidup", API_URL)
    if not CHANNEL_HEADERS["x-halio-channel-key"]:
        log.warning("HALIO_CHANNEL_KEY kosong: tombol 'Tanya pemeriksa manusia' tidak bisa membalas, dan semua pengguna terhitung satu pelapor")


def main() -> None:
    if not TOKEN:
        raise SystemExit("Set TELEGRAM_BOT_TOKEN (dari @BotFather) terlebih dahulu.")
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)  # httpx logs full URLs, which contain the bot token
    log.info("Halio Telegram bot started, API=%s", API_URL)
    startup_checks()
    offset = 0
    while True:
        try:
            updates = httpx.get(f"{TG}/getUpdates", params={"timeout": 30, "offset": offset}, timeout=40).json()
            if not updates.get("ok"):
                # 409 = another bot process is polling with this token; never spin on an error reply.
                log.warning("getUpdates ditolak: %s; mencoba lagi dalam 5 detik", updates.get("description"))
                time.sleep(5)
                continue
            for upd in updates.get("result", []):
                offset = upd["update_id"] + 1
                try:
                    if "message" in upd:
                        handle_message(upd["message"])
                    elif "callback_query" in upd:
                        handle_callback(upd["callback_query"])
                except Exception:  # one bad update must never stop the bot, and the user must not be left waiting
                    log.exception("Failed to handle update %s", upd.get("update_id"))
                    chat = _chat_of(upd)
                    if chat:
                        try:
                            tg("sendMessage", json={"chat_id": chat, "text": BUSY})
                        except Exception:
                            log.exception("Could not send the apology either")
        except (httpx.HTTPError, ValueError) as exc:
            log.warning("Polling error: %s; retrying in 3s", exc)
            time.sleep(3)


if __name__ == "__main__":
    main()
