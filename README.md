# llm-emotion

> 🇰🇷 **실시간 진행상황 먼저 보기:** [`LIVE_STATUS.md`](./LIVE_STATUS.md)

Research project on whether LLMs show human-like regret and deprivation signals in language behavior.

## Scope
This repository studies behavioral-linguistic similarity, not machine consciousness claims.

## Current iteration highlights
- Literature screening quality gate에 **unknown-year top4 absolute share 가드**(`--max-manual-qc-review-traceable-known-query-unknown-year-top4-query-share`)를 추가해, top1~top3가 통과해도 top4 누적 과점이 남는 케이스를 fail-fast로 차단합니다.
- Prompt bank expanded to `v10.4` with **unknown-year group tail ratio backstop / countervoice query-group tail ladder / runner timeout topology tripwire** 시나리오를 추가했습니다 (`screening_unknown_year_group_tail_ratio_backstop_v104`, `prompt_bank_countervoice_query_group_tail_ladder_v104`, `runner_timeout_stage_topology_tripwire_v104`).
- Experiment runner preflight의 **temperature top6 guardrail 실효성**을 보강해 `--max-planned-sample-temperature-top6-share`, `--max-planned-sample-temperature-top6-over-uniform-ratio` 임계치가 실제 fail-fast 체크와 설정 스냅샷에 모두 반영되도록 고정했습니다.
- Literature screening quality gate에 **unknown-year top4/global top4 ratio 가드**(`--max-manual-qc-review-traceable-known-query-unknown-year-top4-over-global-top4-ratio`)를 추가해, top3까지는 통과해도 top4 누적 과점이 남는 케이스를 fail-fast로 차단합니다.
- Prompt bank expanded to `v10.3` with **unknown-year top4 ratio guard / top4 tail counterbalance patch / temperature top6 uniformity tripwire** 시나리오와 신규 페르소나(`unknown_year_top4_ratio_triager_v103`, `top4_tail_counterbalance_architect_v103`, `temperature_top6_uniformity_guard_v103`)를 추가했습니다.
- Experiment runner preflight에 **temperature top6 share + top6-over-uniform guardrail** (`--max-planned-sample-temperature-top6-share`, `--max-planned-sample-temperature-top6-over-uniform-ratio`)을 추가해, top5는 통과해도 top6 누적 집중이 높은 배치를 사전에 차단합니다.
- Literature screening quality gate에 **unknown-year top3/global top3 ratio 가드**(`--max-manual-qc-review-traceable-known-query-unknown-year-top3-over-global-top3-ratio`)를 추가해, top1/top2가 통과해도 top3 누적 과점이 남는 케이스를 fail-fast로 차단합니다.
- Prompt bank expanded to `v10.2` with **unknown-year top3 ratio guard / top3 counterbalance mesh / temperature top5 uniformity tripwire** 시나리오와 신규 페르소나(`unknown_year_top3_ratio_triager_v102`, `top3_counterbalance_mesh_architect_v102`, `temperature_top5_uniformity_guard_v102`)를 추가했습니다.
- Experiment runner preflight에 **temperature top5 share + top5-over-uniform guardrail** (`--max-planned-sample-temperature-top5-share`, `--max-planned-sample-temperature-top5-over-uniform-ratio`)을 추가해, top4는 통과해도 top5 누적 집중이 높은 배치를 사전에 차단합니다.
- Literature screening quality gate에 **unknown-year query-group tail floor/global tail ratio floor 가드**(`--min-manual-qc-review-traceable-known-query-unknown-year-group-tail-share`, `--min-manual-qc-review-traceable-known-query-unknown-year-group-tail-over-global-group-tail-ratio`)를 추가해, top2 과점이 완화돼 보여도 query-group tail이 baseline 대비 수축하는 케이스를 fail-fast로 차단합니다.
- Prompt bank expanded to `v10.1` with **unknown-year group tail ratio floor / tail-ratio mesh patch / temperature floor-gap tripwire** 시나리오와 신규 페르소나(`unknown_year_group_tail_ratio_warden_v101`, `tail_ratio_mesh_curator_v101`, `temperature_floor_gap_auditor_v101`)를 추가했습니다.
- Experiment runner preflight에 **temperature floor-bin share-gap guardrail** (`--max-planned-sample-temperature-floor-bin-share-gap`)을 추가해, floor-bin 개수는 통과했지만 내부 온도 share 편차가 큰 배치를 사전에 차단합니다.
- Literature screening quality gate에 **unknown-year query-group top2/global group top2 ratio guard**(`--max-manual-qc-review-traceable-known-query-unknown-year-group-top2-over-global-group-top2-ratio`)를 추가해, group top1 지표가 통과해도 top2 과점이 남는 케이스를 fail-fast로 차단합니다.
- Prompt bank expanded to `v10.0` with **unknown-year group top2 ratio tripwire / year-group tail rebalance mesh / temperature floor-bin tripwire** 시나리오와 신규 페르소나(`unknown_year_group_top2_ratio_triager_v100`, `year_group_tail_mesh_designer_v100`, `temperature_floor_bin_guardian_v100`)를 추가했습니다.
- Experiment runner preflight에 **temperature floor-bin guardrail** (`--planned-sample-temperature-floor-share`, `--min-planned-sample-temperature-floor-bins`)을 추가해, min-share 단일 통과만으로는 놓치던 온도축 hollowing을 사전에 차단합니다.
- Literature screening quality gate에 **unknown-year top2/global top2 ratio guard**(`--max-manual-qc-review-traceable-known-query-unknown-year-top2-over-global-top2-ratio`)를 추가해, unknown-year top2 share가 절대 임계치는 통과해도 global baseline 대비 상대 과열되는 분포를 fail-fast로 차단합니다.
- Prompt bank expanded to `v9.9` with **unknown-year top2 ratio tripwire / countervoice mesh 확장 / temperature min-share floor** 시나리오와 신규 페르소나(`unknown_year_top2_ratio_auditor_v99`, `countervoice_mesh_curator_v99`, `temperature_min_share_guardian_v99`)를 추가했습니다.
- Experiment runner preflight에 **planned-sample temperature min-share floor guardrail** (`--min-planned-sample-temperature-min-share`)을 추가해, top-k/entropy 지표가 통과해도 특정 온도 버킷이 사실상 비는 배치를 사전에 차단합니다.
- Literature screening quality gate에 **unknown-year query-group top1/global group top1 ratio guard**(`--max-manual-qc-review-traceable-known-query-unknown-year-group-top1-over-global-group-top1-ratio`)를 추가해, unknown-year group top1 share가 단독으로는 통과해도 global baseline 대비 과열된 쏠림을 fail-fast로 차단합니다.
- Prompt bank expanded to `v9.8` with **unknown-year group baseline ratio tripwire / query-group bridge matrix expansion / temperature top2 uniform-ratio guard** 시나리오와 신규 페르소나(`unknown_year_group_ratio_auditor_v98`, `bridge_matrix_expander_v98`, `temperature_top2_uniform_guardian_v98`)를 추가했습니다.
- Experiment runner preflight에 **planned-sample temperature top2-over-uniform guardrail** (`--max-planned-sample-temperature-top2-over-uniform-ratio`)을 추가해, top2 share가 임계치 아래여도 균등 baseline 대비 과열된 온도 집중을 사전에 차단합니다.
- Literature screening quality gate에 **unknown-year query-group drift guard**(`--max-manual-qc-review-traceable-known-query-unknown-year-group-top1-share`, `--max-manual-qc-review-traceable-known-query-unknown-year-vs-global-known-query-group-js-divergence`)를 추가해, raw query 분산이 통과해도 query-group 기준으로 재쏠림이 남는 케이스를 fail-fast로 차단합니다.
- Prompt bank expanded to `v9.7` with **unknown-year query-group drift brake / persona fairness lattice / temperature tail-share tripwire** 시나리오와 신규 페르소나(`unknown_year_group_drift_auditor_v97`, `persona_fairness_lattice_curator_v97`, `temperature_tail_share_governor_v97`)를 추가했습니다.
- Experiment runner preflight에 **planned-sample temperature tail-share guardrail** (`--min-planned-sample-temperature-tail-share`)을 추가해, top-k share와 HHI가 통과해도 상위 2개 온도 바깥 tail budget이 너무 얇은 배치를 사전에 차단합니다.
- Literature screening quality gate에 **unknown-year top1/global top1 비율 가드**(`--max-manual-qc-review-traceable-known-query-unknown-year-top1-over-global-top1-ratio`)를 추가해, JS divergence가 통과해도 unknown-year 복구가 단일 query top1로 과수렴하는 패턴을 fail-fast로 차단합니다.
- Prompt bank expanded to `v9.6` with **query-group global-baseline tail guard / countervoice cross-band mesh patch / temperature HHI tripwire** 시나리오와 신규 페르소나(`query_group_baseline_guardian_v96`, `crossband_mesh_curator_v96`, `temperature_hhi_governor_v96`)를 추가했습니다.
- Experiment runner preflight에 **planned-sample temperature HHI guardrail** (`--max-planned-sample-temperature-hhi`)을 추가해, top-k share가 통과해도 온도축 concentration이 높을 때 실행을 사전에 차단합니다.
- Literature screening quality gate에 **unknown-year vs global known-query JS divergence 가드**(`--max-manual-qc-review-traceable-known-query-unknown-year-vs-global-known-query-js-divergence`)를 추가해, unknown-year 복구가 특정 query 군집으로만 치우치는 드리프트를 fail-fast로 차단합니다.
- Prompt bank expanded to `v9.5` with **query-group tail floor tripwire / countervoice query-group intensity-band patch / timeout-over-selection ratio tripwire** 시나리오와 신규 페르소나(`query_group_tail_floor_guard_v95`, `countervoice_intensity_band_curator_v95`, `timeout_ratio_governor_v95`)를 추가했습니다.
- Experiment runner preflight에 **planned-sample temperature top4 share/over-uniform guardrail** (`--max-planned-sample-temperature-top4-share`, `--max-planned-sample-temperature-top4-over-uniform-ratio`)를 추가해, top3가 통과해도 상위 4개 온도에 예산이 과집중되는 배치를 사전에 차단합니다.
- Literature screening quality gate에 **unknown-year known-query top3 query concentration 가드**(`--max-manual-qc-review-traceable-known-query-unknown-year-top3-query-share`)를 추가해, unknown-year 복구 이후에도 소수 query로 재쏠림되는 케이스를 fail-fast로 차단합니다.
- Prompt bank expanded to `v9.3` with **unknown-year query gap tabletop / countervoice tail-temperature mesh / top3 uniformity repair** scenarios plus new personas (`unknown_year_query_balance_operator_v93`, `temperature_top3_uniformity_guard_v93`).
- Experiment runner preflight에 **planned-sample temperature top3-over-uniform ratio guardrail** (`--max-planned-sample-temperature-top3-over-uniform-ratio`)를 추가해, top3 share가 통과해도 균등 분포 대비 과열된 온도 쏠림을 사전에 차단합니다.
- Literature screening quality gate에 **unknown-year vs known-year query JS divergence 가드**(`--max-manual-qc-review-traceable-known-query-unknown-vs-known-year-query-js-divergence`)를 추가해, year 메타데이터 결측 구간이 known-year 분포와 과도하게 분리되는 케이스를 fail-fast로 차단합니다.
- Prompt bank expanded to `v9.2` with **unknown-year/known-year query alignment patch / countervoice year-query stagger / temperature top3 pressure tripwire** scenarios plus new personas (`unknown_year_alignment_triager_v92`, `countervoice_stagger_mesh_curator_v92`, `temperature_top3_pressure_auditor_v92`).
- Experiment runner preflight에 **planned-sample temperature top3 share guardrail** (`--max-planned-sample-temperature-top3-share`)를 추가해, top1/top2가 통과해도 상위 3개 온도에 예산이 잠기는 배치를 사전에 차단합니다.
- Literature screening quality gate에 **review traceable known-query year-tail query coverage 가드**(`--min-manual-qc-review-traceable-known-query-year-tail-query-coverage`)를 추가해, year-tail 근거가 소수 query에만 몰리는 케이스를 fail-fast로 차단합니다.
- Prompt bank expanded to `v9.1` with **unknown-year top2 concentration relief / multiaxis countervoice mesh / temperature uniform pressure guard** scenarios plus new personas (`unknown_year_top2_dispersion_coach_v91`, `multiaxis_countervoice_mesh_curator_v91`, `temperature_uniformity_tripwire_auditor_v91`).
- Literature screening quality gate에 **review traceable known-query unknown-year query concentration/entropy 가드**(`--max-manual-qc-review-traceable-known-query-unknown-year-top1-query-share`, `--max-manual-qc-review-traceable-known-query-unknown-year-top2-query-share`, `--min-manual-qc-review-traceable-known-query-unknown-year-query-coverage`, `--min-manual-qc-review-traceable-known-query-unknown-year-query-entropy`)를 추가해, year 메타데이터가 비어 있는 구간이 소수 query에 잠기거나 분산이 붕괴되는 케이스를 fail-fast로 차단합니다.
- Experiment runner preflight에 **temperature entropy + planned-sample top1/top2 parity + uniform pressure guardrail** (`--require-min-temperature-entropy`, `--min-planned-sample-temperature-entropy`, `--max-planned-sample-temperature-top1-share`, `--max-planned-sample-temperature-top2-share`, `--max-planned-sample-temperature-share-gap`, `--max-planned-sample-temperature-over-uniform-ratio`)를 추가해, temperature count/span이 통과해도 온도축 분산이 무너진 배치를 사전에 차단합니다.
- Literature screening quality gate에 **review traceable known-query unknown-year 가드**(`--max-manual-qc-review-traceable-known-query-unknown-year-share`, `--min-manual-qc-review-traceable-known-query-known-year-count`)를 추가해, query는 추적되지만 year 메타데이터가 비어 있는 review 큐를 fail-fast로 차단합니다.
- Prompt bank expanded to `v8.8` with **unknown-year traceability backfill / persona-style entropy rebalance / selected-tag entropy tripwire** scenarios plus new personas (`unknown_year_traceability_curator_v88`, `selected_entropy_tripwire_operator_v88`).
- Experiment runner에 **scenario-tag / persona-style-tag entropy guardrail**을 추가해 run 단위(`--require-min-scenario-tag-entropy`, `--require-min-persona-style-tag-entropy`)와 selected 배치 단위(`--require-min-selected-scenario-tag-entropy`, `--require-min-selected-persona-style-tag-entropy`) 분포 편향을 사전 차단할 수 있습니다.
- Literature screening quality gate에 **review traceable known-query year-tail 절대량 가드**(`--min-manual-qc-review-traceable-known-query-year-tail-count`)를 추가해, share/entropy가 통과해도 tail 근거 행 수가 너무 적은 케이스를 fail-fast로 차단합니다.
- Prompt bank expanded to `v8.7` with **year-query coupling tripwire / countervoice style-tag tail patch / persona-style entropy gate postmortem** scenarios plus new personas (`year_query_coupling_recovery_operator_v87`, `persona_entropy_gatekeeper_v87`).
- Experiment runner/dataset generator now support **OR 필터** (`scenario_tags_any`)와 **persona style-tag 필터** (`persona_style_tags_any`)를 run config에서 직접 사용할 수 있어, 프롬프트 뱅크 확장 실험의 타깃 샘플링 재현성이 개선되었습니다.
- Literature screening quality gate에 **review traceable known-query year entropy/coverage 가드**(`--min-manual-qc-review-traceable-known-query-year-entropy`, `--min-manual-qc-review-traceable-known-query-year-coverage`)를 추가해, year top2/tail 비율이 통과하더라도 실질적인 연도 분산이 무너진 케이스를 fail-fast로 차단합니다.
- Prompt bank expanded to `v8.4` with **year-tail counterexample rebalance / unknown-query bridge rescue / countervoice year-grid patch / selected-temperature floor audit** scenarios plus new personas (`review_year_tail_recovery_curator_v84`, `unknown_query_traceability_operator_v84`, `countervoice_year_grid_curator_v84`, `selected_temperature_floor_guard_v84`).
- Experiment runner now supports **aggregate selected-temperature floor guardrail** (`--require-min-selected-temperatures`) so batch-level preflight에서 scenario/persona coverage는 충분해도 temperature 축이 과도하게 좁은 실행을 사전에 차단할 수 있습니다.
- Literature screening quality gate에 **review known-query source-group tail-share floor 가드**(`--min-manual-qc-review-traceable-known-query-group-tail-share`)를 추가해, source-group 상위 집중(top2) 완화 없이 겉보기 traceability만 상승하는 케이스를 fail-fast로 차단합니다.
- Prompt bank expanded to `v8.0` with **source-group tail recovery drill / batch metadata floor audit** scenarios plus new personas (`group_tail_coverage_steward_v80`, `batch_metadata_floor_guard_v80`).
- Experiment runner now supports **batch-level aggregate metadata floor guardrails** (`--require-min-selected-scenario-domains`, `--require-min-selected-scenario-emotion-axes`, `--require-min-selected-scenario-difficulties`) to fail-fast when selected run-id 묶음이 전체 domain/axis/difficulty 커버리지를 충분히 확보하지 못할 때 실행을 중단합니다.
- Literature screening quality gate에 **review known-query source-group JS divergence 가드**(`--max-manual-qc-review-traceable-known-query-group-js-divergence`)를 추가해, review traceable 분포가 전체 manual QC source-group 분포에서 과도하게 벗어나는 경우를 fail-fast로 차단합니다.
- Prompt bank expanded to `v7.9` with **tail-query recovery tabletop / timeout budget rebalance postmortem** scenarios plus new personas (`query_tail_recovery_planner_v79`, `timeout_budget_foreman_v79`).
- Experiment runner now supports **timeout failure pressure guardrail** (`--max-timeout-failure-over-selection-ratio-per-run-id`) in addition to timeout share ceiling (`--max-timeout-failure-share-per-run-id`) to catch run-id-level timeout concentration against selected-cell share.
- Literature screening quality gate에 **duplicate-title / weak-evidence 가드**(`--max-manual-qc-duplicate-title-share`, `--max-review-weak-evidence-share`)를 추가해, manual QC 큐의 중복 잔존과 review 근거 희석을 기존 dedup/risk 지표와 분리해서 감시할 수 있습니다.
- Prompt bank expanded to `v7.7` with **tail-query / countervoice intensity-grid / metadata-tripwire prompts** (`screening_query_tail_cluster_leak`, `prompt_bank_countervoice_domain_intensity_grid`, `runner_resume_metadata_axis_tripwire`) plus new personas (`tail_query_recall_engineer`, `metadata_axis_safety_operator`).
- Experiment runner now supports **scenario domain/emotion entropy guardrails** (`--require-min-scenario-domain-entropy`, `--require-min-scenario-emotion-axis-entropy`) in addition to label entropy; experiment matrix now includes `screening_prompt_runner_metadata_entropy_v77`.
- Literature screening quality gate에 **review known-query group top2 과점 가드**(`--max-manual-qc-review-traceable-known-query-group-top2-share`)를 추가해, source group 분포가 1~2개 그룹에 몰리면서 query 다양성 복구가 지연되는 패턴을 fail-fast로 차단할 수 있습니다.
- Literature screening quality gate에 **review known-query 하단 분포 가드**(`--min-manual-qc-review-traceable-known-query-bottom2-share`)를 추가해 top query 쏠림만 보는 것이 아니라 tail 복구 여지를 수치로 점검할 수 있습니다.
- Literature screening quality gate now supports **review bridge-query coupling gates** (`--min-review-bridge-traceable-known-query-share`, `--max-review-bridge-traceable-unknown-query-share`) to catch cases where bridge evidence exists but query provenance remains weak.
- Literature screening quality gate expanded with **review known-query concentration checks** (`--min-manual-qc-review-traceable-known-query-entropy`, `--max-manual-qc-review-traceable-known-query-top-share`) to catch review queues that look traceable but still overfit to a narrow query slice.
- Prompt bank expanded to `v7.5` with **review bridge unknown-query 복구 / countervoice 회전 공백 패치 / label entropy tripwire** additions (`screening_review_bridge_unknown_query_repair`, `prompt_bank_countervoice_rotation_gap_patch`, `runner_scenario_label_entropy_tripwire`) plus new personas (`review_query_traceability_triager`, `countervoice_rotation_architect`, `label_entropy_tripwire_operator`). Experiment matrix now includes `screening_prompt_runner_entropy_bridge_v75`.
- Prompt bank expanded to `v7.4` with **tail-query rescue / countervoice gap backfill / stage quota recovery** additions (`screening_tail_query_rescue_drill`, `prompt_bank_countervoice_gap_backfill_sprint`, `runner_stage_budget_quota_recovery`) plus new personas (`tail_query_balance_warden`, `countervoice_gap_repairer`, `stage_quota_rebalancer`). Experiment matrix now includes `screening_prompt_runner_tail_quota_v74`.
- Experiment runner now supports **scenario label entropy floor guardrail** (`--require-min-scenario-label-entropy`) in addition to label dominance guardrail (`--require-max-scenario-label-dominance`), so preflight can fail-fast when label count는 충분해도 분포가 실질적으로 편중된 배치가 선택됩니다.
- Experiment runner continues to support **live run-id attempt share tripwires** (`--max-live-generation-attempt-share-per-run-id`, `--max-live-analysis-attempt-share-per-run-id`, `--max-live-combined-attempt-share-per-run-id`) plus post-run budget pressure reports.
- Screening quality gate continues to track **review evidence-link decay share** (`--max-manual-qc-review-evidence-link-decay-share`) to fail fast when review 근거의 문장-링크 연결이 약화됩니다.

