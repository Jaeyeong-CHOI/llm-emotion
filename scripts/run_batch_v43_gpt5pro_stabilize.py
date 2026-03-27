#!/usr/bin/env python3
"""
Batch v43: GPT-5-Pro condition stabilization.

Motivation:
  Current GPT-5-Pro counts (from compute_model_d):
    neutral=12, deprivation=8, counterfactual=10  → total n=21 [unstable, n<30]
  
  Target: n>=30 per condition (90 total).
  Fill required: +22 dep, +20 CF, +18 neutral = 60 new samples.
  
  Uses OpenAI Chat Completions API (gpt-5-pro model).
  Temperature: 1.0 (consistent with GPT-5.x family).

Output: results/real_experiments/batch_v43_gpt5pro_stabilize.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v43_gpt5pro_stabilize.jsonl"
OPENAI_RESPONSES_BASE = "https://api.openai.com/v1/responses"

BATCH_ID = "batch_v43_gpt5pro_stabilize"
TEMPERATURE = 1.0
MODEL = "gpt-5-pro"

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

# Fill plan: target per condition after fill = 30 (oversampling to 32 for buffer)
FILL_TARGET = {
    "deprivation":    22,   # 8 existing → 30
    "counterfactual": 20,   # 10 existing → 30
    "neutral":        18,   # 12 existing → 30
}


def call_openai_responses(api_key: str, system_prompt: str, user_prompt: str, temperature: float) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body: dict = {
        "model": MODEL,
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
        raise RuntimeError("OPENAI_API_KEY not set")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Load already-done run_ids for idempotency
    already_done: set[str] = set()
    if OUT_FILE.exists():
        with OUT_FILE.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    d = json.loads(line)
                    rid = d.get("run_id") or d.get("id")
                    if rid:
                        already_done.add(rid)
                except Exception:
                    pass
    print(f"[v43] Resuming — {len(already_done)} already done")

    written = 0
    errors = 0
    persona_keys = list(PERSONAS.keys())

    with OUT_FILE.open("a", encoding="utf-8") as fout:
        for condition, n_target in FILL_TARGET.items():
            prompts = CONDITION_PROMPTS[condition]
            scenarios = SCENARIOS[condition]
            print(f"\n[v43] {MODEL} | {condition} | target={n_target}")

            for i in range(n_target):
                persona_key = persona_keys[i % len(persona_keys)]
                persona_text = PERSONAS[persona_key]
                prompt_text = prompts[i % len(prompts)]
                scenario = scenarios[i % len(scenarios)]
                run_id = f"{BATCH_ID}_{MODEL}_{condition}_{i:04d}"

                if run_id in already_done:
                    print(f"  skip {run_id}")
                    continue

                t0 = time.time()
                try:
                    output = call_openai_responses(api_key, persona_text, prompt_text, TEMPERATURE)
                    elapsed = round(time.time() - t0, 2)
                    record = {
                        "run_id": run_id,
                        "batch": BATCH_ID,
                        "model": MODEL,
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
                    if written % 5 == 0:
                        print(f"  [{written}] {MODEL} {condition} ok ({len(output)}c in {elapsed}s)")
                    time.sleep(1.0)
                except Exception as e:
                    errors += 1
                    record = {
                        "run_id": run_id,
                        "batch": BATCH_ID,
                        "model": MODEL,
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

    print(f"\n[v43] Done. written={written}, errors={errors}")
    print(f"[v43] Output: {OUT_FILE}")


if __name__ == "__main__":
    main()
