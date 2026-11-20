"""Tanda tangani registri buletin resmi (data/official_bulletins.json) dengan kunci Ed25519 satuan.

    python scripts/sign_bulletins.py            # tulis ulang tanda tangan + data/registry_pubkey.pem
    python scripts/sign_bulletins.py --check    # exit 1 kalau tanda tangan di berkas tidak sah

Kunci privat TIDAK pernah masuk repo: dibaca dari HALIO_SIGN_KEY / HALIO_SIGN_KEY_FILE / ~/.halio/signing_key.pem
(lihat backend/halio/crypto_sign.py). Kunci publiknya (data/registry_pubkey.pem) adalah jangkar kepercayaan: satuan lain yang
memakai registri ini mengganti berkas itu dengan kunci publiknya sendiri, lalu menandatangani ulang buletin yang ia percaya.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from halio import crypto_sign, retrieval  # noqa: E402

DATA = ROOT / "data"
REG = DATA / retrieval.REGISTRY_FILE
PUB = DATA / retrieval.REGISTRY_PUBKEY


def main() -> int:
    raw = json.loads(REG.read_text(encoding="utf-8"))
    if "--check" in sys.argv:
        ok = len(retrieval.load_registry(DATA)) == len(raw["bulletins"]) > 0
        print("registri buletin: tanda tangan SAH" if ok else "registri buletin: TIDAK SAH")
        return 0 if ok else 1
    signer = crypto_sign.get_signer()
    raw["signature"] = crypto_sign.sign_payload(retrieval.registry_payload(raw["bulletins"]), signer)
    REG.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n")
    PUB.write_text(signer.public_pem, encoding="ascii", newline="\n")
    print(f"ditandatangani {len(raw['bulletins'])} buletin, key_id={signer.key_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
