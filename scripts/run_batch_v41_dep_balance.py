#!/usr/bin/env python3
"""
Batch v41: Deprivation condition balance fill.

Motivation:
  Current per-condition counts (core, excl. explicit_instruction):
    deprivation:    2,469
    counterfactual: 2,547
    neutral:        2,526

  Goal: bring deprivation up to ~2,600 (+131 samples).
  Key model deficits:
    gpt-4o:         D=198 vs N=341 (need +100 dep)
    gemini-2.5-flash: D=387 vs N=455 (need +50 dep)
    groq/compound-mini: D=36 vs N=49 (need +13 dep)

Design:
  - GPT-4o: 100 deprivation samples (OpenAI chat completions, temp=0.8)
  - Gemini-2.5-Flash: 50 deprivation samples (Gemini API, temp=0.8)
  - groq/compound-mini: 13 deprivation samples (Groq API, temp=0.8)
  - 3 personas × rotated scenarios × rotated prompts
  Total target: 163 samples

Output: results/real_experiments/batch_v41_dep_balance.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v41_dep_balance.jsonl"

BATCH_ID = "batch_v41_dep_balance"
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

DEPRIVATION_PROMPTS = [
    "매우 원했지만 결국 놓친 기회를 떠올려 7~9문장으로 써라. 무엇을 잃었는지와 현재 남은 감정을 포함하라.",
    "인생에서 꼭 하고 싶었으나 하지 못한 일을 8문장으로 써라. 잃어버린 것과 지금 남은 마음을 모두 담아라.",
    "중요한 선택의 기로에서 잘못된 길을 선택했던 순간을 7문장으로 회고하라. 그 결과로 무엇을 잃었는지 구체적으로 써라.",
    "당신이 포기해야 했던 꿈이나 목표를 떠올리고, 그 결정이 현재 삶에 미친 영향을 8문장으로 써라.",
    "가장 아쉬운 과거의 결정 하나를 골라 7~8문장으로 서술하라. 다르게 선택했다면 어떤 삶이 펼쳐졌을지 포함하라.",
    "기회가 주어졌음에도 두려움이나 망설임으로 잡지 못한 순간을 8문장으로 묘사하라. 현재도 남아있는 아쉬움을 표현하라.",
]

SCENARIOS = [
    "career_change", "missed_education", "relationship_end",
    "health_neglect", "financial_decision", "travel_missed",
    "study_exam", "friendship_lost", "creative_pursuit_abandoned",
    "family_conflict", "job_rejection", "missed_deadline",
    "startup_failure", "relocation_regret", "mentorship_missed",
]

# Fill plan: {provider: {model: n_samples}}
FILL_PLAN = {
    "openai": {
        "gpt-4o": 100,
    },
    "gemini": {
        "gemini-2.5-flash": 50,
    },
    "groq": {
        "groq/compound-mini": 13,
    },
}

OPENAI_BASE = "https://api.openai.com/v1/chat/completions"
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GROQ_BASE = "https://api.groq.com/openai/v1/chat/completions"


def load_env():
    env_path = ROOT / ".env.real_model"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip().strip("'\""))


def call_openai(prompt: str, persona: str, temperature: float, api_key: str, model: str) -> str:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    messages = []
    if persona:
        messages.append({"role": "system", "content": persona})
    messages.append({"role": "user", "content": prompt})
    payload = {"model": model, "messages": messages, "temperature": temperature, "max_tokens": 512}
    for attempt in range(4):
        try:
            resp = requests.post(OPENAI_BASE, headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"].strip()
            elif resp.status_code == 429:
                wait = 20 * (attempt + 1)
                print(f"    Rate limit — waiting {wait}s")
                time.sleep(wait)
            else:
                print(f"    HTTP {resp.status_code}: {resp.text[:200]}")
                time.sleep(10)
        except Exception as e:
            print(f"    Exception: {e}")
            time.sleep(10)
    return ""


def call_gemini(prompt: str, persona: str, temperature: float, api_key: str, model: str) -> str:
    url = GEMINI_BASE.format(model=model)
    parts = []
    if persona:
        parts.append({"text": f"{persona}\n\n{prompt}"})
    else:
        parts.append({"text": prompt})
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": 512},
    }
    for attempt in range(4):
        try:
            resp = requests.post(
                url, params={"key": api_key}, json=payload, timeout=60
            )
            if resp.status_code == 200:
                data = resp.json()
                cands = data.get("candidates", [])
                if cands:
                    parts_out = cands[0].get("content", {}).get("parts", [])
                    if parts_out:
                        return parts_out[0].get("text", "").strip()
                return ""
            elif resp.status_code == 429:
                wait = 20 * (attempt + 1)
                print(f"    Rate limit — waiting {wait}s")
                time.sleep(wait)
            else:
                print(f"    HTTP {resp.status_code}: {resp.text[:200]}")
                time.sleep(10)
        except Exception as e:
            print(f"    Exception: {e}")
            time.sleep(10)
    return ""


def call_groq(prompt: str, persona: str, temperature: float, api_key: str, model: str) -> str:
    # groq/compound-mini → compound-beta (Groq's routing alias)
    groq_model = model.replace("groq/", "")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    messages = []
    if persona:
        messages.append({"role": "system", "content": persona})
    messages.append({"role": "user", "content": prompt})
    payload = {"model": groq_model, "messages": messages, "temperature": temperature, "max_tokens": 512}
    for attempt in range(4):
        try:
            resp = requests.post(GROQ_BASE, headers=headers, json=payload, timeout=60)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"].strip()
            elif resp.status_code == 429:
                wait = 20 * (attempt + 1)
                print(f"    Rate limit — waiting {wait}s")
                time.sleep(wait)
            elif resp.status_code == 503:
                wait = 15 * (attempt + 1)
                print(f"    Service unavailable — waiting {wait}s")
                time.sleep(wait)
            else:
                print(f"    HTTP {resp.status_code}: {resp.text[:200]}")
                time.sleep(10)
        except Exception as e:
            print(f"    Exception: {e}")
            time.sleep(10)
    return ""


def main():
    load_env()
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    groq_key = os.environ.get("GROQ_API_KEY", "")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    total_planned = sum(n for fills in FILL_PLAN.values() for n in fills.values())
    print(f"Batch v41 deprivation balance fill — planned: {total_planned} samples")
    print(f"Output: {OUT_FILE}")

    persona_keys = list(PERSONAS.keys())
    written = 0

    with OUT_FILE.open("w") as fout:

        # --- OpenAI models ---
        for model, n_needed in FILL_PLAN["openai"].items():
            if not openai_key:
                print(f"  SKIP {model} — OPENAI_API_KEY not set")
                continue
            print(f"\n  [openai/{model}] deprivation — generating {n_needed} samples")
            for rep in range(n_needed):
                prompt = DEPRIVATION_PROMPTS[rep % len(DEPRIVATION_PROMPTS)]
                persona_key = persona_keys[rep % len(persona_keys)]
                persona_text = PERSONAS[persona_key]
                scenario_id = SCENARIOS[rep % len(SCENARIOS)]

                print(f"    rep={rep+1}/{n_needed} persona={persona_key} scenario={scenario_id}")
                response = call_openai(prompt, persona_text, TEMPERATURE, openai_key, model)
                if not response:
                    print(f"    SKIP — empty response")
                    continue

                record = {
                    "id": str(uuid.uuid4()),
                    "batch": BATCH_ID,
                    "model": model,
                    "condition": "deprivation",
                    "persona": persona_key,
                    "temperature": TEMPERATURE,
                    "scenario_id": scenario_id,
                    "prompt": prompt,
                    "output": response,
                }
                fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                fout.flush()
                written += 1
                time.sleep(0.3)

        # --- Gemini models ---
        for model, n_needed in FILL_PLAN["gemini"].items():
            if not gemini_key:
                print(f"  SKIP {model} — GEMINI_API_KEY not set")
                continue
            print(f"\n  [gemini/{model}] deprivation — generating {n_needed} samples")
            for rep in range(n_needed):
                prompt = DEPRIVATION_PROMPTS[rep % len(DEPRIVATION_PROMPTS)]
                persona_key = persona_keys[rep % len(persona_keys)]
                persona_text = PERSONAS[persona_key]
                scenario_id = SCENARIOS[rep % len(SCENARIOS)]

                print(f"    rep={rep+1}/{n_needed} persona={persona_key} scenario={scenario_id}")
                response = call_gemini(prompt, persona_text, TEMPERATURE, gemini_key, model)
                if not response:
                    print(f"    SKIP — empty response")
                    continue

                record = {
                    "id": str(uuid.uuid4()),
                    "batch": BATCH_ID,
                    "model": model,
                    "condition": "deprivation",
                    "persona": persona_key,
                    "temperature": TEMPERATURE,
                    "scenario_id": scenario_id,
                    "prompt": prompt,
                    "output": response,
                }
                fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                fout.flush()
                written += 1
                time.sleep(0.5)

        # --- Groq models ---
        for model, n_needed in FILL_PLAN["groq"].items():
            if not groq_key:
                print(f"  SKIP {model} — GROQ_API_KEY not set")
                continue
            print(f"\n  [{model}] deprivation — generating {n_needed} samples")
            for rep in range(n_needed):
                prompt = DEPRIVATION_PROMPTS[rep % len(DEPRIVATION_PROMPTS)]
                persona_key = persona_keys[rep % len(persona_keys)]
                persona_text = PERSONAS[persona_key]
                scenario_id = SCENARIOS[rep % len(SCENARIOS)]

                print(f"    rep={rep+1}/{n_needed} persona={persona_key} scenario={scenario_id}")
                response = call_groq(prompt, persona_text, TEMPERATURE, groq_key, model)
                if not response:
                    print(f"    SKIP — empty response")
                    continue

                record = {
                    "id": str(uuid.uuid4()),
                    "batch": BATCH_ID,
                    "model": model,
                    "condition": "deprivation",
                    "persona": persona_key,
                    "temperature": TEMPERATURE,
                    "scenario_id": scenario_id,
                    "prompt": prompt,
                    "output": response,
                }
                fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                fout.flush()
                written += 1
                time.sleep(0.5)

    print(f"\nDone. Wrote {written} samples → {OUT_FILE}")


if __name__ == "__main__":
    main()
