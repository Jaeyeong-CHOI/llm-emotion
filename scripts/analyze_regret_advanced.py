#!/usr/bin/env python3
"""
Advanced regret marker analysis.
Layer 1: Regex/lexicon (existing proxy)
Layer 2: LIWC-style wordlist alignment (negemo, sad, anx categories)
Layer 3: Semantic embedding cosine similarity to prototype regret narratives

This extends analyze_regret_markers.py with publishable measurement validity.
"""

import argparse
import json
import math
import pathlib
import re
from collections import defaultdict

# ── Layer 1: existing markers ──────────────────────────────────────────────
COUNTERFACTUAL_PATTERNS = [
    r"\bif only\b", r"\bcould have\b", r"\bhad i\b",
    r"\bshould have\b", r"\btoo late\b", r"\bwould have\b",
    r"\bwish i had\b", r"\bif i had\b",
]
REGRET_WORDS = {
    "regret", "miss", "missed", "lost", "wish", "sorry", "late",
    "mistake", "wrong", "failed", "failure", "blame", "fault",
}

# ── Layer 2: LIWC-proxy wordlists (open approximation) ───────────────────
LIWC_NEGEMO = {
    "abandon", "ache", "aching", "afraid", "agony", "alone", "anger",
    "anxious", "awful", "bad", "bitter", "blame", "broken", "burden",
    "cry", "dark", "dead", "depressed", "despair", "disappointed",
    "dread", "embarrass", "empty", "fail", "fear", "frustrate",
    "grief", "guilt", "hate", "helpless", "hopeless", "hurt",
    "lonely", "loss", "lost", "mad", "miserable", "miss", "mourn",
    "pain", "panic", "rage", "regret", "reject", "sad", "shame",
    "shock", "sorrow", "stress", "suffer", "terrible", "tragic",
    "upset", "weep", "worry", "worthless", "wrong",
}
LIWC_SAD = {
    "alone", "cry", "depressed", "despair", "grief", "hopeless",
    "lonely", "mourn", "sad", "sorrow", "tears", "unhappy", "weep",
}
LIWC_ANX = {
    "afraid", "anxious", "apprehensive", "dread", "fearful", "nervous",
    "panic", "scared", "tense", "terror", "uneasy", "worried", "worry",
}

# ── Layer 3: prototype narratives for cosine similarity ──────────────────
# We compute TF-IDF-style bag-of-words similarity to a prototype
PROTOTYPE_REGRET_TOKENS = {
    "regret", "wish", "could", "have", "if", "only", "back", "again",
    "mistake", "wrong", "missed", "opportunity", "lost", "different",
    "chosen", "late", "blame", "fault", "should", "would",
}

PROTOTYPE_NEUTRAL_TOKENS = {
    "today", "morning", "work", "meeting", "coffee", "walk", "home",
    "evening", "task", "list", "finished", "started", "checked",
}


def count_counterfactuals(text: str) -> int:
    t = text.lower()
    return sum(len(re.findall(p, t)) for p in COUNTERFACTUAL_PATTERNS)


def count_regret_words(text: str) -> int:
    tokens = set(re.findall(r"\b[a-z']+\b", text.lower()))
    return len(tokens & REGRET_WORDS)


def count_negemo(text: str) -> int:
    tokens = re.findall(r"\b[a-z']+\b", text.lower())
    return sum(1 for t in tokens if t in LIWC_NEGEMO)


def count_sad(text: str) -> int:
    tokens = re.findall(r"\b[a-z']+\b", text.lower())
    return sum(1 for t in tokens if t in LIWC_SAD)


def count_anx(text: str) -> int:
    tokens = re.findall(r"\b[a-z']+\b", text.lower())
    return sum(1 for t in tokens if t in LIWC_ANX)


def cosine_similarity_to_prototype(text: str, prototype: set) -> float:
    """Bag-of-words cosine similarity between text and prototype token set."""
    tokens = re.findall(r"\b[a-z']+\b", text.lower())
    if not tokens:
        return 0.0
    text_set = set(tokens)
    overlap = len(text_set & prototype)
    if overlap == 0:
        return 0.0
    cos = overlap / (math.sqrt(len(text_set)) * math.sqrt(len(prototype)))
    return round(cos, 6)


def analyze_text(text: str) -> dict:
    n_tokens = max(1, len(re.findall(r"\b[a-z']+\b", text.lower())))
    cf = count_counterfactuals(text)
    rw = count_regret_words(text)
    ne = count_negemo(text)
    sd = count_sad(text)
    ax = count_anx(text)
    sim_regret = cosine_similarity_to_prototype(text, PROTOTYPE_REGRET_TOKENS)
    sim_neutral = cosine_similarity_to_prototype(text, PROTOTYPE_NEUTRAL_TOKENS)
    regret_bias = round(sim_regret - sim_neutral, 6)
    return {
        "counterfactual_count": cf,
        "regret_word_count": rw,
        "negemo_count": ne,
        "sad_count": sd,
        "anx_count": ax,
        "token_count": n_tokens,
        "counterfactual_rate": round(cf / n_tokens, 6),
        "regret_word_rate": round(rw / n_tokens, 6),
        "negemo_rate": round(ne / n_tokens, 6),
        "sad_rate": round(sd / n_tokens, 6),
        "anx_rate": round(ax / n_tokens, 6),
        "semantic_regret_sim": sim_regret,
        "semantic_neutral_sim": sim_neutral,
        "semantic_regret_bias": regret_bias,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True, help="input JSONL dataset")
    ap.add_argument("--out", required=True, help="output metrics JSON")
    ap.add_argument("--per-sample-out", default="", help="optional per-sample JSONL")
    args = ap.parse_args()

    rows = []
    with open(args.inp, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))

    per_sample = []
    grouped: dict = defaultdict(lambda: defaultdict(float))
    grouped_n: dict = defaultdict(int)

    for r in rows:
        key = (
            r.get("scenario", r.get("scenario_id", "unknown")),
            r.get("persona", "none"),
            str(r.get("temperature", 0.0)),
        )
        m = analyze_text(r.get("output", ""))
        n = grouped_n[key]
        for k, v in m.items():
            grouped[key][k] += v
        grouped_n[key] += 1

        if args.per_sample_out:
            per_sample.append({
                "id": r.get("id"),
                "scenario": r.get("scenario", r.get("scenario_id")),
                "persona": r.get("persona"),
                "temperature": r.get("temperature"),
                "prompt_bank_version": r.get("prompt_bank_version"),
                **m,
            })

    summary = []
    for key, totals in sorted(grouped.items()):
        n = max(1, grouped_n[key])
        entry = {
            "scenario": key[0],
            "persona": key[1],
            "temperature": float(key[2]),
            "n": n,
        }
        for metric, total in totals.items():
            if metric == "token_count":
                entry[f"{metric}_mean"] = round(total / n, 2)
            else:
                entry[f"{metric}_per_sample"] = round(total / n, 6)
        # legacy compat
        entry["counterfactual_per_sample"] = entry.get("counterfactual_count_per_sample", 0.0)
        entry["regret_words_per_sample"] = entry.get("regret_word_count_per_sample", 0.0)
        summary.append(entry)

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(summary)} condition cells to {out}")

    if args.per_sample_out and per_sample:
        ps_path = pathlib.Path(args.per_sample_out)
        ps_path.parent.mkdir(parents=True, exist_ok=True)
        with ps_path.open("w", encoding="utf-8") as f:
            for row in per_sample:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"Wrote {len(per_sample)} per-sample rows to {ps_path}")


if __name__ == "__main__":
    main()
