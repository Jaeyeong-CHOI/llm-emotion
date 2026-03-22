# llm-emotion

> 🇰🇷 **실시간 진행상황 먼저 보기:** [`LIVE_STATUS.md`](./LIVE_STATUS.md)

Research project on whether LLMs show human-like regret and deprivation signals in language behavior.

## Scope
This repository studies behavioral-linguistic similarity, not machine consciousness claims.

## Current iteration highlights
- Literature screening quality now reports **query drift/개념 누락 진단**까지 확장되었습니다: `missing_concept_groups`, `query_drift_candidates`, `manual_qc_queue_risk_reason_summary`가 리포트/감사 산출물에 추가되어 alias 보강과 쿼리 재정렬 우선순위를 동시에 추적할 수 있습니다.
- Prompt bank expanded to `v3.1` with four additional scenarios (`screening_synonym_false_friend`, `prompt_bank_boundary_regression`, `runner_partial_resume_duplicate`, `evidence_freeze_late_detection`) and two personas (`query_drift_watchdog`, `resume_consistency_checker`) for screening drift and resume consistency stress tests.
- Experiment runner reproducibility now supports **preflight hard gates**: `--require-prompt-bank-version` and `--require-freeze-artifact` to fail-fast when prompt-bank version mismatches or required evidence-freeze artifacts are missing.

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

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v31_plan --plan-only --print-selection --selection-report results/selection_report_smoke_v31.json --selection-csv results/selection_report_smoke_v31.csv --require-min-scenarios 4 --require-min-personas 4 --require-min-unique-scenario-tags 4 --require-min-unique-persona-style-tags 8 --require-min-temperature-count 2 --require-min-temperature-span 0.3 --require-min-repeats 1 --require-min-condition-cells 48 --require-min-run-cells 12 --require-min-run-ids 5 --require-min-total-samples 8000 --require-min-planned-samples-per-run 1100 --require-prompt-bank-version v3.1 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --manifest-note-file docs/experiment-plan.md --manifest-note "preflight v31"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v24 --include-run-id screening_alias_preflight_v24 --fail-on-missing-run-id --manifest-markdown --max-runs 1 --require-min-total-samples 1000
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
- `results/experiments/<label>/preflight.json` and `preflight.csv` capture selection/preflight diagnostics for review before or after execution
- `--require-prompt-bank-version`으로 실행 전 prompt bank 버전 고정, `--require-freeze-artifact`로 필수 근거 파일 존재 여부를 강제해 evidence-freeze 누락을 fail-fast로 차단할 수 있습니다.
