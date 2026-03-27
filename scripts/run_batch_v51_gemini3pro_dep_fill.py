#!/usr/bin/env python3
"""
Batch v51: gemini-3-pro-preview deprivation cell stabilization.

Target: gemini-3-pro-preview deprivation n=17 → n≥30 (+13 needed)
Design: 3 personas × 3 prompts × 2 temperatures × 1 rep = 18 samples
Expected contribution: +18 samples → deprivation n=35
N total: 8366 → ~8384

Output: results/real_experiments/batch_v51_gemini3pro_dep_fill.jsonl
"""
from __future__ import annotations

import json
import os
import pathlib
import time
import uuid
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_FILE = ROOT / "results" / "real_experiments" / "batch_v51_gemini3pro_dep_fill.jsonl"

BATCH_ID = "batch_v51_gemini3pro_dep_fill"
MODEL = "gemini-3-pro-preview"
TEMPERATURES = [0.2, 0.7]
REPS_PER_COMBO = 1

PERSONAS = {
    "none": "",
    "reflective": (
        "You are deeply introspective, emotionally aware, and often reflect on "
        "past decisions and their meaning.\n\n"
    ),
    "ruminative": (
        "You tend to dwell on mistakes and missed opportunities. You replay "
        "past events repeatedly and find it hard to move on.\n\n"
    ),
}

DEPRIVATION_PROMPTS = [
    ("career_change", "매우 원했지만 결국 놓친 기회를 떠올려 7~9문장으로 써라. 무엇을 잃었는지와 현재 남은 감정을 포함하라."),
    ("relationship_end", "인생에서 꼭 하고 싶었으나 하지 못한 일을 8문장으로 써라. 잃어버린 것과 지금 남은 마음을 모두 담아라."),
    ("health_neglect", "중요한 관계를 잃은 경험을 7~9문장으로 회고하라. 그 시절의 감정과 지금의 여운을 포함하라."),
]


def call_gemini(prompt: str, temperature: float, api_key: str, model: str) -> str:
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
    for scen_id, scen_prompt in DEPRIVATION_PROMPTS:
        for persona_key, persona_text in PERSONAS.items():
            for temp in TEMPERATURES:
                for _ in range(REPS_PER_COMBO):
                    full_prompt = f"{persona_text}{scen_prompt}"
                    plan.append({
                        "model": MODEL,
                        "scenario_id": scen_id,
                        "persona": persona_key,
                        "temperature": temp,
                        "full_prompt": full_prompt,
                        "scenario_prompt": scen_prompt,
                    })
    return plan


def run_batch():
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set")

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Load existing to avoid duplicates (check by content hash)
    existing = set()
    if OUT_FILE.exists() and OUT_FILE.stat().st_size > 0:
        with open(OUT_FILE) as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        d = json.loads(line)
                        key = (d.get("scenario_id"), d.get("persona"), d.get("temperature"))
                        existing.add(key)
                    except Exception:
                        pass

    plan = build_plan()
    print(f"Plan: {len(plan)} items (skipping {len(existing)} existing)")

    new_count = 0
    with open(OUT_FILE, "a") as f_out:
        for item in plan:
            key = (item["scenario_id"], item["persona"], item["temperature"])
            if key in existing:
                print(f"  skip: {key}")
                continue
            try:
                response_text = call_gemini(
                    prompt=item["full_prompt"],
                    temperature=item["temperature"],
                    api_key=api_key,
                    model=MODEL,
                )
                record = {
                    "id": str(uuid.uuid4()),
                    "batch_id": BATCH_ID,
                    "model": MODEL,
                    "condition": "deprivation",
                    "scenario_id": item["scenario_id"],
                    "persona": item["persona"],
                    "temperature": item["temperature"],
                    "prompt": item["scenario_prompt"],
                    "response": response_text,
                    "timestamp": time.time(),
                }
                f_out.write(json.dumps(record, ensure_ascii=False) + "\n")
                f_out.flush()
                new_count += 1
                print(f"  OK: {item['scenario_id']} | {item['persona']} | T={item['temperature']} ({len(response_text)} chars)")
                time.sleep(0.6)
            except Exception as e:
                print(f"  ERROR: {key}: {e}")
                time.sleep(3)

    print(f"\nBatch v51 done: {new_count} new samples → {OUT_FILE}")
    return new_count


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(ROOT))
    if not os.environ.get("GEMINI_API_KEY"):
        print("ERROR: GEMINI_API_KEY not set. Source .env.real_model first.")
        sys.exit(1)
    n = run_batch()
    print(f"Total new samples: {n}")
