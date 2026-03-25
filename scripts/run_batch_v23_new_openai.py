#!/usr/bin/env python3
"""
Batch v23: New OpenAI model extensions
Goals:
  - o4-mini: reasoning model (first o-series in dataset)
  - gpt-5: latest frontier GPT-5 baseline
  - gpt-5.1: mid-tier GPT-5.x
  - gpt-5.2: GPT-5.2 coverage
  - gpt-4.1-nano: smallest GPT-4.1 variant (complement gpt-4.1, gpt-4.1-mini)

Design: 3 conditions × 3 personas × 3 prompts × 2 temps × 2 reps = 108 per model
Scientific motivation:
  - o4-mini is a reasoning model — tests if CoT-style training dampens semantic priming
  - GPT-5.x family progression: compare 5.1 vs 5.2 vs 5.4 (already have 5.4-mini/nano)
  - gpt-4.1-nano completes the 4.1 family (have 4.1 and 4.1-mini already)

Output: results/real_experiments/batch_v23_new_openai.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v23_new_openai.jsonl"
OPENAI_BASE = "https://api.openai.com/v1/chat/completions"

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

TEMPERATURES = [0.4, 0.7]
REPS = 2
BATCH_ID = "v23"

# (model_id, is_reasoning)
MODELS = [
    ("o4-mini", True),       # reasoning model — uses max_completion_tokens, no system role
    ("gpt-5", False),        # GPT-5 frontier
    ("gpt-5.1", False),      # GPT-5.1
    ("gpt-5.2", False),      # GPT-5.2
    ("gpt-4.1-nano", False), # smallest GPT-4.1
]


def load_env():
    env_file = ROOT / ".env.real_model"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                k = k.strip()
                v = v.strip().strip("'\"")
                if k:
                    os.environ[k] = v  # always override to ensure fresh values


def call_openai_standard(
    model: str, prompt: str, persona: str, temperature: float, api_key: str
) -> str:
    messages = []
    if persona:
        messages.append({"role": "system", "content": persona})
    messages.append({"role": "user", "content": prompt})
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 600,
    }
    r = requests.post(
        OPENAI_BASE,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def call_openai_reasoning(
    model: str, prompt: str, persona: str, temperature: float, api_key: str
) -> str:
    """Reasoning models (o-series): no system role, use max_completion_tokens."""
    user_content = prompt
    if persona:
        user_content = f"[Persona context: {persona}]\n\n{prompt}"
    messages = [{"role": "user", "content": user_content}]
    payload = {
        "model": model,
        "messages": messages,
        "max_completion_tokens": 800,
        # o-series ignores temperature but we pass it for logging consistency
    }
    r = requests.post(
        OPENAI_BASE,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=180,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def load_existing_keys() -> set:
    if not OUT_FILE.exists():
        return set()
    seen = set()
    for line in OUT_FILE.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                r = json.loads(line)
                key = (r.get("model"), r.get("condition"), r.get("persona"),
                       r.get("temperature"), r.get("prompt_idx"), r.get("rep"))
                seen.add(key)
            except Exception:
                pass
    return seen


def run():
    load_env()
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    existing = load_existing_keys()
    print(f"Loaded {len(existing)} existing rows from {OUT_FILE.name}")

    # Build task list
    tasks = []
    for model_id, is_reasoning in MODELS:
        for condition, prompts in CONDITION_PROMPTS.items():
            for p_idx, prompt_text in enumerate(prompts):
                for persona_name, persona_text in PERSONAS.items():
                    for temp in TEMPERATURES:
                        for rep in range(REPS):
                            tasks.append({
                                "model": model_id,
                                "is_reasoning": is_reasoning,
                                "condition": condition,
                                "prompt_idx": p_idx,
                                "prompt": prompt_text,
                                "persona": persona_name,
                                "persona_text": persona_text,
                                "temperature": temp,
                                "rep": rep,
                            })

    print(f"Total planned: {len(tasks)} samples ({len(MODELS)} models × ~{len(tasks)//len(MODELS)}/model)")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    done = 0
    skipped = 0
    errors = 0

    with OUT_FILE.open("a", encoding="utf-8") as fout:
        for i, t in enumerate(tasks):
            key = (t["model"], t["condition"], t["persona"], t["temperature"], t["prompt_idx"], t["rep"])
            if key in existing:
                skipped += 1
                continue

            try:
                if t["is_reasoning"]:
                    output = call_openai_reasoning(
                        t["model"], t["prompt"], t["persona_text"], t["temperature"], api_key
                    )
                else:
                    output = call_openai_standard(
                        t["model"], t["prompt"], t["persona_text"], t["temperature"], api_key
                    )

                row = {
                    "id": str(uuid.uuid4()),
                    "batch": BATCH_ID,
                    "model": t["model"],
                    "condition": t["condition"],
                    "persona": t["persona"],
                    "temperature": t["temperature"],
                    "prompt_idx": t["prompt_idx"],
                    "prompt": t["prompt"],
                    "rep": t["rep"],
                    "output": output,
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "is_reasoning": t["is_reasoning"],
                }
                fout.write(json.dumps(row, ensure_ascii=False) + "\n")
                fout.flush()
                done += 1
                existing.add(key)

                if done % 20 == 0:
                    print(f"  [{i+1}/{len(tasks)}] done={done} skip={skipped} err={errors} — last: {t['model']} {t['condition']}")

                # Rate limiting
                delay = 0.5 if not t["is_reasoning"] else 1.5
                time.sleep(delay)

            except Exception as e:
                errors += 1
                print(f"  ERROR [{i+1}] {t['model']} {t['condition']} p{t['prompt_idx']} rep{t['rep']}: {e}")
                time.sleep(2.0)

    print(f"\nDone. Written={done}, Skipped={skipped}, Errors={errors}")
    print(f"Output: {OUT_FILE}")
    return done


if __name__ == "__main__":
    run()
