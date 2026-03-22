# Literature Screening Rubric (v0.2)

This repository now applies a **transparent lexical screening layer** during OpenAlex ingestion.

## Inputs
- `queries/search_queries.json`: retrieval query groups
- `queries/screening_rules.json`: include/high-priority/exclude keyword sets + threshold

## Outputs per paper
- `screening_score`
- `screening_label` (`include` / `review` / `exclude`)
- `matched_terms`
- `screening_reasons`

## Decision policy
1. Score = number of include hits + high-priority hits
2. `include` if score >= threshold and no exclude hit
3. `review` if score >= threshold but contains exclude hit
4. `exclude` otherwise

## Why this helps
- Improves consistency over ad-hoc title triage
- Keeps a reproducible audit trail inside `refs/openalex_results.jsonl`
- Makes downstream evidence table sorting quality-aware

## Known limitations
- Lexical only: can miss semantically relevant papers with uncommon wording
- Can over-include broad AI papers if wording overlaps
- Should be paired with periodic manual quality checks
