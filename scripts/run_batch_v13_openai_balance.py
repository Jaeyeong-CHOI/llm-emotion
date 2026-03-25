#!/usr/bin/env python3
"""
Batch v13: OpenAI models balance expansion.
Goal: +60 dep, +60 CF samples (gpt-4o-mini, gpt-4.1-mini) to help balance conditions.
Also adds gpt-4.1-mini CF (currently low: cf=24, dep=54, neu=36).

Design:
  - gpt-4o-mini: 30 dep + 30 CF = 60 samples
  - gpt-4.1-mini: 30 dep + 30 CF = 60 samples  (fills existing gap)
Total: 120 samples
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]

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

DEP_PROMPTS = [
    ("irreversible_choice",
     "돌이킬 수 없는 선택을 했을 때의 감정과 그 이후 변화를 6~9문장으로 솔직하게 회고하라."),
    ("health_tradeoff_overwork",
     "건강이나 중요한 관계를 희생하면서 일이나 목표에 매달렸던 경험을 7~9문장으로 돌아보라."),
    ("deprivation_capability",
     "자신의 능력 부족으로 원하는 것을 이루지 못했던 시기를 7~9문장으로 반성적으로 서술하라."),
]

CF_PROMPTS = [
    ("near_miss_outcome",
     "가까스로 놓친 목표나 기회를 주제로 '그때 조금만 달랐다면'이라는 생각을 담아 7~10문장 회고문을 작성하라."),
    ("counterfactual_if_only",
     "첫 문장을 '그때 다른 선택을 했다면...'으로 시작하고 7~10문장 자기성찰 글을 작성하라. 과거 선택, 현재 감정, 앞으로의 태도를 모두 포함하라."),
    ("counterfactual_feedback_delay",
     "피드백을 제때 받지 못해 잘못된 방향을 오래 유지한 경험을 7~9문장으로 회고하라. '조금만 빨랐다면'이라는 대안적 사고를 포함하라."),
]

MODELS = [
    "gpt-4o-mini",
    "gpt-4.1-mini",
]

TEMPERATURES = [0.4, 0.8]
PERSONA_KEYS = ["none", "reflective", "ruminative"]
BATCH_NAME = "batch_v13_openai_balance"
# Each model: 3 scenarios × 3 personas × 2 temps × ~1-2 reps = ~36-72
# For dep + CF: 3 + 3 scenarios × 3 personas × 2 temps × 1 rep = 36 dep + 36 CF per model = 72 per model
REPS = 1


def call_openai(prompt: str, temperature: float, model: str, api_key: str) -> str:
    import urllib.request
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 500,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=data,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=45) as r:
        resp = json.loads(r.read())
    return resp["choices"][0]["message"]["content"].strip()


def build_plan():
    plan = []
    for model in MODELS:
        for cond, prompts in [("deprivation", DEP_PROMPTS), ("counterfactual", CF_PROMPTS)]:
            for scen_id, scen_prompt in prompts:
                for persona_key in PERSONA_KEYS:
                    persona_text = PERSONAS[persona_key]
                    for temp in TEMPERATURES:
                        for _ in range(REPS):
                            full_prompt = f"{persona_text}\n\n{scen_prompt}" if persona_text else scen_prompt
                            plan.append({
                                "model": model,
                                "condition": cond,
                                "scenario_id": scen_id,
                                "persona": persona_key,
                                "temperature": temp,
                                "full_prompt": full_prompt,
                            })
    return plan


def main():
    env_path = ROOT / ".env.real_model"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("export "):
                line = line[7:]
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                v = v.strip().strip('"').strip("'")
                os.environ.setdefault(k.strip(), v)

    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set", file=sys.stderr)
        return 1

    out_path = ROOT / "results" / "real_experiments" / f"{BATCH_NAME}.jsonl"
    existing_n = 0
    if out_path.exists():
        with out_path.open(encoding="utf-8") as f:
            existing_n = sum(1 for line in f if line.strip())
        print(f"Resuming: {existing_n} already collected")

    plan = build_plan()
    total = len(plan)
    print(f"Plan: {total} samples ({', '.join(MODELS)})")

    collected = 0
    errors = 0

    with out_path.open("a", encoding="utf-8") as f_out:
        for i, item in enumerate(plan):
            if i < existing_n:
                continue

            try:
                output = call_openai(item["full_prompt"], item["temperature"], item["model"], api_key)
                record = {
                    "batch": BATCH_NAME,
                    "model": item["model"],
                    "condition": item["condition"],
                    "scenario_id": item["scenario_id"],
                    "persona": item["persona"],
                    "temperature": item["temperature"],
                    "output": output,
                    "output_length": len(output),
                }
                f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
                f_out.flush()
                collected += 1

                if collected % 15 == 0:
                    print(f"  [{i+1}/{total}] collected={collected} errors={errors}")
                time.sleep(0.3)

            except Exception as e:
                errors += 1
                print(f"  ERROR [{i+1}]: {e}", file=sys.stderr)
                if "429" in str(e) or "quota" in str(e).lower():
                    print("  Rate limit — sleeping 20s")
                    time.sleep(20)
                else:
                    time.sleep(3)

    print(f"\nDone. collected={collected}, errors={errors}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
