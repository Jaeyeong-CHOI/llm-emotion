#!/usr/bin/env python3
"""
Fill missing ablation cells (incremental, skip existing).
"""
from __future__ import annotations
import json, os, pathlib, sys, time
from collections import Counter

ROOT = pathlib.Path(__file__).resolve().parents[1]
STIMULI = ROOT / "prompts" / "ablation_minimal_pairs_v1.json"
OUT = ROOT / "results" / "real_experiments" / "ablation_minimal_pairs_v1.jsonl"

CONDITIONS = ["neutral", "deprivation", "counterfactual"]
N_PER_CELL = 10


def call_openai(prompt: str, api_key: str) -> str:
    import urllib.request
    payload = {"model": "gpt-4o", "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.7, "max_tokens": 400}
    data = json.dumps(payload).encode()
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=data,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=40) as r:
        resp = json.loads(r.read())
    return resp["choices"][0]["message"]["content"].strip()


def call_gemini(prompt: str, api_key: str) -> str:
    import urllib.request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {"contents": [{"parts": [{"text": prompt}]}],
               "generationConfig": {"temperature": 0.7, "maxOutputTokens": 600}}
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.loads(r.read())
    return resp["candidates"][0]["content"]["parts"][0]["text"].strip()


def score_markers(text: str) -> dict:
    text_lower = text.lower()
    t_len = max(len(text), 1)
    cf_patterns = ["만약", "했다면", "했더라면", "이었다면", "다면", "았다면", "었다면",
                   "could have", "would have", "should have", "if only", "what if", "had i"]
    cf_count = sum(text_lower.count(p) for p in cf_patterns)
    cf_rate = cf_count / (t_len / 100)
    regret_words = ["후회", "아쉽", "아쉬움", "미안", "죄송", "실수", "잘못", "안타깝",
                    "regret", "sorry", "mistake", "wrong", "wish i", "should have"]
    rw_count = sum(text_lower.count(w) for w in regret_words)
    rw_rate = rw_count / (t_len / 100)
    neg_words = ["슬프", "힘들", "괴롭", "고통", "외롭", "우울", "불안", "두렵", "실망",
                 "sad", "pain", "suffer", "lonely", "depress", "anxious", "disappoint"]
    neg_count = sum(text_lower.count(w) for w in neg_words)
    neg_rate = neg_count / (t_len / 100)
    semantic_bias = (cf_count + rw_count * 2) / (t_len / 100)
    return {"cf_rate": round(cf_rate, 4), "regret_word_rate": round(rw_rate, 4),
            "neg_emotion_rate": round(neg_rate, 4), "semantic_regret_bias": round(semantic_bias, 4),
            "response_length": t_len}


def main():
    openai_key = os.getenv("OPENAI_API_KEY", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    stimuli = json.loads(STIMULI.read_text(encoding="utf-8"))
    pairs = stimuli["pairs"]

    # Load existing
    existing = Counter()
    existing_by_cell = {}
    if OUT.exists():
        for line in OUT.read_text(encoding="utf-8").splitlines():
            if not line.strip(): continue
            d = json.loads(line)
            key = (d["pair_id"], d["condition"], d["provider"])
            existing[key] += 1

    # Figure out what to run
    tasks = []
    for pair in pairs:
        for cond in CONDITIONS:
            for provider in ["openai", "gemini"]:
                key = (pair["pair_id"], cond, provider)
                have = existing[key]
                need = max(0, N_PER_CELL - have)
                if need > 0:
                    tasks.append((pair, cond, provider, have, need))

    total_calls = sum(t[4] for t in tasks)
    print(f"Need to run {total_calls} API calls across {len(tasks)} cells")

    done = 0
    for pair, cond, provider, have, need in tasks:
        prompt_text = pair[cond]
        print(f"\n[{pair['pair_id']} | {cond} | {provider}] have={have}, need={need}")
        for i in range(need):
            sample_idx = have + i
            try:
                if provider == "openai":
                    response = call_openai(prompt_text, openai_key)
                else:
                    response = call_gemini(prompt_text, gemini_key)
                markers = score_markers(response)
                rec = {"pair_id": pair["pair_id"], "topic": pair["topic"],
                       "condition": cond, "provider": provider,
                       "model": "gpt-4o" if provider=="openai" else "gemini-2.5-flash",
                       "sample_idx": sample_idx, "prompt": prompt_text,
                       "response": response[:200], **markers}
                with open(OUT, "a", encoding="utf-8") as f:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                done += 1
                print(f"  {done}/{total_calls}: srb={markers['semantic_regret_bias']:.3f}")
                time.sleep(0.4)
            except Exception as e:
                print(f"  ERROR sample {sample_idx}: {e}", file=sys.stderr)
                time.sleep(3)

    print(f"\nDone: {done}/{total_calls}")


if __name__ == "__main__":
    main()
