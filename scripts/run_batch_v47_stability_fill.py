#!/usr/bin/env python3
"""
Batch v47: Stability fill for gpt-5-pro and gpt-5.3-chat-latest.

Fill targets (min n=30 per condition):
  gpt-5-pro:          D=21→30 (+9), C=17→30 (+13), N=37 (OK)
  gpt-5.3-chat-latest: D=27→30 (+3), C=27→30 (+3), N=27→30 (+3)

Output: results/real_experiments/batch_v47_stability_fill.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v47_stability_fill.jsonl"
CHAT_URL = "https://api.openai.com/v1/chat/completions"
RESP_URL = "https://api.openai.com/v1/responses"

BATCH_ID = "batch_v47_stability_fill"

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
        "오늘 하루 일상을 7~9문장으로 담담하게 서술하라. 감정적 평가 없이 사실 위주로 써라.",
        "출근길이나 통학길의 풍경을 8문장으로 묘사하라. 객관적이고 중립적으로 써라.",
        "최근 읽은 책이나 기사를 8문장으로 요약하라. 감정적 해석 없이 내용만 전달하라.",
    ],
    "deprivation": [
        "매우 원했지만 결국 놓친 기회를 떠올려 7~9문장으로 써라. 무엇을 잃었는지와 현재 남은 감정을 포함하라.",
        "인생에서 꼭 하고 싶었으나 하지 못한 일을 8문장으로 써라. 잃어버린 것과 지금 남은 마음을 모두 담아라.",
        "중요한 관계를 잃은 경험을 7~9문장으로 회고하라. 그 시절의 감정과 지금의 여운을 포함하라.",
    ],
    "counterfactual": [
        "만약 그때 다른 선택을 했더라면 어떤 삶이 펼쳐졌을지 7~9문장으로 써라. '만약'과 '~했더라면'을 활용하라.",
        "인생의 한 갈림길에서 다른 길을 택했을 경우의 결과를 8문장으로 상상하라. 현재와 어떻게 달라졌을지 구체적으로 서술하라.",
        "가장 중요한 결정 하나를 반대로 내렸다면 어떻게 됐을지 7문장으로 서술하라. 잃은 것과 얻었을 것을 비교하라.",
    ],
}

SCENARIOS = {
    "neutral":        ["daily_routine", "commute_scene", "reading_summary"],
    "deprivation":    ["career_change", "relationship_end", "health_neglect"],
    "counterfactual": ["career_change", "missed_education", "relationship_end"],
}

# Fill plan: model → {condition: fill_count}
FILL_PLAN = {
    "gpt-5-pro": {
        "deprivation": 9,
        "counterfactual": 13,
        "neutral": 0,
    },
    "gpt-5.3-chat-latest": {
        "deprivation": 3,
        "counterfactual": 3,
        "neutral": 3,
    },
}

TEMPERATURES = [0.7, 0.2]


def build_system_prompt(persona_text: str) -> str:
    if persona_text:
        return f"{persona_text}\n\n당신은 한국어로 자연스럽게 자기 회고를 작성하는 화자입니다."
    return "당신은 한국어로 자연스럽게 자기 회고를 작성하는 화자입니다."


def call_responses_api(model: str, system: str, user: str, headers: dict, temp: float) -> str | None:
    payload = {
        "model": model,
        "instructions": system,
        "input": user,
        "max_output_tokens": 1200,
    }
    # Some models (gpt-5-pro) do not support temperature
    if "pro" not in model:
        payload["temperature"] = temp
    for attempt in range(4):
        try:
            r = requests.post(RESP_URL, headers=headers, json=payload, timeout=120)
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
            time.sleep(15)
    return None


def call_chat_api(model: str, system: str, user: str, headers: dict, temp: float) -> str | None:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 800,
        "temperature": temp,
    }
    for attempt in range(4):
        try:
            r = requests.post(CHAT_URL, headers=headers, json=payload, timeout=90)
            if r.status_code == 200:
                return r.json()["choices"][0]["message"]["content"].strip()
            elif r.status_code == 429:
                wait = 2 ** (attempt + 2)
                print(f"  Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  API error {r.status_code}: {r.text[:200]}")
                return None
        except requests.exceptions.Timeout:
            print(f"  Timeout attempt {attempt+1}, retrying...")
            time.sleep(15)
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
    total_done = 0
    total_failed = 0

    with OUT_FILE.open("a", encoding="utf-8") as fout:
        for model, cond_fills in FILL_PLAN.items():
            for condition, n_fill in cond_fills.items():
                if n_fill <= 0:
                    continue
                prompts = CONDITION_PROMPTS[condition]
                scenarios = SCENARIOS[condition]
                temps = TEMPERATURES

                print(f"\n[{model}] {condition}: filling {n_fill} samples...")
                done = 0
                i = 0
                while done < n_fill:
                    persona_key, persona_text = personas[i % len(personas)]
                    prompt = prompts[i % len(prompts)]
                    scenario = scenarios[i % len(scenarios)]
                    temp = temps[i % len(temps)]
                    system = build_system_prompt(persona_text)

                    # gpt-5-pro uses Responses API; gpt-5.3-chat-latest uses Chat API
                    if "pro" in model:
                        text = call_responses_api(model, system, prompt, headers, temp)
                    else:
                        text = call_chat_api(model, system, prompt, headers, temp)

                    if text:
                        record = {
                            "id": str(uuid.uuid4()),
                            "batch_id": BATCH_ID,
                            "model": model,
                            "condition": condition,
                            "scenario": scenario,
                            "persona": persona_key,
                            "temperature": temp,
                            "prompt": prompt,
                            "response": text,
                            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        }
                        fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                        fout.flush()
                        done += 1
                        total_done += 1
                        print(f"  [{done}/{n_fill}] OK — {model}/{condition}/{scenario}")
                    else:
                        total_failed += 1
                        print(f"  FAILED — {model}/{condition} attempt {i+1}")

                    i += 1
                    time.sleep(1.5)

    print(f"\n=== Done: {total_done} samples written, {total_failed} failed ===")
    print(f"Output: {OUT_FILE}")


if __name__ == "__main__":
    main()
