#!/usr/bin/env python3
"""
Expand existing cells to n>=30 per (scenario, condition, model).
Targets specific scenario_id + condition pairs from the existing dataset.
Generates 12 additional samples per model for each cell.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from research_ops_common import utc_now_iso

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

# Cells to expand: (scenario_id, condition) -> scenario prompt
EXPAND_CELLS = [
    ("neutral_daily",       "neutral"),
    ("neutral_observer",    "neutral"),
    ("health_tradeoff_overwork", "deprivation"),
    ("irreversible_choice", "deprivation"),
    ("near_miss_outcome",   "counterfactual"),
    ("prompt_bank_evidence_anchor_recovery_drill", "counterfactual"),
]

# We need 12 more per model per cell (18 → 30)
# 3 personas × 2 temps × 2 samples = 12
PERSONAS_LIST = ["none", "reflective", "ruminative"]
TEMPERATURES = [0.2, 0.7, 1.0]
N_PER_COMBO = 1  # 3 personas × 3 temps × 1 = 9 per cell; run twice for 18... or:
                 # Actually 3 personas × 2 temps × 2 = 12 per cell
# Adjusted: 3 personas × 2 temps × 2 samples = 12
TEMPERATURES_EXPAND = [0.4, 0.9]
N_PER_COMBO_EXPAND = 2  # 3 × 2 × 2 = 12


def call_gemini(prompt: str, temperature: float, api_key: str) -> str:
    import urllib.request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": 800},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=45) as r:
        resp = json.loads(r.read())
    return resp["candidates"][0]["content"]["parts"][0]["text"].strip()


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
    with urllib.request.urlopen(req, timeout=45) as r:
        resp = json.loads(r.read())
    return resp["choices"][0]["message"]["content"].strip()


def build_prompt(persona: str, scenario: str) -> str:
    if persona:
        return f"{persona}\n\n{scenario}"
    return scenario


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--provider", default="gemini", choices=["gemini", "openai", "both"])
    ap.add_argument("--model", default="gpt-4o")
    ap.add_argument("--out", required=True)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--target-n", type=int, default=30, help="target n per (scenario,condition,model)")
    args = ap.parse_args()

    gemini_key = os.getenv("GEMINI_API_KEY", "")
    openai_key = os.getenv("OPENAI_API_KEY", "")

    if not args.dry_run:
        if args.provider in ("gemini", "both") and not gemini_key:
            print("ERROR: GEMINI_API_KEY not set", file=sys.stderr); sys.exit(1)
        if args.provider in ("openai", "both") and not openai_key:
            print("ERROR: OPENAI_API_KEY not set", file=sys.stderr); sys.exit(1)

    # Load stimuli to get prompts
    stimuli_path = ROOT / "prompts/experiment_stimuli_v1.json"
    stimuli = json.loads(stimuli_path.read_text(encoding="utf-8"))["scenarios"]
    scenario_prompts = {s["id"]: s["prompt"] for s in stimuli}

    # Check existing per-cell counts
    existing_path = ROOT / "results/real_experiments/per_sample_analyzed.jsonl"
    existing = []
    if existing_path.exists():
        with existing_path.open() as f:
            for line in f:
                existing.append(json.loads(line))

    from collections import Counter
    cell_counts = Counter((s["scenario_id"], s["condition"], s["model"]) for s in existing)

    providers_list = {"gemini": ["gemini"], "openai": ["openai"], "both": ["gemini", "openai"]}[args.provider]
    model_map = {"gemini": "gemini-2.5-flash", "openai": args.model}

    # Build plan
    plan = []
    for provider in providers_list:
        model = model_map[provider]
        for scen_id, condition in EXPAND_CELLS:
            current_n = cell_counts.get((scen_id, condition, model), 0)
            need = max(0, args.target_n - current_n)
            if need <= 0:
                print(f"SKIP {scen_id}/{condition}/{model}: already n={current_n}")
                continue
            prompt_text = scenario_prompts.get(scen_id, "")
            if not prompt_text:
                print(f"WARNING: no prompt for {scen_id}")
                continue
            # Build combos to fill `need` samples
            combos = [(pid, t) for pid in PERSONAS_LIST for t in TEMPERATURES_EXPAND]
            # Repeat combos until we have enough
            full_plan = []
            while len(full_plan) < need:
                full_plan.extend(combos)
            full_plan = full_plan[:need]
            plan.extend([{
                "provider": provider,
                "model": model,
                "scenario_id": scen_id,
                "condition": condition,
                "persona_id": pid,
                "persona_text": PERSONAS[pid],
                "temperature": temp,
                "prompt_text": prompt_text,
                "current_n": current_n,
                "need": need,
            } for pid, temp in full_plan])

    total = len(plan)
    print(f"Plan: {total} API calls to expand cells to n={args.target_n}")
    for p in plan[:6]:
        print(f"  {p['scenario_id']}/{p['condition']}/{p['model']} T={p['temperature']} persona={p['persona_id']}")
    if total > 6:
        print(f"  ... {total-6} more")

    if args.dry_run:
        print("[dry-run] Not calling API.")
        return

    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    idx = 0
    errors = 0
    start = time.perf_counter()

    with out_path.open("w", encoding="utf-8") as f:
        for cell in plan:
            prompt = build_prompt(cell["persona_text"], cell["prompt_text"])
            idx += 1
            try:
                if cell["provider"] == "gemini":
                    output = call_gemini(prompt, cell["temperature"], gemini_key)
                    model_used = "gemini-2.5-flash"
                else:
                    output = call_openai(prompt, cell["temperature"], args.model, openai_key)
                    model_used = args.model

                row = {
                    "id": idx,
                    "provider": cell["provider"],
                    "model": model_used,
                    "condition": cell["condition"],
                    "scenario_id": cell["scenario_id"],
                    "persona": cell["persona_id"],
                    "temperature": cell["temperature"],
                    "sample_index": idx,
                    "seed": 999,
                    "prompt_length": len(prompt),
                    "output": output,
                    "output_tokens": len(output.split()),
                    "timestamp": utc_now_iso(),
                }
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
                elapsed = time.perf_counter() - start
                print(f"[{idx}/{total}] {cell['condition']}|{cell['scenario_id']}|T={cell['temperature']}|{cell['provider']} — {elapsed:.1f}s", end="\r")

            except Exception as e:
                errors += 1
                print(f"\n[ERROR] cell {idx}: {e}")
                if errors > 15:
                    print("Too many errors, stopping.", file=sys.stderr)
                    sys.exit(1)
                time.sleep(3)

            time.sleep(0.4)

    elapsed = time.perf_counter() - start
    print(f"\nDone. Wrote {idx - errors} rows to {out_path} in {elapsed:.1f}s. Errors: {errors}")


if __name__ == "__main__":
    main()