## Repository structure
- `docs/`: review protocol, screening rubric, experiment plan, ops notes, reproducibility playbooks (`docs/reproducibility_v104.md`)
- `queries/`: retrieval queries and screening rules
- `prompts/`: Korean prompt bank and scenario source material
- `scripts/`: literature sync, dataset generation, analysis, experiment runner
- `ops/`: experiment matrix and state tracking
- `refs/`: bibliography and collected metadata
- `results/`: experiment outputs

## Quickstart
```bash
python3 scripts/search_openalex.py --config queries/search_queries.json --screening-rules queries/screening_rules.json --out refs/openalex_results.jsonl --report-out results/lit_search_report.json --audit-out results/lit_screening_audit.json --manual-qc-limit 60 --manual-qc-per-label 12 --manual-qc-min-per-label 2 --manual-qc-per-confidence 10 --manual-qc-per-group 10 --manual-qc-csv results/manual_qc_queue.csv
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v82 --min-balanced-review-rows 6 --min-manual-qc-include-rows 2 --min-manual-qc-review-share 0.25 --max-manual-qc-review-share 0.85 --max-manual-qc-label-dominance 0.75 --min-screening-reason-diversity 6 --max-top-screening-reason-share 0.65 --min-screening-reason-entropy 0.55 --min-screening-reason-traceability-share 0.65 --min-include-reason-traceability-share 0.75 --min-review-reason-traceability-share 0.75 --min-include-bridge-signal-share 0.20 --min-review-bridge-signal-share 0.0 --min-review-bridge-traceability-share 0.0 --min-review-bridge-traceability-given-bridge-share 0.70 --min-review-counterexample-share 0.25 --min-manual-qc-review-counterexample-traceability-share 0.55 --min-review-bridge-counterexample-coupled-share 0.18 --min-review-bridge-counterexample-traceable-share 0.12 --min-review-bridge-counterexample-traceability-given-coupled-share 0.55 --min-manual-qc-bridge-signal-share 0.20 --min-manual-qc-query-entropy 0.50 --min-manual-qc-review-query-entropy 0.45 --min-manual-qc-review-traceable-known-query-share 0.55 --max-manual-qc-review-traceable-unknown-query-share 0.15 --min-manual-qc-review-query-traceability-share 0.75 --min-manual-qc-review-traceable-known-query-entropy 0.45 --max-manual-qc-review-traceable-known-query-top-share 0.70 --min-manual-qc-review-traceable-known-query-group-entropy 0.45 --max-manual-qc-review-traceable-known-query-year-js-divergence 0.25 --min-manual-qc-risk-reason-entropy 0.45 --min-manual-qc-review-reason-entropy 0.35 --min-manual-qc-source-groups 3 --min-manual-qc-review-source-groups 2 --max-manual-qc-review-group-dominance 0.70 --max-manual-qc-single-query-share 0.45 --max-manual-qc-unknown-query-share 0.20 --max-manual-qc-dedup-label-conflict-share 0.20 --min-dedup-score-range-alert 1.0 --max-manual-qc-dedup-score-range-alert-share 0.20 --max-manual-qc-duplicate-title-share 0.20 --max-review-weak-evidence-share 0.40 --max-empty-screening-reason-share 0.10 --max-review-counterexample-without-bridge-share 0.35
python3 scripts/build_evidence_table.py --in refs/openalex_results.jsonl --out docs/evidence-table.md

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v82_plan --plan-only --include-run-id screening_prompt_runner_entropy_tail_v81 --include-run-id screening_prompt_runner_year_budget_v82 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v82.json --selection-csv results/selection_report_smoke_v82.csv --preflight-markdown --require-min-scenarios 3 --require-min-personas 4 --require-min-temperature-count 3 --require-min-condition-cells 27 --require-min-total-samples 1600 --require-min-planned-samples-per-run 800 --require-min-unique-scenario-labels 2 --require-min-unique-scenario-tags 10 --require-min-unique-scenario-domains 3 --require-min-unique-scenario-emotion-axes 3 --require-min-unique-scenario-difficulties 1 --require-min-unique-persona-style-tags 12 --require-prompt-bank-version v8.2 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --require-freeze-artifact results/screening_quality_report.json --max-planned-sample-share-per-run-id 0.60 --max-planned-sample-share-gap-per-run-id 0.20 --manifest-note "preflight v82 year-drift + planned-sample-share guard"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v82_exec --include-run-id screening_prompt_runner_year_budget_v82 --fail-on-missing-run-id --manifest-markdown --max-runs 1 --max-retries 1 --max-generation-retries 1 --max-analysis-retries 0 --retry-backoff-seconds 1 --generation-timeout-seconds 120 --analysis-timeout-seconds 90 --max-run-seconds 180 --continue-on-error --max-failed-cells 1 --max-failure-rate 0.5 --max-failure-streak 1 --require-min-successful-cells 1 --require-min-success-rate 0.4 --require-min-run-id-success-rate 0.4 --require-min-generation-success-rate 0.8 --require-min-analysis-success-rate 0.8 --execution-log-jsonl results/experiments/smoke_v82_exec/command_log.jsonl --budget-report-json results/experiments/smoke_v82_exec/budget_report.json --budget-report-md results/experiments/smoke_v82_exec/budget_report.md --require-min-total-samples 400
```

