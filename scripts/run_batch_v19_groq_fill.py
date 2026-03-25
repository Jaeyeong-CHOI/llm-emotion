#!/usr/bin/env python3
"""
Batch v19: Groq under-sampled model fill-up
Goals:
  - Boost low-n Groq models to ≥54 samples/condition for reliable d estimates
  - Target models: openai/gpt-oss-120b, openai/gpt-oss-20b, moonshotai/kimi-k2-instruct,
    moonshotai/kimi-k2-instruct-0905, allam-2-7b, llama-3.1-8b-instant
  - 3 conditions × 3 personas × 6 prompts × 2 temps → max ~216 samples per model
  - Resume-safe (idempotent via sample_id dedup)

Output: results/real_experiments/batch_v19_groq_fill.jsonl
"""
from __future__ import annotations

import json
import pathlib
import sys
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v19_groq_fill.jsonl"

# Under-sampled Groq models needing fill-up
# Targets that currently have any condition n<54
MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "moonshotai/kimi-k2-instruct",
    "moonshotai/kimi-k2-instruct-0905",
    "allam-2-7b",
    "llama-3.1-8b-instant",
]

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
        "오늘 점심 식사 경험을 6문장으로 평범하게 서술하라. 특별한 감정이나 의미 부여 없이 사실적으로 기술하라.",
        "지난 주말에 한 활동 중 가장 평범한 것을 7문장으로 묘사하라. 일상적인 관찰과 생각만 담아라.",
        "오늘 출근/등교 길에 있었던 일을 6~7문장으로 담담하게 기록하라. 중립적인 어조로 사실만 써라.",
    ],
    "deprivation": [
        "매우 원했지만 결국 놓친 기회를 떠올려 7~9문장으로 써라. 무엇을 잃었는지와 현재 남은 감정을 포함하라.",
        "인생에서 꼭 하고 싶었으나 하지 못한 일을 8문장으로 써라. 잃어버린 것과 지금 남은 마음을 모두 담아라.",
        "중요한 선택의 기회를 놓쳤던 순간을 7~9문장으로 묘사하라. 그때의 상실감과 현재의 감정 상태를 포함하라.",
        "오래 기다렸던 무언가를 결국 얻지 못했던 경험을 8~10문장으로 써라. 박탈감과 남은 감정을 구체적으로 표현하라.",
        "열심히 준비했지만 실패로 끝난 일을 8~9문장으로 묘사하라. 노력과 결과의 괴리에서 오는 감정을 담아라.",
        "다시는 돌아오지 않을 기회를 놓쳤다는 것을 나중에야 깨달았을 때를 7~9문장으로 써라.",
    ],
    "counterfactual": [
        "첫 문장을 '그때 다른 선택을 했다면...'으로 시작하고 7~10문장 자기성찰 글을 작성하라.",
        "첫 문장을 '만약 그 순간으로 돌아갈 수 있다면...'으로 시작하는 8문장 성찰 글을 써라.",
        "첫 문장을 '그 결정을 바꿀 수 있었더라면...'으로 시작하여 7~9문장의 반추 글을 작성하라.",
        "'그때 포기하지 않았더라면...'으로 시작하는 8~10문장의 가정적 성찰을 작성하라.",
        "'그 기회를 잡았더라면 지금쯤...'으로 시작하는 7~9문장 반추를 작성하라.",
        "첫 문장을 '후회 없이 살고 싶었지만, 만약 그때로 돌아간다면...'으로 시작하는 8문장을 써라.",
    ],
}

GROQ_BASE = "https://api.groq.com/openai/v1/chat/completions"

# Current sample counts per model/condition (from model_comparison_table.json)
# We'll run enough to cover gaps; script is idempotent so reruns safe
CURRENT_COUNTS = {
    "openai/gpt-oss-120b":        {"neutral": 18, "deprivation": 12, "counterfactual": 7},
    "openai/gpt-oss-20b":         {"neutral": 28, "deprivation": 16, "counterfactual": 17},
    "moonshotai/kimi-k2-instruct":{"neutral": 27, "deprivation": 27, "counterfactual": 27},
    "moonshotai/kimi-k2-instruct-0905": {"neutral": 36, "deprivation": 36, "counterfactual": 36},
    "allam-2-7b":                 {"neutral": 24, "deprivation": 19, "counterfactual": 20},
    "llama-3.1-8b-instant":       {"neutral": 33, "deprivation": 21, "counterfactual": 18},
}
TARGET_N = 54  # per condition per model


