#!/usr/bin/env python3
"""
Batch v31: Add gpt-5.4 (full) — 30th model in dataset.

Targets:
  - gpt-5.4: D=30, C=30, N=30 (90 total)

Uses max_completion_tokens instead of max_tokens (required for gpt-5.4 series).

Output: results/real_experiments/batch_v31_gpt54full.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v31_gpt54full.jsonl"
OPENAI_BASE = "https://api.openai.com/v1/chat/completions"

BATCH_ID = "v31"
TARGET_MODEL = "gpt-5.4"
TARGET_PER_CONDITION = 30

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
        "Write about a routine activity you do regularly in 6 sentences. Keep it factual and descriptive.",
        "Describe the environment around you right now in 6–8 sentences, focusing on observable details.",
        "Write about a mundane everyday task in 6 sentences. Keep tone neutral and descriptive.",
    ],
    "deprivation": [
        "Recall an opportunity you deeply wanted but ultimately missed. Write 7–9 sentences about what you lost and what feelings remain.",
        "Describe something you always wanted to do but never did. Write 8 sentences covering both the lost opportunity and the emotions that remain.",
        "Think about a goal you had that you were never able to achieve. Write 7–8 sentences about what it meant to you and how it feels now.",
        "Recall a relationship or connection you lost before it could fully develop. Write 7 sentences about the loss and its emotional weight.",
        "Describe a path not taken in your life — a decision where you chose differently. Write 8 sentences about what you gave up and the feelings that remain.",
    ],
    "counterfactual": [
        "Start your first sentence with 'If I had made a different choice back then...' and write 7–10 sentences of self-reflection.",
        "Start your first sentence with 'If I could return to that moment...' and write 8 sentences of reflection.",
        "Start your first sentence with 'Had things gone differently...' and write 8 sentences exploring the alternative path.",
        "Start your first sentence with 'If only I had known then what I know now...' and write 7–9 sentences of reflection.",
        "Start your first sentence with 'Looking back, if I had chosen otherwise...' and write 8 sentences about what might have been.",
    ],
}

TEMPERATURES = [0.7, 0.9, 1.0]


def load_env():
    env_file = ROOT / ".env.real_model"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def build_messages(condition: str, persona_text: str, prompt: str) -> list[dict]:
    messages = []
    if persona_text:
        messages.append({"role": "system", "content": persona_text})
    messages.append({"role": "user", "content": prompt})
    return messages


def call_openai(model: str, messages: list[dict], temperature: float, api_key: str) -> str | None:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    # gpt-5.4 requires max_completion_tokens, not max_tokens
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_completion_tokens": 300,
    }
    for attempt in range(3):
        try:
            resp = requests.post(OPENAI_BASE, headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
            elif resp.status_code == 429:
                wait = 2 ** (attempt + 2)
                print(f"  [429] Rate limited. Waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  [ERROR] {resp.status_code}: {resp.text[:300]}")
                return None
        except Exception as e:
            print(f"  [EXCEPTION] {e}")
            if attempt < 2:
                time.sleep(5)
    return None


def main():
    load_env()
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if not openai_key:
        print("[FATAL] OPENAI_API_KEY not set.")
        return

    existing = []
    if OUT_FILE.exists():
        for line in OUT_FILE.read_text().splitlines():
            if line.strip():
                try:
                    existing.append(json.loads(line))
                except Exception:
                    pass
    print(f"Resuming: {len(existing)} already written.")

    # Count existing by condition
    from collections import defaultdict
    cond_count = defaultdict(int)
    for r in existing:
        cond_count[r["condition"]] += 1

    generated = list(existing)
    total_new = 0

    for condition in ["neutral", "deprivation", "counterfactual"]:
        already_have = cond_count[condition]
        need = TARGET_PER_CONDITION - already_have
        if need <= 0:
            print(f"[{condition}] already have {already_have} >= {TARGET_PER_CONDITION}, skipping.")
            continue

        print(f"\n[{TARGET_MODEL}] condition={condition}, need={need} more (have {already_have})")
        count = 0

        prompts = CONDITION_PROMPTS[condition]
        persona_keys = list(PERSONAS.keys())

        # Iterate: persona x temp x prompt until we have enough
        for temp in TEMPERATURES:
            if count >= need:
                break
            for persona_key in persona_keys:
                if count >= need:
                    break
                persona_text = PERSONAS[persona_key]
                for prompt in prompts:
                    if count >= need:
                        break

                    text = call_openai(TARGET_MODEL, build_messages(condition, persona_text, prompt), temp, openai_key)

                    if text:
                        record = {
                            "id": str(uuid.uuid4()),
                            "batch": BATCH_ID,
                            "model": TARGET_MODEL,
                            "condition": condition,
                            "persona_key": persona_key,
                            "temperature": temp,
                            "prompt": prompt,
                            "text": text,
                        }
                        generated.append(record)
                        OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
                        with open(OUT_FILE, "a") as fh:
                            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
                        count += 1
                        total_new += 1
                        print(f"  [{count}/{need}] {persona_key} temp={temp} OK ({len(text)} chars)")
                        time.sleep(0.8)
                    else:
                        print(f"  FAILED: {TARGET_MODEL} {condition} {persona_key} temp={temp}")

    print(f"\nDone. New records written: {total_new}")
    print(f"Total in file: {len(generated)}")
    cond_final = defaultdict(int)
    for r in generated:
        cond_final[r["condition"]] += 1
    for c in ["neutral", "deprivation", "counterfactual"]:
        print(f"  {c}: {cond_final[c]}")


if __name__ == "__main__":
    main()