## Prompt-bank filtering
`scripts/generate_dataset.py` supports reproducible subset selection:

```bash
python3 scripts/generate_dataset.py \
  --out /tmp/mock.jsonl \
  --prompt-bank prompts/prompt_bank_ko.json \
  --scenario-domains research_ops \
  --scenario-emotion-axes regret \
  --scenario-difficulties hard \
  --persona-ids regretful,self_compassionate
```

## Experiment reproducibility
- Run definitions live in `ops/experiment_matrix.json`

### v9.6 스모크 프리플라이트 (2026-03-23)

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v96 --max-manual-qc-review-traceable-known-query-unknown-year-top1-query-share 0.65 --max-manual-qc-review-traceable-known-query-unknown-year-top2-query-share 0.90 --max-manual-qc-review-traceable-known-query-unknown-year-top3-query-share 0.97 --min-manual-qc-review-traceable-known-query-unknown-year-query-coverage 3 --min-manual-qc-review-traceable-known-query-unknown-year-query-entropy 0.40 --max-manual-qc-review-traceable-known-query-unknown-year-vs-global-known-query-js-divergence 0.30 --max-manual-qc-review-traceable-known-query-unknown-year-top1-over-global-top1-ratio 1.25

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v96_plan --plan-only --include-run-id screening_prompt_runner_query_group_hhi_v96 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v96.json --selection-csv results/selection_report_smoke_v96.csv --preflight-markdown --require-prompt-bank-version v9.6 --min-planned-sample-temperature-entropy 0.90 --max-planned-sample-temperature-top3-share 0.90 --max-planned-sample-temperature-top4-share 0.98 --max-planned-sample-temperature-top4-over-uniform-ratio 1.25 --max-planned-sample-temperature-hhi 0.30 --manifest-note "preflight v96 query-group baseline + crossband mesh + temperature HHI guard"
```

### v9.5 스모크 프리플라이트 (2026-03-23)

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v95 --max-manual-qc-review-traceable-known-query-unknown-year-top1-query-share 0.65 --max-manual-qc-review-traceable-known-query-unknown-year-top2-query-share 0.90 --max-manual-qc-review-traceable-known-query-unknown-year-top3-query-share 0.97 --min-manual-qc-review-traceable-known-query-unknown-year-query-coverage 3 --min-manual-qc-review-traceable-known-query-unknown-year-query-entropy 0.40 --max-manual-qc-review-traceable-known-query-unknown-year-vs-global-known-query-js-divergence 0.30

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v95_plan --plan-only --include-run-id screening_prompt_runner_query_group_timeout_ratio_v95 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v95.json --selection-csv results/selection_report_smoke_v95.csv --preflight-markdown --require-prompt-bank-version v9.5 --min-planned-sample-temperature-entropy 0.90 --max-planned-sample-temperature-top3-share 0.95 --max-planned-sample-temperature-top4-share 0.98 --max-planned-sample-temperature-top4-over-uniform-ratio 1.25 --manifest-note "preflight v95 query-group tail + timeout-ratio + temperature top4 guard"
```

