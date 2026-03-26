#!/usr/bin/env python3
"""
Batch v27: o3-mini — OpenAI reasoning model (second o-series in dataset).
Goals:
  - Add o3-mini to cross-model replication table (currently only o4-mini represents reasoning models)
  - Test whether older reasoning model (o3-mini) shows same semantic priming pattern
  - Design: 3 conditions × 3 personas × 3 prompts × 2 temps × 1 rep = 54 samples
  - o3-mini uses max_completion_tokens, no system role injection (same as o4-mini)

Scientific motivation:
  - o4-mini (already in dataset): d_DN=1.45, d_CN=1.36 — reasoning does not suppress priming
  - o3-mini: tests if this pattern is consistent across the o-series generation
  - Expected: similar moderate d, directional D>N and C>N

Output: results/real_experiments/batch_v27_o3mini.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v27_o3mini.jsonl"
OPENAI_BASE = "https://api.openai.com/v1/chat/completions"

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
        "첫 문장을 '그 결정을 되돌릴 수 있다면...'으로 시작해 8~10문장 자기성찰 글을 완성하라.",
    ],
}

TEMPERATURES = [0.4, 0.7]
REPS = 1
BATCH_ID = "v27"
MODEL_ID = "o3-mini"


def load_env():
    env_file = ROOT / ".env.real_model"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip().strip("'\"")


def call_o3mini(prompt: str, persona_text: str, temperature: float, api_key: str) -> str:
    """Call o3-mini (reasoning model). No system role, uses max_completion_tokens."""
    messages = []
    if persona_text:
        user_content = f"{persona_text}\n\n{prompt}"
    else:
        user_content = prompt

    messages.append({"role": "user", "content": user_content})

    payload = {
        "model": MODEL_ID,
        "messages": messages,
        "max_completion_tokens": 800,
    }
    # o3-mini does not support temperature parameter directly; omit it
    # (temperature is fixed at 1 for reasoning models)

    resp = requests.post(
        OPENAI_BASE,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=120,
    )
    if resp.status_code != 200:
        raise RuntimeError(f"HTTP {resp.status_code}: {resp.text[:300]}")
    return resp.json()["choices"][0]["message"]["content"].strip()


def run():
    load_env()
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set — run: source .env.real_model")

    # Load existing to allow resume
    existing = set()
    if OUT_FILE.exists():
        with OUT_FILE.open(encoding="utf-8") as f:
            for line in f:
                try:
                    row = json.loads(line)
                    key = (row["condition"], row["persona"], row.get("temperature", 0), row["prompt_idx"], row.get("rep", 0))
                    existing.add(key)
                except Exception:
                    pass
    print(f"Resuming: {len(existing)} samples already written.")

    tasks = []
    for condition, prompts in CONDITION_PROMPTS.items():
        for p_idx, prompt_text in enumerate(prompts):
            for persona_name, persona_text in PERSONAS.items():
                for temp in TEMPERATURES:
                    for rep in range(REPS):
                        tasks.append({
                            "condition": condition,
                            "prompt_idx": p_idx,
                            "prompt": prompt_text,
                            "persona": persona_name,
                            "persona_text": persona_text,
                            "temperature": temp,
                            "rep": rep,
                        })

    print(f"Total planned: {len(tasks)} samples (model={MODEL_ID})")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    done = 0
    skipped = 0
    errors = 0

    with OUT_FILE.open("a", encoding="utf-8") as fout:
        for i, t in enumerate(tasks):
            key = (t["condition"], t["persona"], t["temperature"], t["prompt_idx"], t["rep"])
            if key in existing:
                skipped += 1
                continue

            try:
                output = call_o3mini(t["prompt"], t["persona_text"], t["temperature"], api_key)

                row = {
                    "id": str(uuid.uuid4()),
                    "batch": BATCH_ID,
                    "model": MODEL_ID,
                    "condition": t["condition"],
                    "persona": t["persona"],
                    "temperature": t["temperature"],
                    "prompt_idx": t["prompt_idx"],
                    "prompt": t["prompt"],
                    "rep": t["rep"],
                    "output": output,
                    "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                    "is_reasoning": True,
                }
                fout.write(json.dumps(row, ensure_ascii=False) + "\n")
                fout.flush()
                done += 1
                existing.add(key)

                if done % 10 == 0:
                    print(f"  [{i+1}/{len(tasks)}] done={done} skip={skipped} err={errors} — {t['condition']} {t['persona']}")

                time.sleep(1.5)  # rate limit for reasoning model

            except Exception as e:
                errors += 1
                print(f"  ERROR [{i+1}] {t['condition']} p{t['prompt_idx']} rep{t['rep']}: {e}")
                time.sleep(3.0)

    print(f"\nDone. Written={done}, Skipped={skipped}, Errors={errors}")
    print(f"Output: {OUT_FILE}")
    return done


if __name__ == "__main__":
    run()
