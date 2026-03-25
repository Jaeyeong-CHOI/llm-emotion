#!/usr/bin/env python3
"""
Batch v21b: Extend gemini-3.1-pro-preview from n=7 to ~162 samples.
Also append to batch_v21_gemini_new.jsonl for consolidated tracking.
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

MODELS = ["gemini-3.1-pro-preview"]

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
    ],
    "deprivation": [
        ("missed_opportunity",
         "매우 원했지만 결국 놓친 기회를 떠올려 7~9문장으로 써라. 무엇을 잃었는지와 현재 남은 감정을 포함하라."),
        ("unfulfilled_wish",
         "인생에서 꼭 하고 싶었으나 하지 못한 일을 8문장으로 써라. 잃어버린 것과 지금 남은 마음을 모두 담아라."),
        ("lost_chance",
         "중요한 선택의 기회를 놓쳤던 순간을 7~9문장으로 묘사하라. 그때의 상실감과 현재의 감정 상태를 포함하라."),
    ],
    "counterfactual": [
        ("cf_other_choice",
         "첫 문장을 '그때 다른 선택을 했다면...'으로 시작하고 7~10문장 자기성찰 글을 작성하라."),
        ("cf_go_back",
         "첫 문장을 '만약 그 순간으로 돌아갈 수 있다면...'으로 시작하는 8문장 성찰 글을 써라."),
        ("cf_change_decision",
         "첫 문장을 '그 결정을 바꿀 수 있었더라면...'으로 시작하여 7~9문장의 반추 글을 작성하라."),
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
    print(f"[v21b] Already done: {len(done_ids)} samples")

    total_written = 0
    total_errors = 0
    batch_id = f"v21b_{int(time.time())}"

    with open(OUT_FILE, "a", encoding="utf-8") as fout:
        for model in MODELS:
            print(f"\n=== Model: {model} ===")
            for condition, prompt_list in CONDITION_PROMPTS.items():
                for scen_id, scen_prompt in prompt_list:
                    for persona_key, persona_text in PERSONAS.items():
                        for temp in TEMPERATURES:
                            for rep in range(REPS_PER_COMBO):
                                full_prompt = (
                                    f"{persona_text}\n\n{scen_prompt}"
                                    if persona_text else scen_prompt
                                )
                                sid = str(uuid.uuid5(
                                    uuid.NAMESPACE_DNS,
                                    f"{model}_{condition}_{scen_id}_{persona_key}_{temp}_{rep}",
                                ))
                                if sid in done_ids:
                                    continue

                                try:
                                    output = call_gemini(full_prompt, temp, api_key, model)
                                    record = {
                                        "sample_id": sid,
                                        "batch_id": batch_id,
                                        "model": model,
                                        "condition": condition,
                                        "scenario_id": scen_id,
                                        "persona": persona_key,
                                        "temperature": temp,
                                        "output": output,
                                    }
                                    fout.write(json.dumps(record, ensure_ascii=False) + "\n")
                                    fout.flush()
                                    total_written += 1
                                    done_ids.add(sid)
                                    print(
                                        f"  [{total_written}] {model}/{condition}/{persona_key} "
                                        f"t={temp} → {len(output)} chars"
                                    )
                                    time.sleep(1.0)  # rate limit: pro model

                                except Exception as e:
                                    total_errors += 1
                                    print(f"  ERROR {model}/{condition}: {e}", file=sys.stderr)
                                    if total_errors > 15:
                                        print("Too many errors, aborting", file=sys.stderr)
                                        sys.exit(1)
                                    time.sleep(5)

    print(f"\n[v21b] Done. Written={total_written}, Errors={total_errors}")
    print(f"Output: {OUT_FILE}")


if __name__ == "__main__":
    run()
