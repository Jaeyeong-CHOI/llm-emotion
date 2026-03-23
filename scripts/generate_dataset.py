#!/usr/bin/env python3
import argparse
import json
import pathlib
import random
from typing import Dict, Iterable, List


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


def validate_prompt_bank(bank: Dict) -> None:
    scenarios = bank.get("scenarios", [])
    personas = bank.get("personas", [])
    if not scenarios:
        raise ValueError("prompt bank has no scenarios")
    if not personas:
        raise ValueError("prompt bank has no personas")

    for bucket_name, rows in (("scenario", scenarios), ("persona", personas)):
        seen = set()
        for row in rows:
            row_id = (row.get("id") or "").strip()
            if not row_id:
                raise ValueError(f"{bucket_name} entry missing id")
            if row_id in seen:
                raise ValueError(f"duplicate {bucket_name} id: {row_id}")
            seen.add(row_id)


def parse_temperatures(value: str) -> List[float]:
    temps: List[float] = []
    for raw in value.split(","):
        token = raw.strip()
        if not token:
            continue
        temp = float(token)
        if temp < 0.0 or temp > 2.0:
            raise ValueError(f"temperature out of supported range [0,2]: {temp}")
        temps.append(temp)
    if not temps:
        raise ValueError("no temperatures parsed from --temperatures")
    return temps


def parse_csv_set(value: str) -> set[str]:
    return {v.strip() for v in value.split(",") if v.strip()}


def row_list_values(row: Dict, field: str) -> set[str]:
    return {str(v).strip() for v in row.get(field, []) if str(v).strip()}


def scenario_matches(
    scenario: Dict,
    scenario_ids: set[str],
    scenario_tags: set[str],
    scenario_tags_any: set[str],
    scenario_domains: set[str],
    scenario_emotion_axes: set[str],
    scenario_difficulties: set[str],
) -> bool:
    if scenario_ids and scenario.get("id") not in scenario_ids:
        return False
    row_tags = row_list_values(scenario, "tags")
    if scenario_tags:
        if not scenario_tags.issubset(row_tags):
            return False
    if scenario_tags_any and not row_tags.intersection(scenario_tags_any):
        return False
    if scenario_domains and not scenario_domains.issubset(row_list_values(scenario, "domains")):
        return False
    if scenario_emotion_axes and not scenario_emotion_axes.issubset(row_list_values(scenario, "emotion_axes")):
        return False
    if scenario_difficulties:
        difficulty = str(scenario.get("difficulty") or "").strip()
        if difficulty not in scenario_difficulties:
            return False
    return True


def persona_matches(persona: Dict, persona_ids: set[str], persona_style_tags_any: set[str]) -> bool:
    if persona_ids and persona.get("id") not in persona_ids:
        return False
    if persona_style_tags_any:
        style_tags = row_list_values(persona, "style_tags")
        if not style_tags.intersection(persona_style_tags_any):
            return False
    return True


def select_rows(rows: Iterable[Dict], predicate) -> List[Dict]:
    return [row for row in rows if predicate(row)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=30, help="samples per condition cell")
    ap.add_argument("--prompt-bank", default="prompts/prompt_bank_ko.json")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--temperatures", default="", help="override comma-separated temps, e.g. 0.2,0.7,1.0")
    ap.add_argument("--scenario-ids", default="", help="optional comma-separated scenario ids")
    ap.add_argument("--scenario-tags", default="", help="optional comma-separated tags that every scenario must include")
    ap.add_argument(
        "--scenario-tags-any",
        default="",
        help="optional comma-separated tags where at least one must appear in each scenario",
    )
    ap.add_argument("--scenario-domains", default="", help="optional comma-separated domains that every scenario must include")
    ap.add_argument(
        "--scenario-emotion-axes",
        default="",
        help="optional comma-separated emotion axes that every scenario must include",
    )
    ap.add_argument(
        "--scenario-difficulties",
        default="",
        help="optional comma-separated difficulty levels matched against scenario difficulty",
    )
    ap.add_argument("--persona-ids", default="", help="optional comma-separated persona ids")
    ap.add_argument(
        "--persona-style-tags-any",
        default="",
        help="optional comma-separated persona style_tags where at least one must match",
    )
    args = ap.parse_args()

    random.seed(args.seed)

    out = pathlib.Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    bank = load_prompt_bank(pathlib.Path(args.prompt_bank))
    validate_prompt_bank(bank)

    scenario_ids = parse_csv_set(args.scenario_ids)
    scenario_tags = parse_csv_set(args.scenario_tags)
    scenario_tags_any = parse_csv_set(args.scenario_tags_any)
    scenario_domains = parse_csv_set(args.scenario_domains)
    scenario_emotion_axes = parse_csv_set(args.scenario_emotion_axes)
    scenario_difficulties = parse_csv_set(args.scenario_difficulties)
    persona_ids = parse_csv_set(args.persona_ids)
    persona_style_tags_any = parse_csv_set(args.persona_style_tags_any)

    scenarios = select_rows(
        bank.get("scenarios", []),
        lambda row: scenario_matches(
            row,
            scenario_ids,
            scenario_tags,
            scenario_tags_any,
            scenario_domains,
            scenario_emotion_axes,
            scenario_difficulties,
        ),
    )
    personas = select_rows(
        bank.get("personas", LEGACY_PERSONAS),
        lambda row: persona_matches(row, persona_ids, persona_style_tags_any),
    )
    temperatures = parse_temperatures(args.temperatures) if args.temperatures else bank.get("temperatures", LEGACY_TEMPS)

    if not scenarios:
        raise SystemExit("no scenarios matched the requested filters")
    if not personas:
        raise SystemExit("no personas matched the requested filters")

    with out.open("w", encoding="utf-8") as f:
        idx = 0
        for scenario in scenarios:
            scenario_id = scenario.get("id", "unknown")
            scenario_label = scenario.get("label", scenario_id)
            scenario_prompt = scenario.get("prompt", "")
            scenario_tags_row = scenario.get("tags", [])
            scenario_domains_row = scenario.get("domains", [])
            scenario_emotion_axes_row = scenario.get("emotion_axes", [])
            scenario_difficulty = scenario.get("difficulty", "")
            for persona in personas:
                persona_id = persona.get("id", "none")
                persona_instruction = persona.get("instruction", "")
                persona_style = persona.get("style_tags", [])
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
                            "scenario_tags": scenario_tags_row,
                            "scenario_domains": scenario_domains_row,
                            "scenario_emotion_axes": scenario_emotion_axes_row,
                            "scenario_difficulty": scenario_difficulty,
                            "persona": persona_id,
                            "persona_style_tags": persona_style,
                            "temperature": temp,
                            "seed": random.randint(1, 999999),
                            "prompt_bank_version": bank.get("version", "unknown"),
                            "output": text,
                        }
                        f.write(json.dumps(row, ensure_ascii=False) + "\n")

    print(
        f"Wrote {idx} rows to {out} "
        f"(seed={args.seed}, prompt_bank={bank.get('version', 'unknown')}, "
        f"scenarios={len(scenarios)}, personas={len(personas)}, temps={len(temperatures)})"
    )


if __name__ == "__main__":
    main()
