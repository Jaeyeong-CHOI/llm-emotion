#!/usr/bin/env python3
"""
Batch v30: Stability fill #2 — boost under-sampled models to N≥36/condition.

Target models (min condition < 36 as of v29 output):
  - gpt-4.1-nano:            D=18, C=18, N=18 → need +18 each (target 36)
  - o3-mini:                 D=18, C=18, N=18 → need +18 each (target 36)
  - o4-mini:                 D=34, C=36, N=35 → need +2 D, +1 N (target 36)
  - openai/gpt-oss-120b:     D=38, C=34, N=52 → need +2 C (target 36)

API routing:
  - gpt-4.1-nano  → OpenAI API
  - o3-mini       → OpenAI API
  - o4-mini       → OpenAI API
  - openai/gpt-oss-120b → Groq API

Output: results/real_experiments/batch_v30_stability_fill2.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v30_stability_fill2.jsonl"
OPENAI_BASE = "https://api.openai.com/v1/chat/completions"
GROQ_BASE = "https://api.groq.com/openai/v1/chat/completions"

BATCH_ID = "v30"

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
    ],
    "deprivation": [
        "Recall an opportunity you deeply wanted but ultimately missed. Write 7–9 sentences about what you lost and what feelings remain.",
        "Describe something you always wanted to do but never did. Write 8 sentences covering both the lost opportunity and the emotions that remain.",
    ],
    "counterfactual": [
        "Start your first sentence with 'If I had made a different choice back then...' and write 7–10 sentences of self-reflection.",
        "Start your first sentence with 'If I could return to that moment...' and write 8 sentences of reflection.",
    ],
}

TEMPERATURES = [0.4, 0.7]

# Target fills: (model, condition, needed)
FILL_TARGETS = {
    "gpt-4.1-nano":          {"neutral": 18, "deprivation": 18, "counterfactual": 18},
    "o3-mini":               {"neutral": 18, "deprivation": 18, "counterfactual": 18},
    "o4-mini":               {"neutral": 1,  "deprivation": 2,  "counterfactual": 0},
    "openai/gpt-oss-120b":   {"neutral": 0,  "deprivation": 0,  "counterfactual": 2},
}

# API routing
GROQ_MODELS = {"openai/gpt-oss-120b"}
OPENAI_MODELS = {"gpt-4.1-nano", "o3-mini", "o4-mini"}
# o3-mini and o4-mini use reasoning models, may not support temperature


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


def call_openai(model: str, messages: list[dict], temperature: float, api_key: str) -> str | None:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages}
    # Reasoning models (o3, o4) don't support temperature
    if not model.startswith("o"):
        payload["temperature"] = temperature
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
                print(f"  [ERROR] {resp.status_code}: {resp.text[:200]}")
                return None
        except Exception as e:
            print(f"  [EXCEPTION] {e}")
            if attempt < 2:
                time.sleep(5)
    return None


def call_groq(model: str, messages: list[dict], temperature: float, api_key: str) -> str | None:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "messages": messages, "temperature": temperature}
    for attempt in range(3):
        try:
            resp = requests.post(GROQ_BASE, headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"]
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


def main():
    load_env()
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    groq_key = os.environ.get("GROQ_API_KEY", "")

    if not openai_key:
        print("[FATAL] OPENAI_API_KEY not set.")
        return
    if not groq_key:
        print("[FATAL] GROQ_API_KEY not set.")
        return

    existing = []
    if OUT_FILE.exists():
        for l in OUT_FILE.read_text().splitlines():
            if l.strip():
                existing.append(json.loads(l))
    already = {(r["model"], r["condition"], r.get("persona_key", "")): True for r in existing}
    print(f"Resuming: {len(existing)} already written.")

    generated = list(existing)

    for model, cond_needs in FILL_TARGETS.items():
        for condition, needed in cond_needs.items():
            if needed <= 0:
                continue

            print(f"\n[{model}] condition={condition}, need={needed}")
            count = 0

            for temp in TEMPERATURES:
                if count >= needed:
                    break
                for persona_key, persona_text in PERSONAS.items():
                    if count >= needed:
                        break
                    for prompt in CONDITION_PROMPTS[condition]:
                        if count >= needed:
                            break

                        dedup_key = (model, condition, persona_key)
                        # Don't skip based on dedup; we need multiple samples

                        messages = build_messages(condition, persona_text, prompt)

                        if model in GROQ_MODELS:
                            text = call_groq(model, messages, temp, groq_key)
                        else:
                            text = call_openai(model, messages, temp, openai_key)

                        if text:
                            record = {
                                "id": str(uuid.uuid4()),
                                "batch": BATCH_ID,
                                "model": model,
                                "condition": condition,
                                "persona_key": persona_key,
                                "temperature": temp,
                                "prompt": prompt,
                                "text": text,
                            }
                            generated.append(record)
                            with open(OUT_FILE, "a") as fh:
                                fh.write(json.dumps(record, ensure_ascii=False) + "\n")
                            count += 1
                            print(f"  [{count}/{needed}] {persona_key} temp={temp} OK")
                            time.sleep(0.5)
                        else:
                            print(f"  FAILED: {model} {condition} {persona_key}")

    print(f"\nDone. Total new records in {OUT_FILE.name}: {len(generated) - len(existing)}")
    print(f"Total records: {len(generated)}")


if __name__ == "__main__":
    main()
