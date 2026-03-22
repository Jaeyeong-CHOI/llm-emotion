#!/usr/bin/env python3
import argparse, json, pathlib, re
from collections import defaultdict

COUNTERFACTUAL_PATTERNS = [r"if only", r"could have", r"had i", r"should have", r"too late"]
REGRET_WORDS = {"regret", "miss", "lost", "wish", "sorry", "late"}


def count_counterfactuals(text: str) -> int:
    t = text.lower()
    return sum(len(re.findall(p, t)) for p in COUNTERFACTUAL_PATTERNS)


def count_regret_words(text: str) -> int:
    tokens = re.findall(r"[a-z']+", text.lower())
    return sum(1 for tok in tokens if tok in REGRET_WORDS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rows = []
    with open(args.inp, "r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))

    grouped = defaultdict(lambda: {"n": 0, "counterfactual": 0, "regret_words": 0})

    for r in rows:
        key = (r["scenario"], r["persona"], str(r["temperature"]))
        grouped[key]["n"] += 1
        grouped[key]["counterfactual"] += count_counterfactuals(r["output"])
        grouped[key]["regret_words"] += count_regret_words(r["output"])

    summary = []
    for key, v in sorted(grouped.items()):
        n = max(1, v["n"])
        summary.append({
            "scenario": key[0],
            "persona": key[1],
            "temperature": float(key[2]),
            "n": v["n"],
            "counterfactual_per_sample": v["counterfactual"] / n,
            "regret_words_per_sample": v["regret_words"] / n,
        })

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote summary to {out}")


if __name__ == "__main__":
    main()
