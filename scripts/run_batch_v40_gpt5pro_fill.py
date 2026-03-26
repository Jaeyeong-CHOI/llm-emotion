#!/usr/bin/env python3
"""
Batch v40: GPT-5-Pro stabilization fill.

Motivation:
  Current GPT-5-Pro count is n=15 (6N/4D/5CF), below the n>=30 threshold
  required for stable per-model effect estimates. This batch targets balanced
  coverage: 10 per condition (neutral/deprivation/counterfactual) = 30 total,
  adding ~15 more samples to reach the stable-model tier.

  GPT-5-Pro uses the OpenAI Responses API (not chat completions).
  Scientific importance: gpt-5-pro is OpenAI's top-tier frontier model;
  its effect size vs. gpt-5.x family provides alignment-dampening evidence.

Design:
  - 3 conditions × 3 personas × 2 prompts × 1 temperature × 1 rep = 18/condition
  - Total target: 54 samples (overcollect slightly, then we have n~33/cond balanced)
  - Temperature: 1.0 (consistent with GPT-5.x family)
  - API: Responses API

Output: results/real_experiments/batch_v40_gpt5pro_fill.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v40_gpt5pro_fill.jsonl"
OPENAI_RESPONSES_BASE = "https://api.openai.com/v1/responses"

BATCH_ID = "batch_v40_gpt5pro_fill"
TEMPERATURE = 1.0
MODEL = "gpt-5-pro"

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
    ],
    "deprivation": [
        "매우 원했지만 결국 놓친 기회를 떠올려 7~9문장으로 써라. 무엇을 잃었는지와 현재 남은 감정을 포함하라.",
        "인생에서 꼭 하고 싶었으나 하지 못한 일을 8문장으로 써라. 잃어버린 것과 지금 남은 마음을 모두 담아라.",
    ],
    "counterfactual": [
        "첫 문장을 '그때 다른 선택을 했다면...'으로 시작하고 7~10문장 자기성찰 글을 작성하라.",
        "첫 문장을 '만약 그 순간으로 돌아갈 수 있다면...'으로 시작하는 8문장 성찰 글을 써라.",
    ],
}


def call_responses_api(api_key: str, system_prompt: str, user_prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body: dict = {
        "model": MODEL,
        "input": user_prompt,
        "max_output_tokens": 512,
        "temperature": TEMPERATURE,
    }
    if system_prompt:
        body["instructions"] = system_prompt

    resp = requests.post(OPENAI_RESPONSES_BASE, headers=headers, json=body, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    # Responses API: output[0].content[0].text
    try:
        return data["output"][0]["content"][0]["text"]
    except (KeyError, IndexError):
        # fallback
        return data.get("output_text", "") or json.dumps(data)


def main() -> None:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    written = 0

    for condition, prompts in CONDITION_PROMPTS.items():
        for persona_id, persona_text in PERSONAS.items():
            for prompt_text in prompts:
                sample_id = str(uuid.uuid4())
                t0 = time.time()
                try:
                    text = call_responses_api(api_key, persona_text, prompt_text)
                    elapsed = time.time() - t0
                    record = {
                        "id": sample_id,
                        "batch_id": BATCH_ID,
                        "model": MODEL,
                        "condition": condition,
                        "persona": persona_id,
                        "prompt": prompt_text,
                        "response": text,
                        "temperature": TEMPERATURE,
                        "elapsed_s": round(elapsed, 2),
                        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "error": None,
                    }
                    print(f"  [OK] {condition}/{persona_id} → {len(text)} chars in {elapsed:.1f}s")
                except Exception as e:
                    elapsed = time.time() - t0
                    record = {
                        "id": sample_id,
                        "batch_id": BATCH_ID,
                        "model": MODEL,
                        "condition": condition,
                        "persona": persona_id,
                        "prompt": prompt_text,
                        "response": "",
                        "temperature": TEMPERATURE,
                        "elapsed_s": round(elapsed, 2),
                        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                        "error": str(e),
                    }
                    print(f"  [ERR] {condition}/{persona_id}: {e}")

                with open(OUT_FILE, "a", encoding="utf-8") as fout:
                    fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                written += 1

                time.sleep(0.5)  # rate limit buffer

    print(f"\n[Done] {written} records written to {OUT_FILE}")


if __name__ == "__main__":
    main()
