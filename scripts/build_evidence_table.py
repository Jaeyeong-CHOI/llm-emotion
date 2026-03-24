#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

from research_ops_common import safe_int


def classify_pillar(group_name: str) -> str:
    if isinstance(group_name, list):
        joined = " ".join(group_name).lower()
    else:
        joined = str(group_name).lower()
    if "tom" in joined:
        return "LLM ToM"
    if "counterfactual" in joined or "regret" in joined:
        return "Psychology"
    if "anthrop" in joined or "emotion" in joined:
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
    score = r.get("screening_score", "")
    decision = r.get("screening_label", "")
    priority = r.get("screening_priority", "")
    cites = r.get("cited_by_count", 0)
    return f"| {i} | {title} | {year} | {venue} | {pillar} | {method} | {score} | {decision} | {priority} | {cites} | {link} |"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    rows = []
    with open(args.inp, "r", encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))

    rows = sorted(
        rows,
        key=lambda r: (
            0 if r.get("screening_label") == "include" else 1,
            -safe_int(r.get("screening_score")),
            -safe_int(r.get("cited_by_count")),
            -safe_int(r.get("year")),
        ),
    )

    header = [
        "# Evidence Table (Auto-generated)",
        "",
        "| # | Title | Year | Venue | Pillar | Type | ScreenScore | Decision | Priority | Cites | DOI/URL |",
        "|---:|---|---:|---|---|---|---:|---|---|---:|---|",
    ]
    body = [row_to_md(i + 1, r) for i, r in enumerate(rows)]
    text = "\n".join(header + body) + "\n"

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print(f"Wrote {len(rows)} rows -> {out}")


if __name__ == "__main__":
    main()