### v9.3 스모크 프리플라이트 (2026-03-23)

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v93 --max-manual-qc-review-traceable-known-query-unknown-year-top1-query-share 0.65 --max-manual-qc-review-traceable-known-query-unknown-year-top2-query-share 0.90 --max-manual-qc-review-traceable-known-query-unknown-year-top3-query-share 0.97 --min-manual-qc-review-traceable-known-query-unknown-year-query-coverage 3 --min-manual-qc-review-traceable-known-query-unknown-year-query-entropy 0.40

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v93_plan --plan-only --include-run-id screening_prompt_runner_unknown_year_top3_uniform_v93 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v93.json --selection-csv results/selection_report_smoke_v93.csv --preflight-markdown --require-prompt-bank-version v9.3 --min-planned-sample-temperature-entropy 0.90 --max-planned-sample-temperature-top3-share 0.95 --max-planned-sample-temperature-top3-over-uniform-ratio 1.20 --manifest-note "preflight v93 unknown-year top3 + top3-uniform guard"
```

### v9.2 스모크 프리플라이트 (2026-03-23)

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v92 --max-manual-qc-review-traceable-known-query-year-top1-share 0.70 --max-manual-qc-review-traceable-known-query-year-top2-share 0.90 --min-manual-qc-review-traceable-known-query-year-tail-share 0.10 --min-manual-qc-review-traceable-known-query-year-tail-count 3 --max-manual-qc-review-traceable-known-query-unknown-vs-known-year-query-js-divergence 0.30

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v92_plan --plan-only --include-run-id screening_prompt_runner_unknown_year_alignment_top3_v92 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v92.json --selection-csv results/selection_report_smoke_v92.csv --preflight-markdown --require-prompt-bank-version v9.2 --min-planned-sample-temperature-entropy 0.90 --max-planned-sample-temperature-top1-share 0.45 --max-planned-sample-temperature-top2-share 0.80 --max-planned-sample-temperature-top3-share 0.95 --manifest-note "preflight v92 unknown-known query alignment + temperature top3 guard"
```

