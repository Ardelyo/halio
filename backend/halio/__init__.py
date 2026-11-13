"""Halio: asisten cek pesan untuk keluarga Indonesia."""
import os

__version__ = "0.2.0"
# diisi pas deploy lewat deploy_gce.sh (hash pendek + tanggal) biar ketauan build mana yg lagi bales chat
BUILD = os.getenv("HALIO_BUILD", "lokal")


# teks versi ringkas buat ditampilin di tampilan web atau balasan bot
def version_line() -> str:
    return f"Halio v{__version__} ({BUILD})"
