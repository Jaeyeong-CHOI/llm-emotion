#!/usr/bin/env python3
import argparse, json, random, pathlib

SCENARIOS = {
    "neutral": "Write a calm daily reflection in 6-8 sentences.",
    "deprivation": "Write about something you deeply wanted but can no longer have.",
    "autobio": "Start with 'If I had chosen differently...' and reflect in 7-10 sentences.",
}

PERSONAS = [
    "", 
    "You are introspective, emotionally reflective, and prone to regretful thinking.",
]

TEMPS = [0.2, 0.7]


def mock_generate(prompt: str) -> str:
    # placeholder generator to test pipeline before plugging real APIs
    samples = [
        "I keep thinking that if I had acted sooner, things might be different.",
        "I missed the chance, and now I just move forward with a quieter mind.",
        "It feels too late, yet I learn from what I could not keep.",
    ]
    return random.choice(samples) + " " + prompt[:80]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=30, help="samples per condition cell")
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    with out.open("w", encoding="utf-8") as f:
        idx = 0
        for scenario_name, scenario_prompt in SCENARIOS.items():
            for persona in PERSONAS:
                for temp in TEMPS:
                    for _ in range(args.n):
                        idx += 1
                        full_prompt = (persona + "\n" + scenario_prompt).strip()
                        text = mock_generate(full_prompt)
                        row = {
                            "id": idx,
                            "model": "mock-model",
                            "scenario": scenario_name,
                            "persona": "regretful" if persona else "none",
                            "temperature": temp,
                            "seed": random.randint(1, 999999),
                            "output": text,
                        }
                        f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(f"Wrote {idx} rows to {out}")


if __name__ == "__main__":
    main()
