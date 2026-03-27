#!/usr/bin/env python3
"""
Batch v45: Final stabilization for gpt-5-pro and gpt-5.3-chat-latest.

Motivation:
  Remaining unstable models (emb counts):
    gpt-5-pro:         n_N=9,  n_D=15, n_C=6  → needs N+21, D+15, C+24
    gpt-5.3-chat-latest: n_N=27, n_D=27, n_C=27 → needs +3 each

  Target: n >= 30 per condition per model for stability.
  Total new samples: 60 + 9 = 69

  gpt-5-pro → OpenAI Responses API (max_output_tokens=1200)
  gpt-5.3-chat-latest → Chat Completions API (max_completion_tokens=1200)

Output: results/real_experiments/batch_v45_stabilize_final.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v45_stabilize_final.jsonl"
CHAT_URL = "https://api.openai.com/v1/chat/completions"
RESP_URL = "https://api.openai.com/v1/responses"

BATCH_ID = "batch_v45_stabilize_final"

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

# Fill plans
FILL_PLAN = {
    "gpt-5-pro": {
        "neutral":        21,
        "deprivation":    15,
        "counterfactual": 24,
    },
    "gpt-5.3-chat-latest": {
        "neutral":        3,
        "deprivation":    3,
        "counterfactual": 3,
    },
}


def build_system_prompt(persona_text: str) -> str:
    if persona_text:
        return f"{persona_text}\n\n당신은 한국어로 자연스럽게 자기 회고를 작성하는 화자입니다."
    return "당신은 한국어로 자연스럽게 자기 회고를 작성하는 화자입니다."


def call_responses_api(model: str, system: str, user: str, headers: dict) -> str | None:
    """OpenAI Responses API for gpt-5-pro."""
    payload = {
        "model": model,
        "instructions": system,
        "input": user,
        "max_output_tokens": 1200,
        "temperature": 1.0,
    }
    for attempt in range(3):
        try:
            r = requests.post(RESP_URL, headers=headers, json=payload, timeout=60)
            if r.status_code == 200:
                data = r.json()
                # responses API: output is a list of content items
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
            print(f"  Timeout attempt {attempt+1}")
            time.sleep(5)
    return None


def call_chat_api(model: str, system: str, user: str, headers: dict) -> str | None:
    """OpenAI Chat Completions API for gpt-5.3-chat-latest."""
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "max_completion_tokens": 1200,
        "temperature": 1.0,
    }
    for attempt in range(3):
        try:
            r = requests.post(CHAT_URL, headers=headers, json=payload, timeout=60)
            if r.status_code == 200:
                data = r.json()
                return data["choices"][0]["message"]["content"].strip()
            elif r.status_code == 429:
                wait = 2 ** (attempt + 2)
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  API error {r.status_code}: {r.text[:200]}")
                return None
        except requests.exceptions.Timeout:
            print(f"  Timeout attempt {attempt+1}")
            time.sleep(5)
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
    done = 0
    failed = 0

    with OUT_FILE.open("a", encoding="utf-8") as fout:
        for model, cond_fills in FILL_PLAN.items():
            use_responses = model == "gpt-5-pro"
            personas = list(PERSONAS.items())
            for condition, n_fill in cond_fills.items():
                prompts = CONDITION_PROMPTS[condition]
                scenarios = SCENARIOS[condition]
                print(f"\n[{model}] {condition}: filling {n_fill} samples...")
                for i in range(n_fill):
                    persona_key, persona_text = personas[i % len(personas)]
                    prompt = prompts[i % len(prompts)]
                    scenario = scenarios[i % len(scenarios)]
                    system = build_system_prompt(persona_text)

                    if use_responses:
                        text = call_responses_api(model, system, prompt, headers)
                    else:
                        text = call_chat_api(model, system, prompt, headers)

                    if text:
                        record = {
                            "id": str(uuid.uuid4()),
                            "batch_id": BATCH_ID,
                            "model": model,
                            "condition": condition,
                            "scenario": scenario,
                            "persona": persona_key,
                            "prompt": prompt,
                            "response": text,
                            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        }
                        fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                        fout.flush()
                        done += 1
                        print(f"  [{done}] OK — {model}/{condition}/{scenario}")
                    else:
                        failed += 1
                        print(f"  FAILED — {model}/{condition} attempt {i+1}")

                    time.sleep(0.8)

    print(f"\nDone: {done} samples written, {failed} failed")
    print(f"Output: {OUT_FILE}")


if __name__ == "__main__":
    main()
