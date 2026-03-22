#!/usr/bin/env python3
import argparse
import json
from pathlib import Path


def classify_pillar(group_name: str) -> str:
    if "tom" in group_name:
        return "LLM ToM"
    if "counterfactual" in group_name or "regret" in group_name:
        return "Psychology"
    if "anthrop" in group_name or "emotion" in group_name:
        return "Anthropomorphism/Emotion"
    return "Other"


def row_to_md(i: int, r: dict) -> str:
    title = (r.get("title") or "").replace("|", "\\|")
    year = r.get("year") or ""
    venue = (r.get("venue") or "").replace("|", "\\|")
    doi = r.get("doi") or ""
    url = r.get("url") or ""
    link = doi if doi else url
    pillar = classify_pillar(r.get("group", ""))
    method = r.get("type") or ""
    return f"| {i} | {title} | {year} | {venue} | {pillar} | {method} | {link} |"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rows = []
    with open(args.inp, "r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))

    header = [
        "# Evidence Table (Auto-generated)",
        "",
        "| # | Title | Year | Venue | Pillar | Type | DOI/URL |",
        "|---:|---|---:|---|---|---|---|",
    ]
    body = [row_to_md(i + 1, r) for i, r in enumerate(rows)]
    text = "\n".join(header + body) + "\n"

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"Wrote {len(rows)} rows -> {out}")


if __name__ == "__main__":
    main()
