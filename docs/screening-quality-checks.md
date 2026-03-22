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
  --run-label screening_qc_v35
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
- `query_drift_candidate_count <= 30`
- `risk_reason_diversity >= 5`
- `review_to_include_ratio <= 5.0`
- `manual_qc_high_risk_share <= 0.85`

## Interpretation
- `status=pass`: all gates passed
- `status=review`: at least one gate failed; review the `hotspots` section before changing queries or thresholds

## Reviewer checkpoints
- Confirm whether `zero_hit_terms` reflect dead aliases or intentionally narrow concepts.
- Inspect `top_qc_risk_reasons` before editing screening rules.
- Use `query_drift_term_suggestions` to decide if new aliases belong in `queries/screening_rules.json`.
