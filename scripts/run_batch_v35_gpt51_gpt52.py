#!/usr/bin/env python3
"""
Batch v35: gpt-5.1, gpt-5.2 — Next-generation GPT-5.x family.
Also fills gpt-5 / gpt-5-mini neutral stability gap (n_N=27 → ≥30).

Scientific motivation:
  - gpt-5.4 variants (mini/nano): small d ≈ 0.42-0.50 (alignment-dampened?)
  - gpt-5 base family (v34): large d ≈ 3.2-4.85 (strong semantic priming)
  - Question: gpt-5.1 / gpt-5.2 (released 2025-11/2025-12) — intermediate or different?
  - Fills longitudinal coverage: 5.0 → 5.1 → 5.2 → 5.4 generational arc
  - gpt-5 neutral fill: bump n_N from 27→≥30 for full stability status

Design:
  - 3 conditions × 3 personas × 3 prompts × 1 temp × 3 reps = 81 samples/model
  - Total new: 162 samples (81 × 2 models)
  - Plus stability fill for gpt-5, gpt-5-mini neutral (≈12 samples each)
  - Temperature: 1.0 only (gpt-5.x family behavior)
  - max_completion_tokens=1024 (not a reasoning model like gpt-5 base)

Output: results/real_experiments/batch_v35_gpt51_gpt52.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v35_gpt51_gpt52.jsonl"
OPENAI_BASE = "https://api.openai.com/v1/chat/completions"

BATCH_ID = "batch_v35_gpt51_gpt52"
TEMPERATURES = [1.0]
REPS = 3

MODELS = ["gpt-5.1", "gpt-5.2"]

# Stability fill models and their needed neutral count
STABILITY_FILL = {
    "gpt-5": {"target_N_neutral": 30, "current_N_neutral": 27, "needs": 3},
    "gpt-5-mini": {"target_N_neutral": 30, "current_N_neutral": 27, "needs": 3},
}

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


def load_env():
    env_path = ROOT / ".env.real_model"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ[k] = v


def call_openai(
    prompt: str, persona_text: str, temperature: float, api_key: str, model: str
) -> str:
    """Call OpenAI chat model — gpt-5.x series uses max_completion_tokens."""
    messages = []
    if persona_text:
        messages.append({"role": "system", "content": persona_text})
    messages.append({"role": "user", "content": prompt})

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload: dict = {
        "model": model,
        "messages": messages,
        "max_completion_tokens": 1024,
    }
    # gpt-5.x family: temperature=1.0 is default; omit to avoid errors
    if temperature != 1.0:
        payload["temperature"] = temperature

    for attempt in range(4):
        try:
            resp = requests.post(OPENAI_BASE, headers=headers, json=payload, timeout=90)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"].strip()
            elif resp.status_code == 429:
                wait = 30 * (attempt + 1)
                print(f"  [rate-limit] waiting {wait}s …")
                time.sleep(wait)
            else:
                print(f"  [error] {resp.status_code}: {resp.text[:200]}")
                return ""
        except requests.exceptions.Timeout:
            print(f"  [timeout] attempt {attempt + 1}")
            time.sleep(15)
    return ""


def main():
    load_env()
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("[FATAL] OPENAI_API_KEY not set.")
        return

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Resume support
    done: set[tuple] = set()
    if OUT_FILE.exists():
        with open(OUT_FILE) as fh:
            for line in fh:
                try:
                    r = json.loads(line)
                    key = (r["model"], r["condition"], r["persona"], r["prompt_idx"],
                           r["temperature"], r["rep"])
                    done.add(key)
                except Exception:
                    pass
        print(f"[resume] {len(done)} rows already written — skipping.")

    total_planned = len(MODELS) * len(CONDITION_PROMPTS) * len(PERSONAS) * 3 * len(TEMPERATURES) * REPS
    print(f"[batch {BATCH_ID}] planned={total_planned} samples for {MODELS}")
    print(f"[stability fill] gpt-5 (+3 neutral), gpt-5-mini (+3 neutral)")

    written = 0

    # --- Main collection: gpt-5.1 and gpt-5.2 ---
    for model in MODELS:
        for cond, prompts in CONDITION_PROMPTS.items():
            for persona_name, persona_text in PERSONAS.items():
                for pidx, prompt in enumerate(prompts):
                    for temp in TEMPERATURES:
                        for rep in range(REPS):
                            key = (model, cond, persona_name, pidx, temp, rep)
                            if key in done:
                                continue

                            text = call_openai(
                                prompt=prompt,
                                persona_text=persona_text,
                                temperature=temp,
                                api_key=api_key,
                                model=model,
                            )
                            if not text:
                                print(f"  [skip] empty response for {key}")
                                continue

                            row = {
                                "id": str(uuid.uuid4()),
                                "batch_id": BATCH_ID,
                                "model": model,
                                "condition": cond,
                                "persona": persona_name,
                                "prompt_idx": pidx,
                                "prompt": prompt,
                                "temperature": temp,
                                "rep": rep,
                                "text": text,
                            }
                            with open(OUT_FILE, "a") as fh:
                                fh.write(json.dumps(row, ensure_ascii=False) + "\n")

                            written += 1
                            print(f"  [{written}] {model} | {cond} | {persona_name} | t={temp} | rep={rep}")
                            time.sleep(0.5)

    # --- Stability fill: gpt-5 and gpt-5-mini neutral top-up ---
    # We add 3 more neutral samples per model per persona (=9 each → 27+9=36, safely over 30)
    fill_prompts = CONDITION_PROMPTS["neutral"]
    fill_models_and_reps = {
        "gpt-5": 3,       # add 3 reps (9 samples) → n_N from 27 to 36
        "gpt-5-mini": 3,  # same
    }
    fill_batch_id = "batch_v35_stability_fill"

    for fill_model, extra_reps in fill_models_and_reps.items():
        for persona_name, persona_text in PERSONAS.items():
            for pidx, prompt in enumerate(fill_prompts):
                for temp in TEMPERATURES:
                    for rep in range(extra_reps):
                        # Use offset reps to avoid collision with existing v34 data
                        key = (fill_model, "neutral", persona_name, pidx, temp, rep + 100)
                        if key in done:
                            continue

                        text = call_openai(
                            prompt=prompt,
                            persona_text=persona_text,
                            temperature=temp,
                            api_key=api_key,
                            model=fill_model,
                        )
                        if not text:
                            print(f"  [fill-skip] empty response for {key}")
                            continue

                        row = {
                            "id": str(uuid.uuid4()),
                            "batch_id": fill_batch_id,
                            "model": fill_model,
                            "condition": "neutral",
                            "persona": persona_name,
                            "prompt_idx": pidx,
                            "prompt": prompt,
                            "temperature": temp,
                            "rep": rep + 100,
                            "text": text,
                        }
                        with open(OUT_FILE, "a") as fh:
                            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

                        written += 1
                        print(f"  [fill {written}] {fill_model} | neutral | {persona_name} | t={temp} | rep={rep+100}")
                        time.sleep(0.5)

    print(f"\n[done] wrote {written} new rows → {OUT_FILE}")
    if written > 0:
        print("Next step: run post_batch_pipeline.sh or embed + LME rerun")


if __name__ == "__main__":
    main()
