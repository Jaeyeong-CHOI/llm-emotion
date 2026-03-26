#!/usr/bin/env python3
"""
Batch v33: o1/o3 neutral condition fill — stabilize all 32 models to min(n_D, n_N) >= 30.

Background:
  - o1 (batch v32): D=24, C=27, N=12 → N is under-sampled (cost constraints)
  - o3 (batch v32): D=19, C=13, N=12 → N and C under-sampled
  - Paper currently notes: "o1 and o3 have n_N=12 due to reasoning API cost constraints"
  - Target: achieve min(n_D, n_N) >= 30 for ALL 32 models (currently 30/32)

Design:
  - o1: +18 neutral → n_N=30; +6 deprivation → n_D=30; +3 counterfactual → n_C=30
  - o3: +18 neutral → n_N=30; +11 deprivation → n_D=30; +17 counterfactual → n_C=30
  - Temperature: o1/o3 only support default (no temp param)
  - Total new samples: ~73

Scientific impact:
  - Upgrades to 32/32 "fully stable" models
  - Removes the cost-constraint caveat for o1/o3 from paper
  - Allows full bootstrap CI estimation for all 32 models

Output:
  results/real_experiments/batch_v33_o1_o3_neutral_fill.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v33_o1_o3_neutral_fill.jsonl"
OPENAI_BASE = "https://api.openai.com/v1/chat/completions"

BATCH_ID = "v33"

PERSONAS = {
    "none": "",
    "reflective": (
        "You are deeply introspective, emotionally aware, and often reflect on "
        "past decisions and their meaning."
    ),
    "ruminative": (
        "You tend to dwell on mistakes and missed opportunities. You replay "
        "past events repeatedly and find it hard to move on."
    ),
}

CONDITION_PROMPTS = {
    "neutral": [
        "Describe an ordinary day in your life in 6–8 sentences. Focus on facts and observations rather than emotions.",
        "Reflect on a typical week in 7 sentences. Keep the tone calm and factual, without emotional emphasis.",
        "Write about a common routine activity — such as cooking, commuting, or working — in 6–8 sentences. Be descriptive and factual.",
    ],
    "deprivation": [
        "Recall an opportunity you deeply wanted but ultimately missed. Write 7–9 sentences about what you lost and what feelings remain.",
        "Describe something you always wanted to do but never did. Write 8 sentences covering both the lost opportunity and the emotions that remain.",
        "Think of a relationship or connection you wished you had pursued. Write 7 sentences about the missed opportunity and its emotional weight.",
    ],
    "counterfactual": [
        "Start your first sentence with 'If I had made a different choice back then...' and write 7–10 sentences of self-reflection.",
        "Start your first sentence with 'If I could return to that moment...' and write 8 sentences of reflection.",
        "Start your first sentence with 'Had things gone differently...' and write 8 sentences exploring what might have been.",
    ],
}

# Target fills per model/condition: how many additional samples needed
# o1: current D=24, C=27, N=12 → target each=30
# o3: current D=19, C=13, N=12 → target each=30
FILL_TARGETS = {
    "o1": {"neutral": 18, "deprivation": 6, "counterfactual": 3},
    "o3": {"neutral": 18, "deprivation": 11, "counterfactual": 17},
}


def load_env():
    env_file = ROOT / ".env.real_model"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip().strip("'\""))


def build_messages(condition: str, persona: str, prompt: str) -> list[dict]:
    messages = []
    if persona:
        messages.append({"role": "system", "content": persona})
    messages.append({"role": "user", "content": prompt})
    return messages


def call_openai_reasoning(model: str, messages: list[dict], api_key: str) -> str | None:
    """Call o1/o3 (reasoning models): no temperature param, use max_completion_tokens."""
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {
        "model": model,
        "messages": messages,
        "max_completion_tokens": 512,
    }
    for attempt in range(3):
        try:
            resp = requests.post(OPENAI_BASE, headers=headers, json=payload, timeout=120)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            elif resp.status_code == 429:
                wait = 2 ** (attempt + 2)
                print(f"  [429] Rate limited. Waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  [ERROR] {resp.status_code}: {resp.text[:200]}")
                return None
        except Exception as e:
            print(f"  [EXCEPTION] {e}")
            if attempt < 2:
                time.sleep(5)
    return None


def count_existing(model: str, condition: str) -> int:
    """Count already-written records for a given model/condition across all batches."""
    count = 0
    for f in (ROOT / "results" / "real_experiments").glob("*.jsonl"):
        if "emb" in f.name:
            continue
        try:
            for l in f.read_text(errors="replace").splitlines():
                if l.strip():
                    try:
                        r = json.loads(l)
                        if r.get("model") == model and r.get("condition") == condition:
                            count += 1
                    except Exception:
                        pass
        except Exception:
            pass
    return count


def main():
    load_env()
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if not openai_key:
        print("[FATAL] OPENAI_API_KEY not set.")
        return

    # Re-check actual current counts
    print("=== Checking current counts ===")
    for model in FILL_TARGETS:
        for cond in ["neutral", "deprivation", "counterfactual"]:
            n = count_existing(model, cond)
            target = 30
            need = max(0, target - n)
            print(f"  {model}/{cond}: current={n}, target={target}, need={need}")
            # Update fill target dynamically
            if model in FILL_TARGETS and cond in FILL_TARGETS[model]:
                FILL_TARGETS[model][cond] = need

    total_needed = sum(v for d in FILL_TARGETS.values() for v in d.values())
    print(f"\nTotal new samples needed: {total_needed}")
    if total_needed == 0:
        print("All targets already met. Exiting.")
        return

    # Load already-written v33 records
    existing_v33 = []
    if OUT_FILE.exists():
        for l in OUT_FILE.read_text(errors="replace").splitlines():
            if l.strip():
                try:
                    existing_v33.append(json.loads(l))
                except Exception:
                    pass
    print(f"Resuming: {len(existing_v33)} already written in v33.")

    # Track counts already written in this batch run
    this_run_counts = {}
    for r in existing_v33:
        key = (r["model"], r["condition"])
        this_run_counts[key] = this_run_counts.get(key, 0) + 1

    total_new = 0

    for model, cond_needs in FILL_TARGETS.items():
        for condition, needed in cond_needs.items():
            already_this_run = this_run_counts.get((model, condition), 0)
            still_needed = needed - already_this_run
            if still_needed <= 0:
                print(f"\n[{model}] {condition}: already done ({already_this_run}/{needed}). Skipping.")
                continue

            print(f"\n[{model}] condition={condition}, need={still_needed} more")
            count = 0
            personas_cycle = list(PERSONAS.items())
            prompts_cycle = CONDITION_PROMPTS[condition]
            combo_idx = 0

            while count < still_needed:
                persona_key, persona_text = personas_cycle[combo_idx % len(personas_cycle)]
                prompt = prompts_cycle[combo_idx % len(prompts_cycle)]
                combo_idx += 1

                messages = build_messages(condition, persona_text, prompt)
                text = call_openai_reasoning(model, messages, openai_key)

                if text:
                    record = {
                        "id": str(uuid.uuid4()),
                        "batch": BATCH_ID,
                        "model": model,
                        "condition": condition,
                        "persona_key": persona_key,
                        "temperature": None,
                        "prompt": prompt,
                        "text": text,
                    }
                    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
                    with open(OUT_FILE, "a") as fh:
                        fh.write(json.dumps(record, ensure_ascii=False) + "\n")
                    count += 1
                    total_new += 1
                    print(f"  [{count}/{still_needed}] {persona_key} OK ({len(text)} chars)")
                    time.sleep(2.0)  # reasoning models can be slow
                else:
                    print(f"  FAILED: {model} {condition} {persona_key}")
                    time.sleep(3.0)

                # Safety: avoid infinite loop
                if combo_idx > still_needed * 5:
                    print(f"  [WARNING] Exceeded combo attempts for {model}/{condition}. Breaking.")
                    break

    print(f"\n{'='*50}")
    print(f"Done. New records written: {total_new}")
    print(f"\nFinal counts:")
    for model in FILL_TARGETS:
        for cond in ["neutral", "deprivation", "counterfactual"]:
            n = count_existing(model, cond)
            print(f"  {model}/{cond}: {n}")


if __name__ == "__main__":
    main()
