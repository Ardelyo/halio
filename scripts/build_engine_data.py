"""Generate web/engine/data.js dari kode Python + data/debunks.json, biar mesin luring di browser ga ngulang daftar manual.

    python scripts/build_engine_data.py           # tulis
    python scripts/build_engine_data.py --check   # exit 1 kalo file-nya basi (dipake tes & CI)

Sumber kebenaran tetap Python: korpus, kosakata, pola regex, dan ambang. Logika vonisnya ditulis ulang di
web/engine/halio-local.js dan dijaga sama persis lewat uji paritas (backend/tests/parity_vectors.json).
"""

from __future__ import annotations

import hashlib
import json
import sys
from dataclasses import fields
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from halio import attribution, claims, manipulation, pii, pipeline, retrieval, textnorm  # noqa: E402
from halio.config import Settings  # noqa: E402

OUT = ROOT / "web" / "engine" / "data.js"
CORPUS = ROOT / "data" / "debunks.json"


def build() -> dict:
    raw = CORPUS.read_bytes()
    corpus = json.loads(raw.decode("utf-8"))
    keep = [f.name for f in fields(retrieval.Debunk)]
    cfg = Settings()
    return {
        "version": "luring-1",
        "corpusSha256": hashlib.sha256(raw).hexdigest(),
        "thresholds": {"match": cfg.match_threshold, "unsure": cfg.unsure_threshold},
        "corpus": [{k: d[k] for k in keep if k in d} for d in corpus["debunks"]],
        "slang": textnorm.SLANG,
        "stopwords": sorted(textnorm.STOPWORDS),
        "claimCues": sorted(claims.CLAIM_CUES),
        "opinionCues": list(claims.OPINION_CUES),
        "regex": {
            "negation": retrieval._NEGATION.pattern,
            "defused": retrieval._DEFUSED.pattern,
            "correction": retrieval._CORRECTION.pattern,
            "notCorrection": retrieval._NOT_A_CORRECTION.pattern,
            "pipelineUrl": pipeline._URL.pattern,
            "url": pii._URL.pattern,
            "bare": pii._BARE.pattern,
            "bareWithPath": pii._BARE_WITH_PATH.pattern,
        },
        "scrub": [[p.pattern, repl] for p, repl in pii._PATTERNS],
        "techniques": [[t.id, t.label, t.explain, t.lesson, list(t.patterns)] for t in manipulation.TECHNIQUES],
        "orgs": attribution.ORGS,
        "statusLabel": pipeline.STATUS_LABEL,
        "severity": pipeline._SEVERITY,
        "short": pipeline._SHORT,
        "plainKinds": sorted(pipeline.PLAIN_KINDS),
        "shorteners": sorted(pipeline.SHORTENERS),
        "officialSuffixes": list(pipeline.OFFICIAL_SUFFIXES),
        "disclaimer": pipeline.DISCLAIMER,
    }


def render() -> str:
    body = json.dumps(build(), ensure_ascii=False, indent=1, sort_keys=False)
    return (
        "// file ini digenerate otomatis lewat scripts/build_engine_data.py dr kode python + data/debunks.json, jgn diedit manual ya\n"
        f"globalThis.HalioEngineData = {body};\n"
    )


def main() -> int:
    text = render()
    if "--check" in sys.argv:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != text:
            print("web/engine/data.js basi: jalankan python scripts/build_engine_data.py")
            return 1
        print("web/engine/data.js up to date")
        return 0
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(text, encoding="utf-8", newline="\n")
    print(f"ditulis {OUT.relative_to(ROOT)} ({len(text)} byte)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
