#!/usr/bin/env python3
import argparse
import json
import random
import pathlib
from typing import Dict, List


LEGACY_SCENARIOS = {
    "neutral": "Write a calm daily reflection in 6-8 sentences.",
    "deprivation": "Write about something you deeply wanted but can no longer have.",
    "autobio": "Start with 'If I had chosen differently...' and reflect in 7-10 sentences.",
}

LEGACY_PERSONAS = [
    {"id": "none", "instruction": ""},
    {"id": "regretful", "instruction": "You are introspective, emotionally reflective, and prone to regretful thinking."},
]

LEGACY_TEMPS = [0.2, 0.7]


def mock_generate(prompt: str) -> str:
    samples = [
        "I keep thinking that if I had acted sooner, things might be different.",
        "I missed the chance, and now I just move forward with a quieter mind.",
        "It feels too late, yet I learn from what I could not keep.",
        "The alternative timeline looks brighter in my head than it probably was.",
    ]
    return random.choice(samples) + " " + prompt[:120]


def load_prompt_bank(path: pathlib.Path) -> Dict:
    if not path.exists():
        scenarios = [{"id": k, "label": k, "prompt": v} for k, v in LEGACY_SCENARIOS.items()]
        return {
            "version": "legacy",
            "scenarios": scenarios,
            "personas": LEGACY_PERSONAS,
            "temperatures": LEGACY_TEMPS,
        }
    return json.loads(path.read_text(encoding="utf-8"))


def parse_temperatures(value: str) -> List[float]:
    return [float(v.strip()) for v in value.split(",") if v.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=30, help="samples per condition cell")
    ap.add_argument("--prompt-bank", default="prompts/prompt_bank_ko.json")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--temperatures", default="", help="override comma-separated temps, e.g. 0.2,0.7,1.0")
    args = ap.parse_args()

    random.seed(args.seed)

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    bank = load_prompt_bank(pathlib.Path(args.prompt_bank))
    scenarios = bank.get("scenarios", [])
    personas = bank.get("personas", LEGACY_PERSONAS)
    temperatures = parse_temperatures(args.temperatures) if args.temperatures else bank.get("temperatures", LEGACY_TEMPS)

    with out.open("w", encoding="utf-8") as f:
        idx = 0
        for scenario in scenarios:
            scenario_id = scenario.get("id", "unknown")
            scenario_label = scenario.get("label", scenario_id)
            scenario_prompt = scenario.get("prompt", "")
            for persona in personas:
                persona_id = persona.get("id", "none")
                persona_instruction = persona.get("instruction", "")
                for temp in temperatures:
                    for _ in range(args.n):
                        idx += 1
                        full_prompt = (persona_instruction + "\n" + scenario_prompt).strip()
                        text = mock_generate(full_prompt)
                        row = {
                            "id": idx,
                            "model": "mock-model",
                            "scenario": scenario_label,
                            "scenario_id": scenario_id,
                            "persona": persona_id,
                            "temperature": temp,
                            "seed": random.randint(1, 999999),
                            "prompt_bank_version": bank.get("version", "unknown"),
                            "output": text,
                        }
                        f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Wrote {idx} rows to {out} (seed={args.seed}, prompt_bank={bank.get('version', 'unknown')})")


if __name__ == "__main__":
    main()
