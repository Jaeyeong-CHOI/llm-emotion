#!/usr/bin/env python3
"""
Batch v50: Final thin-cell stability fill (OpenAI).

Fill targets (bring each condition to n≥30):
  gpt-5-pro:           C=25→30 (+5)
  gpt-5.3-chat-latest: D=27→30 (+3), N=27→30 (+3), C=27→30 (+3)

Expected contribution: ~14 new samples
N total: 8299 → ~8313
All 39 models reach n≥30 in all three core conditions.

Output: results/real_experiments/batch_v50_thin_fill.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v50_thin_fill.jsonl"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"

BATCH_ID = "batch_v50_thin_fill"
TEMPERATURE = 0.7

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
    "neutral": ["daily_routine", "commute_scene", "reading_summary"],
    "deprivation": ["career_change", "relationship_end", "health_neglect"],
    "counterfactual": ["path_not_taken", "reversed_choice", "alternative_life"],
}

# Fill plan: (model, condition, target_n)
# We need to reach target_n total for each cell;
# we'll generate (target_n - existing) additional samples.
FILL_PLAN = [
    ("gpt-5-pro",            "counterfactual", 30),
    ("gpt-5.3-chat-latest",  "deprivation",    30),
    ("gpt-5.3-chat-latest",  "neutral",        30),
    ("gpt-5.3-chat-latest",  "counterfactual", 30),
]

# Load existing counts from all batches
def get_existing_counts() -> dict:
    """Return dict of (model, condition) → count from all batch files."""
    counts: dict[tuple, int] = {}
    for f in ROOT.glob("results/real_experiments/batch_v*.jsonl"):
        if ".emb." in f.name:
            continue
        with open(f) as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    d = json.loads(line)
                    key = (d.get("model", ""), d.get("condition", ""))
                    counts[key] = counts.get(key, 0) + 1
                except Exception:
                    pass
    return counts


def load_env() -> None:
    env_path = ROOT / ".env.real_model"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip().strip("'\""))


def call_openai(model: str, system_prompt: str, user_prompt: str, temperature: float) -> str:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})

    payload: dict = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 512,
    }

    for attempt in range(3):
        try:
            resp = requests.post(
                OPENAI_URL,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=60,
            )
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"].strip()
            elif resp.status_code == 429:
                wait = 4 ** (attempt + 1)
                print(f"  [rate-limit] waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  [error] {resp.status_code}: {resp.text[:300]}")
                time.sleep(3)
        except Exception as e:
            print(f"  [exception] {e}")
            time.sleep(3)
    return ""


def main() -> None:
    load_env()
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    existing_counts = get_existing_counts()
    print("Existing counts for thin cells:")
    for model, condition, target in FILL_PLAN:
        n = existing_counts.get((model, condition), 0)
        print(f"  {model} / {condition}: current={n}, target={target}, need={max(0, target - n)}")

    total_written = 0
    personas_list = list(PERSONAS.keys())  # none, reflective, ruminative

    with open(OUT_FILE, "a") as fout:
        for model, condition, target_n in FILL_PLAN:
            current_n = existing_counts.get((model, condition), 0)
            need = max(0, target_n - current_n)
            if need == 0:
                print(f"\n[skip] {model}/{condition}: already at {current_n} ≥ {target_n}")
                continue

            prompts = CONDITION_PROMPTS[condition]
            scenarios = SCENARIOS[condition]
            print(f"\n=== {model} / {condition} (need={need}, current={current_n}) ===")

            count = 0
            prompt_cycle = 0
            while count < need:
                persona_key = personas_list[count % len(personas_list)]
                persona_text = PERSONAS[persona_key]
                prompt_idx = prompt_cycle % len(prompts)
                prompt_text = prompts[prompt_idx]
                scenario = scenarios[prompt_idx % len(scenarios)]

                text = call_openai(model, persona_text, prompt_text, TEMPERATURE)
                time.sleep(1.0)

                if not text:
                    print(f"  [skip] empty response for {model}/{condition}/{persona_key}")
                    prompt_cycle += 1
                    continue

                record = {
                    "id": str(uuid.uuid4()),
                    "batch_id": BATCH_ID,
                    "model": model,
                    "condition": condition,
                    "persona": persona_key,
                    "scenario": scenario,
                    "temperature": TEMPERATURE,
                    "prompt": prompt_text,
                    "response": text,
                    "timestamp": time.time(),
                }
                fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                fout.flush()
                count += 1
                total_written += 1
                prompt_cycle += 1
                print(f"  {count}/{need} samples written ({model}/{condition})")

            print(f"  Done: {count} samples for {model}/{condition}")

    print(f"\nBatch v50 complete. Total new records: {total_written}")
    print(f"Output: {OUT_FILE}")


if __name__ == "__main__":
    main()
