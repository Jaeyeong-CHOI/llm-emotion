# Literature Screening Rubric (v0.3)

This repository now applies a **weighted + constraint-based screening layer** during OpenAlex ingestion.

## Inputs
- `queries/search_queries.json`: retrieval query groups
- `queries/screening_rules.json`: include/high-priority/exclude keywords + weighted scoring policy

## Outputs per paper
- `screening_score` (continuous weighted score)
- `screening_label` (`include` / `review` / `exclude`)
- `matched_terms`
- `screening_reasons`
- `screening_features` (auditable feature dictionary)

## Decision policy
1. Weighted lexical score = include hits + high-priority hits (with configurable weights)
2. Citation bonus = `log1p(cited_by_count)` scaled by weight
3. Penalties for:
   - exclusion hits
   - missing required concept groups
   - non-preferred language/type
   - publication year below threshold
4. Labeling:
   - `include`: score >= include threshold, no exclude hit, no missing concept groups
   - `review`: score >= review threshold
   - `exclude`: otherwise

## Why this helps
- Better precision than flat lexical counts
- Keeps a reproducible audit trail inside `refs/openalex_results.jsonl`
- Makes downstream evidence ranking quality-aware and transparent

## Known limitations
- Still lexical-first (not full semantic retrieval)
- Citation bonus can favor older mainstream papers
- Requires periodic manual calibration of thresholds/weights
