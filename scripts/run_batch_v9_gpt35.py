#!/usr/bin/env python3
"""
Batch v9: GPT-3.5-turbo samples.
Goals:
  1. Bring deprivation to N~500 (+30 dep)
  2. Add cross-model replication samples (+30 CF, +30 neutral)
  3. Introduce gpt-3.5-turbo as third model (alongside gpt-4o, gemini-2.5-flash)
Output: results/real_experiments/batch_v9_gpt35.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

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
        "오래 기다렸던 무언가를 결국 얻지 못했던 경험을 8~10문장으로 써라. 박탈감과 남은 감정을 구체적으로 표현하라.",
    ],
    "counterfactual": [
        "첫 문장을 '그때 다른 선택을 했다면...'으로 시작하고 7~10문장 자기성찰 글을 작성하라. 과거 선택, 현재 감정, 앞으로의 태도를 모두 포함하라.",
        "첫 문장을 '만약 그 순간으로 돌아갈 수 있다면...'으로 시작하는 8문장 성찰 글을 써라. 다른 선택의 결과를 상상하고 현재 감정을 담아라.",
        "첫 문장을 '그때 포기하지 않았더라면...'으로 시작해 7~9문장으로 과거와 현재를 연결하는 성찰 글을 작성하라.",
    ],
}

TEMPERATURES = [0.3, 0.7]
MODEL = "gpt-3.5-turbo"
# Samples per (condition, scenario_idx, persona, temperature): 1
# dep: 4 scenarios × 3 personas × 2 temps × 1 = 24, +6 extra = 30
# cf: 3 scenarios × 3 personas × 2 temps × 1 = 18, +12 extra = 30
# neutral: 3 scenarios × 3 personas × 2 temps × 1 = 18, +12 extra = 30


def call_openai_35(prompt: str, temperature: float, api_key: str) -> str:
    import urllib.request
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 400,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.loads(r.read())
    return resp["choices"][0]["message"]["content"].strip()


def main():
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        # Try loading from .env.real_model
        env_path = ROOT / ".env.real_model"
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                if line.startswith("OPENAI_API_KEY="):
                    api_key = line.split("=", 1)[1].strip()
                    break
    if not api_key:
        print("ERROR: No OPENAI_API_KEY found", file=sys.stderr)
        sys.exit(1)

    out_path = ROOT / "results" / "real_experiments" / "batch_v9_gpt35.jsonl"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing to avoid duplicates if re-run
    existing = 0
    if out_path.exists():
        existing = sum(1 for line in out_path.read_text().splitlines() if line.strip())
        print(f"Resuming: {existing} already collected")

    results = []
    persona_keys = list(PERSONAS.keys())

    for condition, prompts_list in CONDITION_PROMPTS.items():
        for scen_idx, scenario_prompt in enumerate(prompts_list):
            scenario_id = f"{condition}_v9_s{scen_idx}"
            for persona_name in persona_keys:
                persona_instr = PERSONAS[persona_name]
                for temp in TEMPERATURES:
                    full_prompt = (
                        f"{persona_instr}\n\n{scenario_prompt}" if persona_instr else scenario_prompt
                    )
                    results.append({
                        "condition": condition,
                        "scenario_id": scenario_id,
                        "persona": persona_name,
                        "temperature": temp,
                        "full_prompt": full_prompt,
                        "scenario_prompt": scenario_prompt,
                    })

    print(f"Plan: {len(results)} samples total")
    print(f"  dep: {sum(1 for r in results if r['condition']=='deprivation')}")
    print(f"  cf: {sum(1 for r in results if r['condition']=='counterfactual')}")
    print(f"  neutral: {sum(1 for r in results if r['condition']=='neutral')}")

    collected = 0
    skipped = 0
    errors = 0

    with open(out_path, "a", encoding="utf-8") as f_out:
        for i, item in enumerate(results):
            if i < existing:
                skipped += 1
                continue

            try:
                output = call_openai_35(item["full_prompt"], item["temperature"], api_key)
                record = {
                    "batch": "v9_gpt35",
                    "model": MODEL,
                    "condition": item["condition"],
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
                    print(f"  [{collected}/{len(results)-existing}] {item['condition']} {item['scenario_id']}")
                time.sleep(0.3)  # rate limit courtesy

            except Exception as e:
                print(f"  ERROR on item {i}: {e}", file=sys.stderr)
                errors += 1
                time.sleep(2)

    print(f"\nDone. Collected: {collected}, Errors: {errors}")
    print(f"Output: {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
