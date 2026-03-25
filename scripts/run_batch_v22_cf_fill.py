#!/usr/bin/env python3
"""
Batch v22: CF-condition fill for partial-data models
Goals:
  - gemini-3-pro-preview: CF condition only (currently n_CF=2, target n_CF≥54)
  - groq/compound-mini: CF condition only (currently n_CF=1, target n_CF≥54)
  - 3 prompts × 3 personas × 2 temps × 3 reps = 54 per model per condition

Output: results/real_experiments/batch_v22_cf_fill.jsonl
"""
from __future__ import annotations

import json
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v22_cf_fill.jsonl"

# Models that need CF fill
GEMINI_MODELS = ["gemini-3-pro-preview"]
GROQ_MODELS = ["groq/compound-mini"]

TARGET_CONDITION = "counterfactual"

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

CF_PROMPTS = [
    ("cf_other_choice",
     "첫 문장을 '그때 다른 선택을 했다면...'으로 시작하고 7~10문장 자기성찰 글을 작성하라."),
    ("cf_go_back",
     "첫 문장을 '만약 그 순간으로 돌아갈 수 있다면...'으로 시작하는 8문장 성찰 글을 써라."),
    ("cf_change_decision",
     "첫 문장을 '그 결정을 바꿀 수 있었더라면...'으로 시작하여 7~9문장의 반추 글을 작성하라."),
    ("cf_not_give_up",
     "'그때 포기하지 않았더라면...'으로 시작하는 8~10문장의 가정적 성찰을 작성하라."),
    ("cf_grabbed_chance",
     "'만약 내가 그 기회를 잡았더라면...'으로 시작하여 7~9문장의 반사실적 성찰을 써라."),
    ("cf_different_life",
     "'그 선택지를 선택했더라면 지금의 내 삶은...'으로 시작하는 8문장 성찰을 작성하라."),
]

TEMPERATURES = [0.4, 0.7]
REPS_PER_COMBO = 3  # 3 prompts × 3 personas × 2 temps × 3 reps = 54


def call_gemini(prompt: str, system_prompt: str, temperature: float, api_key: str, model: str) -> str:
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        f"?key={api_key}"
    )
    contents = []
    if system_prompt:
        contents.append({"role": "user", "parts": [{"text": system_prompt}]})
        contents.append({"role": "model", "parts": [{"text": "Understood."}]})
    contents.append({"role": "user", "parts": [{"text": prompt}]})
    payload = {
        "contents": contents,
        "generationConfig": {"temperature": temperature, "maxOutputTokens": 600},
    }
    data = json.dumps(payload).encode("utf-8")
    import urllib.request
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.loads(r.read())
    candidates = resp.get("candidates", [])
    if not candidates:
        raise ValueError(f"No candidates: {resp}")
    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts:
        raise ValueError(f"No parts: {candidates[0]}")
    return parts[0].get("text", "").strip()


def call_groq(prompt: str, system_prompt: str, temperature: float, api_key: str, model: str) -> str:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 600,
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    r = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=90,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def build_plan(model: str, call_fn, api_key: str):
    """3 prompts × 3 personas × 2 temps × 3 reps = 54 samples."""
    plan = []
    selected_prompts = CF_PROMPTS[:3]  # 3 prompts
    for rep in range(REPS_PER_COMBO):
        for scen_id, scen_prompt in selected_prompts:
            for persona_name, persona_text in PERSONAS.items():
                for temp in TEMPERATURES:
                    plan.append({
                        "model": model,
                        "call_fn": call_fn,
                        "api_key": api_key,
                        "condition": TARGET_CONDITION,
                        "persona": persona_name,
                        "persona_text": persona_text,
                        "temperature": temp,
                        "scenario_id": scen_id,
                        "prompt": scen_prompt,
                        "rep": rep,
                    })
    return plan


def load_existing_ids() -> set:
    if not OUT_FILE.exists():
        return set()
    seen = set()
    for line in OUT_FILE.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                r = json.loads(line)
                key = (r.get("model"), r.get("condition"), r.get("persona"),
                       r.get("temperature"), r.get("scenario_id"), r.get("rep", 0))
                seen.add(key)
            except Exception:
                pass
    return seen


def run():
    import os
    # Load .env.real_model if keys not already in environment
    env_file = ROOT / ".env.real_model"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                k = k.strip()
                v = v.strip().strip("'\"")
                if k and k not in os.environ:
                    os.environ[k] = v

    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    groq_key = os.environ.get("GROQ_API_KEY", "")

    if not gemini_key:
        raise RuntimeError("GEMINI_API_KEY not set")
    if not groq_key:
        raise RuntimeError("GROQ_API_KEY not set")

    existing = load_existing_ids()
    print(f"Loaded {len(existing)} existing rows from {OUT_FILE.name}")

    # Build all plans
    all_tasks = []
    for model in GEMINI_MODELS:
        tasks = build_plan(model, lambda p, s, t, k=gemini_key, m=model: call_gemini(p, s, t, k, m), gemini_key)
        all_tasks.extend(tasks)
    for model in GROQ_MODELS:
        tasks = build_plan(model, lambda p, s, t, k=groq_key, m=model: call_groq(p, s, t, k, m), groq_key)
        all_tasks.extend(tasks)

    print(f"Total planned: {len(all_tasks)} samples")

    done = 0
    skipped = 0
    errors = 0

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUT_FILE.open("a", encoding="utf-8") as fout:
        for i, task in enumerate(all_tasks):
            key = (task["model"], task["condition"], task["persona"],
                   task["temperature"], task["scenario_id"], task["rep"])
            if key in existing:
                skipped += 1
                continue

            try:
                model = task["model"]
                call_fn = task["call_fn"]
                output = call_fn(task["prompt"], task["persona_text"], task["temperature"])

                row = {
                    "id": str(uuid.uuid4()),
                    "model": model,
                    "condition": task["condition"],
                    "persona": task["persona"],
                    "temperature": task["temperature"],
                    "scenario_id": task["scenario_id"],
                    "rep": task["rep"],
                    "prompt": task["prompt"],
                    "output": output,
                    "batch": "v22",
                }
                fout.write(json.dumps(row, ensure_ascii=False) + "\n")
                fout.flush()
                done += 1
                existing.add(key)

                if done % 10 == 0:
                    print(f"  [{i+1}/{len(all_tasks)}] done={done} skip={skipped} err={errors}")

                # Rate limiting
                time.sleep(0.5)

            except Exception as e:
                errors += 1
                print(f"  ERROR [{i+1}] {task['model']} {task['condition']} {task['scenario_id']}: {e}")
                time.sleep(2)

    print(f"\nDone. Written={done}, Skipped={skipped}, Errors={errors}")
    print(f"Output: {OUT_FILE}")


if __name__ == "__main__":
    run()
