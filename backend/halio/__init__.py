"""Halio: asisten cek pesan untuk keluarga Indonesia."""
import os

__version__ = "0.2.0"
# Set by deploy/deploy_gce.sh (git short hash + date) so a chat can show exactly which build answers it.
BUILD = os.getenv("HALIO_BUILD", "lokal")


def version_line() -> str:
    return f"Halio v{__version__} ({BUILD})"
