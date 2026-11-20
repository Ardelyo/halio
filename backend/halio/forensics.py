"""Forensik zero-cloud: semua pemeriksaan di sini jalan di perangkat/server sendiri, tanpa mengirim apa pun ke layanan luar.

    analyze_domains          domain tiruan instansi/bank, homograph, punycode, TLD berisiko, pemendek tautan
    analyze_attachment_lure  jebakan berkas .apk/.exe/.scr/.bat di pesan (undangan, tilang, resi, surat dinas)
    inspect_image_bytes      metadata gambar (PNG/JPEG/WebP): tag generator AI, C2PA, jejak editor, ada/tidaknya EXIF kamera

Prinsip kejujuran Halio: semua keluaran ini INDIKATOR TEKNIS, bukan vonis. Metadata mudah dihapus atau dipalsukan, jadi
tidak adanya indikator tidak membuktikan keaslian, dan adanya indikator tidak membuktikan rekayasa.
"""

from __future__ import annotations

import io
import re
import struct
import zlib
from urllib.parse import urlsplit

OFFICIAL_SUFFIXES = (".go.id", ".mil.id")
SHORTENERS = {"bit.ly", "s.id", "cutt.ly", "tinyurl.com", "shorturl.at", "rb.gy", "t.ly", "linktr.ee", "is.gd", "ow.ly", "goo.gl", "wa.me"}
RISKY_TLDS = {"xyz", "top", "click", "icu", "shop", "site", "online", "live", "vip", "cfd", "sbs", "rest", "buzz", "tk", "ml", "cf", "ga", "gq", "monster", "cyou", "work", "link"}

# kata merek/instansi yang sering dicatut -> domain sahnya. Host yang memuat kata ini tapi BUKAN domain sahnya dicurigai.
BRANDS = {
    "tniad": "TNI AD", "tni": "TNI", "kemhan": "Kemhan", "kemensos": "Kemensos", "bmkg": "BMKG", "bpjs": "BPJS", "polri": "Polri",
    "korlantas": "Korlantas", "komdigi": "Komdigi", "kominfo": "Kominfo", "sscasn": "SSCASN BKN", "cpns": "CPNS",
    "bca": "BCA", "bri": "BRI", "bni": "BNI", "mandiri": "Bank Mandiri", "pln": "PLN", "pajak": "DJP Pajak", "dana": "DANA", "gopay": "GoPay",
    "shopee": "Shopee", "tokopedia": "Tokopedia", "jne": "JNE", "jnt": "J&T", "sicepat": "SiCepat",
}
OFFICIAL_DOMAINS = {
    "bca.co.id", "klikbca.com", "bri.co.id", "bni.co.id", "bankmandiri.co.id", "mandiri.co.id", "pln.co.id", "bpjs-kesehatan.go.id",
    "dana.id", "gopay.co.id", "shopee.co.id", "tokopedia.com", "jne.co.id", "jet.co.id", "sicepat.com",
}
_CONFUSABLE = str.maketrans({"0": "o", "1": "l", "3": "e", "5": "s", "4": "a", "7": "t", "@": "a", "$": "s"})
_GOV_FAKE = re.compile(r"(?:^|[.\-_])(?:go|mil)[.\-_]id(?:[.\-_]|$)")
_HOST_IN_TEXT = re.compile(r"https?://([^\s/?#]+)", re.I)


def _registrable(host: str) -> str:
    parts = host.split(".")
    if len(parts) >= 3 and parts[-2] in {"co", "or", "go", "mil", "ac", "sch", "web", "my"} and parts[-1] == "id":
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def _is_official(host: str) -> bool:
    return host.endswith(OFFICIAL_SUFFIXES) or _registrable(host) in OFFICIAL_DOMAINS


def _finding(host: str, kode: str, tingkat: str, penjelasan: str) -> dict:
    return {"host": host, "kode": kode, "tingkat": tingkat, "penjelasan": penjelasan}


