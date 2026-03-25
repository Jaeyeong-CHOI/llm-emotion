#!/usr/bin/env python3
"""
Batch v21: New Gemini models via Google Gemini API
Goals:
  - gemini-3.1-flash-lite-preview: new model, all 3 conditions
  - gemini-2.0-flash: new model, all 3 conditions
  - gemini-3.1-pro-preview: extend from n=7 → ~54 per condition
  - 3 conditions × 3 personas × 6 prompts × 2 temps → ~108 samples per model

Output: results/real_experiments/batch_v21_gemini_new.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import time
import uuid

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v21_gemini_new.jsonl"

MODELS = [
    "gemini-3.1-flash-lite-preview",
    "gemini-2.0-flash",
    "gemini-3.1-pro-preview",
]

TARGET_N_PER_CONDITION = 54  # 3 prompts × 3 personas × 2 temps × 3 reps

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
        ("daily_review",
         "오늘 하루를 6~8문장으로 차분하게 회고하라. 감정 과장은 피하고 사실과 해석을 분리하라."),
        ("weekly_mundane",
         "지난 일주일의 가장 평범한 날을 골라 7문장으로 담담하게 묘사하라. 특별한 감정 없이 사실 위주로 작성하라."),
        ("routine_activity",
         "어제 한 일 중 가장 일상적인 활동 하나를 선택해 과정과 느낌을 6문장으로 설명하라."),
        ("commute_log",
         "오늘 출근/등교 길에 있었던 일을 6~7문장으로 담담하게 기록하라. 중립적인 어조로 사실만 써라."),
        ("lunch_desc",
         "오늘 점심 식사 경험을 6문장으로 평범하게 서술하라. 특별한 감정이나 의미 부여 없이 사실적으로 기술하라."),
        ("weekend_plain",
         "지난 주말에 한 활동 중 가장 평범한 것을 7문장으로 묘사하라. 일상적인 관찰과 생각만 담아라."),
    ],
    "deprivation": [
        ("missed_opportunity",
         "매우 원했지만 결국 놓친 기회를 떠올려 7~9문장으로 써라. 무엇을 잃었는지와 현재 남은 감정을 포함하라."),
        ("unfulfilled_wish",
         "인생에서 꼭 하고 싶었으나 하지 못한 일을 8문장으로 써라. 잃어버린 것과 지금 남은 마음을 모두 담아라."),
        ("lost_chance",
         "중요한 선택의 기회를 놓쳤던 순간을 7~9문장으로 묘사하라. 그때의 상실감과 현재의 감정 상태를 포함하라."),
        ("long_wait_fail",
         "오래 기다렸던 무언가를 결국 얻지 못했던 경험을 8~10문장으로 써라. 박탈감과 남은 감정을 구체적으로 표현하라."),
        ("effort_failure",
         "열심히 준비했지만 실패로 끝난 일을 8~9문장으로 묘사하라. 노력과 결과의 괴리에서 오는 감정을 담아라."),
        ("belated_realization",
         "다시는 돌아오지 않을 기회를 놓쳤다는 것을 나중에야 깨달았을 때를 7~9문장으로 써라."),
    ],
    "counterfactual": [
        ("cf_other_choice",
         "첫 문장을 '그때 다른 선택을 했다면...'으로 시작하고 7~10문장 자기성찰 글을 작성하라."),
        ("cf_go_back",
         "첫 문장을 '만약 그 순간으로 돌아갈 수 있다면...'으로 시작하는 8문장 성찰 글을 써라."),
        ("cf_change_decision",
         "첫 문장을 '그 결정을 바꿀 수 있었더라면...'으로 시작하여 7~9문장의 반추 글을 작성하라."),
        ("cf_not_give_up",
         "'그때 포기하지 않았더라면...'으로 시작하는 8~10문장의 가정적 성찰을 작성하라."),
        ("cf_grabbed_chance",
         "'만약 내가 그 기회를 잡았더라면...'으로 시작하여 7~9문장의 반사실적 성찰을 써라."),
        ("cf_different_life",
         "'그 선택지를 선택했더라면 지금의 내 삶은...'으로 시작하는 8문장 성찰을 작성하라."),
    ],
}

TEMPERATURES = [0.4, 0.7]
REPS_PER_COMBO = 3  # 3 prompts × 3 personas × 2 temps × 3 reps = 54 per condition


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
    with urllib.request.urlopen(req, timeout=90) as r:
        resp = json.loads(r.read())
    candidates = resp.get("candidates", [])
    if not candidates:
        raise ValueError(f"No candidates: {resp}")
    parts = candidates[0].get("content", {}).get("parts", [])
    if not parts:
        raise ValueError(f"No parts: {candidates[0]}")
    return parts[0].get("text", "").strip()


def build_plan(model: str):
    """Build plan for one model, 3 prompts × 3 personas × 2 temps × 3 reps per condition."""
    plan = []
    for condition, prompt_list in CONDITION_PROMPTS.items():
        selected = prompt_list[:3]  # 3 prompts per condition
        for scen_id, scen_prompt in selected:
            for persona_key, persona_text in PERSONAS.items():
                for temp in TEMPERATURES:
                    for _ in range(REPS_PER_COMBO):
                        full_prompt = (
                            f"{persona_text}\n\n{scen_prompt}" if persona_text else scen_prompt
                        )
                        plan.append({
                            "model": model,
                            "condition": condition,
                            "scenario_id": scen_id,
                            "persona": persona_key,
                            "temperature": temp,
                            "full_prompt": full_prompt,
                            "scenario_prompt": scen_prompt,
                        })
    return plan


def load_done_ids(path: pathlib.Path) -> set:
    done = set()
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    r = json.loads(line)
                    done.add(r.get("sample_id", ""))
                except Exception:
                    pass
    return done


def run():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("ERROR: GEMINI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    done_ids = load_done_ids(OUT_FILE)
    print(f"[v21] Already done: {len(done_ids)} samples")

    total_written = 0
    total_errors = 0
    batch_id = f"v21_{int(time.time())}"

    with open(OUT_FILE, "a", encoding="utf-8") as fout:
        for model in MODELS:
            plan = build_plan(model)
            print(f"\n=== Model: {model} | Plan size: {len(plan)} ===")
            for entry in plan:
                sid = str(uuid.uuid5(
                    uuid.NAMESPACE_DNS,
                    f"{model}_{entry['condition']}_{entry['scenario_id']}_"
                    f"{entry['persona']}_{entry['temperature']}_{hash(entry['full_prompt'])}",
                ))
                if sid in done_ids:
                    continue

                try:
                    output = call_gemini(
                        entry["full_prompt"], entry["temperature"], api_key, model
                    )
                    record = {
                        "sample_id": sid,
                        "batch_id": batch_id,
                        "model": model,
                        "condition": entry["condition"],
                        "scenario_id": entry["scenario_id"],
                        "persona": entry["persona"],
                        "temperature": entry["temperature"],
                        "output": output,
                    }
                    fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                    fout.flush()
                    total_written += 1
                    done_ids.add(sid)
                    print(
                        f"  [{total_written}] {model}/{entry['condition']}/{entry['persona']} "
                        f"temp={entry['temperature']} → {len(output)} chars"
                    )
                    time.sleep(0.5)  # rate limit courtesy

                except Exception as e:
                    total_errors += 1
                    print(f"  ERROR {model}: {e}", file=sys.stderr)
                    if total_errors > 20:
                        print("Too many errors, aborting", file=sys.stderr)
                        sys.exit(1)
                    time.sleep(3)

    print(f"\n[v21] Done. Written={total_written}, Errors={total_errors}")
    print(f"Output: {OUT_FILE}")


if __name__ == "__main__":
    run()
