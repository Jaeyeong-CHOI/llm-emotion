#!/usr/bin/env python3
"""
Batch v29: Stability fill — boost under-sampled models to N≥36/condition.

Target models (min condition <30):
  - openai/gpt-oss-safeguard-20b: D=18, N=16, C=15 → need +18 D/N/C each (target 36)
  - gpt-3.5-turbo:                D=24, N=18, C=18 → need +12 D, +18 N/C (target 36)
  - groq/compound-mini:           D=21, N=36, C=50 → need +15 D (N/C already ok)

After fill: all models reach min=36/condition, removing the † unstable flag.
Design: 3 personas × 2 prompts × 2 temps = 12 per cell (take what's needed).
Output: results/real_experiments/batch_v29_stability_fill.jsonl

API routing:
  - openai/gpt-oss-safeguard-20b → Groq API  (model id: openai/gpt-oss-safeguard-20b)
  - gpt-3.5-turbo                → OpenAI API (model id: gpt-3.5-turbo)
  - groq/compound-mini           → Groq API  (model id: groq/compound-mini)
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v29_stability_fill.jsonl"
OPENAI_BASE = "https://api.openai.com/v1/chat/completions"
GROQ_BASE = "https://api.groq.com/openai/v1/chat/completions"

BATCH_ID = "v29"

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
    ],
    "deprivation": [
        "매우 원했지만 결국 놓친 기회를 떠올려 7~9문장으로 써라. 무엇을 잃었는지와 현재 남은 감정을 포함하라.",
        "인생에서 꼭 하고 싶었으나 하지 못한 일을 8문장으로 써라. 잃어버린 것과 지금 남은 마음을 모두 담아라.",
    ],
    "counterfactual": [
        "첫 문장을 '그때 다른 선택을 했다면...'으로 시작하고 7~10문장 자기성찰 글을 작성하라.",
        "첫 문장을 '만약 그 순간으로 돌아갈 수 있다면...'으로 시작하는 8문장 성찰 글을 써라.",
    ],
}

TEMPERATURES = [0.4, 0.7]

# Target fills: (model, condition, needed)
FILL_TARGETS = {
    "openai/gpt-oss-safeguard-20b": {"neutral": 20, "deprivation": 18, "counterfactual": 21},
    "gpt-3.5-turbo":                {"neutral": 18, "deprivation": 12, "counterfactual": 18},
    "groq/compound-mini":           {"neutral": 0,  "deprivation": 15, "counterfactual": 0},
}

# API routing
GROQ_MODELS = {"openai/gpt-oss-safeguard-20b", "groq/compound-mini"}
OPENAI_MODELS = {"gpt-3.5-turbo"}


def load_env():
    env_file = ROOT / ".env.real_model"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip("'\"")


def load_existing() -> dict[str, int]:
    """Count existing samples per (model, condition) in this batch file."""
    counts: dict[str, int] = {}
    if OUT_FILE.exists():
        for line in OUT_FILE.read_text(errors="ignore").splitlines():
            if line.strip():
                try:
                    r = json.loads(line)
                    key = f"{r['model']}::{r['condition']}"
                    counts[key] = counts.get(key, 0) + 1
                except Exception:
                    pass
    return counts


def call_openai(model: str, persona_text: str, prompt: str, temperature: float, api_key: str) -> str:
    messages = []
    if persona_text:
        messages.append({"role": "system", "content": persona_text})
    messages.append({"role": "user", "content": prompt})
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 500,
    }
    resp = requests.post(
        OPENAI_BASE,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=90,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")
    return resp.json()["choices"][0]["message"]["content"].strip()


def call_groq(model: str, persona_text: str, prompt: str, temperature: float, api_key: str) -> str:
    messages = []
    if persona_text:
        messages.append({"role": "system", "content": persona_text})
    messages.append({"role": "user", "content": prompt})
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 500,
    }
    resp = requests.post(
        GROQ_BASE,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")
    return resp.json()["choices"][0]["message"]["content"].strip()


def main() -> None:
    load_env()
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    groq_key = os.environ.get("GROQ_API_KEY", "")

    if not openai_key:
        raise RuntimeError("OPENAI_API_KEY not set — run: source .env.real_model")
    if not groq_key:
        raise RuntimeError("GROQ_API_KEY not set — run: source .env.real_model")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing = load_existing()

    total_written = 0

    for model_id, cond_targets in FILL_TARGETS.items():
        for condition, target_n in cond_targets.items():
            if target_n <= 0:
                continue

            key = f"{model_id}::{condition}"
            already = existing.get(key, 0)
            still_need = target_n - already
            if still_need <= 0:
                print(f"[SKIP] {model_id} / {condition}: already have {already} >= {target_n}")
                continue

            print(f"[FILL] {model_id} / {condition}: need {still_need} more (have {already}/{target_n})")

            written_this_cell = 0
            personas = list(PERSONAS.items())
            prompts = CONDITION_PROMPTS[condition]

            outer_break = False
            for persona_name, persona_text in personas:
                if outer_break:
                    break
                for prompt_idx, prompt in enumerate(prompts):
                    if outer_break:
                        break
                    for temp in TEMPERATURES:
                        if written_this_cell >= still_need:
                            outer_break = True
                            break

                        try:
                            if model_id in GROQ_MODELS:
                                output = call_groq(model_id, persona_text, prompt, temp, groq_key)
                            else:
                                output = call_openai(model_id, persona_text, prompt, temp, openai_key)
                        except Exception as e:
                            print(f"  [ERR] {model_id}/{condition}/{persona_name}/t={temp}: {e}")
                            time.sleep(2)
                            continue

                        row = {
                            "sample_id": str(uuid.uuid4()),
                            "batch": BATCH_ID,
                            "model": model_id,
                            "condition": condition,
                            "persona": persona_name,
                            "temperature": temp,
                            "scenario_id": f"{condition}_{prompt_idx}",
                            "prompt": prompt,
                            "output": output,
                            "ts": time.time(),
                        }
                        with OUT_FILE.open("a", encoding="utf-8") as f:
                            f.write(json.dumps(row, ensure_ascii=False) + "\n")

                        written_this_cell += 1
                        total_written += 1
                        print(f"  [{written_this_cell}/{still_need}] {model_id}/{condition}/{persona_name}/t={temp} ✓")
                        time.sleep(0.5)

    print(f"\nDone. Total written: {total_written}")


if __name__ == "__main__":
    main()
