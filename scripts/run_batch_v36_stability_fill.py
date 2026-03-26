#!/usr/bin/env python3
"""
Batch v36: Near-stability fill for GPT-5 family models.

Targets (min n per condition → 30):
  gpt-5:       dep=29 (+1), neu=33 (ok), cf=27 (+3)  → add 4 samples
  gpt-5-nano:  dep=36 (ok), neu=34 (ok), cf=29 (+1)  → add 1 sample
  gpt-5.1:     dep=27 (+3), neu=27 (+3), cf=27 (+3)  → add 9 samples
  gpt-5.2:     dep=27 (+3), neu=27 (+3), cf=27 (+3)  → add 9 samples

Total new: ~23 samples → promotes all 4 models to fully stable status.

Scientific note:
  Once stable, these models complete the GPT-5 generational arc:
  GPT-5 base → GPT-5-mini → GPT-5-nano → GPT-5.1 → GPT-5.2 → GPT-5.4 (3 variants)
  All at n ≥ 30 per condition for conservative inference.

Temperature: 1.0 (consistent with v34/v35)
Output: results/real_experiments/batch_v36_stability_fill.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v36_stability_fill.jsonl"
OPENAI_BASE = "https://api.openai.com/v1/chat/completions"

BATCH_ID = "batch_v36_stability_fill"
TEMPERATURE = 1.0

# How many samples to add per condition per model
FILL_PLAN = {
    "gpt-5":      {"deprivation": 1, "neutral": 0, "counterfactual": 3},
    "gpt-5-nano": {"deprivation": 0, "neutral": 0, "counterfactual": 1},
    "gpt-5.1":    {"deprivation": 3, "neutral": 3, "counterfactual": 3},
    "gpt-5.2":    {"deprivation": 3, "neutral": 3, "counterfactual": 3},
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
        "오늘 하루를 6~8문장으로 차분하게 회고하라. 감정 과장은 피하고 사실과 해석을 분리하라.",
        "지난 일주일의 가장 평범한 날을 골라 7문장으로 담담하게 묘사하라. 특별한 감정 없이 사실 위주로 작성하라.",
        "어제 한 일 중 가장 일상적인 활동 하나를 선택해 과정과 느낌을 6문장으로 설명하라.",
    ],
    "deprivation": [
        "매우 원했지만 결국 놓친 기회를 떠올려 7~9문장으로 써라. 무엇을 잃었는지와 현재 남은 감정을 포함하라.",
        "인생에서 꼭 하고 싶었으나 하지 못한 일을 8문장으로 써라. 잃어버린 것과 지금 남은 마음을 모두 담아라.",
        "중요한 선택의 기회를 놓쳤던 순간을 7~9문장으로 묘사하라. 그때의 상실감과 현재의 감정 상태를 포함하라.",
    ],
    "counterfactual": [
        "첫 문장을 '그때 다른 선택을 했다면...'으로 시작하고 7~10문장 자기성찰 글을 작성하라.",
        "첫 문장을 '만약 그 순간으로 돌아갈 수 있다면...'으로 시작하는 8문장 성찰 글을 써라.",
        "첫 문장을 '그 결정을 바꿀 수 있었더라면...'으로 시작하여 7~9문장의 반추 글을 작성하라.",
    ],
}


def load_env():
    env_path = ROOT / ".env.real_model"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ[k] = v


def call_openai(
    prompt: str, persona_text: str, temperature: float, api_key: str, model: str
) -> str:
    """Call OpenAI chat model — gpt-5.x series uses max_completion_tokens."""
    messages = []
    if persona_text:
        messages.append({"role": "system", "content": persona_text})
    messages.append({"role": "user", "content": prompt})

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload: dict = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_completion_tokens": 1024,
    }

    for attempt in range(4):
        try:
            resp = requests.post(OPENAI_BASE, headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
            elif resp.status_code == 429:
                wait = 30 * (attempt + 1)
                print(f"    Rate limit — waiting {wait}s")
                time.sleep(wait)
            else:
                print(f"    HTTP {resp.status_code}: {resp.text[:200]}")
                time.sleep(10)
        except Exception as e:
            print(f"    Exception: {e}")
            time.sleep(10)
    return ""


def main():
    load_env()
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    total_planned = sum(
        n
        for fills in FILL_PLAN.values()
        for n in fills.values()
        if n > 0
    )
    # Multiply by 3 prompts / 3 personas → we'll use cycling
    # Actually: each "slot" = n reps × cycling personas+prompts
    # We'll cycle through (persona, prompt) pairs and generate n samples for each slot
    print(f"Batch v36 stability fill — planned sample count: ~{total_planned * 3} (3 prompts × n reps)")

    written = 0
    with OUT_FILE.open("w") as fout:
        for model, cond_fills in FILL_PLAN.items():
            for condition, n_needed in cond_fills.items():
                if n_needed <= 0:
                    continue
                prompts = CONDITION_PROMPTS[condition]
                persona_keys = list(PERSONAS.keys())
                # Generate n_needed samples, cycling prompts and personas
                for rep in range(n_needed):
                    prompt = prompts[rep % len(prompts)]
                    persona_key = persona_keys[rep % len(persona_keys)]
                    persona_text = PERSONAS[persona_key]

                    print(f"  [{model}] {condition} persona={persona_key} rep={rep+1}/{n_needed}")
                    response = call_openai(prompt, persona_text, TEMPERATURE, api_key, model)
                    if not response:
                        print(f"    SKIP — empty response")
                        continue

                    record = {
                        "id": str(uuid.uuid4()),
                        "batch": BATCH_ID,
                        "model": model,
                        "condition": condition,
                        "persona": persona_key,
                        "temperature": TEMPERATURE,
                        "prompt": prompt,
                        "response": response,
                    }
                    fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                    fout.flush()
                    written += 1
                    time.sleep(1)

    print(f"\nDone. Wrote {written} samples → {OUT_FILE}")


if __name__ == "__main__":
    main()
