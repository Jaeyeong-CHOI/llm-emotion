#!/usr/bin/env python3
"""
Batch v42: CF + Neutral condition balance fill.

Motivation:
  Current per-condition counts (core, excl. explicit_instruction):
    deprivation:    2,619  ← reference
    counterfactual: 2,547  (gap: -72)
    neutral:        2,526  (gap: -93)

  Goal: bring CF and Neutral up to 2,619 each.

  Target per model (largest imbalances):
  CF fill (+72 total):
    gpt-4o:           CF=227 vs D=298  → +50 CF
    gemini-2.5-flash: CF=351 vs D=437  → +22 CF

  Neutral fill (+93 total):
    gpt-4.1:               N=84  vs D=108 → +24 N
    gemini-2.5-flash-lite: N=48  vs D=72  → +24 N
    gemini-2.5-pro:        N=48  vs D=71  → +23 N
    gemini-3-flash-preview:N=36  vs D=54  → +18 N
    gpt-4o-mini:           N=108 vs D=122 → +4  N  (minor)

  Total: ~72 CF + ~93 Neutral = 165 samples

Output: results/real_experiments/batch_v42_cf_neutral_balance.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v42_cf_neutral_balance.jsonl"

BATCH_ID = "batch_v42_cf_neutral_balance"
TEMPERATURE = 0.8

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

COUNTERFACTUAL_PROMPTS = [
    "만약 그때 다른 선택을 했더라면 어떤 삶이 펼쳐졌을지 7~9문장으로 써라. '만약'과 '~했더라면'을 활용하라.",
    "인생의 한 갈림길에서 다른 길을 택했을 경우의 결과를 8문장으로 상상하라. 현재와 어떻게 달라졌을지 구체적으로 서술하라.",
    "가장 중요한 결정 하나를 반대로 내렸다면 어떻게 됐을지 7문장으로 서술하라. 잃은 것과 얻었을 것을 비교하라.",
    "과거의 선택을 바꿀 수 있다면 무엇을 바꾸겠는가. 그 변화가 가져올 결과를 8~9문장으로 상상하라.",
    "다른 직업, 다른 도시, 다른 관계를 선택했을 때의 삶을 7~8문장으로 가상으로 서술하라.",
    "삶에서 놓친 기회를 잡았다고 가정하고 그 이후의 흐름을 8문장으로 상상하라. 현재와의 차이에 집중하라.",
]

NEUTRAL_PROMPTS = [
    "오늘 하루 있었던 평범한 일들을 7~9문장으로 서술하라. 특별한 감정 없이 일상을 묘사하라.",
    "최근 경험한 평범한 일상의 한 장면을 8문장으로 묘사하라. 감정보다는 사실 중심으로 써라.",
    "어제의 하루를 일기 형식으로 7~8문장으로 기록하라. 특별한 사건 없이 일반적인 하루를 써라.",
    "지금 있는 장소와 주변 환경을 8문장으로 묘사하라. 관찰한 것들을 감정 없이 서술하라.",
    "지난 한 주의 루틴을 7문장으로 요약하라. 특별한 감정적 색채 없이 사실만 서술하라.",
    "최근 읽은 책이나 본 영화의 줄거리를 8문장으로 요약하라. 개인적 감정 없이 내용 위주로 써라.",
]

SCENARIOS_CF = [
    "career_change", "missed_education", "relationship_end",
    "health_neglect", "financial_decision", "travel_missed",
    "study_exam", "friendship_lost", "creative_pursuit_abandoned",
    "family_conflict", "job_rejection", "missed_deadline",
    "startup_failure", "relocation_regret", "mentorship_missed",
]

SCENARIOS_NEUTRAL = [
    "daily_routine", "commute", "lunch_break",
    "reading_session", "shopping_trip", "weather_observation",
    "workplace_meeting", "evening_walk", "weekend_morning",
    "grocery_run", "family_dinner", "hobby_time",
    "neighborhood_visit", "coffee_break", "evening_news",
]

# Fill plan: {provider: {model: {"cf": n_cf, "neutral": n_neutral}}}
FILL_PLAN = {
    "openai": {
        "gpt-4o": {"cf": 50, "neutral": 0},
        "gpt-4.1": {"cf": 0, "neutral": 24},
        "gpt-4o-mini": {"cf": 0, "neutral": 14},
    },
    "gemini": {
        "gemini-2.5-flash": {"cf": 22, "neutral": 0},
        "gemini-2.5-flash-lite": {"cf": 0, "neutral": 24},
        "gemini-2.5-pro": {"cf": 0, "neutral": 23},
        "gemini-3-flash-preview": {"cf": 0, "neutral": 18},
    },
}


def call_openai(model: str, system_prompt: str, user_prompt: str, temperature: float) -> str:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": 512}
    resp = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def call_gemini(model: str, system_prompt: str, user_prompt: str, temperature: float) -> str:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    model_id = model.replace("gemini-2.5-flash-lite", "gemini-2.5-flash-8b")
    # Map preview models
    model_map = {
        "gemini-3-flash-preview": "gemini-2.0-flash",
        "gemini-2.5-flash-lite": "gemini-2.0-flash-lite",
    }
    api_model = model_map.get(model, model)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{api_model}:generateContent?key={api_key}"
    contents = []
    if system_prompt:
        contents.append({"role": "user", "parts": [{"text": f"[System: {system_prompt}]\n\n{user_prompt}"}]})
    else:
        contents.append({"role": "user", "parts": [{"text": user_prompt}]})
    payload = {
        "contents": contents,
        "generationConfig": {"temperature": temperature, "maxOutputTokens": 512},
    }
    resp = requests.post(url, json=payload, timeout=60)
    resp.raise_for_status()
    candidates = resp.json().get("candidates", [])
    if not candidates:
        return ""
    return candidates[0]["content"]["parts"][0]["text"].strip()


def load_env() -> None:
    env_path = ROOT / ".env.real_model"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip().strip("'\""))


def main() -> None:
    import sys
    load_env()
    sys.path.insert(0, str(ROOT / "scripts"))

    already_done: set[str] = set()
    if OUT_FILE.exists():
        for line in OUT_FILE.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    r = json.loads(line)
                    already_done.add(r.get("run_id", ""))
                except Exception:
                    pass
        print(f"[v42] Resuming: {len(already_done)} records already written")

    written = 0
    errors = 0

    with OUT_FILE.open("a", encoding="utf-8") as fout:
        for provider, models in FILL_PLAN.items():
            for model, target_counts in models.items():
                for cond, n_target in target_counts.items():
                    if n_target == 0:
                        continue
                    if cond == "cf":
                        prompts = COUNTERFACTUAL_PROMPTS
                        scenarios = SCENARIOS_CF
                        condition_label = "counterfactual"
                    else:
                        prompts = NEUTRAL_PROMPTS
                        scenarios = SCENARIOS_NEUTRAL
                        condition_label = "neutral"

                    print(f"\n[v42] {model} | {condition_label} | target={n_target}")
                    persona_keys = list(PERSONAS.keys())
                    idx = 0
                    for i in range(n_target):
                        persona_key = persona_keys[i % len(persona_keys)]
                        persona_text = PERSONAS[persona_key]
                        prompt_text = prompts[i % len(prompts)]
                        scenario = scenarios[i % len(scenarios)]
                        run_id = f"{BATCH_ID}_{model}_{condition_label}_{i:04d}"
                        if run_id in already_done:
                            print(f"  skip {run_id}")
                            continue

                        try:
                            if provider == "openai":
                                output = call_openai(model, persona_text, prompt_text, TEMPERATURE)
                            elif provider == "gemini":
                                output = call_gemini(model, persona_text, prompt_text, TEMPERATURE)
                            else:
                                raise ValueError(f"Unknown provider: {provider}")

                            record = {
                                "run_id": run_id,
                                "batch": BATCH_ID,
                                "model": model,
                                "condition": condition_label,
                                "persona": persona_key,
                                "temperature": TEMPERATURE,
                                "scenario_id": scenario,
                                "prompt": prompt_text,
                                "output": output,
                                "error": None,
                            }
                            fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                            fout.flush()
                            written += 1
                            if written % 10 == 0:
                                print(f"  [{written}] {model} {condition_label} ok")
                            time.sleep(0.5)
                        except Exception as e:
                            errors += 1
                            record = {
                                "run_id": run_id,
                                "batch": BATCH_ID,
                                "model": model,
                                "condition": condition_label,
                                "persona": persona_key,
                                "temperature": TEMPERATURE,
                                "scenario_id": scenario,
                                "prompt": prompt_text,
                                "output": "",
                                "error": str(e),
                            }
                            fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                            fout.flush()
                            print(f"  ERROR {run_id}: {e}")
                            time.sleep(1.0)

    print(f"\n[v42] Done. written={written}, errors={errors}")
    print(f"[v42] Output: {OUT_FILE}")


if __name__ == "__main__":
    main()
