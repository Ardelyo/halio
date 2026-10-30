"""Honest offline evaluation of the check pipeline.

    python eval/run_eval.py            # prints metrics, writes eval/RESULTS.md
    python eval/run_eval.py --sweep    # threshold sweep to recalibrate config

The metric that matters most is the FALSE-HOAX rate: how often Halio labels a
true or unknown statement "terbukti salah". One wrong label on a sensitive
topic destroys trust, so thresholds are chosen to keep it at zero first.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from halio import pipeline  # noqa: E402
from halio.config import Settings  # noqa: E402


SETS = {
    "dev": ("testset.jsonl", "tuning set: the rules were adjusted while looking at these"),
    "holdout": ("holdout.jsonl", "held-out set: written before the guard fix and never tuned on"),
}


def load(name: str = "dev") -> list[dict]:
    path = ROOT / "eval" / SETS[name][0]
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def evaluate(cfg: Settings, items: list[dict]) -> dict:
    rows, tp, fn, wrong_id, false_hoax, abstain_ok, opinion_ok = [], 0, 0, 0, 0, 0, 0
    pos = [i for i in items if i["expect"] == "terbukti_salah"]
    neg = [i for i in items if i["expect"] == "not_debunked"]
    opi = [i for i in items if i["expect"] == "opinion"]
    for item in items:
        r = pipeline.check(item["text"], cfg)
        got_id = (r["match"] or {}).get("debunk_id")
        score = (r["match"] or {}).get("score")
        ok = False
        if item["expect"] == "terbukti_salah":
            if r["status"] == "terbukti_salah" and got_id == item["debunk"]:
                tp += 1; ok = True
            elif r["status"] == "terbukti_salah":
                wrong_id += 1
            else:
                fn += 1
        elif item["expect"] == "not_debunked":
            if r["status"] == "terbukti_salah":
                false_hoax += 1
            else:
                abstain_ok += 1; ok = True
        else:
            if r["reason"] == "bukan_klaim_faktual":
                opinion_ok += 1; ok = True
        rows.append((ok, item["expect"], r["status"], r["reason"], score, item["text"][:70]))
    return {
        "n": len(items),
        "recall_known_hoax": tp / max(1, len(pos)),
        "wrong_debunk": wrong_id,
        "false_hoax_rate": false_hoax / max(1, len(neg)),
        "false_hoax": false_hoax,
        "abstain_correct": abstain_ok / max(1, len(neg)),
        "opinion_detect": opinion_ok / max(1, len(opi)),
        "counts": {"positives": len(pos), "negatives": len(neg), "opinions": len(opi)},
        "rows": rows,
    }


def report(cfg: Settings, m: dict, name: str) -> str:
    lines = [
        f"## {name}: {SETS[name][0]}",
        "",
        f"{SETS[name][1].capitalize()}. {m['n']} hand-written items ({m['counts']['positives']} paraphrases of known debunks, "
        f"{m['counts']['negatives']} true/unknown statements, {m['counts']['opinions']} opinions/greetings). "
        "Written by the team, so results are optimistic. Not a benchmark.",
        "",
        f"Thresholds: match >= {cfg.match_threshold}, unsure >= {cfg.unsure_threshold}. Mode: retrieval only (no LLM, no ClaimReview).",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| False-hoax rate (true/unknown labelled 'terbukti salah') | **{m['false_hoax_rate']:.0%}** ({m['false_hoax']}/{m['counts']['negatives']}) |",
        f"| Recall on paraphrased known hoaxes | {m['recall_known_hoax']:.0%} |",
        f"| Matched the wrong debunk | {m['wrong_debunk']} |",
        f"| Correct abstain on true/unknown | {m['abstain_correct']:.0%} |",
        f"| Opinion/greeting detected | {m['opinion_detect']:.0%} |",
        "",
        "### Per item",
        "",
        "| ok | expected | status | reason | score | text |",
        "|---|---|---|---|---|---|",
    ]
    for ok, exp, st, reason, score, text in m["rows"]:
        lines.append(f"| {'✅' if ok else '❌'} | {exp} | {st} | {reason} | {score if score is not None else '-'} | {text} |")
    return "\n".join(lines) + "\n"


HEADER = """# Halio offline evaluation

Two hand-written sets, both by the team, so neither is a benchmark. The number to watch is the
false-hoax rate: a true statement labelled "terbukti salah". Retrieval only (no LLM, no ClaimReview).

"""

HISTORY = """## History (honest record)

| When | dev false-hoax | holdout false-hoax | holdout recall |
|---|---|---|---|
| Before the guard fix (audit, Oct 2026) | 6/32 | 5/34 | 81% |
| Guard fix, first holdout run | 0/32 | 1/34 | 88% |
| After adding "tidak ada bukti / tidak terbukti" as a correction cue | see above | see above | see above |

The last row was changed after looking at a holdout failure, so the holdout is no longer fully clean.
The next fresh set should be written by someone outside the team, from real forwarded messages.

"""

LIMITS = """## Known limitations

- Both sets were written by the same people who wrote the corpus. Real forwarded messages will be messier.
- Same-topic TRUE statements score close to the threshold; that is why the 'tidak yakin' band exists.
- Retrieval is lexical; heavy paraphrase without shared words is missed (falls to 'belum ada pemeriksaan', which is safe).
- The T2 LLM step (HALIO_LLM=1) is not measured here. It can confirm or downgrade, and may lift a
  'mirip' case only when the core-claim guard and the correction check both pass, with an exact quote.
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sweep", action="store_true")
    args = ap.parse_args()
    base = Settings(google_factcheck_key=None, llm_enabled=False)

    if args.sweep:
        print("match  unsure  recall  false_hoax  abstain_ok")
        for mt in [x / 100 for x in range(30, 61, 2)]:
            for ut in (0.20, 0.24, 0.28):
                m = evaluate(replace(base, match_threshold=mt, unsure_threshold=ut), load("dev"))
                print(f"{mt:.2f}   {ut:.2f}    {m['recall_known_hoax']:.2f}    {m['false_hoax_rate']:.2f}        {m['abstain_correct']:.2f}")
        return

    parts, summary = [], []
    for name in SETS:
        m = evaluate(base, load(name))
        parts.append(report(base, m, name))
        summary.append(f"{name:<8} false-hoax {m['false_hoax']}/{m['counts']['negatives']}  recall {m['recall_known_hoax']:.0%}  "
                       f"wrong-debunk {m['wrong_debunk']}  opinion {m['opinion_detect']:.0%}")
    (ROOT / "eval" / "RESULTS.md").write_text(HEADER + "\n".join(parts) + "\n" + HISTORY + LIMITS, encoding="utf-8")
    print("\n".join(summary))


if __name__ == "__main__":
    main()
