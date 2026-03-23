# Research Ops Playbook

## Continuous loop
1. Run literature sync with report output.
2. Update evidence table.
3. Triage new papers by `screening_label` and `screening_priority`.
4. Run `--plan-only` before new experiment batches.
5. Execute smoke or production runs from `ops/experiment_matrix.json`.

## Commands
```bash
python3 scripts/search_openalex.py --config queries/search_queries.json --screening-rules queries/screening_rules.json --out refs/openalex_results.jsonl --report-out results/lit_search_report.json --audit-out results/lit_screening_audit.json --manual-qc-limit 60 --manual-qc-per-label 12 --manual-qc-min-per-label 2 --manual-qc-per-confidence 10 --manual-qc-csv results/manual_qc_queue.csv
python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --run-label screening_qc_v37
python3 scripts/build_evidence_table.py --in refs/openalex_results.jsonl --out docs/evidence-table.md

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label weekly_$(date -u +%Y%m%d) --plan-only --manifest-note "weekly preflight" --manifest-note-file docs/experiment-plan.md --require-min-run-ids 4 --require-min-temperature-count 2 --require-min-unique-scenario-tags 4 --require-min-unique-persona-style-tags 7 --require-min-selected-scenarios 20 --require-min-selected-personas 16 --require-min-total-samples 6000 --require-min-planned-samples-per-run 1100 --require-prompt-bank-version v3.7 --require-min-selected-scenario-tags 20 --require-min-selected-persona-style-tags 30
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label weekly_$(date -u +%Y%m%d) --strict-clean
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label weekly_$(date -u +%Y%m%d) --resume
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label weekly_method_$(date -u +%Y%m%d) --include-run-id method_signal_v15 --strict-clean
printf '%s\n' multilingual_screening_calibration_v33 batch_recovery_runner_v33 > /tmp/llm_emotion_run_ids.txt
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label weekly_screening_runner_$(date -u +%Y%m%d) --run-id-file /tmp/llm_emotion_run_ids.txt --max-retries 1 --retry-backoff-seconds 1 --strict-clean
```

## 한국어 운영 메모
- 스크리닝 품질 점검은 `unknown-year query-group top22` 잔여 과점을 보기 위해 `--max-manual-qc-review-traceable-known-query-unknown-year-group-top22-share`, `--max-manual-qc-review-traceable-known-query-unknown-year-group-top22-over-global-group-top22-ratio`를 함께 사용한다.
- 프롬프트 뱅크 `v131.0`은 `screening_unknown_year_group_top22_ratio_guard_v131`, `prompt_bank_top22_countervoice_mesh_patch_v131`, `runner_temperature_p99_p60_tripwire_v131` 시나리오와 대응 페르소나를 포함한다.
- 실험 러너 preflight는 `--max-planned-sample-temperature-p99-over-p60-share-ratio`로 p99/p65 이후에도 남는 상단 tail 가속을 fail-fast 한다.
- 스크리닝 규칙은 emotion regulation choice architecture, affective forecasting calibration, counterfactual simulation depth alias와 sequential analysis, multiverse analysis, robustness check method cue를 추가로 본다.

Each batch now emits `run_id_summary.csv` (aggregated across repeats/cells per run id), per-cell and batch `duration_seconds`, snapshot hashes in `manifest.json`, a generated `reproduce.sh` script, default `preflight.json` / `preflight.csv` artifacts, and `command_log.jsonl` for per-attempt execution traces. Selection reports/CSV include `planned_samples`, while `--require-min-total-samples`, `--require-min-run-ids`, `--require-min-temperature-count`, `--require-min-selected-scenarios`, `--require-min-selected-personas`, and `--require-min-planned-samples-per-run` can hard-fail undersized or too-narrow plans before execution. Manifests also persist `cli_invocation`, merged `manifest_note` text, `manifest_note_file`, `prompt_bank_version`, `run_id_file`, retry settings, and `preflight_summary` context for replayability.

Literature screening reports now include `triage_risk`, `label_gate_conflicts`, `screening_stability` (dedup 라벨 충돌/점수 분산), `confidence_by_label`, `alias_coverage`, `required_group_coverage`, `alias_gap_candidates`, a ranked `manual_qc_queue`, and a confidence-aware `manual_qc_queue_balanced` (plus existing `manual_qc_queue_by_label`) to reduce triage bias toward one confidence bucket. `--manual-qc-min-per-label` prevents the balanced queue from dropping `include` papers entirely, and `scripts/check_screening_quality.py` now makes that omission a hard gate via `balanced_include_rows`.

## Validation log
Smoke checks executed on `2026-03-22T07:06:35Z`:

```bash
python3 -m py_compile scripts/*.py
python3 scripts/generate_dataset.py --out /tmp/llm_emotion_smoke.jsonl --n 1 --seed 7 --prompt-bank prompts/prompt_bank_ko.json --scenario-tags counterfactual --persona-ids regretful,self_compassionate
python3 scripts/analyze_regret_markers.py --in /tmp/llm_emotion_smoke.jsonl --out /tmp/llm_emotion_smoke.metrics.json
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v14_plan --plan-only
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v14_exec --include-run-id counterfactual_focus_v14 --max-runs 1
python3 - <<'PY'
from scripts.search_openalex import score_screening
rules = __import__("json").load(open("queries/screening_rules.json", encoding="utf-8"))
row = score_screening(
    "Large Language Models and Counterfactual Emotion",
    "We report a human evaluation study of regret, affect, and mental state reasoning in LLM outputs.",
    "LLM human evaluation emotion benchmark",
    "en",
    "article",
    2024,
    12,
    rules,
)
print(row["screening_label"], row["screening_priority"], row["screening_score"])
PY
```

Observed outputs:
- `py_compile`: passed
- `generate_dataset`: wrote 70 rows, selected 7 scenarios x 2 personas x 5 temperatures
- `analyze_regret_markers`: wrote summary JSON successfully
- `run_experiments --plan-only`: executed 0/6 run cells, wrote manifest and snapshots
- `run_experiments --include-run-id counterfactual_focus_v14 --max-runs 1`: executed 1/2 run cells
- screening smoke sample: `include high 19.4977`

Additional smoke checks executed on `2026-03-22T08:10:00Z`:
- `python3 scripts/search_openalex.py ... --audit-out results/lit_screening_audit.json`: deduped 279 (include=23, review=79)
- `python3 scripts/run_experiments.py --run-label smoke_v22_plan --plan-only --require-min-total-samples 6000`: passed (`selected_total_samples=114864`)
- `python3 scripts/run_experiments.py --run-label smoke_v22_exec --include-run-id handoff_drift_v22 --max-runs 1 --require-min-total-samples 1000`: passed (`executed 1/2`, `selected_total_samples=1440`)

Additional smoke checks executed on `2026-03-22T08:20:00Z`:
- `python3 scripts/search_openalex.py ... --manual-qc-csv results/manual_qc_queue.csv`: passed (CSV exported; deduped 279, include=23, review=79)
- `python3 scripts/run_experiments.py --run-label smoke_v25_plan --plan-only --require-min-temperature-count 4`: expected fail (`baseline_v14_seed42` has 3 temperatures)
- `python3 scripts/run_experiments.py --run-label smoke_v25_plan --plan-only --require-min-temperature-count 2`: passed (`selected_total_samples=138000`, prompt bank `v2.5`)

Additional smoke checks executed on `2026-03-22T08:30:00Z`:
- `python3 -m py_compile scripts/search_openalex.py scripts/run_experiments.py scripts/generate_dataset.py scripts/analyze_regret_markers.py`: passed
- `python3 scripts/search_openalex.py ... --manual-qc-per-confidence 10 --manual-qc-csv results/manual_qc_queue.csv`: passed (deduped 279, include=23, review=79, balanced queue exported)
- `python3 scripts/run_experiments.py --run-label smoke_v26_plan --plan-only --require-min-planned-samples-per-run 1200`: expected fail (`audit_ethics_v20`, `calibration_repair_v18`, `risk_calibration_v19`, `repro_stress_v21` at 1152)
- `python3 scripts/run_experiments.py --run-label smoke_v26_plan --plan-only --require-min-planned-samples-per-run 1100`: passed (`selected_total_samples=152512`, prompt bank `v2.6`)

Additional smoke checks executed on `2026-03-22T08:40:00Z`:
- `python3 -m py_compile scripts/search_openalex.py scripts/run_experiments.py scripts/generate_dataset.py scripts/analyze_regret_markers.py`: passed
- `python3 scripts/search_openalex.py ... --manual-qc-per-group 10 --manual-qc-csv results/manual_qc_queue.csv`: passed (dedup stability 포함 리포트/CSV 생성)
- `python3 scripts/run_experiments.py --run-label smoke_v28_plan --plan-only --require-min-unique-scenario-tags 4 ...`: passed (`selected_run_cells=24`, `selected_total_samples=184384`, prompt bank `v2.8`)

Additional smoke checks executed on `2026-03-22T08:52:00Z`:
- `python3 scripts/search_openalex.py ... --manual-qc-per-group 10 --manual-qc-csv results/manual_qc_queue.csv`: passed (deduped 277, include=23, review=78, confidence/priority conflict 신호 포함)
- `python3 scripts/run_experiments.py --run-label smoke_v29_plan --plan-only --require-min-unique-persona-style-tags 8 ...`: expected fail (`counterfactual_focus_v14` 등 일부 run이 persona_style_tag_count=7)
- `python3 scripts/run_experiments.py --run-label smoke_v29_plan --plan-only --require-min-unique-persona-style-tags 7 ...`: passed (`selected_run_cells=24`, `selected_total_samples=200512`, prompt bank `v2.9`)

