"""Shared test setup: keep every test offline and independent of the machine's HALIO_ENGINE."""

import os

# semua unit test wajib jalan offline tanpa nyentuh internet. kunci default ke engine v1 dulu;
# tes yg nguji v2 bakal ngisi evidence_engine="v2" sendiri + suntik mock biar ga tergantung env mesin.
os.environ["HALIO_ENGINE"] = "v1"