def analyze_domains(domains: list[str], text: str = "") -> list[dict]:
    """Daftar temuan per domain. `tingkat`: tinggi | sedang | rendah. Domain sah (.go.id/.mil.id asli) tidak menghasilkan temuan."""
    hosts = list(dict.fromkeys(d.lower().strip(".") for d in domains))
    for raw in _HOST_IN_TEXT.findall(text or ""):  # hostname non-ASCII (homograph) tidak ditangkap pengurai domain biasa
        host = raw.rsplit("@", 1)[-1].split(":")[0].lower().strip(".")
        if host and host not in hosts and not host.isascii():
            hosts.append(host)
    out: list[dict] = []
    for host in hosts:
        if not host or _is_official(host):
            continue
        found = len(out)
        if not host.isascii():
            out.append(_finding(host, "homograph", "tinggi", "Alamat memakai huruf non-Latin yang menyerupai huruf biasa untuk menyamar sebagai situs lain."))
        if any(label.startswith("xn--") for label in host.split(".")):
            out.append(_finding(host, "punycode", "tinggi", "Alamat berkode punycode (xn--): sering dipakai untuk meniru tampilan situs resmi."))
        if _GOV_FAKE.search(host):
            out.append(_finding(host, "tiruan_domain_resmi", "tinggi", "Alamat memuat 'go.id' atau 'mil.id' tetapi bukan berakhiran itu, jadi bukan situs pemerintah/TNI sungguhan."))
        reg = _registrable(host)
        flat = re.sub(r"[^a-z0-9]", "", host)
        brand_hit = next((b for b in BRANDS if re.search(rf"(?<![a-z]){b}(?![a-z])", re.sub(r"[^a-z0-9]+", " ", host)) or (len(b) >= 4 and b != "dana" and b in flat)), None)
        if brand_hit is None:
            fixed = host.translate(_CONFUSABLE)
            fixed_flat = re.sub(r"[^a-z0-9]", "", fixed).replace("rn", "m").replace("vv", "w")
            hit = next((b for b in BRANDS if len(b) >= 4 and b != "dana" and b in fixed_flat and b not in flat), None)
            if hit:
                out.append(_finding(host, "homograph_angka_huruf", "tinggi", f"Alamat menukar huruf dengan angka/simbol mirip untuk menyamar sebagai {BRANDS[hit]}."))
        elif not any(f["kode"] == "tiruan_domain_resmi" for f in out[found:]):
            out.append(_finding(host, "tiruan_instansi", "tinggi", f"Alamat memuat nama {BRANDS[brand_hit]} tetapi domain aslinya {reg}, bukan situs resmi {BRANDS[brand_hit]}."))
        if host in SHORTENERS:
            out.append(_finding(host, "pemendek_tautan", "sedang", "Tautan pendek menyembunyikan alamat tujuan. Jangan diklik sebelum tahu tujuannya."))
        tld = host.rsplit(".", 1)[-1]
        if tld in RISKY_TLDS and len(out) == found:
            out.append(_finding(host, "tld_berisiko", "rendah", f"Akhiran .{tld} murah dan sering dipakai situs penipuan. Bukan bukti, tetapi tambah hati-hati."))
    return out


# ---------- jebakan berkas ----------

_DANGEROUS = {"apk": "aplikasi Android", "apks": "aplikasi Android", "xapk": "aplikasi Android", "exe": "program Windows", "scr": "program Windows", "bat": "skrip Windows",
              "cmd": "skrip Windows", "msi": "pemasang Windows", "vbs": "skrip Windows", "jar": "program Java", "ps1": "skrip PowerShell", "lnk": "pintasan Windows"}
_FILE = re.compile(r"([\w\-. ()]{1,80}?)\.(" + "|".join(_DANGEROUS) + r")\b", re.I)
_LURE_WORDS = {
    "undangan": "undangan", "nikah": "undangan pernikahan", "pernikahan": "undangan pernikahan", "tilang": "surat tilang", "e-tilang": "surat tilang",
    "resi": "resi kurir", "paket": "paket kurir", "kurir": "resi kurir", "surat dinas": "surat dinas", "surat panggilan": "surat panggilan",
    "tagihan": "tagihan", "bpjs": "tagihan BPJS", "pln": "tagihan PLN", "pajak": "surat pajak", "foto": "foto/video", "video": "foto/video", "bansos": "bantuan sosial",
    "kelulusan": "surat kelulusan", "lamaran": "lamaran kerja", "sk ": "surat keputusan",
}
_INSTALL = re.compile(r"\b(install|instal|pasang|unduh|download)\w*\s+(aplikasi|apk|file|berkas)\b", re.I)


