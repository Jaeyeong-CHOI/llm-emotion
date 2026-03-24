#!/usr/bin/env python3
"""
Analyze real experiment data (bilingual: Korean + English).
Reports condition-level markers with Korean NLP support.
"""

import json
import pathlib
import re
import statistics
from collections import defaultdict

ROOT = pathlib.Path(__file__).resolve().parents[1]

# English markers
CF_PATTERNS_EN = [
    r"\bif only\b", r"\bcould have\b", r"\bhad i\b", r"\bshould have\b",
    r"\btoo late\b", r"\bwould have\b", r"\bwish i had\b", r"\bif i had\b",
]
REGRET_EN = {"regret", "miss", "missed", "lost", "wish", "sorry", "mistake",
             "wrong", "failed", "failure", "blame", "fault"}
SAD_EN = {"alone", "cry", "depressed", "despair", "grief", "hopeless",
          "lonely", "mourn", "sad", "sorrow", "weep"}
NEGEMO_EN = {"afraid", "anxious", "awful", "bad", "bitter", "broken", "burden",
             "dread", "empty", "fail", "fear", "guilt", "hate", "helpless",
             "hopeless", "hurt", "lonely", "lost", "pain", "regret", "sad",
             "shame", "suffer", "terrible", "upset", "worry", "worthless"}

# Korean markers
CF_PATTERNS_KO = [
    r"다른\s*선택", r"했더라면", r"했을\s*텐데", r"다면\s*좋았을",
    r"돌아갈\s*수", r"다시\s*선택", r"그\s*때로\s*돌아", r"달랐을",
    r"바꿀\s*수", r"후회", r"아쉽", r"미련", r"했어야",
]
REGRET_KO = ["후회", "아쉽", "미련", "후회스럽", "유감", "죄책", "자책", "회한"]
SAD_KO = ["슬프", "눈물", "비통", "허전", "외롭", "고독", "우울", "절망", "공허"]
NEGEMO_KO = ["화가", "불안", "두렵", "걱정", "고통", "괴롭", "아프", "힘들", "무서"]

PROTOTYPE_REGRET = {"regret", "wish", "could", "have", "if", "only", "back",
                    "again", "mistake", "wrong", "missed", "opportunity", "lost",
                    "different", "chosen", "late", "blame", "fault", "should", "would"}
PROTOTYPE_NEUTRAL = {"today", "morning", "work", "meeting", "coffee", "walk",
                     "home", "evening", "task", "list", "finished", "started"}


def is_korean(text: str) -> bool:
    ko_chars = len(re.findall(r"[\uAC00-\uD7A3]", text))
    return ko_chars > len(text) * 0.1


