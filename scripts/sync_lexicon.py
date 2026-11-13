"""Generate extension/lexicon_data.js from the Python rules, so the extension and server never drift.

    python scripts/sync_lexicon.py           # write
    python scripts/sync_lexicon.py --check   # exit 1 if the file is stale (used by the tests)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from halio import manipulation, pii  # noqa: E402

# file js hasil generate buat ekstensi biar ga usah nulis ulang pola regex dua kali
OUT = ROOT / "extension" / "lexicon_data.js"


def render() -> str:
    # kumpulin pola teknik manipulasi, kata kunci judol, sm aturan sensor data pribadi dr backend
    data = {
        "techniques": [[t.id, t.label, list(t.patterns)] for t in manipulation.TECHNIQUES],
        "judolStrong": list(manipulation.JUDOL_STRONG),
        "judolWeak": list(manipulation.JUDOL_WEAK),
        # urutannya wajib persis kaya pii.scrub(): sikat URL dulu, link tanpa skema, baru nomor/identitas pribadi
        "scrub": [[pii._URL.pattern, "gi", "[TAUTAN]"], [pii._BARE_WITH_PATH.pattern, "gi", "[TAUTAN]"]]
                 + [[p.pattern, "g", repl] for p, repl in pii._PATTERNS],
        "maxClaimChars": pii.MAX_CLAIM_CHARS,
    }
    body = json.dumps(data, ensure_ascii=False, indent=1)
    return ("// file ini digenerate otomatis lewat scripts/sync_lexicon.py dr manipulation.py & pii.py — jgn diedit manual ya\n"
            f"globalThis.HalioLexiconData = {body};\n")


def main() -> None:
    text = render()
    # mode --check dipake di test/CI buat mastiin file js ekstensi ga ketinggalan update
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            raise SystemExit("extension/lexicon_data.js is stale: run python scripts/sync_lexicon.py")
        return
    # timpa langsung file target pake encoding utf-8
    OUT.write_text(text, encoding="utf-8")
    print("wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
