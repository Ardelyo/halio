"""Pemeriksa keaslian: Kartu Halio PNG atau berkas laporan JSON (LAPSUS, dossier).

    python -m halio.verify kartu.png            # exit 0 = SAH, exit 1 = TIDAK SAH / DIMODIFIKASI
    python -m halio.verify lapsus.json --pubkey kunci_publik.pem

Tanpa --pubkey dipakai kunci satuan lokal (halio.crypto_sign.get_signer).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import crypto_sign


def verify_bytes(data: bytes, public_key_pem: str, filename: str = "") -> dict:
    """Kembalikan {sah, alasan, jenis, ringkasan}. PNG dikenali dari tanda tangan PNG-nya, selain itu dianggap JSON."""
    is_png = data[:8] == b"\x89PNG\r\n\x1a\n"
    if is_png:
        envelope = crypto_sign.extract_png_signature(data)
        if envelope is None:
            try:
                crypto_sign.pixel_hash(data)
            except Exception:
                return {"sah": False, "jenis": "png", "alasan": "Berkas PNG rusak atau sudah diubah: gambar tidak bisa dibaca utuh.", "ringkasan": None}
            return {"sah": False, "jenis": "png", "alasan": "Gambar ini tidak membawa tanda tangan Halio (mungkin dikirim ulang lewat aplikasi yang menghapus metadata, atau bukan Kartu Halio).", "ringkasan": None}
    else:
        try:
            envelope = json.loads(data.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return {"sah": False, "jenis": "tidak_dikenal", "alasan": "Berkas bukan PNG Kartu Halio maupun JSON laporan yang terbaca.", "ringkasan": None}
    ok, reason = crypto_sign.verify_payload(envelope, public_key_pem)
    payload = envelope.get("payload") if isinstance(envelope, dict) and isinstance(envelope.get("payload"), dict) else {}
    if ok and is_png:
        try:
            same = crypto_sign.pixel_hash(data) == payload.get("pixels_sha256")
        except Exception:
            same = False
        if not same:
            ok, reason = False, "Isi gambar sudah diubah: hash piksel tidak cocok dengan yang ditandatangani."
    summary = None
    if ok:
        summary = {k: payload.get(k) for k in ("kind", "status", "claim", "verif_id", "created", "period") if payload.get(k) is not None}
        summary["key_id"] = envelope.get("key_id")
        summary["issued_at"] = envelope.get("issued_at")
    return {"sah": ok, "jenis": "png" if is_png else "json", "alasan": reason, "ringkasan": summary}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="halio.verify", description="Periksa keaslian Kartu Halio PNG atau laporan JSON.")
    ap.add_argument("path")
    ap.add_argument("--pubkey", help="berkas PEM kunci publik satuan (default: kunci lokal)")
    args = ap.parse_args(argv)
    path = Path(args.path)
    if not path.is_file():
        print(f"TIDAK SAH: berkas tidak ditemukan: {path}")
        return 1
    pem = Path(args.pubkey).read_text(encoding="ascii") if args.pubkey else crypto_sign.get_signer().public_pem
    res = verify_bytes(path.read_bytes(), pem, path.name)
    print(("SAH" if res["sah"] else "TIDAK SAH / DIMODIFIKASI") + f": {res['alasan']}")
    if res["ringkasan"]:
        print(json.dumps(res["ringkasan"], ensure_ascii=False, indent=1))
    return 0 if res["sah"] else 1


if __name__ == "__main__":
    sys.exit(main())
