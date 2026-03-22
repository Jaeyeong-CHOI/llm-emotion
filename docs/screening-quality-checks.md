# Screening Quality Checks

## Purpose
`scripts/check_screening_quality.py` reads the latest literature screening report, audit bundle, and manual QC CSV, then emits a compact gate-check report for reproducible reviewer handoff.

## Inputs
- `results/lit_search_report.json`
- `results/lit_screening_audit.json`
- `results/manual_qc_queue.csv`

## Outputs
- `results/screening_quality_report.json`
- `results/screening_quality_report.md`

## Command
```bash
python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report.json \
  --out-md results/screening_quality_report.md \
  --run-label screening_qc_v53 --min-balanced-min-per-label 2 --min-screening-reason-diversity 6 --max-top-screening-reason-share 0.65 \
  --min-screening-reason-entropy 0.55 --min-manual-qc-query-entropy 0.50 --min-manual-qc-risk-reason-entropy 0.45 \
  --min-manual-qc-source-groups 3 --min-include-bridge-signal-share 0.20 --min-review-bridge-signal-share 0.0 --min-review-bridge-traceability-share 0.0 --min-manual-qc-bridge-signal-share 0.20 --min-manual-qc-review-source-groups 2 \
  --max-manual-qc-review-group-dominance 0.70 --max-manual-qc-single-query-share 0.45 \
  --max-manual-qc-unknown-query-share 0.20 --max-empty-screening-reason-share 0.10
```

## Default gates
- `deduped_records >= 200`
- `manual_qc_rows >= 20`
- `single_source_share <= 0.95`
- `low_confidence_share <= 0.90`
- `zero_hit_terms <= 6`
- `gate_failures_near_threshold <= 180`
- `balanced_label_bins >= 2`
- `balanced_confidence_bins >= 3`
- `balanced_group_bins >= 3`
- `balanced_label_dominance <= 0.80`
- `balanced_include_rows >= 2`
- `query_drift_candidate_count <= 30`
- `risk_reason_diversity >= 5`
- `top_risk_reason_share <= 0.55`
- `screening_reason_diversity >= 6`
- `top_screening_reason_share <= 0.65`
- `screening_reason_entropy >= 0.55`
- `manual_qc_query_entropy >= 0.50`
- `manual_qc_risk_reason_entropy >= 0.45`
- `review_to_include_ratio <= 5.0`
- `include_bridge_signal_share >= 0.0` (필요 시 더 높은 floor로 강화)
- `review_bridge_signal_share >= 0.0` (review 근거문장 bridge가 충분한 배치에서는 0.2+ 권장)
- `manual_qc_high_risk_share <= 0.85`
- `manual_qc_source_group_diversity >= 3`
- `manual_qc_bridge_signal_share >= 0.20`
- `manual_qc_review_source_group_diversity >= 2`
- `manual_qc_review_group_dominance <= 0.70`
- `manual_qc_single_query_share <= 0.45`
- `manual_qc_unknown_query_share <= 0.20`
- `empty_screening_reason_share <= 0.10`

## Interpretation
- `status=pass`: all gates passed
- `status=review`: at least one gate failed; review the `hotspots` section before changing queries or thresholds

## Reviewer checkpoints
- Confirm whether `zero_hit_terms` reflect dead aliases or intentionally narrow concepts.
- Inspect `top_qc_risk_reasons` and `top_screening_reasons` before editing screening rules.
- Confirm that the balanced QC queue still contains `include` rows before trusting reviewer disagreement estimates.
- Use `query_drift_term_suggestions` to decide if new aliases belong in `queries/screening_rules.json`.
- `manual_qc_bridge_signal_share`가 낮으면 alias hit만 있고 의미 연결 근거가 약한 review/include 후보가 많다는 뜻이므로 `bridge_sentence_hits`가 남는 규칙과 alias 세트를 함께 재검토합니다.

- `search_openalex.py`가 생성하는 `manual_qc_queue_balanced_min_per_label` 필드를 읽어 라벨별 최소 샘플 목표 충족 여부를 gate로 검사합니다.
