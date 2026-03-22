# llm-emotion

> 🇰🇷 **실시간 진행상황 먼저 보기:** [`LIVE_STATUS.md`](./LIVE_STATUS.md)

Research project on whether LLMs show human-like regret and deprivation signals in language behavior.

## Scope
This repository studies behavioral-linguistic similarity, not machine consciousness claims.

## Current iteration highlights
- Literature screening quality now tracks **dedup 안정성(conflict) 신호**: 동일 논문이 여러 쿼리에서 상충 라벨을 받는 경우 `screening_stability`를 기록하고, `manual_qc_queue` 위험 점수에 `dedup_label_conflict`/`dedup_high_score_variance`를 반영해 오분류 위험 샘플을 앞당깁니다.
- Prompt bank expanded to `v2.8` with four additional scenarios (`screening_conflict_resolution_loop`, `prompt_bank_version_drift`, `runner_preflight_gate_miss`, `manual_qc_diversity_rebalance`) and two personas (`screening_conflict_mediator`, `preflight_gate_keeper`) for screening conflict mediation and runner preflight discipline.
- Experiment runner reproducibility upgraded with stronger preflight checks: `--require-min-planned-samples-per-run`, `--require-min-repeats`, `--require-min-temperature-span`에 더해 `--require-min-unique-scenario-tags`로 run별 시나리오 다양성 하한을 강제하고 manifest `run_preflight`에 태그 커버리지를 남깁니다.

## Repository structure
- `docs/`: review protocol, screening rubric, experiment plan, ops notes
- `queries/`: retrieval queries and screening rules
- `prompts/`: Korean prompt bank and scenario source material
- `scripts/`: literature sync, dataset generation, analysis, experiment runner
- `ops/`: experiment matrix and state tracking
- `refs/`: bibliography and collected metadata
- `results/`: experiment outputs

## Quickstart
```bash
python3 scripts/search_openalex.py --config queries/search_queries.json --screening-rules queries/screening_rules.json --out refs/openalex_results.jsonl --report-out results/lit_search_report.json --audit-out results/lit_screening_audit.json --manual-qc-limit 60 --manual-qc-per-label 12 --manual-qc-per-confidence 10 --manual-qc-per-group 10 --manual-qc-csv results/manual_qc_queue.csv
python3 scripts/build_evidence_table.py --in refs/openalex_results.jsonl --out docs/evidence-table.md

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v29_plan --plan-only --print-selection --selection-report results/selection_report_smoke_v29.json --selection-csv results/selection_report_smoke_v29.csv --require-min-scenarios 4 --require-min-personas 4 --require-min-unique-scenario-tags 4 --require-min-unique-persona-style-tags 8 --require-min-temperature-count 2 --require-min-temperature-span 0.3 --require-min-repeats 1 --require-min-condition-cells 48 --require-min-run-cells 10 --require-min-run-ids 4 --require-min-total-samples 6000 --require-min-planned-samples-per-run 1100 --manifest-note-file docs/experiment-plan.md --manifest-note "preflight v29"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v22 --include-run-id handoff_drift_v22 --fail-on-missing-run-id --manifest-markdown --max-runs 1 --require-min-total-samples 1000
```

## Prompt-bank filtering
`scripts/generate_dataset.py` supports reproducible subset selection:

```bash
python3 scripts/generate_dataset.py \
  --out /tmp/mock.jsonl \
  --prompt-bank prompts/prompt_bank_ko.json \
  --scenario-tags counterfactual \
  --persona-ids regretful,self_compassionate
```

## Experiment reproducibility
- Run definitions live in `ops/experiment_matrix.json`
- `results/experiments/<label>/manifest.json` records environment and cell status
- `results/experiments/<label>/snapshots/` stores the config and prompt-bank snapshots used for the batch
the batch
