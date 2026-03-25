#!/usr/bin/env python3
"""
Batch v25: Balance groq/compound to ~54/condition.
Current: D=32, N=36, CF=32 → need +22 D, +22 CF (N already at 36 ~ok)

Design: 3 personas × selected prompts × 2 temps = up to 36/condition
Output: results/real_experiments/batch_v25_groq_compound_balance.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v25_groq_compound_balance.jsonl"
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
    "deprivation": [
        "매우 원했지만 결국 놓친 기회를 떠올려 7~9문장으로 써라. 무엇을 잃었는지와 현재 남은 감정을 포함하라.",
        "인생에서 꼭 하고 싶었으나 하지 못한 일을 8문장으로 써라. 잃어버린 것과 지금 남은 마음을 모두 담아라.",
        "중요한 선택의 기회를 놓쳤던 순간을 7~9문장으로 묘사하라. 그때의 상실감과 현재의 감정 상태를 포함하라.",
        "오래 기다렸던 무언가를 결국 얻지 못했던 경험을 8~10문장으로 써라. 박탈감과 남은 감정을 구체적으로 표현하라.",
    ],
    "counterfactual": [
        "첫 문장을 '그때 다른 선택을 했다면...'으로 시작하고 7~10문장 자기성찰 글을 작성하라.",
        "첫 문장을 '만약 그 순간으로 돌아갈 수 있다면...'으로 시작하는 8문장 성찰 글을 써라.",
        "첫 문장을 '그 결정을 되돌릴 수 있다면...'으로 시작해 8~10문장 자기성찰 글을 완성하라.",
        "첫 문장을 '다시 선택할 수 있다면 나는...'으로 시작해 7~9문장의 반성문을 작성하라.",
    ],
}

TEMPERATURES = [0.2, 0.7]
REPS = 3  # 4 prompts × 3 personas × 2 temps × 3 reps = 72 → take 22/condition needed

MODEL = "groq/compound"

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")


def call_groq(model: str, system_prompt: str, user_prompt: str, temperature: float) -> str:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 400,
    }
    resp = requests.post(
        GROQ_BASE,
        headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def load_existing() -> set[str]:
    """Load existing samples to avoid duplicates."""
    seen = set()
    if OUT_FILE.exists():
        for line in OUT_FILE.read_text(errors="replace").splitlines():
            if line.strip():
                try:
                    r = json.loads(line)
                    key = f"{r.get('condition')}_{r.get('persona')}_{r.get('temperature')}_{r.get('prompt_idx', 0)}"
                    seen.add(key)
                except Exception:
                    pass
    return seen


def main() -> None:
    if not GROQ_API_KEY:
        raise RuntimeError("GROQ_API_KEY not set — run: source .env.real_model")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Count existing per condition
    existing = {"deprivation": 0, "counterfactual": 0}
    if OUT_FILE.exists():
        for line in OUT_FILE.read_text(errors="replace").splitlines():
            if line.strip():
                try:
                    r = json.loads(line)
                    c = r.get("condition", "")
                    if c in existing:
                        existing[c] += 1
                except Exception:
                    pass

    # Also count from main batch
    main_batch = ROOT / "results" / "real_experiments" / "batch_v17_groq_compound.jsonl"
    base_counts = {"deprivation": 0, "counterfactual": 0, "neutral": 0}
    if main_batch.exists():
        for line in main_batch.read_text(errors="replace").splitlines():
            if line.strip():
                try:
                    r = json.loads(line)
                    c = r.get("condition", "")
                    if c in base_counts and r.get("model") == MODEL:
                        base_counts[c] += 1
                except Exception:
                    pass
    # Also check all other batches for groq/compound
    for bf in ROOT.glob("results/real_experiments/batch_v*.jsonl"):
        if "emb" in bf.name or bf.name == "batch_v17_groq_compound.jsonl":
            continue
        try:
            for line in bf.read_text(errors="replace").splitlines():
                if line.strip():
                    r = json.loads(line)
                    if r.get("model") == MODEL:
                        c = r.get("condition", "")
                        if c in base_counts:
                            base_counts[c] += 1
        except Exception:
            pass

    print(f"Base counts for {MODEL}: {base_counts}")
    TARGET = 54
    need = {
        "deprivation": max(0, TARGET - base_counts["deprivation"] - existing["deprivation"]),
        "counterfactual": max(0, TARGET - base_counts["counterfactual"] - existing["counterfactual"]),
    }
    print(f"Need: {need}")

    total_written = 0
    for condition, prompts in CONDITION_PROMPTS.items():
        if need.get(condition, 0) <= 0:
            print(f"Skipping {condition} (already at target)")
            continue

        written_for_cond = 0
        for persona_name, persona_text in PERSONAS.items():
            for prompt_idx, prompt in enumerate(prompts):
                for temp in TEMPERATURES:
                    if written_for_cond >= need[condition]:
                        break
                    try:
                        output = call_groq(MODEL, persona_text, prompt, temp)
                        record = {
                            "id": str(uuid.uuid4()),
                            "batch": "batch_v25_groq_compound_balance",
                            "model": MODEL,
                            "condition": condition,
                            "persona": persona_name,
                            "temperature": temp,
                            "prompt_idx": prompt_idx,
                            "prompt": prompt,
                            "output": output,
                        }
                        with open(OUT_FILE, "a", encoding="utf-8") as f:
                            f.write(json.dumps(record, ensure_ascii=False) + "\n")
                        written_for_cond += 1
                        total_written += 1
                        print(f"  [{condition}/{persona_name}/t={temp}/p{prompt_idx}] → {len(output)} chars")
                        time.sleep(0.5)
                    except Exception as e:
                        print(f"  ERROR: {e}")
                        time.sleep(2)

    print(f"\nDone. Written {total_written} new samples to {OUT_FILE}")


if __name__ == "__main__":
    main()
