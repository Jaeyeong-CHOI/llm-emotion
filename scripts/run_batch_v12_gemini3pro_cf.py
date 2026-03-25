#!/usr/bin/env python3
"""
Batch v12: gemini-3-pro-preview CF condition fill.
Goal: add counterfactual samples for gemini-3-pro-preview.
Currently: dep=19, cf=0, neu=36 → need CF to match other models (~54 CF).
Strategy: 3 CF scenarios × 3 personas × 2 temps × 3 reps = 54 samples.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]

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
    ("near_miss_outcome",
     "가까스로 놓친 목표나 기회를 주제로 '그때 조금만 달랐다면'이라는 생각을 담아 7~10문장 회고문을 작성하라."),
    ("counterfactual_if_only",
     "첫 문장을 '그때 다른 선택을 했다면...'으로 시작하고 7~10문장 자기성찰 글을 작성하라. 과거 선택, 현재 감정, 앞으로의 태도를 모두 포함하라."),
    ("counterfactual_feedback_delay",
     "피드백을 제때 받지 못해 잘못된 방향을 오래 유지한 경험을 7~9문장으로 회고하라. '조금만 빨랐다면'이라는 대안적 사고를 포함하라."),
]

MODEL = "gemini-3-pro-preview"
TEMPERATURES = [0.2, 0.7]
PERSONA_KEYS = ["none", "reflective", "ruminative"]
BATCH_NAME = "batch_v12_gemini3pro_cf"
# 3 scenarios × 3 personas × 2 temps × 3 reps = 54
REPS_PER_COMBO = 3


def call_gemini(prompt: str, temperature: float, api_key: str, model: str) -> str:
    import urllib.request
    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
        f"?key={api_key}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": 600},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.loads(r.read())
    return resp["candidates"][0]["content"]["parts"][0]["text"].strip()


def build_plan():
    plan = []
    for scen_id, scen_prompt in CF_PROMPTS:
        for persona_key in PERSONA_KEYS:
            persona_text = PERSONAS[persona_key]
            for temp in TEMPERATURES:
                for _ in range(REPS_PER_COMBO):
                    full_prompt = f"{persona_text}\n\n{scen_prompt}" if persona_text else scen_prompt
                    plan.append({
                        "model": MODEL,
                        "scenario_id": scen_id,
                        "persona": persona_key,
                        "temperature": temp,
                        "full_prompt": full_prompt,
                        "scenario_prompt": scen_prompt,
                    })
    return plan


def main():
    # Load .env
    env_path = ROOT / ".env.real_model"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("export "):
                line = line[7:]
            if "=" in line and not line.startswith("#"):
                k, v = line.split("=", 1)
                v = v.strip().strip('"').strip("'")
                os.environ.setdefault(k.strip(), v)

    gemini_key = os.environ.get("GEMINI_API_KEY", "")
    if not gemini_key:
        print("ERROR: GEMINI_API_KEY not set", file=sys.stderr)
        return 1

    out_path = ROOT / "results" / "real_experiments" / f"{BATCH_NAME}.jsonl"
    existing_n = 0
    if out_path.exists():
        with out_path.open(encoding="utf-8") as f:
            existing_n = sum(1 for line in f if line.strip())
        print(f"Resuming: {existing_n} already collected in {out_path.name}")

    plan = build_plan()
    total = len(plan)
    print(f"Plan: {total} CF samples for {MODEL}")

    collected = 0
    errors = 0

    with out_path.open("a", encoding="utf-8") as f_out:
        for i, item in enumerate(plan):
            if i < existing_n:
                continue

            try:
                output = call_gemini(item["full_prompt"], item["temperature"], gemini_key, MODEL)

                record = {
                    "batch": BATCH_NAME,
                    "model": MODEL,
                    "condition": "counterfactual",
                    "scenario_id": item["scenario_id"],
                    "persona": item["persona"],
                    "temperature": item["temperature"],
                    "output": output,
                    "output_length": len(output),
                }
                f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
                f_out.flush()
                collected += 1

                if collected % 10 == 0:
                    print(f"  [{i+1}/{total}] collected={collected} errors={errors}")
                time.sleep(1.0)

            except Exception as e:
                errors += 1
                print(f"  ERROR [{i+1}]: {e}", file=sys.stderr)
                if "429" in str(e) or "quota" in str(e).lower():
                    print("  Rate limit — sleeping 30s", file=sys.stderr)
                    time.sleep(30)
                else:
                    time.sleep(3)

    print(f"\nDone. collected={collected}, errors={errors}, total_in_file={existing_n + collected}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
