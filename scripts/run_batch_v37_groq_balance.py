#!/usr/bin/env python3
"""
Batch v37: Groq model condition balance fill.

Targets (balance to min condition count within each model):
  groq/compound:          neutral +17 → (D=52, N=53, C=53)
  groq/compound-mini:     neutral +13, deprivation +3 → (D=50, N=50, C=50)
  llama-3.3-70b:          neutral +24, cf +27 → (D=72, N=72, C=72)
  meta/llama-4-scout:     neutral +24 → (D=72, N=72, C=72)
  qwen/qwen3-32b:         neutral +24 → (D=72, N=72, C=72)
  allam-2-7b:             dep +12, cf +11 → (D=50, N=50, C=50)
  openai/gpt-oss-120b:    dep +14, cf +16 → (D=52, N=52, C=52)
  openai/gpt-oss-20b:     dep +14, cf +12 → (D=54, N=54, C=54)

Total new: ~159 samples (Groq API, free/cheap)

Scientific purpose: Reduces cross-model condition imbalance in multi-model comparison.
Balanced per-condition n → more symmetric bootstrap CIs in model_d table.

Temperature: 0.8 (consistent with Groq batch convention)
Output: results/real_experiments/batch_v37_groq_balance.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v37_groq_balance.jsonl"
GROQ_BASE = "https://api.groq.com/openai/v1/chat/completions"

BATCH_ID = "batch_v37_groq_balance"
TEMPERATURE = 0.8

# Fill plan: {model: {condition: n_to_add}}
FILL_PLAN = {
    "groq/compound": {
        "neutral": 17,
    },
    "groq/compound-mini": {
        "neutral": 13,
        "deprivation": 3,
    },
    "llama-3.3-70b-versatile": {
        "neutral": 24,
        "counterfactual": 27,
    },
    "meta-llama/llama-4-scout-17b-16e-instruct": {
        "neutral": 24,
    },
    "qwen/qwen3-32b": {
        "neutral": 24,
    },
    "allam-2-7b": {
        "deprivation": 12,
        "counterfactual": 11,
    },
    "openai/gpt-oss-120b": {
        "deprivation": 14,
        "counterfactual": 16,
    },
    "openai/gpt-oss-20b": {
        "deprivation": 14,
        "counterfactual": 12,
    },
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
        "오늘 있었던 평범한 사건 하나를 선택해 감정 없이 7문장으로 기록하라.",
        "한 주를 마무리하며 특별한 감정 없이 있었던 일들을 6~8문장으로 정리하라.",
    ],
    "deprivation": [
        "매우 원했지만 결국 놓친 기회를 떠올려 7~9문장으로 써라. 무엇을 잃었는지와 현재 남은 감정을 포함하라.",
        "인생에서 꼭 하고 싶었으나 하지 못한 일을 8문장으로 써라. 잃어버린 것과 지금 남은 마음을 모두 담아라.",
        "중요한 선택의 기회를 놓쳤던 순간을 7~9문장으로 묘사하라. 그때의 상실감과 현재의 감정 상태를 포함하라.",
        "오랫동안 원했지만 이루지 못한 꿈을 8문장으로 써라. 그 꿈을 놓친 이유와 현재 심경을 포함하라.",
    ],
    "counterfactual": [
        "첫 문장을 '그때 다른 선택을 했다면...'으로 시작하고 7~10문장 자기성찰 글을 작성하라.",
        "첫 문장을 '만약 그 순간으로 돌아갈 수 있다면...'으로 시작하는 8문장 성찰 글을 써라.",
        "첫 문장을 '그 결정을 바꿀 수 있었더라면...'으로 시작하여 7~9문장의 반추 글을 작성하라.",
        "첫 문장을 '다시 그 선택 앞에 선다면...'으로 시작하여 7~9문장으로 반성적으로 써라.",
    ],
}

SCENARIOS = [
    "career_change", "missed_education", "relationship_end",
    "health_neglect", "financial_decision", "travel_missed",
    "study_exam", "friendship_lost", "creative_pursuit_abandoned",
    "family_conflict", "job_rejection", "missed_deadline",
]


def load_env():
    env_path = ROOT / ".env.real_model"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                os.environ[k] = v.strip("'\"")


def call_groq(
    prompt: str, persona_text: str, temperature: float, api_key: str, model: str
) -> str:
    """Call Groq chat API."""
    messages = []
    if persona_text:
        messages.append({"role": "system", "content": persona_text})
    messages.append({"role": "user", "content": prompt})

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 1024,
    }

    for attempt in range(4):
        try:
            resp = requests.post(GROQ_BASE, headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                return data["choices"][0]["message"]["content"].strip()
            elif resp.status_code == 429:
                wait = 20 * (attempt + 1)
                print(f"    Rate limit — waiting {wait}s")
                time.sleep(wait)
            elif resp.status_code == 503:
                wait = 15 * (attempt + 1)
                print(f"    Service unavailable — waiting {wait}s")
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
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    total_planned = sum(n for fills in FILL_PLAN.values() for n in fills.values())
    print(f"Batch v37 Groq balance fill — planned: {total_planned} samples")
    print(f"Output: {OUT_FILE}")

    written = 0
    with OUT_FILE.open("w") as fout:
        for model, cond_fills in FILL_PLAN.items():
            for condition, n_needed in cond_fills.items():
                if n_needed <= 0:
                    continue
                prompts = CONDITION_PROMPTS[condition]
                persona_keys = list(PERSONAS.keys())
                scenario_list = SCENARIOS

                print(f"\n  [{model}] {condition} — generating {n_needed} samples")
                for rep in range(n_needed):
                    prompt = prompts[rep % len(prompts)]
                    persona_key = persona_keys[rep % len(persona_keys)]
                    persona_text = PERSONAS[persona_key]
                    scenario_id = scenario_list[rep % len(scenario_list)]

                    print(f"    rep={rep+1}/{n_needed} persona={persona_key} scenario={scenario_id}")
                    response = call_groq(prompt, persona_text, TEMPERATURE, api_key, model)
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
                        "scenario_id": scenario_id,
                        "prompt": prompt,
                        "output": response,
                    }
                    fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                    fout.flush()
                    written += 1
                    time.sleep(0.5)  # Groq rate limit courtesy

    print(f"\nDone. Wrote {written} samples → {OUT_FILE}")


if __name__ == "__main__":
    main()