def analyze_attachment_lure(text: str) -> list[dict]:
    """Berkas .apk/.exe/... yang disebut di pesan. APK dari luar Play Store selalu tinggi: itu cara spyware/pencuri OTP masuk ke HP."""
    low = (text or "").lower()
    context = next((label for key, label in _LURE_WORDS.items() if key in low), None)
    out, seen = [], set()
    for m in _FILE.finditer(text or ""):
        ext = m.group(2).lower()
        name = (m.group(1).strip() + "." + ext)[-80:]
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        kind = _DANGEROUS[ext]
        why = f"Berkas '{name}' adalah {kind}, bukan dokumen atau foto."
        if context:
            why += f" Pesan berkedok {context}; modus ini umum dipakai untuk memasang aplikasi pencuri data."
        out.append({"berkas": name, "ekstensi": ext, "jenis": kind, "tingkat": "tinggi" if ext in ("apk", "apks", "xapk") else "sedang", "konteks": context, "penjelasan": why})
    if not out and _INSTALL.search(low) and context:
        out.append({"berkas": None, "ekstensi": None, "jenis": "aplikasi", "tingkat": "sedang", "konteks": context,
                    "penjelasan": f"Pesan berkedok {context} menyuruh memasang aplikasi dari luar toko resmi. Jangan dipasang."})
    return out


# ---------- metadata gambar ----------

AI_TAGS = {
    "midjourney": "Midjourney", "dall-e": "DALL-E", "dalle": "DALL-E", "stable diffusion": "Stable Diffusion", "stablediffusion": "Stable Diffusion",
    "adobe firefly": "Adobe Firefly", "firefly": "Adobe Firefly", "comfyui": "ComfyUI", "automatic1111": "Stable Diffusion WebUI", "novelai": "NovelAI",
    "leonardo.ai": "Leonardo AI", "imagen": "Google Imagen", "made with google ai": "Google AI", "gemini": "Google Gemini", "openai": "OpenAI", "bing image creator": "Bing Image Creator",
    "ideogram": "Ideogram", "flux": "FLUX",
}
EDITORS = {"photoshop": "Adobe Photoshop", "canva": "Canva", "gimp": "GIMP", "lightroom": "Adobe Lightroom", "snapseed": "Snapseed", "picsart": "PicsArt", "paint.net": "Paint.NET"}
_SD_PARAMS = re.compile(r"steps:\s*\d+.*sampler:", re.I | re.S)
NOTE = "Ini indikator teknis dari metadata berkas, bukan vonis. Metadata mudah dihapus atau dipalsukan, dan banyak aplikasi (termasuk WhatsApp) membuangnya."


def _png_blobs(data: bytes) -> tuple[list[bytes], bool, bytes | None]:
    blobs, c2pa, exif = [], False, None
    pos = 8
    while pos + 8 <= len(data):
        length, kind = struct.unpack(">I4s", data[pos : pos + 8])
        body = data[pos + 8 : pos + 8 + length]
        if kind in (b"tEXt", b"iTXt"):
            blobs.append(body)
        elif kind == b"zTXt":
            try:
                blobs.append(body.split(b"\0", 1)[0] + b"\0" + zlib.decompress(body.split(b"\0", 1)[1][1:], 0, 200_000))
            except (zlib.error, IndexError):
                pass
        elif kind == b"caBX":
            c2pa = True
        elif kind == b"eXIf":
            exif = body
        elif kind == b"IDAT":
            break
        pos += 12 + length
    return blobs, c2pa, exif


def _jpeg_blobs(data: bytes) -> tuple[list[bytes], bool, bytes | None]:
    blobs, c2pa, exif = [], False, None
    pos = 2
    while pos + 4 <= len(data) and data[pos] == 0xFF:
        marker = data[pos + 1]
        if marker == 0xDA:  # mulai data piksel
            break
        length = struct.unpack(">H", data[pos + 2 : pos + 4])[0]
        body = data[pos + 4 : pos + 2 + length]
        if marker == 0xE1 and body.startswith(b"Exif\0\0"):
            exif = body[6:]
        elif marker == 0xE1:
            blobs.append(body)
        elif marker == 0xEB and (b"jumb" in body[:12] or b"c2pa" in body[:64]):
            c2pa = True
        elif marker in (0xED, 0xFE, 0xE0):
            blobs.append(body)
        pos += 2 + length
    return blobs, c2pa, exif


def _webp_blobs(data: bytes) -> tuple[list[bytes], bool, bytes | None]:
    blobs, c2pa, exif = [], False, None
    pos = 12
    while pos + 8 <= len(data):
        kind, size = struct.unpack("<4sI", data[pos : pos + 8])
        body = data[pos + 8 : pos + 8 + size]
        if kind == b"XMP ":
            blobs.append(body)
        elif kind == b"EXIF":
            exif = body[6:] if body.startswith(b"Exif\0\0") else body
        elif kind == b"C2PA":
            c2pa = True
        pos += 8 + size + (size & 1)
    return blobs, c2pa, exif


