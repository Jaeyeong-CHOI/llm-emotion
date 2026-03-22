#!/usr/bin/env python3
import argparse
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List


DEFAULT_SCREENING_RULES = {
    "include_any": [
        "large language model",
        "llm",
        "counterfactual",
        "regret",
        "emotion",
        "anthropomorphism",
        "theory of mind",
        "mental state",
    ],
    "high_priority": [
        "regret",
        "counterfactual",
        "theory of mind",
        "anthropomorphism",
    ],
    "exclude_if_any": [
        "vision transformer",
        "speech recognition",
        "graph neural network",
        "protein",
        "medical imaging",
    ],
    "threshold_include": 2,
}


def fetch_openalex(query: str, per_page: int = 25):
    base = "https://api.openalex.org/works"
    params = {
        "search": query,
        "per-page": per_page,
        "select": "id,display_name,publication_year,doi,primary_location,authorships,concepts,type,abstract_inverted_index,cited_by_count,language",
    }
    url = f"{base}?{urllib.parse.urlencode(params)}"
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def reconstruct_abstract(inv_idx: Dict) -> str:
    if not inv_idx:
        return ""
    max_pos = -1
    for positions in inv_idx.values():
        if positions:
            max_pos = max(max_pos, max(positions))
    if max_pos < 0:
        return ""

    words = [""] * (max_pos + 1)
    for token, positions in inv_idx.items():
        for pos in positions:
            if 0 <= pos < len(words):
                words[pos] = token

    return " ".join(words).strip()


def _contains_phrase(text: str, phrase: str) -> bool:
    phrase_re = r"\b" + re.escape(phrase.lower()) + r"\b"
    return re.search(phrase_re, text) is not None


def score_screening(title: str, abstract: str, rules: Dict) -> Dict:
    text = f"{title or ''}\n{abstract or ''}".lower()
    include_hits: List[str] = [k for k in rules["include_any"] if _contains_phrase(text, k)]
    high_priority_hits: List[str] = [k for k in rules["high_priority"] if _contains_phrase(text, k)]
    exclude_hits: List[str] = [k for k in rules["exclude_if_any"] if _contains_phrase(text, k)]

    score = len(include_hits) + len(high_priority_hits)
    label = "include" if score >= int(rules["threshold_include"]) and not exclude_hits else "exclude"
    if score >= int(rules["threshold_include"]) and exclude_hits:
        label = "review"

    reasons = []
    if include_hits:
        reasons.append(f"include_hits={', '.join(include_hits[:6])}")
    if high_priority_hits:
        reasons.append(f"high_priority={', '.join(high_priority_hits[:6])}")
    if exclude_hits:
        reasons.append(f"exclude_hits={', '.join(exclude_hits[:6])}")

    return {
        "screening_score": score,
        "screening_label": label,
        "screening_reasons": reasons,
        "matched_terms": sorted(set(include_hits + high_priority_hits)),
    }


def normalize_row(item, group, query, rules):
    title = item.get("display_name")
    year = item.get("publication_year")
    doi = item.get("doi")
    location = item.get("primary_location") or {}
    landing = location.get("landing_page_url")
    source = (location.get("source") or {}).get("display_name")
    abstract = reconstruct_abstract(item.get("abstract_inverted_index"))

    authors = []
    for a in item.get("authorships", [])[:5]:
        name = (a.get("author") or {}).get("display_name")
        if name:
            authors.append(name)

    screening = score_screening(title or "", abstract, rules)

    return {
        "group": group,
        "query": query,
        "title": title,
        "year": year,
        "doi": doi,
        "url": landing,
        "venue": source,
        "authors": authors,
        "type": item.get("type"),
        "openalex_id": item.get("id"),
        "language": item.get("language"),
        "cited_by_count": item.get("cited_by_count", 0),
        "abstract": abstract,
        **screening,
    }


def dedup_key(row):
    if row.get("doi"):
        return ("doi", row["doi"].lower())
    return ("title", (row.get("title") or "").strip().lower())


def merge_rows(existing: Dict, new_row: Dict) -> Dict:
    better = existing
    if (new_row.get("screening_score") or 0) > (existing.get("screening_score") or 0):
        better = new_row
    elif (new_row.get("cited_by_count") or 0) > (existing.get("cited_by_count") or 0):
        better = new_row

    merged = dict(better)
    merged["query"] = sorted(set([existing.get("query", ""), new_row.get("query", "")]))
    return merged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--screening-rules", default="queries/screening_rules.json")
    args = ap.parse_args()

    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    per_query = int(cfg.get("per_query", 25))

    rules_path = Path(args.screening_rules)
    rules = DEFAULT_SCREENING_RULES
    if rules_path.exists():
        loaded = json.loads(rules_path.read_text(encoding="utf-8"))
        rules = {
            **DEFAULT_SCREENING_RULES,
            **loaded,
        }

    rows = []
    for g in cfg.get("groups", []):
        gname = g.get("name", "unknown")
        for q in g.get("queries", []):
            data = fetch_openalex(q, per_page=per_query)
            for item in data.get("results", []):
                rows.append(normalize_row(item, gname, q, rules))
            time.sleep(0.5)

    deduped: Dict = {}
    for r in rows:
        k = dedup_key(r)
        if k not in deduped:
            deduped[k] = r
        else:
            deduped[k] = merge_rows(deduped[k], r)

    ordered = sorted(
        deduped.values(),
        key=lambda x: (
            0 if x.get("screening_label") == "include" else 1,
            -(x.get("screening_score") or 0),
            -(x.get("cited_by_count") or 0),
            -(x.get("year") or 0),
        ),
    )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for r in ordered:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    include_n = sum(1 for r in ordered if r.get("screening_label") == "include")
    review_n = sum(1 for r in ordered if r.get("screening_label") == "review")
    print(
        f"Fetched {len(rows)} records, deduped to {len(deduped)} (include={include_n}, review={review_n}) -> {out}"
    )


if __name__ == "__main__":
    main()
