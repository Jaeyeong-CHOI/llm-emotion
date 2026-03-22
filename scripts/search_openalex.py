#!/usr/bin/env python3
import argparse
import csv
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
    "review_priority_any": [
        "human evaluation",
        "annotator",
        "behavioral experiment",
        "psychology",
        "emotion benchmark",
    ],
    "method_cues_any": [
        "human evaluation",
        "human study",
        "annotator",
        "annotation",
        "behavioral experiment",
        "survey",
        "inter-rater",
        "manual coding",
        "benchmark",
    ],
    "term_aliases": {
        "large language model": ["large language model", "large language models", "llm", "llms", "language model"],
        "counterfactual": ["counterfactual", "counterfactuals", "counterfactual thinking"],
        "regret": ["regret", "regretful"],
        "emotion": ["emotion", "emotions", "emotional", "affect", "affective"],
        "anthropomorphism": ["anthropomorphism", "anthropomorphic"],
        "theory of mind": ["theory of mind", "mentalizing", "mental state"],
        "self-reflection": ["self-reflection", "self reflection", "reflective reasoning"],
    },
    "weights": {
        "include_any": 1.0,
        "high_priority": 2.0,
        "cited_by_log1p": 0.35,
        "query_overlap": 0.2,
        "concept_diversity": 0.15,
        "title_hit": 0.35,
        "review_priority": 0.5,
        "method_cue": 0.6,
        "recency_year": 0.08,
        "abstract_density": 0.25,
        "bridge_sentence": 0.45,
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
    "max_recent_year_bonus_span": 6,
    "include_requires_any": {
        "min_include_hits": 2,
        "method_or_review_signal": True,
        "include_margin_min": 0.35,
        "max_penalty_for_include": 0.5,
        "min_concept_diversity": 2,
        "min_abstract_tokens_for_include": 50,
        "require_title_or_bridge_signal": True,
        "min_bridge_sentence_hits": 1,
        "require_llm_concept": True,
    },
    "review_requires_any": {
        "min_include_hits_or_priority": 1,
        "method_or_review_signal": False,
        "require_llm_concept": True,
    },
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


def _term_variants(term: str, rules: Dict) -> List[str]:
    aliases = rules.get("term_aliases", {})
    values = aliases.get(term, [term])
    return [str(v).lower() for v in values if str(v).strip()]


def _hit_terms(text: str, terms: Sequence[str], rules: Dict) -> List[str]:
    hits = []
    for term in terms:
        variants = _term_variants(term, rules)
        if any(_contains_phrase(text, variant) for variant in variants):
            hits.append(term)
    return hits


def _query_terms(query: str) -> List[str]:
    # lightweight lexical tokens from OpenAlex query string
    candidates = re.findall(r"[a-zA-Z][a-zA-Z\-]{2,}", query.lower())
    stop = {"and", "or", "the", "for", "with", "without", "from", "into", "about"}
    return [c for c in candidates if c not in stop]


def _token_count(text: str) -> int:
    return len(re.findall(r"\w+", text or ""))


def _split_sentences(text: str) -> List[str]:
    if not text:
        return []
    parts = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip().lower() for p in parts if p and p.strip()]


def _bridge_sentence_hits(text: str, group_a: Sequence[str], group_b: Sequence[str], rules: Dict) -> int:
    # Count sentences containing at least one term from each concept group.
    sentences = _split_sentences(text)
    hits = 0
    for sent in sentences:
        a_hit = bool(_hit_terms(sent, group_a, rules))
        b_hit = bool(_hit_terms(sent, group_b, rules))
        if a_hit and b_hit:
            hits += 1
    return hits


def _priority_label(label: str, exclude_hits: List[str], missing_groups: int, review_hits: List[str], score: float) -> str:
    if label == "include":
        return "high"
    if label == "review" and not exclude_hits and missing_groups <= 1 and (review_hits or score >= 2.5):
        return "high"
    if label == "review":
        return "medium"
    return "low"


