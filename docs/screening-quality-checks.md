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
  --run-label screening_qc_v43 --min-balanced-min-per-label 2 --min-screening-reason-diversity 6 --max-top-screening-reason-share 0.65 \
  --min-screening-reason-entropy 0.55 --min-manual-qc-query-entropy 0.50 \
  --min-manual-qc-source-groups 3 --max-manual-qc-single-query-share 0.45 --max-empty-screening-reason-share 0.10
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
- `review_to_include_ratio <= 5.0`
- `manual_qc_high_risk_share <= 0.85`
- `manual_qc_source_group_diversity >= 3`
- `manual_qc_single_query_share <= 0.45`
- `empty_screening_reason_share <= 0.10`

## Interpretation
- `status=pass`: all gates passed
- `status=review`: at least one gate failed; review the `hotspots` section before changing queries or thresholds

## Reviewer checkpoints
- Confirm whether `zero_hit_terms` reflect dead aliases or intentionally narrow concepts.
- Inspect `top_qc_risk_reasons` and `top_screening_reasons` before editing screening rules.
- Confirm that the balanced QC queue still contains `include` rows before trusting reviewer disagreement estimates.
- Use `query_drift_term_suggestions` to decide if new aliases belong in `queries/screening_rules.json`.

- `search_openalex.py`가 생성하는 `manual_qc_queue_balanced_min_per_label` 필드를 읽어 라벨별 최소 샘플 목표 충족 여부를 gate로 검사합니다.
