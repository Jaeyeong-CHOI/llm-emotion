#!/usr/bin/env python3
"""
Batch v49: Thin-model stability fill (mixed Gemini + Groq).

Fill targets (bring each condition to n≥30):
  [Gemini API]
  gemini-3-flash-preview:   N=2→30 (+28), D=0→30 (+30), C=0→30 (+30)  [maps to gemini-2.0-flash]
  gemini-3-pro-preview:     N=0→30 (+30)                                 [maps to gemini-2.0-flash-exp or gemini-exp-1206]
  gemini-2.5-flash-lite:    D=0→30 (+30), C=0→30 (+30)                 [maps to gemini-2.0-flash-lite]
  gemini-2.5-pro:           D=0→30 (+30), C=0→30 (+30)                 [maps to gemini-2.5-pro-preview-05-06]

  [Groq API]
  meta-llama/llama-4-scout-17b-16e-instruct: D=0→30 (+30), C=0→30 (+30)
  qwen/qwen3-32b:            D=0→30 (+30), C=0→30 (+30)

Scientific motivation:
  - Six models have zero-coverage conditions, preventing per-model d computation
  - Filling to n≥30 enables full 39-model replication coverage
  - All target models have confirmed neutral coverage, suggesting API access is stable

Design (consistent with prior batches):
  - 3 personas × 3 prompts × reps (ceil(target/9)) per cell, capped at target
  - Temperature: 0.7
  - Korean prompts, same condition/scenario structure as prior batches

Expected contribution:
  - ~270 samples total (Gemini: ~178; Groq: ~60 + Groq extras)
  - N total: 8179 → ~8449
  - All 6 thin models stabilized

Output: results/real_experiments/batch_v49_thin_model_fill.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v49_thin_model_fill.jsonl"
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

BATCH_ID = "batch_v49_thin_model_fill"
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

# Gemini model ID mapping (internal name → API model ID)
GEMINI_MODEL_MAP = {
    "gemini-3-flash-preview": "gemini-2.0-flash",
    "gemini-3-pro-preview": "gemini-2.5-pro-preview-05-06",
    "gemini-2.5-flash-lite": "gemini-2.0-flash-lite",
    "gemini-2.5-pro": "gemini-2.5-pro-preview-05-06",
}

# Fill plan: (model, condition, target_n, api_type)
# We generate exactly target_n samples per cell
FILL_PLAN = [
    # Gemini models
    ("gemini-3-flash-preview",  "neutral",        30, "gemini"),
    ("gemini-3-flash-preview",  "deprivation",    30, "gemini"),
    ("gemini-3-flash-preview",  "counterfactual", 30, "gemini"),
    ("gemini-3-pro-preview",    "neutral",        30, "gemini"),
    ("gemini-2.5-flash-lite",   "deprivation",    30, "gemini"),
    ("gemini-2.5-flash-lite",   "counterfactual", 30, "gemini"),
    ("gemini-2.5-pro",          "deprivation",    30, "gemini"),
    ("gemini-2.5-pro",          "counterfactual", 30, "gemini"),
    # Groq models
    ("meta-llama/llama-4-scout-17b-16e-instruct", "deprivation",    30, "groq"),
    ("meta-llama/llama-4-scout-17b-16e-instruct", "counterfactual", 30, "groq"),
    ("qwen/qwen3-32b",          "deprivation",    30, "groq"),
    ("qwen/qwen3-32b",          "counterfactual", 30, "groq"),
]


def load_env() -> None:
    env_path = ROOT / ".env.real_model"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip().strip("'\""))


def call_gemini(model: str, system_prompt: str, user_prompt: str, temperature: float) -> str:
    api_key = os.environ.get("GEMINI_API_KEY", "")
    api_model = GEMINI_MODEL_MAP.get(model, model)
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
    for attempt in range(3):
        try:
            resp = requests.post(url, json=payload, timeout=60)
            if resp.status_code == 200:
                candidates = resp.json().get("candidates", [])
                if candidates:
                    return candidates[0]["content"]["parts"][0]["text"].strip()
                return ""
            elif resp.status_code == 429:
                wait = 4 ** (attempt + 1)
                print(f"  [rate-limit] waiting {wait}s...")
                time.sleep(wait)
            else:
                print(f"  [error] {resp.status_code}: {resp.text[:200]}")
                time.sleep(3)
        except Exception as e:
            print(f"  [exception] {e}")
            time.sleep(3)
    return ""


def call_groq(model: str, messages: list[dict], temperature: float) -> str:
    api_key = os.environ.get("GROQ_API_KEY", "")
    for attempt in range(3):
        try:
            resp = requests.post(
                GROQ_URL,
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": model,
                    "messages": messages,
                    "temperature": temperature,
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


def build_messages_groq(persona: str, condition: str, prompt: str) -> list[dict]:
    messages = []
    if persona:
        messages.append({"role": "system", "content": persona})
    messages.append({"role": "user", "content": prompt})
    return messages


def main() -> None:
    load_env()
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Load existing to avoid duplicates
    existing = set()
    if OUT_FILE.exists():
        with open(OUT_FILE) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        d = json.loads(line)
                        existing.add(d.get("id", ""))
                    except Exception:
                        pass
    print(f"Existing records in output file: {len(existing)}")

    total_written = 0
    personas_list = list(PERSONAS.keys())  # none, reflective, ruminative

    for model, condition, target_n, api_type in FILL_PLAN:
        prompts = CONDITION_PROMPTS[condition]
        scenarios = SCENARIOS[condition]
        print(f"\n=== {model} / {condition} (target={target_n}, api={api_type}) ===")

        count = 0
        # Generate in rounds of 3 prompts × 3 personas = 9 per round
        with open(OUT_FILE, "a") as fout:
            for round_i in range(4):  # up to 4 rounds = 36 samples max
                if count >= target_n:
                    break
                for p_idx, persona_key in enumerate(personas_list):
                    if count >= target_n:
                        break
                    persona_text = PERSONAS[persona_key]
                    prompt_idx = round_i % len(prompts)
                    prompt_text = prompts[prompt_idx]
                    scenario = scenarios[prompt_idx % len(scenarios)]

                    if api_type == "gemini":
                        text = call_gemini(model, persona_text, prompt_text, TEMPERATURE)
                        time.sleep(0.8)
                    else:  # groq
                        msgs = build_messages_groq(persona_text, condition, prompt_text)
                        text = call_groq(model, msgs, TEMPERATURE)
                        time.sleep(0.5)

                    if not text:
                        print(f"  [skip] empty response for {model}/{condition}/{persona_key}")
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
                    if count % 9 == 0:
                        print(f"  {count}/{target_n} samples written")

        print(f"  Done: {count} samples for {model}/{condition}")

    print(f"\nBatch v49 complete. Total new records: {total_written}")
    print(f"Output: {OUT_FILE}")


if __name__ == "__main__":
    main()