### v8.9 스모크 프리플라이트 (2026-03-23)

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v89 --max-manual-qc-review-traceable-known-query-year-top1-share 0.70 --max-manual-qc-review-traceable-known-query-year-top2-share 0.90 --min-manual-qc-review-traceable-known-query-year-tail-share 0.10 --min-manual-qc-review-traceable-known-query-year-tail-count 3 --min-manual-qc-review-traceable-known-query-year-entropy 0.45 --min-manual-qc-review-traceable-known-query-year-coverage 3 --max-manual-qc-review-traceable-known-query-unknown-year-share 0.20 --min-manual-qc-review-traceable-known-query-known-year-count 3

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v89_plan --plan-only --include-run-id screening_prompt_runner_year_query_persona_entropy_v87 --include-run-id screening_prompt_runner_selected_entropy_v88 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v89.json --selection-csv results/selection_report_smoke_v89.csv --preflight-markdown --require-prompt-bank-version v8.9 --require-min-selected-temperatures 3 --require-min-selected-temperature-span 0.7 --require-min-selected-scenario-tag-entropy 0.70 --require-min-selected-persona-style-tag-entropy 0.70 --require-min-scenario-tag-entropy 0.65 --require-min-persona-style-tag-entropy 0.65 --max-planned-sample-share-per-run-id 0.60 --max-planned-sample-share-gap-per-run-id 0.25 --manifest-note "preflight v88 unknown-year + selected entropy guard"
```

### v9.2 스모크 프리플라이트 (2026-03-23)

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v92 --max-manual-qc-review-traceable-known-query-year-top1-share 0.70 --max-manual-qc-review-traceable-known-query-year-top2-share 0.90 --min-manual-qc-review-traceable-known-query-year-tail-share 0.10 --min-manual-qc-review-traceable-known-query-year-tail-count 3 --max-manual-qc-review-traceable-known-query-unknown-vs-known-year-query-js-divergence 0.30

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v92_plan --plan-only --include-run-id screening_prompt_runner_unknown_year_alignment_top3_v92 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v92.json --selection-csv results/selection_report_smoke_v92.csv --preflight-markdown --require-prompt-bank-version v9.2 --min-planned-sample-temperature-entropy 0.90 --max-planned-sample-temperature-top1-share 0.45 --max-planned-sample-temperature-top2-share 0.80 --max-planned-sample-temperature-top3-share 0.95 --max-planned-sample-share-per-run-id 0.60 --manifest-note "preflight v92 unknown-known query alignment + temperature top3 guard"
```

