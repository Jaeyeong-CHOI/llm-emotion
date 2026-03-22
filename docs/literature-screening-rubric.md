# Literature Screening Rubric (v0.7)

This repository applies a weighted, auditable screening layer during OpenAlex ingestion.

## Inputs
- `queries/search_queries.json`: retrieval query groups, now including a methods-oriented human-evaluation lane
- `queries/screening_rules.json`: inclusion/exclusion terms, alias map, priority cues, weights, thresholds

## Outputs per paper
- `screening_score`: weighted score
- `screening_label`: `include` / `review` / `exclude`
- `screening_priority`: `high` / `medium` / `low` manual follow-up priority
- `matched_terms`
- `screening_reasons`
- `screening_features`

## Scoring policy (v0.7)
1. Canonical lexical hits use alias expansion, so variants like `LLMs`, `anthropomorphic`, and `counterfactual reasoning` map back to the same audited concept.
2. Weighted score adds:
   - include hits
   - high-priority hits
   - citation bonus
   - query overlap bonus
   - concept diversity bonus
   - title-hit bonus
   - review-priority bonus for methodology cues such as `human evaluation`, `annotator`, and `behavioral experiment`
   - method-cue bonus (explicit study design/annotation cues)
   - recency bonus (bounded year-aware preference)
   - abstract-density bonus for concentrated relevance signals
3. Penalties remain in place for:
   - exclusion hits
   - missing concept groups
   - non-preferred language/type
   - pre-threshold publication year
   - very short abstracts

## Labeling and triage policy
- `include`: score >= include threshold, no exclude hit, no missing concept groups, include-gate constraints satisfied (`min_include_hits`, method/review/high-priority signal), and include-guard passed (`include_margin_min`, `max_penalty_for_include`)
- `review`: score >= review threshold
- `exclude`: otherwise

Manual follow-up should use `screening_priority`:
- `high`: direct include or review items with strong method cues / low ambiguity
- `medium`: review items worth checking but with weaker concept coverage
- `low`: likely noise or already disfavored by exclusion/coverage penalties

## Retrieval diagnostics
```bash
python3 scripts/search_openalex.py \
  --config queries/search_queries.json \
  --screening-rules queries/screening_rules.json \
  --out refs/openalex_results.jsonl \
  --report-out results/lit_search_report.json
```

`results/lit_search_report.json` now includes:
- overall label distribution
- overall priority distribution
- overall method-signal coverage (`with_method_cues` vs `without_method_cues`)
- include-guard pass/fail counts (overall + per-query)
- per-query label/priority/method counts
- top high-priority titles for manual screening

## Why this helps
- Better recall on lexical variants without giving up reproducibility
- Separates relevance from follow-up priority, which is useful during title/abstract screening
- Surfaces methods-heavy papers that can inform benchmark design and human-comparison protocol
- Keeps the screening decision inspectable in JSONL output
