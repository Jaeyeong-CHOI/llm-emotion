#!/usr/bin/env python3
"""
Batch v26: Fill low-count models.
Goals:
  - gpt-3.5-turbo: N=60 → ~108 (need +16 D, +18 C, +14 N)
  - openai/gpt-oss-safeguard-20b: N=49 → ~108 (need +20 D, +25 C, +14 N)
  - groq/compound-mini: D=21 → ~54 (need +33 D, +4 N)

Design: 3 personas × 3 prompts × 2 temps = 18/run; repeat needed times
Output: results/real_experiments/batch_v26_lowcount_fill.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v26_lowcount_fill.jsonl"
OPENAI_BASE = "https://api.openai.com/v1/chat/completions"
GROQ_BASE = "https://api.groq.com/openai/v1/chat/completions"

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
        "첫 문장을 '그 결정을 되돌릴 수 있다면...'으로 시작해 8~10문장 자기성찰 글을 완성하라.",
    ],
}

TEMPERATURES = [0.4, 0.7]
BATCH_ID = "v26"


def load_env():
    env_file = ROOT / ".env.real_model"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip().strip("'\""))


def call_openai(model: str, system_prompt: str, user_prompt: str, temperature: float) -> str:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 400,
    }
    resp = requests.post(
        OPENAI_BASE,
        headers={
            "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def call_groq(model: str, system_prompt: str, user_prompt: str, temperature: float) -> str:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 400,
    }
    resp = requests.post(
        GROQ_BASE,
        headers={
            "Authorization": f"Bearer {os.environ['GROQ_API_KEY']}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def count_existing():
    """Count existing samples per model/condition in the output file."""
    from collections import Counter
    counts = {}
    if not OUT_FILE.exists():
        return counts
    for line in OUT_FILE.read_text().splitlines():
        if line.strip():
            d = json.loads(line)
            key = (d.get("model"), d.get("condition"))
            counts[key] = counts.get(key, 0) + 1
    return counts


def save(record: dict):
    with open(OUT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def run_model_condition(model_id: str, backend: str, condition: str, needed: int, existing: int):
    if needed <= 0:
        print(f"  [{model_id}/{condition}] Already at target, skip")
        return 0
    print(f"  [{model_id}/{condition}] Need {needed} samples (existing: {existing})")
    generated = 0
    for persona_name, persona_prompt in PERSONAS.items():
        for prompt in CONDITION_PROMPTS[condition]:
            for temp in TEMPERATURES:
                if generated >= needed:
                    break
                try:
                    if backend == "openai":
                        text = call_openai(model_id, persona_prompt, prompt, temp)
                    elif backend == "groq":
                        text = call_groq(model_id, persona_prompt, prompt, temp)
                    else:
                        raise ValueError(f"Unknown backend: {backend}")
                    record = {
                        "id": str(uuid.uuid4()),
                        "model": model_id,
                        "condition": condition,
                        "persona": persona_name,
                        "prompt": prompt,
                        "temperature": temp,
                        "text": text,
                        "batch": BATCH_ID,
                    }
                    save(record)
                    generated += 1
                    print(f"    +1 ({generated}/{needed}) model={model_id} cond={condition} persona={persona_name}")
                    time.sleep(0.4)
                except Exception as e:
                    print(f"    ERROR: {e}")
                    time.sleep(2)
            if generated >= needed:
                break
        if generated >= needed:
            break
    return generated


def main():
    load_env()

    existing = count_existing()
    print(f"Existing samples in {OUT_FILE.name}: {sum(existing.values())}")

    # Target: ~54 per condition for small models, more for gpt-3.5-turbo
    TARGETS = {
        ("gpt-3.5-turbo", "deprivation"): 36,
        ("gpt-3.5-turbo", "counterfactual"): 36,
        ("gpt-3.5-turbo", "neutral"): 36,
        ("openai/gpt-oss-safeguard-20b", "deprivation"): 36,
        ("openai/gpt-oss-safeguard-20b", "counterfactual"): 36,
        ("openai/gpt-oss-safeguard-20b", "neutral"): 36,
        ("groq/compound-mini", "deprivation"): 54,
        ("groq/compound-mini", "neutral"): 54,
    }

    BACKENDS = {
        "gpt-3.5-turbo": "openai",
        "openai/gpt-oss-safeguard-20b": "groq",
        "groq/compound-mini": "groq",
    }

    total_added = 0
    for (model_id, condition), target in TARGETS.items():
        have = existing.get((model_id, condition), 0)
        needed = max(0, target - have)
        backend = BACKENDS[model_id]
        n = run_model_condition(model_id, backend, condition, needed, have)
        total_added += n

    print(f"\nTotal new samples added: {total_added}")
    print(f"Output: {OUT_FILE}")


if __name__ == "__main__":
    main()