def analyze(text: str) -> dict:
    ko = is_korean(text)
    if ko:
        cf = sum(len(re.findall(p, text)) for p in CF_PATTERNS_KO)
        rw = sum(1 for w in REGRET_KO if w in text)
        sd = sum(1 for w in SAD_KO if w in text)
        ne = sum(1 for w in NEGEMO_KO if w in text)
        n = max(1, len(text) // 3)  # rough Korean token estimate
    else:
        tokens_lower = re.findall(r"\b[a-z']+\b", text.lower())
        token_set = set(tokens_lower)
        cf = sum(len(re.findall(p, text.lower())) for p in CF_PATTERNS_EN)
        rw = len(token_set & REGRET_EN)
        sd = len(token_set & SAD_EN)
        ne = len(token_set & NEGEMO_EN)
        n = max(1, len(tokens_lower))

    # Semantic bias (prototype cosine, language-agnostic approximation)
    if ko:
        # Korean keyword presence as proxy
        regret_kw = sum(1 for w in REGRET_KO if w in text)
        neutral_kw = sum(1 for w in ["오늘", "아침", "회의", "업무", "커피", "퇴근"] if w in text)
        regret_sim = regret_kw / max(1, len(REGRET_KO))
        neutral_sim = neutral_kw / 6
    else:
        import math
        tokens = set(re.findall(r"\b[a-z']+\b", text.lower()))
        overlap_r = len(tokens & PROTOTYPE_REGRET)
        overlap_n = len(tokens & PROTOTYPE_NEUTRAL)
        regret_sim = overlap_r / (math.sqrt(len(tokens)) * math.sqrt(len(PROTOTYPE_REGRET))) if tokens else 0
        neutral_sim = overlap_n / (math.sqrt(len(tokens)) * math.sqrt(len(PROTOTYPE_NEUTRAL))) if tokens else 0

    return {
        "lang": "ko" if ko else "en",
        "n_tokens": n,
        "cf_count": cf,
        "regret_count": rw,
        "sad_count": sd,
        "negemo_count": ne,
        "cf_rate": round(cf / n * 100, 4),
        "regret_rate": round(rw / n * 100, 4),
        "negemo_rate": round(ne / n * 100, 4),
        "semantic_regret_sim": round(regret_sim, 5),
        "semantic_neutral_sim": round(neutral_sim, 5),
        "semantic_regret_bias": round(regret_sim - neutral_sim, 5),
    }


def load_jsonl(path: pathlib.Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out-summary", required=True)
    ap.add_argument("--out-report", default="")
    args = ap.parse_args()

    rows = load_jsonl(ROOT / args.inp)
    by_cond: dict = defaultdict(list)
    by_persona: dict = defaultdict(list)
    per_sample_results = []

    for r in rows:
        m = analyze(r.get("output", ""))
        m["condition"] = r.get("condition", "unknown")
        m["persona"] = r.get("persona", "none")
        m["temperature"] = r.get("temperature", 0.0)
        m["scenario_id"] = r.get("scenario_id", r.get("scenario", ""))
        m["model"] = r.get("model", "unknown")
        m["id"] = r.get("id")
        by_cond[m["condition"]].append(m)
        by_persona[m["persona"]].append(m)
        per_sample_results.append(m)

    # Condition-level summary
    def agg(group: list) -> dict:
        keys = ["cf_count", "regret_count", "sad_count", "negemo_count",
                "cf_rate", "regret_rate", "negemo_rate", "semantic_regret_bias"]
        return {k: round(statistics.mean(r[k] for r in group), 5) for k in keys}

    cond_summary = {c: {**agg(g), "n": len(g)} for c, g in by_cond.items()}
    persona_summary = {p: {**agg(g), "n": len(g)} for p, g in by_persona.items()}

    out = {
        "n_total": len(rows),
        "conditions": cond_summary,
        "personas": persona_summary,
        "per_sample": per_sample_results,
    }
    out_path = ROOT / args.out_summary
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Summary written to {out_path}")

    # Print readable report
    print("\n=== CONDITION-LEVEL RESULTS ===")
    print(f"{'Condition':<16} {'n':>4} {'CF/100c':>8} {'Regret/c':>9} {'NegEmo/c':>9} {'RegretBias':>12}")
    print("-" * 60)
    for cond in ["neutral", "deprivation", "counterfactual"]:
        if cond not in cond_summary:
            continue
        d = cond_summary[cond]
        print(f"{cond:<16} {d['n']:>4} {d['cf_rate']:>8.4f} {d['regret_rate']:>9.4f} {d['negemo_rate']:>9.4f} {d['semantic_regret_bias']:>12.5f}")

    print("\n=== PERSONA EFFECT ===")
    for p in ["none", "reflective", "ruminative"]:
        if p not in persona_summary:
            continue
        d = persona_summary[p]
        print(f"  {p:<14} CF={d['cf_rate']:.4f}  Regret={d['regret_rate']:.4f}  Bias={d['semantic_regret_bias']:.5f}")

    if args.out_report:
        rpt_path = ROOT / args.out_report
        lines = [
            "# Real Experiment v1 — Pilot Results (GPT-4o)\n",
            f"- N total samples: {len(rows)}\n",
            f"- Model: GPT-4o\n\n",
            "## Condition-level markers\n\n",
            "| Condition | N | CF/100c | Regret/c | NegEmo/c | RegretBias |\n",
            "|---|---|---|---|---|---|\n",
        ]
        for cond in ["neutral", "deprivation", "counterfactual"]:
            if cond not in cond_summary:
                continue
            d = cond_summary[cond]
            lines.append(f"| {cond} | {d['n']} | {d['cf_rate']:.4f} | {d['regret_rate']:.4f} | {d['negemo_rate']:.4f} | {d['semantic_regret_bias']:.5f} |\n")
        lines += [
            "\n## Persona effect\n\n",
            "| Persona | N | CF/100c | Regret/c | RegretBias |\n",
            "|---|---|---|---|---|\n",
        ]
        for p in ["none", "reflective", "ruminative"]:
            if p not in persona_summary:
                continue
            d = persona_summary[p]
            lines.append(f"| {p} | {d['n']} | {d['cf_rate']:.4f} | {d['regret_rate']:.4f} | {d['semantic_regret_bias']:.5f} |\n")
        rpt_path.write_text("".join(lines), encoding="utf-8")
        print(f"Report written to {rpt_path}")


if __name__ == "__main__":
    main()
