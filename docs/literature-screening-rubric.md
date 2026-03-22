# Literature Screening Rubric (v0.4)

This repository applies a **weighted + constraint-based screening layer** during OpenAlex ingestion.

## Inputs
- `queries/search_queries.json`: retrieval query groups
- `queries/screening_rules.json`: include/high-priority/exclude keywords + weighted scoring policy

## Outputs per paper
- `screening_score` (continuous weighted score)
- `screening_label` (`include` / `review` / `exclude`)
- `matched_terms`
- `screening_reasons`
- `screening_features` (auditable feature dictionary)

## Scoring policy (v0.4)
1. Weighted lexical score = include hits + high-priority hits (configurable weights)
2. Citation bonus = `log1p(cited_by_count)` scaled by weight
3. **Query overlap bonus**: overlap between query lexical tokens and title/abstract
4. **Concept diversity bonus**: how many required concept groups are covered
5. Penalties for:
   - exclusion hits
   - missing required concept groups
   - non-preferred language/type
   - publication year below threshold
   - very short abstract (`min_abstract_tokens`)

## Labeling policy
- `include`: score >= include threshold, no exclude hit, no missing concept groups
- `review`: score >= review threshold
- `exclude`: otherwise

## Diagnostics for retrieval quality
Use optional report output to monitor query quality over time:

```bash
python3 scripts/search_openalex.py \
  --config queries/search_queries.json \
  --screening-rules queries/screening_rules.json \
  --out refs/openalex_results.jsonl \
  --report-out results/lit_search_report.json
```

`results/lit_search_report.json` includes per-query fetched count, label distribution, and top score.

## Why this helps
- Better precision than flat lexical counts
- Adds retrieval diagnostics for systematic query refinement
- Keeps a reproducible audit trail inside `refs/openalex_results.jsonl`
- Makes downstream evidence ranking quality-aware and transparent

## Known limitations
- Still lexical-first (not full semantic retrieval)
- Citation bonus can favor older mainstream papers
- Requires periodic manual calibration of thresholds/weights
