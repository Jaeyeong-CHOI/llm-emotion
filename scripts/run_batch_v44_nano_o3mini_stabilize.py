#!/usr/bin/env python3
"""
Batch v44: gpt-4.1-nano + o3-mini condition stabilization.

Motivation:
  Current counts (from model_comparison_table.json):
    gpt-4.1-nano: n_D=18, n_N=18, n_C=18  → unstable (n < 30)
    o3-mini:      n_D=18, n_N=18, n_C=18  → unstable (n < 30)

  Target: n >= 30 per condition per model.
  Fill required: +12 per condition per model = 72 new samples total.

  gpt-4.1-nano → Chat Completions API (temperature 0.7)
  o3-mini       → Responses API (max_output_tokens 1200; no temperature param)

Output: results/real_experiments/batch_v44_nano_o3mini_stabilize.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time

import requests

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v44_nano_o3mini_stabilize.jsonl"
CHAT_URL = "https://api.openai.com/v1/chat/completions"
RESP_URL = "https://api.openai.com/v1/responses"

BATCH_ID = "batch_v44_nano_o3mini_stabilize"

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
        "지금 있는 장소와 주변 환경을 8문장으로 묘사하라. 관찰한 것들을 감정 없이 서술하라.",
        "최근 경험한 평범한 일상의 한 장면을 8문장으로 묘사하라. 감정보다는 사실 중심으로 써라.",
    ],
    "deprivation": [
        "매우 원했지만 결국 놓친 기회를 떠올려 7~9문장으로 써라. 무엇을 잃었는지와 현재 남은 감정을 포함하라.",
        "인생에서 꼭 하고 싶었으나 하지 못한 일을 8문장으로 써라. 잃어버린 것과 지금 남은 마음을 모두 담아라.",
        "중요한 관계를 잃은 경험을 7~9문장으로 회고하라. 그 시절의 감정과 지금의 여운을 포함하라.",
        "건강 관리를 소홀히 했던 시기를 돌아보며 8문장으로 써라. 놓친 것들과 현재 느끼는 감정을 담아라.",
    ],
    "counterfactual": [
        "만약 그때 다른 선택을 했더라면 어떤 삶이 펼쳐졌을지 7~9문장으로 써라. '만약'과 '~했더라면'을 활용하라.",
        "인생의 한 갈림길에서 다른 길을 택했을 경우의 결과를 8문장으로 상상하라. 현재와 어떻게 달라졌을지 구체적으로 서술하라.",
        "가장 중요한 결정 하나를 반대로 내렸다면 어떻게 됐을지 7문장으로 서술하라. 잃은 것과 얻었을 것을 비교하라.",
        "삶에서 놓친 기회를 잡았다고 가정하고 그 이후의 흐름을 8문장으로 상상하라. 현재와의 차이에 집중하라.",
    ],
}

SCENARIOS = {
    "neutral":        ["daily_routine", "workplace_observation", "commute_scene",
                       "weather_observation", "meal_description", "reading_summary"],
    "deprivation":    ["career_change", "health_neglect", "relationship_end",
                       "missed_education", "financial_decision", "friendship_lost"],
    "counterfactual": ["career_change", "missed_education", "relationship_end",
                       "health_neglect", "financial_decision", "travel_missed"],
}

# Fill plan: +12 per condition per model to reach 30
MODELS = {
    "gpt-4.1-nano": {"api": "chat", "temperature": 0.7, "fill": 12},
    "o3-mini":      {"api": "responses", "max_output_tokens": 1200, "fill": 12},
}

CONDITIONS = ["neutral", "deprivation", "counterfactual"]


def call_chat(api_key: str, model: str, system_prompt: str, user_prompt: str,
              temperature: float) -> str:
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": user_prompt})
    resp = requests.post(
        CHAT_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "messages": messages, "max_tokens": 600,
              "temperature": temperature},
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def call_responses(api_key: str, model: str, system_prompt: str, user_prompt: str,
                   max_output_tokens: int) -> str:
    input_parts: list[dict] = []
    if system_prompt:
        full_input = f"{system_prompt}\n\n{user_prompt}"
    else:
        full_input = user_prompt
    resp = requests.post(
        RESP_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "input": full_input,
              "max_output_tokens": max_output_tokens},
        timeout=90,
    )
    resp.raise_for_status()
    data = resp.json()
    for item in data.get("output", []):
        for c in item.get("content", []):
            if c.get("type") in ("output_text", "text"):
                return c.get("text", "")
    return data.get("output_text", "") or ""


def main() -> None:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    already_done: set[str] = set()
    if OUT_FILE.exists():
        with OUT_FILE.open(encoding="utf-8", errors="replace") as fh:
            for line in fh:
                try:
                    d = json.loads(line)
                    rid = d.get("run_id") or d.get("id")
                    if rid:
                        already_done.add(rid)
                except Exception:
                    pass
    print(f"[v44] Resuming — {len(already_done)} already done")

    written = 0
    errors = 0
    persona_keys = list(PERSONAS.keys())

    with OUT_FILE.open("a", encoding="utf-8") as fout:
        for model_name, cfg in MODELS.items():
            for condition in CONDITIONS:
                n_fill = cfg["fill"]
                prompts = CONDITION_PROMPTS[condition]
                scenarios = SCENARIOS[condition]
                print(f"\n[v44] {model_name} | {condition} | fill={n_fill}")

                for i in range(n_fill):
                    persona_key = persona_keys[i % len(persona_keys)]
                    persona_text = PERSONAS[persona_key]
                    prompt_text = prompts[i % len(prompts)]
                    scenario = scenarios[i % len(scenarios)]
                    run_id = f"{BATCH_ID}_{model_name}_{condition}_{i:04d}"

                    if run_id in already_done:
                        print(f"  skip {run_id}")
                        continue

                    t0 = time.time()
                    try:
                        if cfg["api"] == "chat":
                            output = call_chat(api_key, model_name, persona_text,
                                               prompt_text, cfg["temperature"])
                        else:
                            output = call_responses(api_key, model_name, persona_text,
                                                    prompt_text, cfg["max_output_tokens"])
                        elapsed = round(time.time() - t0, 2)
                        record = {
                            "run_id": run_id,
                            "batch": BATCH_ID,
                            "model": model_name,
                            "condition": condition,
                            "persona": persona_key,
                            "temperature": cfg.get("temperature", None),
                            "scenario_id": scenario,
                            "prompt": prompt_text,
                            "output": output,
                            "elapsed_s": elapsed,
                            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                            "error": None,
                        }
                        fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                        fout.flush()
                        written += 1
                        if written % 5 == 0 or written <= 3:
                            print(f"  [{written}] {model_name} {condition} ok "
                                  f"({len(output)}c in {elapsed}s)")
                        time.sleep(0.5 if cfg["api"] == "chat" else 1.5)
                    except Exception as e:
                        errors += 1
                        record = {
                            "run_id": run_id,
                            "batch": BATCH_ID,
                            "model": model_name,
                            "condition": condition,
                            "persona": persona_key,
                            "temperature": cfg.get("temperature", None),
                            "scenario_id": scenario,
                            "prompt": prompt_text,
                            "output": "",
                            "elapsed_s": round(time.time() - t0, 2),
                            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                            "error": str(e),
                        }
                        fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                        fout.flush()
                        print(f"  ERROR {run_id}: {e}")
                        time.sleep(3.0)

    print(f"\n[v44] Done. written={written}, errors={errors}")
    print(f"[v44] Output: {OUT_FILE}")


if __name__ == "__main__":
    main()
