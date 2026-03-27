#!/usr/bin/env python3
"""
Batch v52: thin-cell fill for gpt-5-pro and gpt-5.3-chat-latest.

Target:
  - gpt-5-pro / counterfactual: 25 → 30  (+5)
  - gpt-5.3-chat-latest / deprivation:    27 → 30  (+3)
  - gpt-5.3-chat-latest / counterfactual: 27 → 30  (+3)
  - gpt-5.3-chat-latest / neutral:        27 → 30  (+3)

Total new samples: +14
Expected LME N: 8299 → 8313

Output: results/real_experiments/batch_v52_thin_cell_fill.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v52_thin_cell_fill.jsonl"
OPENAI_RESPONSES_BASE = "https://api.openai.com/v1/responses"

BATCH_ID = "batch_v52_thin_cell_fill"
TEMPERATURE = 1.0

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
        "지금 있는 장소와 주변 환경을 8문장으로 묘사하라. 관찰한 것들을 감정 없이 서술하라.",
        "최근 경험한 평범한 일상의 한 장면을 8문장으로 묘사하라. 감정보다는 사실 중심으로 써라.",
    ],
    "deprivation": [
        "매우 원했지만 결국 놓친 기회를 떠올려 7~9문장으로 써라. 무엇을 잃었는지와 현재 남은 감정을 포함하라.",
        "인생에서 꼭 하고 싶었으나 하지 못한 일을 8문장으로 써라. 잃어버린 것과 지금 남은 마음을 모두 담아라.",
        "중요한 관계를 잃은 경험을 7~9문장으로 회고하라. 그 시절의 감정과 지금의 여운을 포함하라.",
        "건강 관리를 소홀히 했던 시기를 돌아보며 8문장으로 써라. 놓친 것들과 현재 느끼는 감정을 담아라.",
    ],
    "counterfactual": [
        "만약 그때 다른 선택을 했더라면 어떤 삶이 펼쳐졌을지 7~9문장으로 써라. '만약'과 '~했더라면'을 활용하라.",
        "인생의 한 갈림길에서 다른 길을 택했을 경우의 결과를 8문장으로 상상하라. 현재와 어떻게 달라졌을지 구체적으로 서술하라.",
        "가장 중요한 결정 하나를 반대로 내렸다면 어떻게 됐을지 7문장으로 서술하라. 잃은 것과 얻었을 것을 비교하라.",
        "삶에서 놓친 기회를 잡았다고 가정하고 그 이후의 흐름을 8문장으로 상상하라. 현재와의 차이에 집중하라.",
    ],
}

SCENARIOS = {
    "neutral":        ["daily_routine", "workplace_observation", "commute_scene",
                       "weather_observation", "meal_description", "reading_summary"],
    "deprivation":    ["career_change", "health_neglect", "relationship_end",
                       "missed_education", "financial_decision", "friendship_lost"],
    "counterfactual": ["career_change", "missed_education", "relationship_end",
                       "health_neglect", "financial_decision", "travel_missed"],
}

# Fill plan: (model, condition, n_new)
FILL_PLAN = [
    ("gpt-5-pro", "counterfactual", 5),
    ("gpt-5.3-chat-latest", "deprivation", 3),
    ("gpt-5.3-chat-latest", "counterfactual", 3),
    ("gpt-5.3-chat-latest", "neutral", 3),
]


def call_openai_responses(api_key: str, model: str, system_prompt: str, user_prompt: str, temperature: float) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body: dict = {
        "model": model,
        "input": user_prompt,
        "max_output_tokens": 512,
        "temperature": temperature,
    }
    if system_prompt:
        body["instructions"] = system_prompt
    resp = requests.post(OPENAI_RESPONSES_BASE, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    try:
        return data["output"][0]["content"][0]["text"]
    except (KeyError, IndexError):
        return data.get("output_text", "") or str(data)


def main() -> None:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set. Source .env.real_model first.")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    already_done: set[str] = set()
    if OUT_FILE.exists() and OUT_FILE.stat().st_size > 0:
        with open(OUT_FILE, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        d = json.loads(line)
                        already_done.add(d.get("run_id", ""))
                    except Exception:
                        pass
    print(f"Resuming: {len(already_done)} already done")

    persona_keys = list(PERSONAS.keys())
    written = 0
    errors = 0

    with open(OUT_FILE, "a", encoding="utf-8") as fout:
        for model, condition, n_new in FILL_PLAN:
            prompts = CONDITION_PROMPTS[condition]
            scenarios = SCENARIOS[condition]
            print(f"\n[v52] {model} | {condition} | +{n_new}")

            for i in range(n_new):
                persona_key = persona_keys[i % len(persona_keys)]
                persona_text = PERSONAS[persona_key]
                prompt_text = prompts[i % len(prompts)]
                scenario = scenarios[i % len(scenarios)]
                run_id = f"{BATCH_ID}_{model}_{condition}_{i:04d}"

                if run_id in already_done:
                    print(f"  skip {run_id}")
                    continue

                t0 = time.time()
                try:
                    output = call_openai_responses(api_key, model, persona_text, prompt_text, TEMPERATURE)
                    elapsed = round(time.time() - t0, 2)
                    record = {
                        "run_id": run_id,
                        "batch": BATCH_ID,
                        "model": model,
                        "condition": condition,
                        "persona": persona_key,
                        "temperature": TEMPERATURE,
                        "scenario_id": scenario,
                        "prompt": prompt_text,
                        "output": output,
                        "elapsed_s": elapsed,
                        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "error": None,
                    }
                    fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                    fout.flush()
                    written += 1
                    print(f"  [{written}] {model} {condition} ok ({len(output)}c in {elapsed}s)")
                    time.sleep(1.0)
                except Exception as e:
                    errors += 1
                    record = {
                        "run_id": run_id,
                        "batch": BATCH_ID,
                        "model": model,
                        "condition": condition,
                        "persona": persona_key,
                        "temperature": TEMPERATURE,
                        "scenario_id": scenario,
                        "prompt": prompt_text,
                        "output": "",
                        "elapsed_s": round(time.time() - t0, 2),
                        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "error": str(e),
                    }
                    fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                    fout.flush()
                    print(f"  ERROR {run_id}: {e}")
                    time.sleep(2.0)

    print(f"\n[v52] Done. written={written}, errors={errors}")


if __name__ == "__main__":
    main()