### v8.9 스모크 프리플라이트 (2026-03-23)

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v89 --max-manual-qc-review-traceable-known-query-year-top1-share 0.70 --max-manual-qc-review-traceable-known-query-year-top2-share 0.90 --min-manual-qc-review-traceable-known-query-year-tail-share 0.10 --min-manual-qc-review-traceable-known-query-year-tail-count 3 --min-manual-qc-review-traceable-known-query-year-tail-query-coverage 2 --min-manual-qc-review-traceable-known-query-year-entropy 0.45 --min-manual-qc-review-traceable-known-query-year-coverage 3

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v89_plan --plan-only --include-run-id screening_prompt_runner_year_query_persona_entropy_v87 --include-run-id screening_prompt_runner_temperature_parity_v88 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v89.json --selection-csv results/selection_report_smoke_v89.csv --preflight-markdown --require-prompt-bank-version v8.9 --require-min-selected-temperatures 3 --require-min-selected-temperature-span 0.7 --min-planned-sample-temperature-entropy 0.90 --max-planned-sample-temperature-top1-share 0.45 --max-planned-sample-share-per-run-id 0.60 --max-planned-sample-share-gap-per-run-id 0.25 --manifest-note "preflight v89 year-tail-query-coverage + temperature parity guard"
```

### v8.7 스모크 프리플라이트 (2026-03-23)

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v87 --max-manual-qc-review-traceable-known-query-year-top1-share 0.70 --max-manual-qc-review-traceable-known-query-year-top2-share 0.90 --min-manual-qc-review-traceable-known-query-year-tail-share 0.10 --min-manual-qc-review-traceable-known-query-year-tail-count 3 --min-manual-qc-review-traceable-known-query-year-entropy 0.45 --min-manual-qc-review-traceable-known-query-year-coverage 3

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v87_plan --plan-only --include-run-id screening_prompt_runner_entropy_top2_v86 --include-run-id screening_prompt_runner_year_query_persona_entropy_v87 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v87.json --selection-csv results/selection_report_smoke_v87.csv --preflight-markdown --require-prompt-bank-version v8.7 --require-min-selected-temperatures 3 --require-min-selected-temperature-span 0.7 --max-planned-sample-share-per-run-id 0.60 --max-planned-sample-share-gap-per-run-id 0.25 --manifest-note "preflight v87 year-tail-count + persona-style entropy prep"
```

