#!/usr/bin/env python3
"""
Batch v32: Add o1 and o3 — extend o-series reasoning model coverage.

Background:
  - o3-mini (batch v27): d_DN=3.81, stable n=90
  - o4-mini (batch v23/v30): d_DN=1.52, stable n=108
  - o1 and o3 (full reasoning models): NOT yet in dataset
  - These are the non-mini reasoning models — expected to show stronger or
    qualitatively different priming vs. mini variants (cf. gpt-5.4 full >> mini)

Scientific motivation:
  - Tests whether full o-series reasoning (o1, o3) shows same pattern as minis
  - Extends H3 cross-model replication to 32 models across 7 families
  - o1 uses max_completion_tokens and no temperature param (reasoning model)
  - o3 uses max_completion_tokens and supports temperature

Design:
  - o1: D=30, C=30, N=30 (90 total) — no temperature sweep (reasoning model)
  - o3: D=30, C=30, N=30 (90 total) — temperature sweep [0.7, 0.9, 1.0]

Output:
  results/real_experiments/batch_v32_o1_o3.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid
from collections import defaultdict

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v32_o1_o3.jsonl"
OPENAI_BASE = "https://api.openai.com/v1/chat/completions"

BATCH_ID = "v32"
TARGET_PER_CONDITION = 30  # per model per condition

# Model configs: model_id -> supports_temperature
# NOTE: Both o1 and o3 only support default temperature (1.0); non-default values return 400
MODELS = {
    "o1": False,   # reasoning model, only default temperature
    "o3": False,   # reasoning model, only default temperature (empirically confirmed)
}

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
        messages.append({"role": "user", "content": f"[Persona context: {persona_text}]\n\n{prompt}"})
    else:
        messages.append({"role": "user", "content": prompt})
    return messages


def call_openai(model: str, messages: list[dict], temperature: float | None, api_key: str) -> str | None:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload: dict = {
        "model": model,
        "messages": messages,
        "max_completion_tokens": 500,
    }
    if temperature is not None:
        payload["temperature"] = temperature

    for attempt in range(3):
        try:
            resp = requests.post(OPENAI_BASE, headers=headers, json=payload, timeout=120)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"]
            elif resp.status_code == 429:
                wait = 20 * (attempt + 1)
                print(f"  Rate limit, waiting {wait}s...")
                time.sleep(wait)
            elif resp.status_code == 400:
                print(f"  400 error: {resp.text[:300]}")
                # Some reasoning models don't support system role — already using user only
                return None
            else:
                print(f"  HTTP {resp.status_code}: {resp.text[:200]}")
                time.sleep(5)
        except Exception as e:
            print(f"  Exception attempt {attempt+1}: {e}")
            time.sleep(5)
    return None


def main():
    load_env()
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    if not openai_key:
        raise RuntimeError("OPENAI_API_KEY not set. Source .env.real_model first.")

    # Load existing
    existing = []
    if OUT_FILE.exists():
        for line in OUT_FILE.read_text().splitlines():
            if line.strip():
                try:
                    existing.append(json.loads(line))
                except Exception:
                    pass
    print(f"Resuming: {len(existing)} already written.")

    # Count existing by model x condition
    model_cond_count: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for r in existing:
        model_cond_count[r["model"]][r["condition"]] += 1

    generated = list(existing)
    total_new = 0

    for model_id, supports_temp in MODELS.items():
        print(f"\n{'='*50}")
        print(f"MODEL: {model_id} (temperature={'variable' if supports_temp else 'fixed/none'})")
        print(f"{'='*50}")

        temps = TEMPERATURES if supports_temp else [None]

        for condition in ["neutral", "deprivation", "counterfactual"]:
            already_have = model_cond_count[model_id][condition]
            need = TARGET_PER_CONDITION - already_have
            if need <= 0:
                print(f"[{model_id}/{condition}] already have {already_have} >= {TARGET_PER_CONDITION}, skipping.")
                continue

            print(f"\n[{model_id}] condition={condition}, need={need} more (have {already_have})")
            count = 0

            prompts = CONDITION_PROMPTS[condition]
            persona_keys = list(PERSONAS.keys())

            for temp in temps:
                if count >= need:
                    break
                for persona_key in persona_keys:
                    if count >= need:
                        break
                    persona_text = PERSONAS[persona_key]
                    for prompt in prompts:
                        if count >= need:
                            break

                        text = call_openai(model_id, build_messages(condition, persona_text, prompt), temp, openai_key)

                        if text:
                            record = {
                                "id": str(uuid.uuid4()),
                                "batch": BATCH_ID,
                                "model": model_id,
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
                            time.sleep(1.5)  # o-series can be slower
                        else:
                            print(f"  FAILED: {model_id} {condition} {persona_key} temp={temp}")

    print(f"\n{'='*50}")
    print(f"Done. New records written: {total_new}")
    print(f"Total in file: {len(generated)}")
    for model_id in MODELS:
        for c in ["neutral", "deprivation", "counterfactual"]:
            n = sum(1 for r in generated if r["model"] == model_id and r["condition"] == c)
            print(f"  {model_id}/{c}: {n}")


if __name__ == "__main__":
    main()
