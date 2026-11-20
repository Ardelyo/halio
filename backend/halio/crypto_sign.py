"""Tanda tangan digital Halio: Kartu Halio PNG dan laporan LAPSUS bisa dibuktikan asli, dan 1 byte diubah = ditolak.

Aktif: Ed25519 (pustaka `cryptography`, jalan di Windows ARM64 tanpa kompilasi). Skemanya pluggable: `ALGORITHMS` memetakan
nama algoritma ke penanda tangan/pemeriksa, jadi ML-DSA-65 (pasca-kuantum) tinggal didaftarkan bila `liboqs` tersedia.

Amplop (envelope):
    version, alg, key_id, issued_at, payload, sha256, signature_b64
`sha256` = hash dari byte kanonik (version, alg, key_id, issued_at, payload); tanda tangan dihitung atas byte yang sama.
Kunci publik TIDAK ikut di amplop: pemalsu bisa menyematkan kuncinya sendiri. Pemeriksa wajib memegang kunci publik satuan.
"""

from __future__ import annotations

import base64
import hashlib
import io
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

VERSION = 1
PNG_KEY = "halio-sig-v1"
ALG_ED25519 = "Ed25519"


def canonical(obj: Any) -> bytes:
    """Byte kanonik: kunci diurut, tanpa spasi, UTF-8. Dua mesin yang sepakat pada ini menghasilkan hash sama."""
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def key_id_of(public_key: Ed25519PublicKey) -> str:
    raw = public_key.public_bytes(serialization.Encoding.Raw, serialization.PublicFormat.Raw)
    return sha256_hex(raw)[:16]


class Signer:
    """Pemegang kunci privat Ed25519 satuan."""

    alg = ALG_ED25519

    def __init__(self, private_key: Ed25519PrivateKey):
        self._key = private_key
        self.public_key = private_key.public_key()
        self.key_id = key_id_of(self.public_key)

    @property
    def public_pem(self) -> str:
        return self.public_key.public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo).decode("ascii")

    def sign(self, message: bytes) -> bytes:
        return self._key.sign(message)


def _verify_ed25519(public_pem: str, message: bytes, signature: bytes) -> bool:
    key = serialization.load_pem_public_key(public_pem.encode("ascii"))
    if not isinstance(key, Ed25519PublicKey):
        return False
    try:
        key.verify(signature, message)
        return True
    except InvalidSignature:
        return False


# nama algoritma -> fungsi pemeriksa. Daftarkan "ML-DSA-65" di sini kalau liboqs ada; amplop dgn alg lain ditolak.
ALGORITHMS = {ALG_ED25519: _verify_ed25519}


def default_key_path() -> Path:
    return Path(os.getenv("HALIO_SIGN_KEY_FILE") or Path.home() / ".halio" / "signing_key.pem")


def _load_private(pem: bytes) -> Ed25519PrivateKey:
    key = serialization.load_pem_private_key(pem, password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise ValueError("Kunci penandatangan harus Ed25519")
    return key


def load_signer(path: Path | None = None) -> Signer:
    """Urutan: env HALIO_SIGN_KEY (PEM) -> berkas kunci satuan -> buat kunci baru dan simpan (izin 0600 bila bisa)."""
    env_pem = os.getenv("HALIO_SIGN_KEY")
    if env_pem:
        return Signer(_load_private(env_pem.replace("\\n", "\n").encode("ascii")))
    path = path or default_key_path()
    if path.exists():
        return Signer(_load_private(path.read_bytes()))
    key = Ed25519PrivateKey.generate()
    pem = key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption())
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(pem)
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
    except OSError:
        pass  # disk read-only: kunci sesi saja, tanda tangan sah selama proses hidup
    return Signer(key)


_signer: Signer | None = None
_lock = threading.Lock()


def get_signer() -> Signer:
    global _signer
    with _lock:
        if _signer is None:
            _signer = load_signer()
        return _signer


def sign_payload(payload: dict, signer: Signer | None = None) -> dict:
    signer = signer or get_signer()
    body = {"version": VERSION, "alg": signer.alg, "key_id": signer.key_id, "issued_at": _now(), "payload": payload}
    message = canonical(body)
    return {**body, "sha256": sha256_hex(message), "signature_b64": base64.b64encode(signer.sign(message)).decode("ascii")}


def verify_payload(envelope: Any, public_key_pem: str) -> tuple[bool, str]:
    """(sah, alasan). Alasan selalu bahasa Indonesia yang bisa ditampilkan apa adanya."""
    if not isinstance(envelope, dict):
        return False, "Amplop tanda tangan tidak terbaca."
    need = ("version", "alg", "key_id", "issued_at", "payload", "sha256", "signature_b64")
    if any(k not in envelope for k in need):
        return False, "Amplop tanda tangan tidak lengkap."
    if envelope["version"] != VERSION:
        return False, "Versi tanda tangan tidak dikenal."
    check = ALGORITHMS.get(envelope["alg"])
    if check is None:
        return False, f"Algoritma {envelope['alg']} belum didukung pemeriksa ini."
    body = {k: envelope[k] for k in ("version", "alg", "key_id", "issued_at", "payload")}
    message = canonical(body)
    if sha256_hex(message) != envelope["sha256"]:
        return False, "Isi sudah diubah: hash tidak cocok."
    try:
        signature = base64.b64decode(str(envelope["signature_b64"]), validate=True)
        ok = check(public_key_pem, message, signature)
    except (ValueError, TypeError):
        return False, "Tanda tangan rusak atau kunci publik tidak valid."
    if not ok:
        return False, "Tanda tangan tidak cocok dengan kunci publik satuan ini."
    return True, "Tanda tangan sah dan isi belum diubah."


# ---------- PNG ----------

def pixel_hash(png_bytes: bytes) -> str:
    """Hash piksel hasil dekode (bukan byte berkas), supaya tetap cocok walau chunk teks ditambah."""
    from PIL import Image

    with Image.open(io.BytesIO(png_bytes)) as img:
        rgb = img.convert("RGB")
        return sha256_hex(f"{rgb.width}x{rgb.height}".encode() + rgb.tobytes())


def embed_png_signature(png_bytes: bytes, envelope: dict) -> bytes:
    """Sematkan amplop ke chunk tEXt `halio-sig-v1`. Hasilnya tetap PNG biasa yang dibuka semua aplikasi."""
    from PIL import Image, PngImagePlugin

    info = PngImagePlugin.PngInfo()
    info.add_text(PNG_KEY, canonical(envelope).decode("utf-8"))
    out = io.BytesIO()
    with Image.open(io.BytesIO(png_bytes)) as img:
        img.save(out, format="PNG", optimize=True, pnginfo=info)
    return out.getvalue()


def extract_png_signature(png_bytes: bytes) -> dict | None:
    from PIL import Image

    try:
        with Image.open(io.BytesIO(png_bytes)) as img:
            raw = (getattr(img, "text", None) or img.info).get(PNG_KEY)
    except Exception:
        return None
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except ValueError:
        return None
    return data if isinstance(data, dict) else None