### v8.5 스모크 프리플라이트 (2026-03-23)

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v85 --max-manual-qc-review-traceable-known-query-year-top1-share 0.70 --max-manual-qc-review-traceable-known-query-year-top2-share 0.90 --min-manual-qc-review-traceable-known-query-year-tail-share 0.10 --min-manual-qc-review-traceable-known-query-year-entropy 0.45 --min-manual-qc-review-traceable-known-query-year-coverage 3

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v85_plan --plan-only --include-run-id screening_prompt_runner_year_unknown_temp_v84 --include-run-id screening_prompt_runner_year_query_temp_span_v85 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v85.json --selection-csv results/selection_report_smoke_v85.csv --preflight-markdown --require-prompt-bank-version v8.5 --require-min-selected-temperatures 3 --require-min-selected-temperature-span 0.7 --max-planned-sample-share-per-run-id 0.60 --max-planned-sample-share-gap-per-run-id 0.25 --manifest-note "preflight v85 year-top1 + selected-temperature-span guard"
```

### v8.4 스모크 프리플라이트 (2026-03-23)

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v84 --max-manual-qc-review-traceable-known-query-year-js-divergence 0.25 --max-manual-qc-review-traceable-known-query-year-top2-share 0.90 --min-manual-qc-review-traceable-known-query-year-tail-share 0.10 --min-manual-qc-review-traceable-known-query-year-entropy 0.45 --min-manual-qc-review-traceable-known-query-year-coverage 3

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v84_plan --plan-only --include-run-id screening_prompt_runner_year_tail_pressure_v83 --include-run-id screening_prompt_runner_year_unknown_temp_v84 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v84.json --selection-csv results/selection_report_smoke_v84.csv --preflight-markdown --require-prompt-bank-version v8.4 --require-min-selected-temperatures 3 --max-planned-sample-share-per-run-id 0.60 --max-planned-sample-share-gap-per-run-id 0.25 --manifest-note "preflight v84 year-entropy + unknown-query + temperature-floor guard"
```

