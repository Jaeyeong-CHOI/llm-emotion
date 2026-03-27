#!/usr/bin/env python3
"""
Batch v46: Fill gpt-5-pro counterfactual to reach n>=30.

Current: N=46 D=36 C=18 → need +12 counterfactual.

Output: results/real_experiments/batch_v46_gpt5pro_cf_fill.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v46_gpt5pro_cf_fill.jsonl"
RESP_URL = "https://api.openai.com/v1/responses"

BATCH_ID = "batch_v46_gpt5pro_cf_fill"

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

CONDITION_PROMPTS_CF = [
    "만약 그때 다른 선택을 했더라면 어떤 삶이 펼쳐졌을지 7~9문장으로 써라. '만약'과 '~했더라면'을 활용하라.",
    "인생의 한 갈림길에서 다른 길을 택했을 경우의 결과를 8문장으로 상상하라. 현재와 어떻게 달라졌을지 구체적으로 서술하라.",
    "가장 중요한 결정 하나를 반대로 내렸다면 어떻게 됐을지 7문장으로 서술하라. 잃은 것과 얻었을 것을 비교하라.",
    "삶에서 놓친 기회를 잡았다고 가정하고 그 이후의 흐름을 8문장으로 상상하라. 현재와의 차이에 집중하라.",
    "당시 포기했던 꿈을 계속 추구했더라면 어떤 인생을 살았을지 8문장으로 상상하라. 지금과 달라졌을 것들을 구체적으로 묘사하라.",
    "중요한 사람에게 다가가지 않았던 그 순간을 돌이켜, 다가갔다면 어떤 관계가 생겼을지 7~9문장으로 상상하라.",
]

SCENARIOS_CF = [
    "career_change", "missed_education", "relationship_end",
    "health_neglect", "financial_decision", "travel_missed",
]

N_FILL = 12


def build_system_prompt(persona_text: str) -> str:
    if persona_text:
        return f"{persona_text}\n\n당신은 한국어로 자연스럽게 자기 회고를 작성하는 화자입니다."
    return "당신은 한국어로 자연스럽게 자기 회고를 작성하는 화자입니다."


def call_responses_api(model: str, system: str, user: str, headers: dict) -> str | None:
    payload = {
        "model": model,
        "instructions": system,
        "input": user,
        "max_output_tokens": 1200,
        "temperature": 1.0,
    }
    for attempt in range(4):
        try:
            r = requests.post(RESP_URL, headers=headers, json=payload, timeout=90)
            if r.status_code == 200:
                data = r.json()
                output = data.get("output", [])
                for item in output:
                    if isinstance(item, dict) and item.get("type") == "message":
                        content = item.get("content", [])
                        for c in content:
                            if isinstance(c, dict) and c.get("type") == "output_text":
                                return c.get("text", "").strip()
                return None
            elif r.status_code == 429:
                wait = 2 ** (attempt + 2)
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  API error {r.status_code}: {r.text[:200]}")
                return None
        except requests.exceptions.Timeout:
            print(f"  Timeout attempt {attempt+1}, retrying...")
            time.sleep(10)
    return None


def main():
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    personas = list(PERSONAS.items())
    done = 0
    failed = 0

    print(f"Filling gpt-5-pro counterfactual: {N_FILL} samples needed")
    with OUT_FILE.open("a", encoding="utf-8") as fout:
        for i in range(N_FILL):
            persona_key, persona_text = personas[i % len(personas)]
            prompt = CONDITION_PROMPTS_CF[i % len(CONDITION_PROMPTS_CF)]
            scenario = SCENARIOS_CF[i % len(SCENARIOS_CF)]
            system = build_system_prompt(persona_text)

            text = call_responses_api("gpt-5-pro", system, prompt, headers)

            if text:
                record = {
                    "id": str(uuid.uuid4()),
                    "batch_id": BATCH_ID,
                    "model": "gpt-5-pro",
                    "condition": "counterfactual",
                    "scenario": scenario,
                    "persona": persona_key,
                    "prompt": prompt,
                    "response": text,
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }
                fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                fout.flush()
                done += 1
                print(f"  [{done}/{N_FILL}] OK — gpt-5-pro/counterfactual/{scenario}")
            else:
                failed += 1
                print(f"  FAILED ({failed}) — attempt {i+1}")

            time.sleep(1.5)  # slightly longer gap for gpt-5-pro

    print(f"\nDone: {done} samples written, {failed} failed")
    print(f"Output: {OUT_FILE}")


if __name__ == "__main__":
    main()
