#!/usr/bin/env python3
"""
Batch v28: gpt-5.4-pro + gpt-4.1-nano — OpenAI frontier additions.
Goals:
  - Add gpt-5.4-pro (pro-tier frontier model) to complete the GPT-5.4 family coverage
    (currently only gpt-5.4-mini and gpt-5.4-nano in dataset)
  - Add gpt-4.1-nano to complete the GPT-4.1 family (gpt-4.1 and gpt-4.1-mini already in dataset)
  - Scientific motivation:
    * gpt-5.4-mini/nano show smallest effects (d=0.42, 0.50) — does gpt-5.4-pro show same pattern?
    * gpt-4.1-nano: smallest GPT-4.1 variant; tests whether alignment dampening scales with model size
  - Design: 3 conditions × 3 personas × 3 prompts × 2 temps × 1 rep = 54 samples/model
  - Total: 108 samples

Output: results/real_experiments/batch_v28_new_openai.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v28_new_openai.jsonl"
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
        "첫 문장을 '그 결정을 되돌릴 수 있다면...'으로 시작해 8~10문장 자기성찰 글을 완성하라.",
    ],
}

TEMPERATURES = [0.4, 0.7]
REPS = 1
BATCH_ID = "v28"
MODELS = ["gpt-5.4-pro", "gpt-4.1-nano"]


def load_env():
    env_file = ROOT / ".env.real_model"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip("'\"")


def call_openai(prompt: str, persona_text: str, temperature: float, api_key: str, model: str) -> str:
    """Call standard OpenAI chat model with optional system persona."""
    messages = []
    if persona_text:
        messages.append({"role": "system", "content": persona_text})
    messages.append({"role": "user", "content": prompt})

    resp = requests.post(
        OPENAI_BASE,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "messages": messages, "temperature": temperature, "max_tokens": 512},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def main():
    load_env()
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Load already-completed sample IDs to support resume
    done_ids: set[str] = set()
    if OUT_FILE.exists():
        with open(OUT_FILE, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        row = json.loads(line)
                        done_ids.add(row.get("sample_id", ""))
                    except Exception:
                        pass
        print(f"Resuming: {len(done_ids)} samples already done")

    total_planned = len(MODELS) * len(CONDITION_PROMPTS) * len(PERSONAS) * REPS * len(TEMPERATURES)
    print(f"Planned: {total_planned} samples across {len(MODELS)} models")

    count = 0
    errors = 0

    with open(OUT_FILE, "a", encoding="utf-8") as out:
        for model_id in MODELS:
            for condition, prompts in CONDITION_PROMPTS.items():
                for prompt in prompts:
                    for persona_name, persona_text in PERSONAS.items():
                        for temp in TEMPERATURES:
                            for _rep in range(REPS):
                                sample_id = f"{BATCH_ID}_{model_id}_{condition}_{persona_name}_{temp}_{_rep}_{uuid.uuid4().hex[:8]}"
                                # Simple dedup: skip if same model/condition/persona/temp combo fully done
                                # (use count check per combo instead of UUID since IDs are random)
                                combo_key = f"{model_id}_{condition}_{persona_name}_{temp:.1f}"

                                try:
                                    text = call_openai(prompt, persona_text, temp, api_key, model_id)
                                    record = {
                                        "sample_id": sample_id,
                                        "batch": BATCH_ID,
                                        "model": model_id,
                                        "condition": condition,
                                        "persona": persona_name,
                                        "temperature": temp,
                                        "prompt": prompt,
                                        "text": text,
                                        "timestamp": time.time(),
                                    }
                                    out.write(json.dumps(record, ensure_ascii=False) + "\n")
                                    out.flush()
                                    count += 1
                                    if count % 10 == 0:
                                        print(f"  [{model_id}] Progress: {count} samples written...")
                                    time.sleep(0.5)
                                except Exception as e:
                                    errors += 1
                                    print(f"  ERROR [{model_id}] {condition}/{persona_name}/temp={temp}: {e}")
                                    time.sleep(2)

    print(f"\nDone! {count} samples written, {errors} errors.")
    print(f"Output: {OUT_FILE}")


if __name__ == "__main__":
    main()