### v8.3 스모크 프리플라이트 (2026-03-23)

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v83 --max-manual-qc-review-traceable-known-query-year-js-divergence 0.25 --max-manual-qc-review-traceable-known-query-year-top2-share 0.90 --min-manual-qc-review-traceable-known-query-year-tail-share 0.10

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v83_plan --plan-only --include-run-id screening_prompt_runner_year_budget_v82 --include-run-id screening_prompt_runner_year_tail_pressure_v83 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v83.json --selection-csv results/selection_report_smoke_v83.csv --preflight-markdown --require-prompt-bank-version v8.3 --max-planned-sample-share-per-run-id 0.60 --max-planned-sample-share-gap-per-run-id 0.20 --max-planned-sample-over-selection-ratio-per-run-id 1.20 --manifest-note "preflight v83 year-tail + planned-sample-pressure guard"
```

### v8.2 스모크 프리플라이트 (2026-03-22)

```bash
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --out results/screening_quality_report.json --out-md results/screening_quality_report.md --run-label screening_qc_v82 --max-manual-qc-review-traceable-known-query-year-js-divergence 0.25

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v82_plan --plan-only --include-run-id screening_prompt_runner_entropy_tail_v81 --include-run-id screening_prompt_runner_year_budget_v82 --fail-on-missing-run-id --print-selection --selection-report results/selection_report_smoke_v82.json --selection-csv results/selection_report_smoke_v82.csv --preflight-markdown --require-prompt-bank-version v8.2 --max-planned-sample-share-per-run-id 0.60 --max-planned-sample-share-gap-per-run-id 0.20 --manifest-note "preflight v82 year-budget"
```
- `results/experiments/<label>/manifest.json` records environment and cell status
- `results/experiments/<label>/snapshots/` stores the config and prompt-bank snapshots used for the batch
- `results/experiments/<label>/preflight.json` and `preflight.csv` capture selection/preflight diagnostics for review before or after execution
- `results/experiments/<label>/command_log.jsonl` records each command attempt with timestamps, return code, stdout, and stderr when execution occurs
- `results/experiments/<label>/budget_report.json` and `budget_report.md` summarize selected-cell share, generation/analysis attempt share, attempt-pressure ratio, and failed-cell concentration by run id
- `results/experiments/<label>/budget_violations.json` stores machine-readable threshold violations (rule, threshold, violating run ids) for reproducible audits
- `--require-prompt-bank-version`으로 실행 전 prompt bank 버전 고정, `--require-freeze-artifact`로 필수 근거 파일 존재 여부를 강제해 evidence-freeze 누락을 fail-fast로 차단할 수 있습니다.
- `--scenario-domains`, `--scenario-emotion-axes`, `--scenario-difficulties`로 prompt bank 메타데이터 축을 선택 조건에 넣고, 동일 축이 생성 데이터셋/selection/preflight 산출물에도 함께 기록됩니다.
- `--require-min-selected-scenarios`, `--require-min-selected-personas`, `--require-min-selected-scenario-labels`로 배치 전체의 aggregate coverage floor를 강제해, scenario 수는 많아도 label 축이 편향된 실험 묶음이 통과하지 못하게 할 수 있습니다.
- `--max-planned-sample-share-per-run-id`, `--max-planned-sample-share-gap-per-run-id`로 run-id별 `n × condition_cells × repeats` 예산 편중을 preflight에서 차단해, selected cell 수는 비슷하지만 실제 샘플 예산이 한 run id에 몰리는 배치를 막을 수 있습니다.
- `--run-id-file`로 배치 실행 대상을 파일 기반으로 고정하고, `--max-retries`/`--retry-backoff-seconds`로 부분 실패 복구 정책을 명시적으로 재현할 수 있습니다.
- `--max-selected-cell-share-per-run-id`, `--max-attempt-share-per-run-id`, `--max-attempt-over-selection-ratio`로 특정 run id가 selection 대비 과도한 retry budget을 소비할 때 즉시 중단할 수 있습니다.