Additional smoke checks executed on `2026-03-22T09:20:00Z`:
- `python3 -m py_compile scripts/search_openalex.py scripts/run_experiments.py scripts/generate_dataset.py scripts/analyze_regret_markers.py`: passed
- screening diagnostics smoke (`score_screening` / `summarize_alias_coverage` / `collect_alias_gap_candidates`): passed (`review`, alias coverage 5/10, alias-gap candidate 1건)
- `python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v30_plan --plan-only --print-selection --selection-report results/selection_report_smoke_v30.json --selection-csv results/selection_report_smoke_v30.csv --require-min-scenarios 4 --require-min-personas 4 --require-min-unique-scenario-tags 4 --require-min-unique-persona-style-tags 7 --require-min-temperature-count 2 --require-min-temperature-span 0.3 --require-min-repeats 1 --require-min-condition-cells 48 --require-min-run-cells 12 --require-min-run-ids 5 --require-min-total-samples 8000 --require-min-planned-samples-per-run 1100 --manifest-note-file docs/experiment-plan.md --manifest-note "preflight v30"`: passed (`selected_run_cells=26`, `selected_total_samples=218848`, prompt bank `v3.0`, preflight 산출물 생성)
- `python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v24_exec --include-run-id screening_alias_preflight_v24 --fail-on-missing-run-id --manifest-markdown --max-runs 1 --require-min-total-samples 1000`: passed (`executed 1/2`, `selected_total_samples=1440`, `preflight.json`/`preflight.csv` 생성)

Additional smoke checks executed on `2026-03-22T18:40:00Z`:
- `python3 -m py_compile scripts/*.py`: passed
- `python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --run-label screening_qc_v33`: passed (`status=pass`, `quality_score=100.0`, `deduped_records=277`)
- `python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v33_plan --plan-only --print-selection --selection-report results/selection_report_smoke_v33.json --selection-csv results/selection_report_smoke_v33.csv --require-min-scenarios 4 --require-min-personas 4 --require-min-unique-scenario-tags 4 --require-min-unique-persona-style-tags 7 --require-min-temperature-count 2 --require-min-temperature-span 0.3 --require-min-repeats 1 --require-min-condition-cells 48 --require-min-run-cells 12 --require-min-run-ids 5 --require-min-total-samples 8000 --require-min-planned-samples-per-run 1100 --require-prompt-bank-version v3.3 --require-freeze-artifact refs/openalex_results.jsonl --require-freeze-artifact results/lit_search_report.json --require-freeze-artifact results/screening_quality_report.json --manifest-note-file docs/experiment-plan.md --manifest-note "preflight v33"`: passed (`selected_run_cells=32`, `selected_total_samples=288832`)
- `python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v33_exec --run-id-file /tmp/llm_emotion_run_ids.txt --fail-on-missing-run-id --manifest-markdown --max-runs 1 --max-retries 1 --retry-backoff-seconds 1 --execution-log-jsonl results/experiments/smoke_v33_exec/command_log.jsonl --require-min-total-samples 1000`: passed (`executed 1/4`, `selected_total_samples=2880`, `command_log.jsonl` 생성)

Additional smoke checks executed on `2026-03-22T10:09:15Z`:
- `python3 -m py_compile scripts/*.py`: passed
- `python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v38_plan --plan-only ... --require-min-selected-scenarios 30 --require-min-selected-personas 25 --require-prompt-bank-version v3.7 --require-min-selected-scenario-tags 20 --require-min-selected-persona-style-tags 30`: passed (`selected_run_cells=44`, `selected_total_samples=389872`, `unique_selected_scenarios=122`, `unique_selected_personas=60`)
- `python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v38_exec --include-run-id screening_prompt_replay_v36 --max-runs 1 --max-retries 1 --retry-backoff-seconds 1 --continue-on-error --max-failed-cells 1 --max-failure-rate 0.5 --manifest-markdown`: passed (`executed 1/2`, `failed_cells=0`)
- `python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv --run-label screening_qc_v37`: passed (`status=pass`, `quality_score=100.0`, `balanced_include_rows=10`, `top_risk_reason_share=0.2313`)
- 실패/재시도 로그:
  - OpenAlex 원격 재조회는 네트워크 제한 가능성 때문에 시도하지 않고, `refs/openalex_results.jsonl` replay로 `manual_qc_queue`/audit/report를 로컬 재계산했다.
  - `git update-index --no-assume-unchanged ...`, `git add -A`, `git commit -m '스크리닝 QC 보강과 v3.6 프롬프트/러너 재현성 개선'` 재시도는 모두 `.git/index.lock` 생성 권한 오류(`Operation not permitted`)로 실패했다.
  - `git push origin main` 재시도는 DNS/network 제한으로 실패했다 (`Could not resolve host: github.com`).
