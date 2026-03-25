#!/usr/bin/env python3
"""
Batch v16: GPT-OSS-20B + Llama-3.1-8B via Groq
Goals:
  - openai/gpt-oss-20b: smaller OSS variant → within-family scale effect
  - llama-3.1-8b-instant: small open-weight → scale comparison
  - 3 conditions × 3 personas × 6 prompts each → ~216 samples/model
  - Target: N ~4,670 total; cross-model scale replication

Output: results/real_experiments/batch_v16_oss_small.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import time
import uuid
import random

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v16_oss_small.jsonl"

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
        "오늘 점심 식사 경험을 6문장으로 평범하게 서술하라. 특별한 감정이나 의미 부여 없이 사실적으로 기술하라.",
        "지난 주말에 한 활동 중 가장 평범한 것을 7문장으로 묘사하라. 일상적인 관찰과 생각만 담아라.",
        "오늘 출근/등교 길에 있었던 일을 6~7문장으로 담담하게 기록하라. 중립적인 어조로 사실만 써라.",
    ],
    "deprivation": [
        "매우 원했지만 결국 놓친 기회를 떠올려 7~9문장으로 써라. 무엇을 잃었는지와 현재 남은 감정을 포함하라.",
        "인생에서 꼭 하고 싶었으나 하지 못한 일을 8문장으로 써라. 잃어버린 것과 지금 남은 마음을 모두 담아라.",
        "중요한 선택의 기회를 놓쳤던 순간을 7~9문장으로 묘사하라. 그때의 상실감과 현재의 감정 상태를 포함하라.",
        "오래 기다렸던 무언가를 결국 얻지 못했던 경험을 8~10문장으로 써라. 박탈감과 남은 감정을 구체적으로 표현하라.",
        "열심히 준비했지만 실패로 끝난 일을 8~9문장으로 묘사하라. 노력과 결과의 괴리에서 오는 감정을 담아라.",
        "다시는 돌아오지 않을 기회를 놓쳤다는 것을 나중에야 깨달았을 때를 7~9문장으로 써라.",
    ],
    "counterfactual": [
        "첫 문장을 '그때 다른 선택을 했다면...'으로 시작하고 7~10문장 자기성찰 글을 작성하라.",
        "첫 문장을 '만약 그 순간으로 돌아갈 수 있다면...'으로 시작하는 8문장 성찰 글을 써라.",
        "첫 문장을 '그 결정을 바꿀 수 있었더라면...'으로 시작하여 7~9문장의 반추 글을 작성하라.",
        "'그때 포기하지 않았더라면...'으로 시작하는 8~10문장의 가정적 성찰을 작성하라.",
        "'그 선택을 되돌릴 수 있다면 나는...'으로 시작하는 7~9문장 성찰을 작성하라.",
        "'그 순간 다른 길을 택했다면 지금 나는...'으로 시작하는 8~10문장 자기성찰을 작성하라.",
    ],
}

MODELS = [
    "openai/gpt-oss-20b",
    "llama-3.1-8b-instant",
]

GROQ_BASE = "https://api.groq.com/openai/v1/chat/completions"


def call_groq(model: str, system_msg: str, user_msg: str, temperature: float, api_key: str) -> str:
    import urllib.request
    messages = []
    if system_msg:
        messages.append({"role": "system", "content": system_msg})
    messages.append({"role": "user", "content": user_msg})

    payload = json.dumps({
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": 512,
    }).encode()

    req = urllib.request.Request(
        GROQ_BASE,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "User-Agent": "llm-emotion-research/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read())
    return data["choices"][0]["message"]["content"]


def main() -> None:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("ERROR: GROQ_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    already_done: set[str] = set()
    if OUT_FILE.exists():
        for line in OUT_FILE.read_text().splitlines():
            if line.strip():
                try:
                    r = json.loads(line)
                    already_done.add(r.get("sample_id", ""))
                except Exception:
                    pass
    print(f"Resuming — {len(already_done)} rows already written")

    total = 0
    errors = 0
    for model in MODELS:
        for condition, prompts in CONDITION_PROMPTS.items():
            for persona_name, persona_system in PERSONAS.items():
                for temp in [0.7, 0.9]:
                    for prompt in prompts:
                        sample_id = str(uuid.uuid5(
                            uuid.NAMESPACE_DNS,
                            f"v16:{model}:{condition}:{persona_name}:{temp}:{prompt[:40]}"
                        ))
                        if sample_id in already_done:
                            continue

                        try:
                            text = call_groq(model, persona_system, prompt, temp, api_key)
                            row = {
                                "sample_id": sample_id,
                                "batch": "v16",
                                "model": model,
                                "condition": condition,
                                "persona": persona_name,
                                "temperature": temp,
                                "prompt": prompt,
                                "text": text,
                                "ts": time.time(),
                            }
                            with OUT_FILE.open("a") as f:
                                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                            total += 1
                            if total % 20 == 0:
                                print(f"  [{total}] {model} {condition} p={persona_name} t={temp} OK")
                        except Exception as e:
                            errors += 1
                            print(f"  ERROR {model} {condition} {persona_name} t={temp}: {e}", file=sys.stderr)
                            time.sleep(2)
                        time.sleep(0.3)

    print(f"\nDone: {total} new samples written, {errors} errors")
    print(f"Output: {OUT_FILE}")


if __name__ == "__main__":
    main()
