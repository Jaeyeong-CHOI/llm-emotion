#!/usr/bin/env python3
import argparse
import json
import math
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, List, Sequence, Tuple


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
    "required_concepts_any": [
        ["large language model", "llm", "language model"],
        ["regret", "counterfactual", "emotion", "affect", "anthropomorphism", "mental state", "theory of mind"],
    ],
    "weights": {
        "include_any": 1.0,
        "high_priority": 2.0,
        "cited_by_log1p": 0.35,
        "query_overlap": 0.2,
        "concept_diversity": 0.15,
    },
    "penalties": {
        "exclude_hit": 2.0,
        "missing_concept_group": 1.0,
        "non_preferred_language": 1.0,
        "non_preferred_type": 1.0,
        "short_abstract": 0.4,
    },
    "preferred_languages": ["en", "ko"],
    "preferred_types": ["article", "preprint", "conference", "book-chapter"],
    "min_year": 2018,
    "min_abstract_tokens": 40,
    "threshold_include": 3.0,
    "threshold_review": 1.5,
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


def _hit_terms(text: str, terms: Sequence[str]) -> List[str]:
    return [k for k in terms if _contains_phrase(text, k)]


def _query_terms(query: str) -> List[str]:
    # lightweight lexical tokens from OpenAlex query string
    candidates = re.findall(r"[a-zA-Z][a-zA-Z\-]{2,}", query.lower())
    stop = {"and", "or", "the", "for", "with", "without", "from", "into", "about"}
    return [c for c in candidates if c not in stop]


def _token_count(text: str) -> int:
    return len(re.findall(r"\w+", text or ""))


def score_screening(title: str, abstract: str, query: str, language: str, pub_type: str, year: int, cited_by_count: int, rules: Dict) -> Dict:
    title_l = (title or "").lower()
    abstract_l = (abstract or "").lower()
    text = f"{title_l}\n{abstract_l}"

    include_hits: List[str] = _hit_terms(text, rules["include_any"])
    high_priority_hits: List[str] = _hit_terms(text, rules["high_priority"])
    exclude_hits: List[str] = _hit_terms(text, rules["exclude_if_any"])

    concept_groups = rules.get("required_concepts_any", [])
    concept_hits = []
    missing_groups = 0
    for group in concept_groups:
        g_hits = _hit_terms(text, group)
        concept_hits.append(g_hits)
        if not g_hits:
            missing_groups += 1

    weights = rules.get("weights", {})
    penalties = rules.get("penalties", {})

    lexical = len(include_hits) * float(weights.get("include_any", 1.0))
    priority = len(high_priority_hits) * float(weights.get("high_priority", 2.0))
    citation_bonus = float(weights.get("cited_by_log1p", 0.35)) * (0 if cited_by_count <= 0 else math.log1p(cited_by_count))

    query_terms = _query_terms(query)
    query_overlap_n = sum(1 for qt in set(query_terms) if _contains_phrase(text, qt))
    query_overlap_bonus = query_overlap_n * float(weights.get("query_overlap", 0.2))

    concept_diversity = sum(1 for g_hits in concept_hits if g_hits)
    concept_diversity_bonus = concept_diversity * float(weights.get("concept_diversity", 0.15))

    penalty_exclude = len(exclude_hits) * float(penalties.get("exclude_hit", 2.0))
    penalty_missing_group = missing_groups * float(penalties.get("missing_concept_group", 1.0))

    lang_penalty = 0.0
    preferred_languages = rules.get("preferred_languages", [])
    if preferred_languages and (language or "").lower() not in {l.lower() for l in preferred_languages}:
        lang_penalty = float(penalties.get("non_preferred_language", 1.0))

    type_penalty = 0.0
    preferred_types = {t.lower() for t in rules.get("preferred_types", [])}
    if preferred_types and (pub_type or "").lower() not in preferred_types:
        type_penalty = float(penalties.get("non_preferred_type", 1.0))

    year_penalty = 0.0
    min_year = int(rules.get("min_year", 0) or 0)
    if min_year and (year or 0) < min_year:
        year_penalty = 0.5

    abstract_tokens = _token_count(abstract)
    short_abstract_penalty = 0.0
    min_abstract_tokens = int(rules.get("min_abstract_tokens", 0) or 0)
    if min_abstract_tokens and abstract_tokens < min_abstract_tokens:
        short_abstract_penalty = float(penalties.get("short_abstract", 0.4))

    weighted_score = (
        lexical
        + priority
        + citation_bonus
        + query_overlap_bonus
        + concept_diversity_bonus
        - penalty_exclude
        - penalty_missing_group
        - lang_penalty
        - type_penalty
        - year_penalty
        - short_abstract_penalty
    )
    weighted_score = round(weighted_score, 4)

    include_threshold = float(rules.get("threshold_include", 3.0))
    review_threshold = float(rules.get("threshold_review", include_threshold / 2))

    if weighted_score >= include_threshold and not exclude_hits and missing_groups == 0:
        label = "include"
    elif weighted_score >= review_threshold:
        label = "review"
    else:
        label = "exclude"

    reasons = []
    if include_hits:
        reasons.append(f"include_hits={', '.join(include_hits[:6])}")
    if high_priority_hits:
        reasons.append(f"high_priority={', '.join(high_priority_hits[:6])}")
    if exclude_hits:
        reasons.append(f"exclude_hits={', '.join(exclude_hits[:6])}")
    if query_overlap_n:
        reasons.append(f"query_overlap={query_overlap_n}")
    if missing_groups:
        reasons.append(f"missing_concept_groups={missing_groups}")
    if lang_penalty:
        reasons.append(f"non_preferred_language={language or 'unknown'}")
    if type_penalty:
        reasons.append(f"non_preferred_type={pub_type or 'unknown'}")
    if year_penalty:
        reasons.append(f"before_min_year={year}")
    if short_abstract_penalty:
        reasons.append(f"short_abstract_tokens={abstract_tokens}")

    return {
        "screening_score": weighted_score,
        "screening_label": label,
        "screening_reasons": reasons,
        "matched_terms": sorted(set(include_hits + high_priority_hits)),
        "screening_features": {
            "include_hits": len(include_hits),
            "high_priority_hits": len(high_priority_hits),
            "exclude_hits": len(exclude_hits),
            "missing_concept_groups": missing_groups,
            "cited_by_count": cited_by_count or 0,
            "query_overlap": query_overlap_n,
            "concept_diversity": concept_diversity,
            "abstract_tokens": abstract_tokens,
            "language": language,
            "type": pub_type,
            "year": year,
        },
    }