def _camera(exif: bytes | None) -> dict | None:
    if not exif:
        return None
    try:
        from PIL import Image

        tags = Image.Exif()
        tags.load(exif)
        make, model, taken, software = (str(tags.get(k) or "").strip("\0 ") for k in (0x010F, 0x0110, 0x9003, 0x0131))
        ifd = tags.get_ifd(0x8769) if hasattr(tags, "get_ifd") else {}
        taken = taken or str(ifd.get(0x9003) or "").strip("\0 ")
    except Exception:
        return None
    if not (make or model or taken or software):
        return None
    return {"merek": make or None, "model": model or None, "waktu_ambil": taken or None, "perangkat_lunak": software or None}


def inspect_image_bytes(data: bytes) -> dict:
    """Periksa metadata PNG/JPEG/WebP. Tidak pernah mengunduh atau mengirim gambar ke mana pun."""
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        fmt, parse = "png", _png_blobs
    elif data[:3] == b"\xff\xd8\xff":
        fmt, parse = "jpeg", _jpeg_blobs
    elif data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        fmt, parse = "webp", _webp_blobs
    else:
        return {"format": None, "indikator": [], "kamera": None, "ringkasan": "tidak_didukung", "catatan": "Format gambar tidak dikenali (didukung: PNG, JPEG, WebP)."}
    try:
        blobs, c2pa, exif = parse(data)
    except (struct.error, ValueError):
        blobs, c2pa, exif = [], False, None
    text = b"\n".join(blobs + ([exif] if exif else [])).decode("latin-1").lower()
    indicators: list[dict] = []
    ai = sorted({name for key, name in AI_TAGS.items() if key in text})
    for name in ai:
        indicators.append({"kode": "tag_generator_ai", "label": f"Metadata menyebut {name}", "penjelasan": "Tag pembuat gambar AI tertanam di berkas."})
    if _SD_PARAMS.search(text):
        indicators.append({"kode": "parameter_generator_ai", "label": "Parameter generator gambar (Steps/Sampler)", "penjelasan": "Pola parameter khas Stable Diffusion tertanam di berkas."})
    if c2pa or "c2pa" in text or "jumbf" in text:
        indicators.append({"kode": "c2pa", "label": "Content Credentials (C2PA) hadir", "penjelasan": "Berkas membawa manifes asal-usul C2PA. Isinya perlu dibaca dengan pemeriksa C2PA; adanya tidak otomatis berarti AI."})
    editors = sorted({name for key, name in EDITORS.items() if key in text})
    for name in editors:
        indicators.append({"kode": "jejak_editor", "label": f"Jejak penyuntingan: {name}", "penjelasan": "Gambar pernah dibuka atau disimpan lewat aplikasi penyunting."})
    camera = _camera(exif)
    if camera and (camera["merek"] or camera["model"]):
        indicators.append({"kode": "exif_kamera", "label": "Ada metadata kamera/perangkat", "penjelasan": "Konsisten dengan foto dari perangkat, tetapi metadata bisa disalin atau dipalsukan."})
    elif not exif and not blobs and not c2pa:
        indicators.append({"kode": "tanpa_metadata", "label": "Tidak ada metadata sama sekali", "penjelasan": "Umum pada gambar yang dikirim lewat aplikasi chat, tangkapan layar, atau hasil generator yang membuang metadata."})
    elif not camera:
        indicators.append({"kode": "tanpa_exif_kamera", "label": "Tidak ada metadata kamera", "penjelasan": "Tidak ada merek/model kamera di berkas."})
    if ai or c2pa or _SD_PARAMS.search(text):
        summary = "indikator_ai"
    elif editors:
        summary = "ada_jejak_editor"
    elif camera and (camera["merek"] or camera["model"]):
        summary = "metadata_kamera"
    else:
        summary = "tanpa_metadata"
    return {"format": fmt, "ukuran_byte": len(data), "indikator": indicators, "kamera": camera, "ringkasan": summary, "catatan": NOTE}


def analyze_text(text: str, domains: list[str]) -> dict:
    """Gabungan untuk pipeline.check(): domain tiruan + jebakan berkas dari teks pesan."""
    return {"domain": analyze_domains(domains, text), "lampiran": analyze_attachment_lure(text)}
