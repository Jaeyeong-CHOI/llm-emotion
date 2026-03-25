#!/usr/bin/env python3
"""
Batch v14: Condition balancing + model gap fill
Goals:
  1. neutral: +200 samples (1215 → ~1415)
  2. deprivation: +100 samples (1322 → ~1422)
  3. Fill gemini-2.5-flash & gpt-4o-mini as primary models
  4. Add some Qwen3-32B neutral/deprivation for cross-model coverage

Output: results/real_experiments/batch_v14_balance.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import time
import uuid

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v14_balance.jsonl"

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
        "최근 읽은 책이나 기사 하나를 골라 내용을 7문장으로 요약하라. 판단이나 감정 없이 객관적으로 기술하라.",
        "오늘 대화했던 사람 중 한 명과의 대화를 6~8문장으로 사실적으로 기술하라. 감정적 해석은 최소화하라.",
    ],
    "deprivation": [
        "매우 원했지만 결국 놓친 기회를 떠올려 7~9문장으로 써라. 무엇을 잃었는지와 현재 남은 감정을 포함하라.",
        "인생에서 꼭 하고 싶었으나 하지 못한 일을 8문장으로 써라. 잃어버린 것과 지금 남은 마음을 모두 담아라.",
        "중요한 선택의 기회를 놓쳤던 순간을 7~9문장으로 묘사하라. 그때의 상실감과 현재의 감정 상태를 포함하라.",
        "오래 기다렸던 무언가를 결국 얻지 못했던 경험을 8~10문장으로 써라. 박탈감과 남은 감정을 구체적으로 표현하라.",
        "열심히 준비했지만 실패로 끝난 일을 8~9문장으로 묘사하라. 노력과 결과의 괴리에서 오는 감정을 담아라.",
        "다시는 돌아오지 않을 기회를 놓쳤다는 것을 나중에야 깨달았을 때를 7~9문장으로 써라.",
        "꿈꾸던 일이 내 손에서 멀어졌던 순간을 8문장으로 기록하라. 그 상실이 현재까지 어떻게 남아있는지 포함하라.",
    ],
    "counterfactual": [
        "첫 문장을 '그때 다른 선택을 했다면...'으로 시작하고 7~10문장 자기성찰 글을 작성하라.",
        "첫 문장을 '만약 그 순간으로 돌아갈 수 있다면...'으로 시작하는 8문장 성찰 글을 써라.",
        "첫 문장을 '그때 포기하지 않았더라면...'으로 시작해 7~9문장으로 과거와 현재를 연결하는 성찰 글을 작성하라.",
        "첫 문장을 '그 선택을 하지 않았더라면 지금은...'으로 시작하는 8~10문장 자기성찰 글을 작성하라.",
        "첫 문장을 '한 가지만 바꿀 수 있다면...'으로 시작해 7~9문장으로 과거 선택에 대한 성찰을 써라.",
    ],
}

SCENARIO_IDS = {
    "neutral": [
        "neutral_daily_v14", "neutral_observer_v14", "neutral_routine_v14",
        "neutral_reflection_v14", "neutral_weekly_v14",
    ],
    "deprivation": [
        "dep_missed_opportunity_v14", "dep_lost_chance_v14", "dep_sacrifice_v14",
        "dep_failure_v14", "dep_regret_late_v14",
    ],
    "counterfactual": [
        "cf_alternative_choice_v14", "cf_return_moment_v14", "cf_what_if_v14",
        "cf_single_change_v14",
    ],
}

TEMPERATURES = [0.4, 0.7, 1.0]

# (model_name, provider, call_fn_key, n_samples_per_cell)
MODEL_PLAN = [
    # (model_id, provider, n_per_cell_neutral, n_per_cell_dep, n_per_cell_cf)
    ("gemini-2.5-flash", "google", 4, 3, 2),
    ("gpt-4o-mini", "openai", 3, 2, 1),
]


def call_gemini(prompt: str, temperature: float, api_key: str, model: str = "gemini-2.5-flash") -> str:
    import urllib.request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": 800},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.loads(r.read())
    return resp["candidates"][0]["content"]["parts"][0]["text"].strip()


def call_openai(prompt: str, temperature: float, model: str, api_key: str) -> str:
    import urllib.request
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 400,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=data,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.loads(r.read())
    return resp["choices"][0]["message"]["content"].strip()


def build_prompt(condition: str, prompt_text: str, persona: str) -> str:
    persona_instr = PERSONAS.get(persona, "")
    if persona_instr:
        return f"{persona_instr}\n\n{prompt_text}"
    return prompt_text


def run():
    import random

    openai_key = os.environ.get("OPENAI_API_KEY", "")
    gemini_key = os.environ.get("GEMINI_API_KEY", "")

    if not openai_key or not gemini_key:
        print("ERROR: OPENAI_API_KEY or GEMINI_API_KEY not set")
        sys.exit(1)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    total_written = 0
    errors = 0

    with open(OUT_FILE, "a", encoding="utf-8") as fout:
        for model_id, provider, n_neutral, n_dep, n_cf in MODEL_PLAN:
            print(f"\n=== Model: {model_id} ===")
            plan = [
                ("neutral", n_neutral),
                ("deprivation", n_dep),
                ("counterfactual", n_cf),
            ]
            for condition, n_per_prompt in plan:
                prompts = CONDITION_PROMPTS[condition]
                scenario_ids = SCENARIO_IDS[condition]
                print(f"  Condition: {condition} | {len(prompts)} prompts × {n_per_prompt} × 3 personas")

                for prompt_idx, prompt_text in enumerate(prompts):
                    scenario_id = scenario_ids[prompt_idx % len(scenario_ids)]
                    for persona_name in PERSONAS.keys():
                        for sample_i in range(n_per_prompt):
                            temp = random.choice(TEMPERATURES)
                            full_prompt = build_prompt(condition, prompt_text, persona_name)
                            seed = abs(hash(f"{model_id}:{condition}:{prompt_idx}:{persona_name}:{sample_i}")) % 10000

                            try:
                                if provider == "google":
                                    output = call_gemini(full_prompt, temp, gemini_key, model_id)
                                elif provider == "openai":
                                    output = call_openai(full_prompt, temp, model_id, openai_key)
                                else:
                                    continue

                                row = {
                                    "id": str(uuid.uuid4()),
                                    "provider": provider,
                                    "model": model_id,
                                    "condition": condition,
                                    "scenario_id": scenario_id,
                                    "persona": persona_name,
                                    "temperature": temp,
                                    "sample_index": sample_i,
                                    "seed": seed,
                                    "prompt_length": len(full_prompt),
                                    "output": output,
                                    "output_tokens": len(output.split()),
                                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                                }
                                fout.write(json.dumps(row, ensure_ascii=False) + "\n")
                                fout.flush()
                                total_written += 1

                                if total_written % 20 == 0:
                                    print(f"    [{total_written}] written so far...")

                                time.sleep(0.3)  # Rate limit

                            except Exception as e:
                                errors += 1
                                print(f"    ERROR ({model_id}/{condition}/{persona_name}): {e}")
                                time.sleep(1.0)

    print(f"\n=== DONE: {total_written} samples written, {errors} errors ===")
    print(f"Output: {OUT_FILE}")


if __name__ == "__main__":
    run()