def normalize_row(item, group, query, rules):
    title = item.get("display_name")
    year = item.get("publication_year")
    doi = item.get("doi")
    location = item.get("primary_location") or {}
    landing = location.get("landing_page_url")
    source = (location.get("source") or {}).get("display_name")
    abstract = reconstruct_abstract(item.get("abstract_inverted_index"))
    pub_type = item.get("type")
    language = item.get("language")
    cites = item.get("cited_by_count", 0)

    authors = []
    for a in item.get("authorships", [])[:5]:
        name = (a.get("author") or {}).get("display_name")
        if name:
            authors.append(name)

    screening = score_screening(title or "", abstract, query, language, pub_type, year, cites, rules)

    return {
        "group": group,
        "query": query,
        "title": title,
        "year": year,
        "doi": doi,
        "url": landing,
        "venue": source,
        "authors": authors,
        "type": pub_type,
        "openalex_id": item.get("id"),
        "language": language,
        "cited_by_count": cites,
        "abstract": abstract,
        **screening,
    }


def dedup_key(row):
    if row.get("doi"):
        return ("doi", row["doi"].lower())
    return ("title", (row.get("title") or "").strip().lower())


def _query_set(value) -> set:
    if isinstance(value, list):
        return {v for v in value if v}
    if isinstance(value, str) and value:
        return {value}
    return set()


def merge_rows(existing: Dict, new_row: Dict) -> Dict:
    better = existing
    if (new_row.get("screening_score") or 0) > (existing.get("screening_score") or 0):
        better = new_row
    elif (new_row.get("cited_by_count") or 0) > (existing.get("cited_by_count") or 0):
        better = new_row

    merged = dict(better)
    merged["query"] = sorted(_query_set(existing.get("query")) | _query_set(new_row.get("query")))
    return merged


def summarize_labels(rows: List[Dict]) -> Dict[str, int]:
    out = {"include": 0, "review": 0, "exclude": 0}
    for r in rows:
        label = r.get("screening_label", "exclude")
        out[label] = out.get(label, 0) + 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--screening-rules", default="queries/screening_rules.json")
    ap.add_argument("--report-out", default="", help="optional JSON report path for retrieval/screening diagnostics")
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
    query_stats: Dict[str, Dict] = {}
    for g in cfg.get("groups", []):
        gname = g.get("name", "unknown")
        for q in g.get("queries", []):
            data = fetch_openalex(q, per_page=per_query)
            normalized = [normalize_row(item, gname, q, rules) for item in data.get("results", [])]
            rows.extend(normalized)
            query_stats[q] = {
                "group": gname,
                "fetched": len(normalized),
                "labels": summarize_labels(normalized),
                "top_score": max((r.get("screening_score", 0.0) for r in normalized), default=0.0),
            }
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
            0 if x.get("screening_label") == "include" else (1 if x.get("screening_label") == "review" else 2),
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

    if args.report_out:
        report_path = Path(args.report_out)
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report = {
            "config": args.config,
            "screening_rules": args.screening_rules,
            "raw_records": len(rows),
            "deduped_records": len(deduped),
            "labels": summarize_labels(ordered),
            "per_query": query_stats,
        }
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"report: {report_path}")


if __name__ == "__main__":
    main()