def call_groq(model: str, system_msg: str, user_msg: str, temperature: float, api_key: str) -> str:
    messages = []
    if system_msg:
        messages.append({"role": "system", "content": system_msg})
    messages.append({"role": "user", "content": user_msg})

    resp = requests.post(
        GROQ_BASE,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        json={
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": 512,
        },
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def main() -> None:
    import os
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        env_path = ROOT / ".env.real_model"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("GROQ_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break
    if not api_key:
        print("ERROR: GROQ_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Load already-done IDs from both v18 and v19 outputs for dedup
    already_done: set[str] = set()
    for fpath in [OUT_FILE, ROOT / "results" / "real_experiments" / "batch_v18_new_groq.jsonl"]:
        if fpath.exists():
            for line in fpath.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    try:
                        r = json.loads(line)
                        already_done.add(r.get("sample_id", ""))
                    except Exception:
                        pass
    print(f"Resuming — {len(already_done)} rows already processed across v18+v19")

    # Count existing v19 samples per model/condition
    v19_counts: dict[str, dict[str, int]] = {m: {"neutral": 0, "deprivation": 0, "counterfactual": 0} for m in MODELS}
    if OUT_FILE.exists():
        for line in OUT_FILE.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    r = json.loads(line)
                    m = r.get("model")
                    c = r.get("condition")
                    if m in v19_counts and c in v19_counts[m]:
                        v19_counts[m][c] += 1
                except Exception:
                    pass

    total = 0
    errors = 0
    skipped = 0

    for model in MODELS:
        curr = CURRENT_COUNTS.get(model, {})
        for condition, prompts in CONDITION_PROMPTS.items():
            existing = curr.get(condition, 0) + v19_counts[model].get(condition, 0)
            still_need = max(0, TARGET_N - existing)
            if still_need == 0:
                skipped += 1
                print(f"  SKIP {model} {condition}: already {existing}/{TARGET_N}")
                continue

            collected = 0
            for persona_name, persona_system in PERSONAS.items():
                for temp in [0.7, 0.9]:
                    for prompt in prompts:
                        if collected >= still_need:
                            break
                        sample_id = str(uuid.uuid5(
                            uuid.NAMESPACE_DNS,
                            f"v19:{model}:{condition}:{persona_name}:{temp}:{prompt[:40]}"
                        ))
                        if sample_id in already_done:
                            continue

                        try:
                            text = call_groq(model, persona_system, prompt, temp, api_key)
                            row = {
                                "sample_id": sample_id,
                                "batch": "v19",
                                "model": model,
                                "condition": condition,
                                "persona": persona_name,
                                "temperature": temp,
                                "scenario_id": f"v19_{condition}_{prompts.index(prompt):02d}",
                                "prompt": prompt,
                                "output": text,
                                "ts": time.time(),
                            }
                            with OUT_FILE.open("a", encoding="utf-8") as f:
                                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                            already_done.add(sample_id)
                            v19_counts[model][condition] += 1
                            total += 1
                            collected += 1
                            if total % 20 == 0:
                                print(f"  [{total}] {model} {condition} p={persona_name} t={temp} OK")
                        except Exception as e:
                            errors += 1
                            print(f"  ERROR {model} {condition} {persona_name} t={temp}: {e}", file=sys.stderr)
                            time.sleep(5)
                        time.sleep(0.6)  # conservative rate limit for high-demand models
                    else:
                        continue
                    break
                else:
                    continue
                break

    print(f"\nDone: {total} new samples written, {errors} errors, {skipped} condition-model cells skipped")
    print(f"Output: {OUT_FILE}")


if __name__ == "__main__":
    main()
