# Literature Screening Rubric (v1.0)

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
1. Canonical lexical hits use alias expansion, so variants like `LLMs`, `anthropomorphic`, `counterfactual reasoning`, `emotion appraisal`, and `anticipated regret` map back to the same audited concept.
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
  --audit-out results/lit_screening_audit.json \
  --manual-qc-limit 60 \
  --manual-qc-csv results/manual_qc_queue.csv
```

`results/lit_search_report.json` now includes:
- overall label distribution
- overall priority distribution
- overall confidence distribution (`high`/`medium`/`low`)
- LLM-concept coverage (`with_llm_concept` vs `without_llm_concept`)
- alias coverage (`term_hit_counts`, `zero_hit_terms`) to reveal dead lexical branches in the screening rule set
- required concept-group coverage (`required_group_coverage`) to show which audited concept groups are still being missed
- overall method-signal coverage (`with_method_cues` vs `without_method_cues`)
- overall bridge-signal coverage (`with_bridge_sentence` vs `without_bridge_sentence`)
- include-guard pass/fail counts (overall + per-query)
- per-query label/priority/method/bridge/confidence counts
- top high-priority titles for manual screening
- quality-alert slices for adjudication: include-gate failures near include threshold, review-gate failures above review threshold, and LLM-signal rows lacking method/review support
- alias-gap candidates near thresholds where LLM evidence exists but one required concept group is still missing
- balanced QC risk-reason summary (`manual_qc_queue_risk_reason_summary`) for reviewer calibration
- expanded review/method cues such as `qualitative analysis`, `error analysis`, `systematic review`, and `rubric` for methods-heavy benchmark screening

`results/lit_screening_audit.json` adds manual-QC aids:
- borderline `include` and `review` candidates near thresholds
- high-score excludes that still miss LLM concept evidence
- compact reasons for fast adjudication during title/abstract screening
- same quality-alert slices mirrored in audit output for reviewer workload planning
- same alias-gap candidates and QC risk-reason summary mirrored for reproducible handoff

`--manual-qc-csv results/manual_qc_queue.csv` exports the ranked triage queue in spreadsheet-ready form (`rank`, `risk_score`, `label`, `title`, `openalex_id`, `doi`, `source_query`, reason columns) for reproducible human screening handoff.

## Quality gate checkpoint
After generating the screening artifacts, run:

```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v58 \
  --min-review-bridge-counterexample-coupled-share 0.18 \
  --min-review-bridge-counterexample-traceable-share 0.12
```

This checkpoint freezes:
- threshold pass/fail status for deduped volume, manual-QC coverage, low-confidence share, zero-hit alias count, and near-threshold gate failures
- dedup instability signals in the manual-QC queue (`dedup_label_conflict`, `dedup_score_range`) so merge-induced label drift is visible before thresholds are tuned
- review traceability 결합 신호(`bridge × counterexample`) 커버리지와 추적 가능 결합 비율
- top QC risk reasons and balanced manual-QC distribution by label/confidence
- query-drift term suggestions that should be considered before changing retrieval rules

## Why this helps
- Better recall on lexical variants without giving up reproducibility
- Makes alias/개념군 누락을 직접 계량화해 쿼리·규칙 보강 우선순위를 정할 수 있음
- Separates relevance from follow-up priority, which is useful during title/abstract screening
- Surfaces methods-heavy papers that can inform benchmark design and human-comparison protocol
- Keeps the screening decision inspectable in JSONL output
