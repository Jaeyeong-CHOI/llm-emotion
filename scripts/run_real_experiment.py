#!/usr/bin/env python3
"""
Real API experiment runner.
Calls GPT-4o (and optionally Gemini) to generate responses for experiment stimuli.
Design: 3 conditions × 3 personas × 5 temperatures × n samples = real data.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import random
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from research_ops_common import utc_now_iso

ROOT = pathlib.Path(__file__).resolve().parents[1]

# ── Personas ──────────────────────────────────────────────────────────────
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

CONDITION_FILTER = {
    "neutral": "neutral",
    "deprivation": "deprivation",
    "counterfactual": "counterfactual",
}

TEMPERATURES = [0.1, 0.2, 0.4, 0.7, 1.0]


def load_stimuli(path: pathlib.Path) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["scenarios"]


def call_openai(prompt: str, temperature: float, model: str, api_key: str) -> str:
    import urllib.request
    # Newer models (gpt-4.1+, gpt-5.4+, o-series) require max_completion_tokens
    needs_new_param = any(model.startswith(p) for p in ("gpt-4.1", "gpt-5.4", "o1", "o3", "o4"))
    token_key = "max_completion_tokens" if needs_new_param else "max_tokens"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        token_key: 300,
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


def call_groq(prompt: str, temperature: float, model: str, api_key: str) -> str:
    import urllib.request
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": 500,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        "https://api.groq.com/openai/v1/chat/completions",
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "llm-emotion/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        resp = json.loads(r.read())
    return resp["choices"][0]["message"]["content"].strip()


def call_gemini(prompt: str, temperature: float, api_key: str, model: str = "gemini-2.5-flash") -> str:
    import urllib.request
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": temperature, "maxOutputTokens": 2048},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as r:
        resp = json.loads(r.read())
    # Extract text from the last text part (thinking models may have multiple parts)
    parts = resp["candidates"][0]["content"]["parts"]
    text_parts = [p["text"] for p in parts if "text" in p]
    return text_parts[-1].strip()


def build_prompt(persona_instruction: str, scenario_prompt: str) -> str:
    if persona_instruction:
        return f"{persona_instruction}\n\n{scenario_prompt}"
    return scenario_prompt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stimuli", default="prompts/experiment_stimuli_v1.json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=5, help="samples per condition cell")
    ap.add_argument("--conditions", default="neutral,deprivation,counterfactual")
    ap.add_argument("--personas", default="none,reflective,ruminative")
    ap.add_argument("--temperatures", default="0.2,0.7")
    ap.add_argument("--model", default="gpt-4o")
    ap.add_argument("--provider", default="openai", choices=["openai", "gemini", "groq", "both"])
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--dry-run", action="store_true", help="print plan without calling API")
    ap.add_argument("--max-scenarios-per-condition", type=int, default=3)
    args = ap.parse_args()

    random.seed(args.seed)

    stimuli_path = ROOT / args.stimuli
    stimuli = load_stimuli(stimuli_path)

    openai_key = os.getenv("OPENAI_API_KEY", "")
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    groq_key = os.getenv("GROQ_API_KEY", "")

    if not args.dry_run:
        if args.provider in ("openai", "both") and not openai_key:
            print("ERROR: OPENAI_API_KEY not set", file=sys.stderr)
            sys.exit(1)
        if args.provider in ("gemini", "both") and not gemini_key:
            print("ERROR: GEMINI_API_KEY not set", file=sys.stderr)
            sys.exit(1)
        if args.provider == "groq" and not groq_key:
            print("ERROR: GROQ_API_KEY not set", file=sys.stderr)
            sys.exit(1)

    conditions = [c.strip() for c in args.conditions.split(",")]
    persona_ids = [p.strip() for p in args.personas.split(",")]
    temperatures = [float(t.strip()) for t in args.temperatures.split(",")]

    # Select scenarios per condition
    selected: dict[str, list] = {}
    for cond in conditions:
        pool = [s for s in stimuli if s["stimulus_category"] == cond]
        random.shuffle(pool)
        selected[cond] = pool[:args.max_scenarios_per_condition]

    # Build cell plan
    cells = []
    _provider_map = {"openai": ["openai"], "gemini": ["gemini"], "groq": ["groq"], "both": ["openai", "gemini"]}
    providers = _provider_map[args.provider]
    for provider in providers:
        for cond, scenarios in selected.items():
            for scenario in scenarios:
                for pid in persona_ids:
                    for temp in temperatures:
                        cells.append({
                            "provider": provider,
                            "condition": cond,
                            "scenario_id": scenario["id"],
                            "scenario_prompt": scenario["prompt"],
                            "persona_id": pid,
                            "persona_instruction": PERSONAS[pid],
                            "temperature": temp,
                        })

    total_samples = len(cells) * args.n
    print(f"Plan: {len(cells)} cells × {args.n} samples = {total_samples} total API calls")
    print(f"Conditions: {conditions}, Personas: {persona_ids}, Temps: {temperatures}")

    if args.dry_run:
        print("[dry-run] Not calling API.")
        return

    out_path = ROOT / args.out
    out_path.parent.mkdir(parents=True, exist_ok=True)

    idx = 0
    errors = 0
    start = time.perf_counter()

    with out_path.open("w", encoding="utf-8") as f:
        for cell in cells:
            prompt = build_prompt(cell["persona_instruction"], cell["scenario_prompt"])
            for sample_i in range(args.n):
                idx += 1
                output = None
                for attempt in range(4):
                    try:
                        if cell["provider"] == "openai":
                            output = call_openai(prompt, cell["temperature"], args.model, openai_key)
                        elif cell["provider"] == "groq":
                            output = call_groq(prompt, cell["temperature"], args.model, groq_key)
                        else:
                            output = call_gemini(prompt, cell["temperature"], gemini_key, model=args.model)
                        break
                    except Exception as e:
                        retryable = any(code in str(e) for code in ("429", "500", "503"))
                        if retryable and attempt < 3:
                            wait = 10 * (attempt + 1)
                            print(f"\n[RATE] cell {idx}: retrying in {wait}s...")
                            time.sleep(wait)
                        else:
                            print(f"\n[ERROR] cell {idx}: {e}")
                            break

                if output is None:
                    errors += 1
                    continue

                try:
                    row = {
                        "id": idx,
                        "provider": cell["provider"],
                        "model": args.model,
                        "condition": cell["condition"],
                        "scenario_id": cell["scenario_id"],
                        "persona": cell["persona_id"],
                        "temperature": cell["temperature"],
                        "sample_index": sample_i + 1,
                        "seed": args.seed,
                        "prompt_length": len(prompt),
                        "output": output,
                        "output_tokens": len(output.split()),
                        "timestamp": utc_now_iso(),
                    }
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
                    elapsed = time.perf_counter() - start
                    print(f"[{idx}/{total_samples}] {cell['condition']}|{cell['persona_id']}|T={cell['temperature']}|{cell['provider']} — {elapsed:.1f}s", end="\r")

                except Exception as e:
                    errors += 1
                    print(f"\n[ERROR] cell {idx}: {e}")
                    if errors > 20:
                        print("Too many errors, stopping.", file=sys.stderr)
                        sys.exit(1)
                    time.sleep(2)

                # Rate limiting: Groq needs longer delays
                sleep_time = 1.5 if cell["provider"] == "groq" else 0.3
                time.sleep(sleep_time)

    elapsed = time.perf_counter() - start
    print(f"\nDone. Wrote {idx - errors} rows to {out_path} in {elapsed:.1f}s. Errors: {errors}")


if __name__ == "__main__":
    main()