def score_screening(title: str, abstract: str, query: str, language: str, pub_type: str, year: int, cited_by_count: int, rules: Dict) -> Dict:
    title_l = (title or "").lower()
    abstract_l = (abstract or "").lower()
    text = f"{title_l}\n{abstract_l}"

    include_hits: List[str] = _hit_terms(text, rules["include_any"], rules)
    high_priority_hits: List[str] = _hit_terms(text, rules["high_priority"], rules)
    exclude_hits: List[str] = _hit_terms(text, rules["exclude_if_any"], rules)
    review_hits: List[str] = _hit_terms(text, rules.get("review_priority_any", []), rules)
    method_hits: List[str] = _hit_terms(text, rules.get("method_cues_any", []), rules)
    title_hits: List[str] = _hit_terms(title_l, rules["include_any"], rules)

    concept_groups = rules.get("required_concepts_any", [])
    concept_hits = []
    missing_groups = 0
    for group in concept_groups:
        g_hits = _hit_terms(text, group, rules)
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
    title_bonus = len(title_hits) * float(weights.get("title_hit", 0.35))
    review_priority_bonus = len(review_hits) * float(weights.get("review_priority", 0.5))
    method_cue_bonus = len(method_hits) * float(weights.get("method_cue", 0.6))

    bridge_sentence_hits = 0
    if len(concept_groups) >= 2:
        bridge_sentence_hits = _bridge_sentence_hits(abstract_l, concept_groups[0], concept_groups[1], rules)
    bridge_sentence_bonus = bridge_sentence_hits * float(weights.get("bridge_sentence", 0.45))

    current_year = time.gmtime().tm_year
    span = max(1, int(rules.get("max_recent_year_bonus_span", 6) or 6))
    recency_delta = max(0, min(span, current_year - (year or current_year)))
    recency_bonus = float(weights.get("recency_year", 0.08)) * (span - recency_delta)

    abstract_tokens = _token_count(abstract)
    density_bonus = 0.0
    if abstract_tokens:
        hit_density = (len(include_hits) + len(high_priority_hits) + len(review_hits)) / abstract_tokens
        density_bonus = min(hit_density, 0.08) * float(weights.get("abstract_density", 0.25)) * 100.0

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
        + title_bonus
        + review_priority_bonus
        + method_cue_bonus
        + recency_bonus
        + density_bonus
        + bridge_sentence_bonus
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

    include_constraints = rules.get("include_requires_any", {})
    min_include_hits = int(include_constraints.get("min_include_hits", 0) or 0)
    require_method_or_review = bool(include_constraints.get("method_or_review_signal", False))
    include_margin_min = float(include_constraints.get("include_margin_min", 0.0) or 0.0)
    max_penalty_for_include = float(include_constraints.get("max_penalty_for_include", 999.0) or 999.0)
    min_concept_diversity = int(include_constraints.get("min_concept_diversity", 0) or 0)
    min_abstract_tokens_for_include = int(include_constraints.get("min_abstract_tokens_for_include", 0) or 0)
    require_title_or_bridge_signal = bool(include_constraints.get("require_title_or_bridge_signal", False))
    min_bridge_sentence_hits = int(include_constraints.get("min_bridge_sentence_hits", 0) or 0)
    require_llm_concept_for_include = bool(include_constraints.get("require_llm_concept", False))
    llm_concept_hits = concept_hits[0] if concept_hits else []

    include_gate_ok = True
    if min_include_hits and len(include_hits) < min_include_hits:
        include_gate_ok = False
    if require_method_or_review and not (method_hits or review_hits or high_priority_hits):
        include_gate_ok = False
    if min_concept_diversity and concept_diversity < min_concept_diversity:
        include_gate_ok = False
    if min_abstract_tokens_for_include and abstract_tokens < min_abstract_tokens_for_include:
        include_gate_ok = False
    if min_bridge_sentence_hits and bridge_sentence_hits < min_bridge_sentence_hits:
        include_gate_ok = False
    if require_title_or_bridge_signal and not (title_hits or bridge_sentence_hits > 0):
        include_gate_ok = False
    if require_llm_concept_for_include and not llm_concept_hits:
        include_gate_ok = False

    total_penalty = round(
        penalty_exclude + penalty_missing_group + lang_penalty + type_penalty + year_penalty + short_abstract_penalty,
        4,
    )
    include_margin = round(weighted_score - include_threshold, 4)
    include_guard_ok = include_margin >= include_margin_min and total_penalty <= max_penalty_for_include

    review_constraints = rules.get("review_requires_any", {})
    min_include_hits_or_priority = int(review_constraints.get("min_include_hits_or_priority", 0) or 0)
    review_requires_signal = bool(review_constraints.get("method_or_review_signal", False))
    require_llm_concept_for_review = bool(review_constraints.get("require_llm_concept", False))
    review_gate_ok = True
    signal_hits = len(include_hits) + len(high_priority_hits)
    if min_include_hits_or_priority and signal_hits < min_include_hits_or_priority:
        review_gate_ok = False
    if review_requires_signal and not (method_hits or review_hits):
        review_gate_ok = False
    if require_llm_concept_for_review and not llm_concept_hits:
        review_gate_ok = False

    if weighted_score >= include_threshold and not exclude_hits and missing_groups == 0 and include_gate_ok and include_guard_ok:
        label = "include"
    elif weighted_score >= review_threshold and review_gate_ok:
        label = "review"
    else:
        label = "exclude"

    priority = _priority_label(label, exclude_hits, missing_groups, review_hits, weighted_score)

    reasons = []
    if include_hits:
        reasons.append(f"include_hits={', '.join(include_hits[:6])}")
    if high_priority_hits:
        reasons.append(f"high_priority={', '.join(high_priority_hits[:6])}")
    if title_hits:
        reasons.append(f"title_hits={', '.join(title_hits[:4])}")
    if review_hits:
        reasons.append(f"review_priority={', '.join(review_hits[:4])}")
    if method_hits:
        reasons.append(f"method_cues={', '.join(method_hits[:4])}")
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
    if bridge_sentence_hits:
        reasons.append(f"bridge_sentence_hits={bridge_sentence_hits}")
    if not include_gate_ok:
        reasons.append("include_gate=failed")
        if min_concept_diversity and concept_diversity < min_concept_diversity:
            reasons.append(f"low_concept_diversity={concept_diversity}")
        if min_abstract_tokens_for_include and abstract_tokens < min_abstract_tokens_for_include:
            reasons.append(f"include_abstract_tokens_too_short={abstract_tokens}")
        if min_bridge_sentence_hits and bridge_sentence_hits < min_bridge_sentence_hits:
            reasons.append(f"bridge_sentence_too_low={bridge_sentence_hits}")
        if require_title_or_bridge_signal and not (title_hits or bridge_sentence_hits > 0):
            reasons.append("no_title_or_bridge_signal")
        if require_llm_concept_for_include and not llm_concept_hits:
            reasons.append("missing_llm_concept_for_include")
    if include_gate_ok and not include_guard_ok and weighted_score >= include_threshold:
        reasons.append("include_guard=failed")
    if weighted_score >= review_threshold and not review_gate_ok:
        reasons.append("review_gate=failed")
        if require_llm_concept_for_review and not llm_concept_hits:
            reasons.append("missing_llm_concept_for_review")

    confidence = "high"
    if missing_groups > 0 or total_penalty > max_penalty_for_include:
        confidence = "low"
    elif abstract_tokens < max(min_abstract_tokens, 60) or concept_diversity < 2 or bridge_sentence_hits == 0:
        confidence = "medium"

    return {
        "screening_score": weighted_score,
        "screening_label": label,
        "screening_priority": priority,
        "screening_reasons": reasons,
        "matched_terms": sorted(set(include_hits + high_priority_hits + review_hits)),
        "screening_confidence": confidence,
        "screening_features": {
            "include_hits": len(include_hits),
            "high_priority_hits": len(high_priority_hits),
            "review_priority_hits": len(review_hits),
            "method_hits": len(method_hits),
            "exclude_hits": len(exclude_hits),
            "missing_concept_groups": missing_groups,
            "cited_by_count": cited_by_count or 0,
            "query_overlap": query_overlap_n,
            "concept_diversity": concept_diversity,
            "llm_concept_hits": len(llm_concept_hits),
            "title_hits": len(title_hits),
            "abstract_tokens": abstract_tokens,
            "language": language,
            "type": pub_type,
            "year": year,
            "recency_bonus": round(recency_bonus, 4),
            "bridge_sentence_hits": bridge_sentence_hits,
            "bridge_sentence_bonus": round(bridge_sentence_bonus, 4),
            "total_penalty": total_penalty,
            "include_margin": include_margin,
            "include_gate_ok": include_gate_ok,
            "include_guard_ok": include_guard_ok,
            "review_gate_ok": review_gate_ok,
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
    merged["group"] = sorted(_query_set(existing.get("group")) | _query_set(new_row.get("group")))
    merged["matched_terms"] = sorted(_query_set(existing.get("matched_terms")) | _query_set(new_row.get("matched_terms")))
    merged["screening_reasons"] = sorted(_query_set(existing.get("screening_reasons")) | _query_set(new_row.get("screening_reasons")))
    if "high" in {existing.get("screening_priority"), new_row.get("screening_priority")}:
        merged["screening_priority"] = "high"
    elif "medium" in {existing.get("screening_priority"), new_row.get("screening_priority")}:
        merged["screening_priority"] = "medium"
    else:
        merged["screening_priority"] = merged.get("screening_priority", "low")
    return merged


def summarize_labels(rows: List[Dict]) -> Dict[str, int]:
    out = {"include": 0, "review": 0, "exclude": 0}
    for r in rows:
        label = r.get("screening_label", "exclude")
        out[label] = out.get(label, 0) + 1
    return out


def summarize_priorities(rows: List[Dict]) -> Dict[str, int]:
    out = {"high": 0, "medium": 0, "low": 0}
    for r in rows:
        priority = r.get("screening_priority", "low")
        out[priority] = out.get(priority, 0) + 1
    return out


def summarize_confidence(rows: List[Dict]) -> Dict[str, int]:
    out = {"high": 0, "medium": 0, "low": 0}
    for r in rows:
        c = (r.get("screening_confidence") or "low").lower()
        out[c] = out.get(c, 0) + 1
    return out


def summarize_confidence_by_label(rows: List[Dict]) -> Dict[str, Dict[str, int]]:
    out = {
        "include": {"high": 0, "medium": 0, "low": 0},
        "review": {"high": 0, "medium": 0, "low": 0},
        "exclude": {"high": 0, "medium": 0, "low": 0},
    }
    for row in rows:
        label = (row.get("screening_label") or "exclude").lower()
        confidence = (row.get("screening_confidence") or "low").lower()
        if label not in out:
            out[label] = {"high": 0, "medium": 0, "low": 0}
        out[label][confidence] = out[label].get(confidence, 0) + 1
    return out


def summarize_llm_concept(rows: List[Dict]) -> Dict[str, int]:
    out = {"with_llm_concept": 0, "without_llm_concept": 0}
    for r in rows:
        features = r.get("screening_features") or {}
        llm_hits = int(features.get("llm_concept_hits", 0) or 0)
        if llm_hits > 0:
            out["with_llm_concept"] += 1
        else:
            out["without_llm_concept"] += 1
    return out


def collect_borderline(rows: List[Dict], include_th: float, review_th: float, margin: float = 0.4) -> Dict[str, List[Dict]]:
    include_borderline = []
    review_borderline = []
    for r in rows:
        score = float(r.get("screening_score") or 0.0)
        if r.get("screening_label") == "include" and abs(score - include_th) <= margin:
            include_borderline.append(r)
        if r.get("screening_label") == "review" and abs(score - review_th) <= margin:
            review_borderline.append(r)
    include_borderline = sorted(include_borderline, key=lambda x: x.get("screening_score", 0.0))[:25]
    review_borderline = sorted(review_borderline, key=lambda x: x.get("screening_score", 0.0))[:25]
    def compact(row: Dict) -> Dict:
        return {
            "title": row.get("title"),
            "year": row.get("year"),
            "score": row.get("screening_score"),
            "label": row.get("screening_label"),
            "confidence": row.get("screening_confidence"),
            "priority": row.get("screening_priority"),
            "reasons": row.get("screening_reasons", [])[:6],
        }
    return {
        "include": [compact(r) for r in include_borderline],
        "review": [compact(r) for r in review_borderline],
    }


def summarize_method_signal(rows: List[Dict]) -> Dict[str, int]:
    out = {"with_method_cues": 0, "without_method_cues": 0}
    for r in rows:
        mh = ((r.get("screening_features") or {}).get("method_hits") or 0)
        if mh > 0:
            out["with_method_cues"] += 1
        else:
            out["without_method_cues"] += 1
    return out


def summarize_include_guard(rows: List[Dict]) -> Dict[str, int]:
    out = {"passed": 0, "failed": 0}
    for r in rows:
        features = r.get("screening_features") or {}
        if features.get("include_guard_ok", True):
            out["passed"] += 1
        else:
            out["failed"] += 1
    return out


def summarize_triage_risk(rows: List[Dict], include_th: float, review_th: float) -> Dict[str, int]:
    out = {
        "include_low_confidence": 0,
        "review_high_score": 0,
        "exclude_near_review_threshold": 0,
        "gate_failures_near_threshold": 0,
    }
    for r in rows:
        label = r.get("screening_label")
        confidence = (r.get("screening_confidence") or "low").lower()
        score = float(r.get("screening_score") or 0.0)
        features = r.get("screening_features") or {}

        if label == "include" and confidence != "high":
            out["include_low_confidence"] += 1
        if label == "review" and score >= include_th - 0.35:
            out["review_high_score"] += 1
        if label == "exclude" and score >= review_th - 0.25:
            out["exclude_near_review_threshold"] += 1
        if score >= review_th and (not features.get("include_gate_ok", True) or not features.get("review_gate_ok", True)):
            out["gate_failures_near_threshold"] += 1
    return out


def collect_quality_alerts(rows: List[Dict], include_th: float, review_th: float) -> Dict[str, List[Dict]]:
    def compact(row: Dict, extra: Dict | None = None) -> Dict:
        payload = {
            "title": row.get("title"),
            "year": row.get("year"),
            "score": row.get("screening_score"),
            "label": row.get("screening_label"),
            "confidence": row.get("screening_confidence"),
            "priority": row.get("screening_priority"),
            "reasons": row.get("screening_reasons", [])[:6],
        }
        if extra:
            payload.update(extra)
        return payload

    include_gate_fail_near = []
    review_gate_fail_near = []
    llm_only_weak_method = []

    for row in rows:
        features = row.get("screening_features") or {}
        score = float(row.get("screening_score") or 0.0)
        method_hits = int(features.get("method_hits", 0) or 0)
        review_hits = int(features.get("review_priority_hits", 0) or 0)
        include_hits = int(features.get("include_hits", 0) or 0)
        llm_hits = int(features.get("llm_concept_hits", 0) or 0)

        if score >= (include_th - 0.6) and not features.get("include_gate_ok", True):
            include_gate_fail_near.append(compact(row, {"include_gate_ok": False}))

        if score >= review_th and not features.get("review_gate_ok", True):
            review_gate_fail_near.append(compact(row, {"review_gate_ok": False}))

        if llm_hits > 0 and include_hits >= 2 and method_hits == 0 and review_hits == 0:
            llm_only_weak_method.append(compact(row, {"method_hits": method_hits, "review_hits": review_hits}))

    include_gate_fail_near = sorted(include_gate_fail_near, key=lambda x: x.get("score", 0), reverse=True)[:30]
    review_gate_fail_near = sorted(review_gate_fail_near, key=lambda x: x.get("score", 0), reverse=True)[:30]
    llm_only_weak_method = sorted(llm_only_weak_method, key=lambda x: x.get("score", 0), reverse=True)[:30]

    return {
        "include_gate_fail_near_threshold": include_gate_fail_near,
        "review_gate_fail_near_threshold": review_gate_fail_near,
        "llm_signal_but_weak_method_evidence": llm_only_weak_method,
    }


def summarize_bridge_signal(rows: List[Dict]) -> Dict[str, int]:
    out = {"with_bridge_sentence": 0, "without_bridge_sentence": 0}
    for r in rows:
        features = r.get("screening_features") or {}
        bridge_hits = int(features.get("bridge_sentence_hits", 0) or 0)
        if bridge_hits > 0:
            out["with_bridge_sentence"] += 1
        else:
            out["without_bridge_sentence"] += 1
    return out


def collect_manual_qc_queue(rows: List[Dict], include_th: float, review_th: float, limit: int = 40) -> List[Dict]:
    queue = []
    for row in rows:
        label = row.get("screening_label")
        confidence = (row.get("screening_confidence") or "low").lower()
        score = float(row.get("screening_score") or 0.0)
        features = row.get("screening_features") or {}
        include_margin = float(features.get("include_margin", 0.0) or 0.0)

        risk = 0.0
        reasons = []

        if label == "include" and confidence != "high":
            risk += 2.0
            reasons.append("include_non_high_confidence")
        if label == "review" and score >= include_th - 0.35:
            risk += 1.8
            reasons.append("review_close_to_include_threshold")
        if label == "exclude" and score >= review_th - 0.25:
            risk += 2.2
            reasons.append("exclude_close_to_review_threshold")
        if not features.get("include_gate_ok", True):
            risk += 1.0
            reasons.append("include_gate_failed")
        if not features.get("review_gate_ok", True):
            risk += 0.8
            reasons.append("review_gate_failed")
        if abs(include_margin) <= 0.4:
            risk += 0.7
            reasons.append("small_include_margin")
        if int(features.get("bridge_sentence_hits", 0) or 0) == 0:
            risk += 0.4
            reasons.append("no_bridge_sentence")

        if risk <= 0:
            continue

        queue.append(
            {
                "title": row.get("title"),
                "year": row.get("year"),
                "openalex_id": row.get("id"),
                "doi": row.get("doi"),
                "source_query": row.get("query"),
                "source_group": row.get("group"),
                "label": label,
                "score": score,
                "confidence": confidence,
                "priority": row.get("screening_priority"),
                "risk_score": round(risk, 3),
                "risk_reasons": reasons,
                "screening_reasons": row.get("screening_reasons", [])[:6],
            }
        )

    queue.sort(key=lambda x: (-(x.get("risk_score") or 0.0), -(x.get("score") or 0.0)))
    return queue[:limit]


def collect_manual_qc_queue_by_label(rows: List[Dict], include_th: float, review_th: float, per_label_limit: int = 10) -> Dict[str, List[Dict]]:
    full_queue = collect_manual_qc_queue(rows, include_th, review_th, limit=max(40, per_label_limit * 6))
    out = {"include": [], "review": [], "exclude": []}
    for row in full_queue:
        label = str(row.get("label") or "exclude")
        if label not in out:
            continue
        if len(out[label]) >= per_label_limit:
            continue
        out[label].append(row)
    return out


def collect_manual_qc_queue_balanced(
    rows: List[Dict],
    include_th: float,
    review_th: float,
    limit: int = 40,
    per_label_limit: int = 10,
    per_confidence_limit: int = 8,
    per_group_limit: int = 12,
) -> List[Dict]:
    ranked = collect_manual_qc_queue(rows, include_th, review_th, limit=max(limit * 4, 80))
    selected = []
    label_counts = {"include": 0, "review": 0, "exclude": 0}
    confidence_counts = {"high": 0, "medium": 0, "low": 0}
    group_counts: Dict[str, int] = {}

    def _norm_group(value) -> str:
        if isinstance(value, list):
            values = [str(v).strip() for v in value if str(v).strip()]
            return values[0] if values else "unknown"
        if isinstance(value, str):
            value = value.strip()
            return value if value else "unknown"
        return "unknown"

    # First pass: balanced by both label and confidence to avoid review bias.
    for row in ranked:
        if len(selected) >= limit:
            break
        label = str(row.get("label") or "exclude")
        confidence = str(row.get("confidence") or "low").lower()
        if label not in label_counts:
            continue
        if label_counts[label] >= per_label_limit:
            continue
        if confidence_counts.get(confidence, 0) >= per_confidence_limit:
            continue
        group_name = _norm_group(row.get("source_group"))
        if group_counts.get(group_name, 0) >= per_group_limit:
            continue
        selected.append(row)
        label_counts[label] += 1
        confidence_counts[confidence] = confidence_counts.get(confidence, 0) + 1
        group_counts[group_name] = group_counts.get(group_name, 0) + 1

    # Second pass: fill remaining slots with top-risk items while keeping label ceilings.
    for row in ranked:
        if len(selected) >= limit:
            break
        if row in selected:
            continue
        label = str(row.get("label") or "exclude")
        if label not in label_counts:
            continue
        if label_counts[label] >= per_label_limit:
            continue
        group_name = _norm_group(row.get("source_group"))
        if group_counts.get(group_name, 0) >= per_group_limit:
            continue
        selected.append(row)
        label_counts[label] += 1
        group_counts[group_name] = group_counts.get(group_name, 0) + 1

    return selected


def summarize_label_gate_conflicts(rows: List[Dict]) -> Dict[str, int]:
    out = {
        "include_with_gate_failures": 0,
        "review_with_gate_failures": 0,
        "exclude_with_strong_signal": 0,
    }
    for row in rows:
        label = row.get("screening_label")
        score = float(row.get("screening_score") or 0.0)
        features = row.get("screening_features") or {}
        include_gate_ok = bool(features.get("include_gate_ok", True))
        review_gate_ok = bool(features.get("review_gate_ok", True))
        include_margin = float(features.get("include_margin", 0.0) or 0.0)

        if label == "include" and (not include_gate_ok or not review_gate_ok):
            out["include_with_gate_failures"] += 1
        if label == "review" and (not include_gate_ok or not review_gate_ok):
            out["review_with_gate_failures"] += 1
        if label == "exclude" and score >= 2.0 and include_margin > -0.5:
            out["exclude_with_strong_signal"] += 1

    return out


def write_manual_qc_csv(path: Path, queue: List[Dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = [
        "rank",
        "label",
        "risk_score",
        "score",
        "confidence",
        "priority",
        "year",
        "title",
        "openalex_id",
        "doi",
        "source_query",
        "source_group",
        "risk_reasons",
        "screening_reasons",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for idx, row in enumerate(queue, start=1):
            writer.writerow(
                {
                    "rank": idx,
                    "label": row.get("label"),
                    "risk_score": row.get("risk_score"),
                    "score": row.get("score"),
                    "confidence": row.get("confidence"),
                    "priority": row.get("priority"),
                    "year": row.get("year"),
                    "title": row.get("title"),
                    "openalex_id": row.get("openalex_id"),
                    "doi": row.get("doi"),
                    "source_query": row.get("source_query"),
                    "source_group": row.get("source_group"),
                    "risk_reasons": ";".join(row.get("risk_reasons") or []),
                    "screening_reasons": ";".join(row.get("screening_reasons") or []),
                }
            )


def summarize_manual_qc_queue(queue: List[Dict]) -> Dict[str, Dict[str, int]]:
    summary = {
        "by_label": {},
        "by_confidence": {},
        "by_group": {},
    }
    for row in queue:
        label = str(row.get("label") or "exclude")
        confidence = str(row.get("confidence") or "low").lower()
        group = row.get("source_group")
        if isinstance(group, list):
            group = next((str(v).strip() for v in group if str(v).strip()), "unknown")
        else:
            group = str(group or "unknown").strip() or "unknown"

        summary["by_label"][label] = summary["by_label"].get(label, 0) + 1
        summary["by_confidence"][confidence] = summary["by_confidence"].get(confidence, 0) + 1
        summary["by_group"][group] = summary["by_group"].get(group, 0) + 1
    return summary


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--screening-rules", default="queries/screening_rules.json")
    ap.add_argument("--report-out", default="", help="optional JSON report path for retrieval/screening diagnostics")
    ap.add_argument("--audit-out", default="", help="optional JSON path for borderline/manual-QC screening candidates")
    ap.add_argument("--manual-qc-limit", type=int, default=40, help="max size of ranked manual QC queue")
    ap.add_argument("--manual-qc-per-label", type=int, default=10, help="max manual QC candidates per label bucket")
    ap.add_argument(
        "--manual-qc-per-confidence",
        type=int,
        default=8,
        help="max manual QC candidates per confidence bucket in balanced queue",
    )
    ap.add_argument("--manual-qc-csv", default="", help="optional CSV path for ranked manual QC triage queue")
    ap.add_argument(
        "--manual-qc-per-group",
        type=int,
        default=12,
        help="max manual QC candidates per retrieval group in balanced queue",
    )
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
                "priorities": summarize_priorities(normalized),
                "method_signal": summarize_method_signal(normalized),
                "bridge_signal": summarize_bridge_signal(normalized),
                "include_guard": summarize_include_guard(normalized),
                "confidence": summarize_confidence(normalized),
                "llm_concept": summarize_llm_concept(normalized),
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

    include_th = float(rules.get("threshold_include", 3.0))
    review_th = float(rules.get("threshold_review", include_th / 2))
    ranked_manual_qc_queue = collect_manual_qc_queue(ordered, include_th, review_th, limit=args.manual_qc_limit)
    balanced_manual_qc_queue = collect_manual_qc_queue_balanced(
        ordered,
        include_th,
        review_th,
        limit=args.manual_qc_limit,
        per_label_limit=args.manual_qc_per_label,
        per_confidence_limit=args.manual_qc_per_confidence,
        per_group_limit=args.manual_qc_per_group,
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
            "priorities": summarize_priorities(ordered),
            "method_signal": summarize_method_signal(ordered),
            "bridge_signal": summarize_bridge_signal(ordered),
            "include_guard": summarize_include_guard(ordered),
            "confidence": summarize_confidence(ordered),
            "confidence_by_label": summarize_confidence_by_label(ordered),
            "llm_concept": summarize_llm_concept(ordered),
            "triage_risk": summarize_triage_risk(ordered, include_th, review_th),
            "label_gate_conflicts": summarize_label_gate_conflicts(ordered),
            "per_query": query_stats,
            "top_priority_titles": [r.get("title") for r in ordered[:10] if r.get("screening_priority") == "high"],
            "quality_alerts": collect_quality_alerts(ordered, include_th, review_th),
            "manual_qc_queue": ranked_manual_qc_queue,
            "manual_qc_queue_balanced": balanced_manual_qc_queue,
            "manual_qc_queue_balanced_summary": summarize_manual_qc_queue(balanced_manual_qc_queue),
            "manual_qc_queue_by_label": collect_manual_qc_queue_by_label(
                ordered, include_th, review_th, per_label_limit=args.manual_qc_per_label
            ),
        }
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"report: {report_path}")

    if args.manual_qc_csv:
        csv_path = Path(args.manual_qc_csv)
        write_manual_qc_csv(csv_path, balanced_manual_qc_queue)
        print(f"manual_qc_csv: {csv_path}")

    if args.audit_out:
        audit_path = Path(args.audit_out)
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        audit_payload = {
            "config": args.config,
            "screening_rules": args.screening_rules,
            "thresholds": {"include": include_th, "review": review_th},
            "counts": {
                "records": len(ordered),
                "labels": summarize_labels(ordered),
                "confidence": summarize_confidence(ordered),
                "confidence_by_label": summarize_confidence_by_label(ordered),
                "llm_concept": summarize_llm_concept(ordered),
                "triage_risk": summarize_triage_risk(ordered, include_th, review_th),
                "label_gate_conflicts": summarize_label_gate_conflicts(ordered),
            },
            "borderline": collect_borderline(ordered, include_th, review_th),
            "quality_alerts": collect_quality_alerts(ordered, include_th, review_th),
            "manual_qc_queue": ranked_manual_qc_queue,
            "manual_qc_queue_balanced": balanced_manual_qc_queue,
            "manual_qc_queue_balanced_summary": summarize_manual_qc_queue(balanced_manual_qc_queue),
            "manual_qc_queue_by_label": collect_manual_qc_queue_by_label(
                ordered, include_th, review_th, per_label_limit=args.manual_qc_per_label
            ),
            "exclude_high_score_without_llm": [
                {
                    "title": r.get("title"),
                    "year": r.get("year"),
                    "score": r.get("screening_score"),
                    "reasons": r.get("screening_reasons", [])[:6],
                }
                for r in ordered
                if r.get("screening_label") == "exclude"
                and float(r.get("screening_score") or 0.0) >= review_th
                and int(((r.get("screening_features") or {}).get("llm_concept_hits", 0) or 0)) == 0
            ][:30],
        }
        audit_path.write_text(json.dumps(audit_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"audit: {audit_path}")

if __name__ == "__main__":
    main()
