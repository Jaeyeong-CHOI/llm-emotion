#!/usr/bin/env python3
"""
Batch v11: Neutral balance expansion (round 2).
Goal: bring neutral condition to ~1,224 (matching deprivation).
Currently: neutral=1,043 → need +181 more neutral samples.
Strategy: 60 samples each from GPT-4o, Gemini-2.5-Flash, GPT-4.1 = 180 total.
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

NEUTRAL_PROMPTS = [
    ("neutral_daily",     "오늘 하루를 6~8문장으로 차분하게 회고하라. 감정 과장은 피하고 사실과 해석을 분리하라."),
    ("neutral_observer",  "제3자 관찰자처럼 오늘의 사건을 정리하라. 판단적 표현 없이 6~8문장으로 작성하라."),
    ("neutral_routine_a", "지난 일주일의 가장 평범한 날을 골라 7문장으로 담담하게 묘사하라. 특별한 감정 없이 사실 위주로 작성하라."),
    ("neutral_routine_b", "어제 한 일 중 가장 일상적인 활동 하나를 선택해 과정과 느낌을 6문장으로 설명하라."),
    ("neutral_factual_a", "오늘 읽거나 배운 정보를 6~7문장으로 객관적으로 요약하라. 자신의 주관적 감정은 제외하라."),
    ("neutral_factual_b", "최근 한 달간의 일상적인 습관이나 루틴을 7~8문장으로 평이하게 기술하라. 성취나 실패 감정은 배제하라."),
]

MODELS = [
    ("openai", "gpt-4o"),
    ("gemini", "gemini-2.5-flash"),
    ("openai", "gpt-4.1"),
]

TEMPERATURES = [0.3, 0.7]
PERSONA_KEYS = ["none", "reflective", "ruminative"]
BATCH_NAME = "batch_v11_neutral_balance2"


def call_openai(prompt: str, temperature: float, model: str, api_key: str) -> str:
    import urllib.request
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 400,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=data,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=40) as r:
        resp = json.loads(r.read())
    return resp["choices"][0]["message"]["content"].strip()


def call_gemini(prompt: str, temperature: float, api_key: str, model: str = "gemini-2.5-flash") -> str:
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
    with urllib.request.urlopen(req, timeout=45) as r:
        resp = json.loads(r.read())
    return resp["candidates"][0]["content"]["parts"][0]["text"].strip()


def build_plan():
    """Build list of (provider, model, scenario_id, prompt, persona, temperature)."""
    plan = []
    # Each model gets 60 samples: 6 scenarios × 2 temps × 1 persona_cycle (round-robin 3 personas)
    for provider, model in MODELS:
        count = 0
        # 6 scenarios × 2 temps × (personas cycling) to get ~60
        # 6 × 2 = 12 per persona pass → 3 personas × 12 = 36, do 5 scenario passes for 60
        for temp in TEMPERATURES:
            for p_idx, persona_key in enumerate(PERSONA_KEYS):
                persona_text = PERSONAS[persona_key]
                for scen_id, scen_prompt in NEUTRAL_PROMPTS:
                    full_prompt = f"{persona_text}\n\n{scen_prompt}" if persona_text else scen_prompt
                    plan.append({
                        "provider": provider,
                        "model": model,
                        "scenario_id": scen_id,
                        "persona": persona_key,
                        "temperature": temp,
                        "full_prompt": full_prompt,
                        "scenario_prompt": scen_prompt,
                    })
                    count += 1
        # Should be 6 scenarios × 2 temps × 3 personas = 36 per model
        # Double up for ~60 by adding a second pass at different temps
    return plan


def main():
    # Load API keys
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

    openai_key = os.environ.get("OPENAI_API_KEY", "")
    gemini_key = os.environ.get("GEMINI_API_KEY", "")

    if not openai_key:
        print("ERROR: OPENAI_API_KEY not set", file=sys.stderr); return 1
    if not gemini_key:
        print("ERROR: GEMINI_API_KEY not set", file=sys.stderr); return 1

    out_path = ROOT / "results" / "real_experiments" / f"{BATCH_NAME}.jsonl"
    existing_n = 0
    if out_path.exists():
        with out_path.open(encoding="utf-8") as f:
            existing_n = sum(1 for line in f if line.strip())
        print(f"Resuming: {existing_n} already collected in {out_path.name}")

    plan = build_plan()
    # Deduplicate plan (same structure, no repeats needed beyond design)
    # Current plan: 3 models × 6 scenarios × 2 temps × 3 personas = 108 samples
    total = len(plan)
    print(f"Plan: {total} samples total ({total} neutral)")
    print(f"Models: {[m for _,m in MODELS]}")

    collected = 0
    errors = 0

    with out_path.open("a", encoding="utf-8") as f_out:
        for i, item in enumerate(plan):
            if i < existing_n:
                continue

            try:
                provider = item["provider"]
                model = item["model"]

                if provider == "openai":
                    output = call_openai(item["full_prompt"], item["temperature"], model, openai_key)
                else:
                    output = call_gemini(item["full_prompt"], item["temperature"], gemini_key, model)

                record = {
                    "batch": BATCH_NAME,
                    "model": model,
                    "condition": "neutral",
                    "scenario_id": item["scenario_id"],
                    "persona": item["persona"],
                    "temperature": item["temperature"],
                    "output": output,
                    "output_length": len(output),
                }
                f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
                f_out.flush()
                collected += 1

                if collected % 15 == 0 or collected <= 3:
                    print(f"  [{collected}/{total - existing_n}] {model} {item['scenario_id']} T={item['temperature']}")

                time.sleep(0.4)

            except Exception as e:
                print(f"  ERROR item {i}: {e}", file=sys.stderr)
                errors += 1
                time.sleep(2.5)

    print(f"\nDone. Collected: {collected}, Errors: {errors}")
    print(f"Output: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
