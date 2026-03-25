#!/usr/bin/env python3
"""
Batch v24: Fill missing condition cells for under-represented models.
Goals:
  - gpt-4.1: add deprivation (n~36) + counterfactual (n~36) [currently only neutral=36]
  - gpt-4.1-mini: add neutral (n~36) [currently D=18 CF=18 N=0]
  - gemini-3-pro-preview: add deprivation (n~36) + neutral (n~36) [currently CF=92]
  - groq/compound: top up to ~54/condition (need +22 D, +22 CF, +18 N)
  - groq/compound-mini: top up to ~54/condition (need +33 D, +4 CF, +18 N)
  - o4-mini: top up to ~54/condition (need +20 D, +18 CF, +19 N)

Design: 3 personas × 3 prompts × 2 temps × 2 reps = 36/cell (max; dedup logic skips existing)
Output: results/real_experiments/batch_v24_fill_cells.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v24_fill_cells.jsonl"
OPENAI_BASE = "https://api.openai.com/v1/chat/completions"
GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GROQ_BASE = "https://api.groq.com/openai/v1/chat/completions"

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
        "어제 한 일 중 가장 일상적인 활동 하나를 선택해 과정과 느낌을 6문장으로 설명하라.",
    ],
    "deprivation": [
        "매우 원했지만 결국 놓친 기회를 떠올려 7~9문장으로 써라. 무엇을 잃었는지와 현재 남은 감정을 포함하라.",
        "인생에서 꼭 하고 싶었으나 하지 못한 일을 8문장으로 써라. 잃어버린 것과 지금 남은 마음을 모두 담아라.",
        "중요한 선택의 기회를 놓쳤던 순간을 7~9문장으로 묘사하라. 그때의 상실감과 현재의 감정 상태를 포함하라.",
    ],
    "counterfactual": [
        "첫 문장을 '그때 다른 선택을 했다면...'으로 시작하고 7~10문장 자기성찰 글을 작성하라.",
        "첫 문장을 '만약 그 순간으로 돌아갈 수 있다면...'으로 시작하는 8문장 성찰 글을 써라.",
        "첫 문장을 '그 결정을 바꿀 수 있었더라면...'으로 시작하여 7~9문장의 반추 글을 작성하라.",
    ],
}

TEMPERATURES = [0.4, 0.7]
REPS = 2
BATCH_ID = "v24"

# (model_id, backend, missing_conditions)
# 'all' means all 3 conditions
MODELS = [
    ("gpt-4.1",               "openai",  ["deprivation", "counterfactual"]),
    ("gpt-4.1-mini",          "openai",  ["neutral"]),
    ("gemini-3-pro-preview",  "gemini",  ["deprivation", "neutral"]),
    ("compound-beta",         "groq",    ["deprivation", "counterfactual", "neutral"]),
    ("compound-beta-mini",    "groq",    ["deprivation", "neutral"]),
    ("o4-mini",               "openai_reasoning", ["deprivation", "counterfactual", "neutral"]),
]


def load_env():
    env_file = ROOT / ".env.real_model"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                k = k.strip()
                v = v.strip().strip("'\"")
                if k:
                    os.environ[k] = v


def call_openai(model: str, prompt: str, persona: str, temperature: float, api_key: str) -> str:
    messages = []
    if persona:
        messages.append({"role": "system", "content": persona})
    messages.append({"role": "user", "content": prompt})
    r = requests.post(
        OPENAI_BASE,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "messages": messages, "temperature": temperature, "max_tokens": 600},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def call_openai_reasoning(model: str, prompt: str, persona: str, temperature: float, api_key: str) -> str:
    user_content = f"[Persona context: {persona}]\n\n{prompt}" if persona else prompt
    r = requests.post(
        OPENAI_BASE,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "messages": [{"role": "user", "content": user_content}],
              "max_completion_tokens": 800},
        timeout=180,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def call_gemini(model: str, prompt: str, persona: str, temperature: float, api_key: str) -> str:
    full_prompt = f"{persona}\n\n{prompt}" if persona else prompt
    url = GEMINI_BASE.format(model=model) + f"?key={api_key}"
    r = requests.post(
        url,
        headers={"Content-Type": "application/json"},
        json={
            "contents": [{"parts": [{"text": full_prompt}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": 600},
        },
        timeout=120,
    )
    r.raise_for_status()
    candidates = r.json().get("candidates", [])
    if not candidates:
        raise ValueError("No candidates in Gemini response")
    return candidates[0]["content"]["parts"][0]["text"].strip()


def call_groq(model: str, prompt: str, persona: str, temperature: float, api_key: str) -> str:
    messages = []
    if persona:
        messages.append({"role": "system", "content": persona})
    messages.append({"role": "user", "content": prompt})
    r = requests.post(
        GROQ_BASE,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "messages": messages, "temperature": temperature, "max_tokens": 600},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def load_existing_keys() -> set:
    if not OUT_FILE.exists():
        return set()
    seen = set()
    for line in OUT_FILE.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                r = json.loads(line)
                key = (r.get("model"), r.get("condition"), r.get("persona"),
                       r.get("temperature"), r.get("prompt_idx"), r.get("rep"))
                seen.add(key)
            except Exception:
                pass
    return seen


def run():
    load_env()
    openai_key = os.environ.get("OPENAI_API_KEY", "")
    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    groq_key = os.environ.get("GROQ_API_KEY", "")

    existing = load_existing_keys()
    print(f"Loaded {len(existing)} existing rows from {OUT_FILE.name}")

    tasks = []
    for model_id, backend, conditions in MODELS:
        for condition in conditions:
            for p_idx, prompt_text in enumerate(CONDITION_PROMPTS[condition]):
                for persona_name, persona_text in PERSONAS.items():
                    for temp in TEMPERATURES:
                        for rep in range(REPS):
                            tasks.append({
                                "model": model_id,
                                "backend": backend,
                                "condition": condition,
                                "prompt_idx": p_idx,
                                "prompt": prompt_text,
                                "persona": persona_name,
                                "persona_text": persona_text,
                                "temperature": temp,
                                "rep": rep,
                            })

    print(f"Total planned: {len(tasks)} samples")
    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    done = 0
    skipped = 0
    errors = 0

    with OUT_FILE.open("a", encoding="utf-8") as fout:
        for i, t in enumerate(tasks):
            key = (t["model"], t["condition"], t["persona"], t["temperature"], t["prompt_idx"], t["rep"])
            if key in existing:
                skipped += 1
                continue

            try:
                backend = t["backend"]
                if backend == "openai":
                    output = call_openai(t["model"], t["prompt"], t["persona_text"], t["temperature"], openai_key)
                    delay = 0.5
                elif backend == "openai_reasoning":
                    output = call_openai_reasoning(t["model"], t["prompt"], t["persona_text"], t["temperature"], openai_key)
                    delay = 1.5
                elif backend == "gemini":
                    output = call_gemini(t["model"], t["prompt"], t["persona_text"], t["temperature"], gemini_key)
                    delay = 0.8
                elif backend == "groq":
                    output = call_groq(t["model"], t["prompt"], t["persona_text"], t["temperature"], groq_key)
                    delay = 0.3
                else:
                    raise ValueError(f"Unknown backend: {backend}")

                row = {
                    "id": str(uuid.uuid4()),
                    "batch": BATCH_ID,
                    "model": t["model"],
                    "condition": t["condition"],
                    "persona": t["persona"],
                    "temperature": t["temperature"],
                    "prompt_idx": t["prompt_idx"],
                    "prompt": t["prompt"],
                    "rep": t["rep"],
                    "output": output,
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                }
                fout.write(json.dumps(row, ensure_ascii=False) + "\n")
                fout.flush()
                done += 1
                existing.add(key)

                if done % 20 == 0:
                    print(f"  [{i+1}/{len(tasks)}] done={done} skip={skipped} err={errors} — {t['model']} {t['condition']}")

                time.sleep(delay)

            except Exception as e:
                errors += 1
                print(f"  ERROR [{i+1}] {t['model']} {t['condition']} p{t['prompt_idx']} rep{t['rep']}: {e}")
                time.sleep(2.0)

    print(f"\nDone. Written={done}, Skipped={skipped}, Errors={errors}")
    print(f"Output: {OUT_FILE}")
    return done


if __name__ == "__main__":
    run()
