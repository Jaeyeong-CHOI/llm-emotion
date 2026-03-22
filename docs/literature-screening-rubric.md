# Literature Screening Rubric (v0.9)

This repository applies a weighted, auditable screening layer during OpenAlex ingestion.

## Inputs
- `queries/search_queries.json`: retrieval query groups, now including a methods-oriented human-evaluation lane
- `queries/screening_rules.json`: inclusion/exclusion terms, alias map, priority cues, weights, thresholds

## Outputs per paper
- `screening_score`: weighted score
- `screening_label`: `include` / `review` / `exclude`
- `screening_priority`: `high` / `medium` / `low` manual follow-up priority
- `screening_confidence`: `high` / `medium` / `low` evidence-confidence estimate for triage
- `matched_terms`
- `screening_reasons`
- `screening_features`

## Scoring policy (v1.0)
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
   - bridge-sentence bonus when the abstract contains at least one sentence that jointly mentions an LLM concept and a target affect/counterfactual concept
3. Penalties remain in place for:
   - exclusion hits
   - missing concept groups
   - non-preferred language/type
   - pre-threshold publication year
   - very short abstracts

## Labeling and triage policy
- `include`: score >= include threshold, no exclude hit, no missing concept groups, include-gate constraints satisfied (`min_include_hits`, method/review/high-priority signal, `min_concept_diversity`, `min_abstract_tokens_for_include`, `min_bridge_sentence_hits`, title-or-bridge requirement, `require_llm_concept`), and include-guard passed (`include_margin_min`, `max_penalty_for_include`)
- `review`: score >= review threshold and review-gate constraints satisfied (`min_include_hits_or_priority`, optional method/review signal requirement, `require_llm_concept`)
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
  --report-out results/lit_search_report.json \
  --audit-out results/lit_screening_audit.json
```

`results/lit_search_report.json` now includes:
- overall label distribution
- overall priority distribution
- overall confidence distribution (`high`/`medium`/`low`)
- LLM-concept coverage (`with_llm_concept` vs `without_llm_concept`)
- overall method-signal coverage (`with_method_cues` vs `without_method_cues`)
- overall bridge-signal coverage (`with_bridge_sentence` vs `without_bridge_sentence`)
- include-guard pass/fail counts (overall + per-query)
- per-query label/priority/method/bridge/confidence counts
- top high-priority titles for manual screening

`results/lit_screening_audit.json` adds manual-QC aids:
- borderline `include` and `review` candidates near thresholds
- high-score excludes that still miss LLM concept evidence
- compact reasons for fast adjudication during title/abstract screening

## Why this helps
- Better recall on lexical variants without giving up reproducibility
- Separates relevance from follow-up priority, which is useful during title/abstract screening
- Surfaces methods-heavy papers that can inform benchmark design and human-comparison protocol
- Keeps the screening decision inspectable in JSONL output
