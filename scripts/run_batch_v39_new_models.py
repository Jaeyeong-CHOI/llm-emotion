#!/usr/bin/env python3
"""
Batch v39: New model family additions.

Targets:
  1. gpt-5-pro  — via OpenAI Responses API (not chat completions)
     Scientific motivation: gpt-5-pro is OpenAI's top-tier frontier model
     as of late 2025. Prior GPT-5 base family shows large effects (d=1.68-1.85).
     gpt-5-pro may show dampened or amplified effects due to enhanced RLHF.

  2. gpt-5.3-chat-latest — via OpenAI chat completions
     Scientific motivation: Fills the generational arc gap between gpt-5.2
     and gpt-5.4. Completing 5.0→5.1→5.2→5.3→5.4 arc gives a longitudinal
     view of alignment dampening across the GPT-5 family.

Design (consistent with prior batches):
  - 3 conditions × 3 personas × 3 prompts × 1 temperature × 3 reps = 81 samples/model
  - Total: 162 samples (81 × 2 models)
  - Temperature: 1.0 (consistent with GPT-5.x family convention)
  - gpt-5-pro: Responses API (requires different calling convention)
  - gpt-5.3-chat-latest: standard chat completions API

Expected contribution:
  - Extends coverage from 37 → 39 model variants
  - Completes GPT-5.x generational arc (5.0, 5.1, 5.2, 5.3, 5.4)
  - Tests whether top-tier pro model shows alignment-dampened effect

Output: results/real_experiments/batch_v39_new_models.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v39_new_models.jsonl"
OPENAI_CHAT_BASE = "https://api.openai.com/v1/chat/completions"
OPENAI_RESPONSES_BASE = "https://api.openai.com/v1/responses"

BATCH_ID = "batch_v39_new_models"
TEMPERATURE = 1.0
REPS = 3

# Models and their calling convention
# Format: (model_id, api_type)
# api_type: "chat" | "responses"
MODELS = [
    ("gpt-5.3-chat-latest", "chat"),
    ("gpt-5-pro", "responses"),
]

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


def load_env() -> None:
    env_path = ROOT / ".env.real_model"
    if env_path.exists():
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    k, v = line.split("=", 1)
                    os.environ[k] = v


def call_chat(
    prompt: str, persona_text: str, api_key: str, model: str
) -> str:
    """Call OpenAI chat completions API (gpt-5.3-chat-latest)."""
    messages = []
    if persona_text:
        messages.append({"role": "system", "content": persona_text})
    messages.append({"role": "user", "content": prompt})

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload: dict = {
        "model": model,
        "messages": messages,
        "max_completion_tokens": 1024,
        # temperature=1.0 is default for GPT-5.x; omit to avoid issues
    }

    for attempt in range(4):
        try:
            resp = requests.post(OPENAI_CHAT_BASE, headers=headers, json=payload, timeout=90)
            if resp.status_code == 200:
                return resp.json()["choices"][0]["message"]["content"].strip()
            elif resp.status_code == 429:
                wait = 30 * (attempt + 1)
                print(f"  [rate-limit] waiting {wait}s ...")
                time.sleep(wait)
            else:
                print(f"  [error {resp.status_code}] {resp.text[:200]}")
                return ""
        except requests.exceptions.Timeout:
            print(f"  [timeout] attempt {attempt + 1}")
            time.sleep(15)
    return ""


def call_responses(
    prompt: str, persona_text: str, api_key: str, model: str
) -> str:
    """Call OpenAI Responses API (gpt-5-pro)."""
    # Responses API: concatenate system+user or use instructions param
    full_input = prompt
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload: dict = {
        "model": model,
        "input": full_input,
        "max_output_tokens": 1024,
    }
    if persona_text:
        payload["instructions"] = persona_text

    for attempt in range(4):
        try:
            resp = requests.post(OPENAI_RESPONSES_BASE, headers=headers, json=payload, timeout=120)
            if resp.status_code == 200:
                data = resp.json()
                # Extract text from output
                for item in data.get("output", []):
                    if item.get("type") == "message":
                        for content in item.get("content", []):
                            if content.get("type") == "output_text":
                                return content.get("text", "").strip()
                # Fallback: check text field
                text_obj = data.get("text", {})
                if isinstance(text_obj, dict) and "value" in text_obj:
                    return text_obj["value"].strip()
                return ""
            elif resp.status_code == 429:
                wait = 30 * (attempt + 1)
                print(f"  [rate-limit] waiting {wait}s ...")
                time.sleep(wait)
            else:
                print(f"  [error {resp.status_code}] {resp.text[:200]}")
                return ""
        except requests.exceptions.Timeout:
            print(f"  [timeout] attempt {attempt + 1}")
            time.sleep(15)
    return ""


def main() -> None:
    load_env()
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("[FATAL] OPENAI_API_KEY not set.")
        return

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Resume support
    done: set = set()
    if OUT_FILE.exists():
        with open(OUT_FILE) as fh:
            for line in fh:
                try:
                    r = json.loads(line)
                    key = (r["model"], r["condition"], r["persona"], r["prompt_idx"],
                           r["rep"])
                    done.add(key)
                except Exception:
                    pass
        print(f"[resume] {len(done)} rows already written — skipping.")

    total_planned = len(MODELS) * len(CONDITION_PROMPTS) * len(PERSONAS) * 3 * REPS
    print(f"[batch {BATCH_ID}] planned={total_planned} samples for {[m for m,_ in MODELS]}")

    written = 0

    for model_id, api_type in MODELS:
        print(f"\n[model] {model_id} (API: {api_type})")
        for cond, prompts in CONDITION_PROMPTS.items():
            for persona_name, persona_text in PERSONAS.items():
                for pidx, prompt in enumerate(prompts):
                    for rep in range(REPS):
                        key = (model_id, cond, persona_name, pidx, rep)
                        if key in done:
                            continue

                        if api_type == "chat":
                            text = call_chat(prompt, persona_text, api_key, model_id)
                        else:
                            text = call_responses(prompt, persona_text, api_key, model_id)

                        if not text:
                            print(f"  [skip] empty response for {key}")
                            continue

                        row = {
                            "id": str(uuid.uuid4()),
                            "batch_id": BATCH_ID,
                            "model": model_id,
                            "condition": cond,
                            "persona": persona_name,
                            "prompt_idx": pidx,
                            "prompt": prompt,
                            "temperature": TEMPERATURE,
                            "rep": rep,
                            "text": text,
                        }
                        with open(OUT_FILE, "a") as fh:
                            fh.write(json.dumps(row, ensure_ascii=False) + "\n")

                        written += 1
                        print(f"  [{written}] {model_id} | {cond} | {persona_name} | rep={rep}")
                        time.sleep(0.8)

    print(f"\n[done] wrote {written} new rows → {OUT_FILE}")
    if written > 0:
        print("Next step: bash scripts/post_batch_v39_pipeline.sh")


if __name__ == "__main__":
    main()
