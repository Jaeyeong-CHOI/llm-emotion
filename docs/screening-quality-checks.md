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
  --run-label screening_qc_v59 --min-balanced-min-per-label 2 --min-screening-reason-diversity 6 --max-top-screening-reason-share 0.65 \
  --min-screening-reason-entropy 0.55 --min-manual-qc-query-entropy 0.50 --min-manual-qc-risk-reason-entropy 0.45 \
  --min-manual-qc-source-groups 3 --min-include-bridge-signal-share 0.20 --min-review-bridge-signal-share 0.0 --min-review-bridge-traceability-share 0.0 --min-review-bridge-traceability-given-bridge-share 0.70 --min-review-counterexample-share 0.25 --min-manual-qc-bridge-signal-share 0.20 --min-manual-qc-review-source-groups 2 \
  --max-manual-qc-review-group-dominance 0.70 --max-manual-qc-single-query-share 0.45 \
  --max-manual-qc-dedup-label-conflict-share 0.20 --min-dedup-score-range-alert 1.0 --max-manual-qc-dedup-score-range-alert-share 0.20 \
  --max-manual-qc-duplicate-title-share 0.20 --max-review-weak-evidence-share 0.40 \
  --max-review-bridge-counterexample-traceability-gap-share 0.45 \
  --max-manual-qc-review-evidence-link-decay-share 0.45 \
  --max-manual-qc-review-traceable-known-query-year-js-divergence 0.25 \
  --max-manual-qc-review-traceable-known-query-year-top3-share 0.95 \
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
- `review_bridge_traceability_given_bridge_share >= 0.0` (bridge가 잡힌 review subset에서 traceability가 얼마나 유지되는지 별도로 점검)
- `review_counterexample_share >= 0.0` (review subset에서 반례 근거가 언급되는 비율을 점검; 0.25+ 권장)
- `review_bridge_counterexample_traceability_gap_share <= 0.45` (bridge+counterexample가 잡힌 review 중 traceability가 비는 비율 상한)
- `review_evidence_link_decay_share <= 0.45` (review 근거에서 query/title/include 링크가 빠진 비율 상한)
- `manual_qc_review_traceable_known_query_year_js_divergence <= 0.25` (review traceable known-query 연도 분포가 전체 manual QC 연도 분포에서 과도하게 멀어지는지 점검)
- `manual_qc_review_traceable_known_query_year_top2_share <= 0.90` (연도 분포 상위 2개 연도 과점 여부를 별도로 점검)
- `manual_qc_review_traceable_known_query_year_top3_share <= 0.95` (상위 3개 연도까지 과점되는 패턴을 추가로 차단)
- `manual_qc_review_traceable_known_query_year_tail_share >= 0.10` (older year tail 근거가 최소 비율 이상 유지되는지 점검)
- `manual_qc_high_risk_share <= 0.85`
- `manual_qc_source_group_diversity >= 3`
- `manual_qc_bridge_signal_share >= 0.20`
- `manual_qc_review_source_group_diversity >= 2`
- `manual_qc_review_group_dominance <= 0.70`
- `manual_qc_single_query_share <= 0.45`
- `manual_qc_unknown_query_share <= 0.20`
- `manual_qc_dedup_label_conflict_share <= 0.20`
- `manual_qc_dedup_score_range_alert_share <= 0.20` (`dedup_score_range >= 1.0` rows 기준)
- `manual_qc_duplicate_title_share <= 0.20` (manual QC 큐에서 동일/거의 동일 제목이 반복되는 비율 상한)
- `review_weak_evidence_share <= 0.35` (review 행에서 `include/title/query/bridge` 근거 신호가 1개 이하인 비율 상한)
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
- `manual_qc_dedup_label_conflict_share` 또는 `manual_qc_dedup_score_range_alert_share`가 높으면 dedup 병합 이후 라벨 안정성이 무너진 상태이므로, threshold 자체를 바꾸기 전에 dedup 키·source merge·동일 논문 정규화 규칙을 먼저 재검토합니다.
- `manual_qc_duplicate_title_share`가 높으면 dedup 키가 통과해도 수동 QC 큐에 동일 연구가 반복 노출되고 있을 가능성이 높으므로, title 정규화·DOI 보강·query provenance 병합 규칙을 우선 점검합니다.
- `review_weak_evidence_share`가 높으면 review 판정이 남아 있어도 근거 체인이 `include_hits`나 `query_overlap` 하나에만 의존하는 경우가 많다는 뜻이므로, review_reason traceability를 유지한 채 bridge/title 근거를 같이 복구해야 합니다.

- `search_openalex.py`가 생성하는 `manual_qc_queue_balanced_min_per_label` 필드를 읽어 라벨별 최소 샘플 목표 충족 여부를 gate로 검사합니다.

- `manual_qc_review_traceable_known_query_top3_share <= 0.95` (review traceable known-query 분포가 상위 3개 query에 과도하게 잠기지 않도록 점검)
- `manual_qc_review_traceable_known_query_js_divergence <= 0.35` (review traceable known-query 분포가 전체 manual QC known-query 분포와 과도하게 이탈하지 않도록 점검)
