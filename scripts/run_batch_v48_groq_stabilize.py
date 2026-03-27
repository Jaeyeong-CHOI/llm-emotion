#!/usr/bin/env python3
"""
Batch v48: Groq model stabilization fill.

Targets (thin-coverage Groq-accessible models):
  openai/gpt-oss-120b:   C=34→54 (+20)
  allam-2-7b:            D=38→54 (+16)
  groq/compound:         N=36→54 (+18)
  groq/compound-mini:    N=37→54 (+17)

Scientific motivation:
  - gpt-oss-120b CF cell underpowered (n=34 vs n≥50 for primary analysis)
  - allam-2-7b deprivation fill to match counterfactual cell
  - groq/compound and compound-mini neutral cells thin (n=36-37)
  - All models show strong effects (d≥2.3); stabilization improves SE estimates

Design (consistent with prior batches):
  - 3 personas × 3 prompts × 1 temperature × 2 reps per target cell
  - Temperature: 0.7 (balanced creative output for Korean prompts)
  - API: Groq OpenAI-compatible chat completions

Expected contribution:
  - +71 samples total across 4 models
  - Reduces within-model SE for thin cells
  - N total: 8110 → ~8181

Output: results/real_experiments/batch_v48_groq_stabilize.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v48_groq_stabilize.jsonl"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

BATCH_ID = "batch_v48_groq_stabilize"
TEMPERATURE = 0.7
REPS = 2

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
    "counterfactual": ["path_not_taken", "reversed_choice", "alternative_life"],
}

# Fill targets: (model, condition, reps)
FILL_TARGETS = [
    ("openai/gpt-oss-120b",  "counterfactual", 2),
    ("allam-2-7b",           "deprivation",    2),
    ("groq/compound",        "neutral",         2),
    ("groq/compound-mini",   "neutral",         2),
]


def build_messages(persona: str, condition: str, prompt: str) -> list[dict]:
    messages = []
    if persona:
        messages.append({"role": "system", "content": persona})
    messages.append({"role": "user", "content": prompt})
    return messages


def call_groq(model: str, messages: list[dict], max_retries: int = 3) -> str:
    api_key = os.environ.get("GROQ_API_KEY", "")
    for attempt in range(max_retries):
        try:
            resp = requests.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": TEMPERATURE,
                    "max_tokens": 512,
                },
                timeout=30,
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"].strip()
            elif resp.status_code == 429:
                wait = 2 ** (attempt + 1)
                print(f"  [rate-limit] waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  [error] {resp.status_code}: {resp.text[:200]}")
                time.sleep(2)
        except Exception as e:
            print(f"  [exception] {e}")
            time.sleep(2)
    return ""


def main():
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    total = 0
    for (model, condition, reps) in FILL_TARGETS:
        prompts = CONDITION_PROMPTS[condition]
        scenarios = SCENARIOS[condition]
        for p_idx, (prompt_text, scenario_id) in enumerate(zip(prompts, scenarios)):
            for persona_name, persona_text in PERSONAS.items():
                for rep in range(reps):
                    messages = build_messages(persona_text, condition, prompt_text)
                    output = call_groq(model, messages)
                    if not output:
                        print(f"  [skip] no output for {model}/{condition}/{persona_name}")
                        continue
                    record = {
                        "id": str(uuid.uuid4()),
                        "batch_id": BATCH_ID,
                        "model": model,
                        "condition": condition,
                        "persona": persona_name,
                        "temperature": TEMPERATURE,
                        "scenario_id": scenario_id,
                        "prompt": prompt_text,
                        "output": output,
                    }
                    with open(OUT_FILE, "a", encoding="utf-8") as f:
                        f.write(json.dumps(record, ensure_ascii=False) + "\n")
                    total += 1
                    print(f"  [{total}] {model}/{condition}/{persona_name}/rep{rep+1}: {len(output)} chars")
                    time.sleep(0.3)  # polite pacing

    print(f"\nDone. {total} samples → {OUT_FILE}")


if __name__ == "__main__":
    main()
