#!/usr/bin/env python3
"""
Minimal-pair ablation runner.
For each pair, runs all 3 framing conditions (N/D/C) with identical topic.
Outputs: results/real_experiments/ablation_minimal_pairs_v1.jsonl
"""
from __future__ import annotations
import argparse, json, os, pathlib, random, sys, time

ROOT = pathlib.Path(__file__).resolve().parents[1]
STIMULI = ROOT / "prompts" / "ablation_minimal_pairs_v1.json"
OUT_DEFAULT = ROOT / "results" / "real_experiments" / "ablation_minimal_pairs_v1.jsonl"

CONDITIONS = ["neutral", "deprivation", "counterfactual"]


def call_openai(prompt: str, temperature: float, model: str, api_key: str) -> str:
    import urllib.request
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 400,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=data,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=40) as r:
        resp = json.loads(r.read())
    return resp["choices"][0]["message"]["content"].strip()


def call_gemini(prompt: str, temperature: float, api_key: str) -> str:
    import urllib.request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": 600},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.loads(r.read())
    return resp["candidates"][0]["content"]["parts"][0]["text"].strip()


def score_markers(text: str) -> dict:
    """Simple marker scoring (matches main experiment logic)."""
    import re
    text_lower = text.lower()
    t_len = max(len(text), 1)

    # Counterfactual markers
    cf_patterns = ["만약", "했다면", "했더라면", "이었다면", "다면", "았다면", "었다면",
                   "could have", "would have", "should have", "if only", "what if", "had i"]
    cf_count = sum(text_lower.count(p) for p in cf_patterns)
    cf_rate = cf_count / (t_len / 100)

    # Regret word markers
    regret_words = ["후회", "아쉽", "아쉬움", "미안", "죄송", "실수", "잘못", "안타깝", "惜",
                    "regret", "sorry", "mistake", "wrong", "wish i", "should have"]
    rw_count = sum(text_lower.count(w) for w in regret_words)
    rw_rate = rw_count / (t_len / 100)

    # Negative emotion markers
    neg_words = ["슬프", "힘들", "괴롭", "고통", "외롭", "우울", "불안", "두렵", "실망",
                 "sad", "pain", "suffer", "lonely", "depress", "anxious", "disappoint"]
    neg_count = sum(text_lower.count(w) for w in neg_words)
    neg_rate = neg_count / (t_len / 100)

    # Semantic regret bias (simplified: sum of CF + regret markers)
    semantic_bias = (cf_count + rw_count * 2) / (t_len / 100)

    return {
        "cf_rate": round(cf_rate, 4),
        "regret_word_rate": round(rw_rate, 4),
        "neg_emotion_rate": round(neg_rate, 4),
        "semantic_regret_bias": round(semantic_bias, 4),
        "response_length": t_len,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(OUT_DEFAULT))
    ap.add_argument("--n", type=int, default=10, help="samples per cell")
    ap.add_argument("--provider", default="both", choices=["openai", "gemini", "both"])
    ap.add_argument("--temperature", type=float, default=0.7)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--seed", type=int, default=99)
    args = ap.parse_args()

    random.seed(args.seed)
    stimuli = json.loads(STIMULI.read_text(encoding="utf-8"))
    openai_key = os.getenv("OPENAI_API_KEY", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    out_path = pathlib.Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    models = []
    if args.provider in ("openai", "both"):
        if not args.dry_run and not openai_key:
            print("ERROR: OPENAI_API_KEY not set", file=sys.stderr); sys.exit(1)
        models.append(("openai", "gpt-4o"))
    if args.provider in ("gemini", "both"):
        if not args.dry_run and not gemini_key:
            print("ERROR: GEMINI_API_KEY not set", file=sys.stderr); sys.exit(1)
        models.append(("gemini", "gemini-2.5-flash"))

    pairs = stimuli["pairs"]
    total = len(pairs) * len(CONDITIONS) * len(models) * args.n
    print(f"Plan: {len(pairs)} pairs × {len(CONDITIONS)} conditions × {len(models)} models × {args.n} samples = {total} API calls")
    if args.dry_run:
        print("DRY RUN — no API calls"); return

    results = []
    done = 0
    for pair in pairs:
        for cond in CONDITIONS:
            prompt_text = pair[cond]
            for provider, model_name in models:
                for i in range(args.n):
                    try:
                        if provider == "openai":
                            response = call_openai(prompt_text, args.temperature, "gpt-4o", openai_key)
                        else:
                            response = call_gemini(prompt_text, args.temperature, gemini_key)
                        markers = score_markers(response)
                        rec = {
                            "pair_id": pair["pair_id"],
                            "topic": pair["topic"],
                            "condition": cond,
                            "provider": provider,
                            "model": model_name,
                            "sample_idx": i,
                            "prompt": prompt_text,
                            "response": response,
                            **markers,
                        }
                        results.append(rec)
                        with open(out_path, "a", encoding="utf-8") as f:
                            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                        done += 1
                        if done % 10 == 0:
                            print(f"  [{done}/{total}] {pair['pair_id']} | {cond} | {provider}")
                        time.sleep(0.3)
                    except Exception as e:
                        print(f"ERROR: {pair['pair_id']} {cond} {provider} sample {i}: {e}", file=sys.stderr)
                        time.sleep(2)

    print(f"\nDone: {done}/{total} samples written to {out_path}")

    # Quick summary
    from collections import defaultdict
    import statistics
    by_cond = defaultdict(list)
    for r in results:
        by_cond[r["condition"]].append(r["semantic_regret_bias"])

    print("\n=== Ablation Quick Summary: semantic_regret_bias ===")
    for cond in CONDITIONS:
        vals = by_cond[cond]
        if vals:
            print(f"  {cond:15s}: M={statistics.mean(vals):.3f}  SD={statistics.stdev(vals) if len(vals)>1 else 0:.3f}  n={len(vals)}")


if __name__ == "__main__":
    main()
