# Research Ops Playbook

## Continuous loop
1. Run literature sync with report output.
2. Update evidence table.
3. Triage new papers by `screening_label` and `screening_priority`.
4. Run `--plan-only` before new experiment batches.
5. Execute smoke or production runs from `ops/experiment_matrix.json`.

## Commands
```bash
python3 scripts/search_openalex.py --config queries/search_queries.json --screening-rules queries/screening_rules.json --out refs/openalex_results.jsonl --report-out results/lit_search_report.json --audit-out results/lit_screening_audit.json --manual-qc-limit 60 --manual-qc-per-label 12 --manual-qc-per-confidence 10 --manual-qc-csv results/manual_qc_queue.csv
python3 scripts/build_evidence_table.py --in refs/openalex_results.jsonl --out docs/evidence-table.md

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label weekly_$(date -u +%Y%m%d) --plan-only --manifest-note "weekly preflight" --manifest-note-file docs/experiment-plan.md --require-min-run-ids 4 --require-min-temperature-count 2 --require-min-unique-scenario-tags 4 --require-min-unique-persona-style-tags 8 --require-min-total-samples 6000 --require-min-planned-samples-per-run 1100
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label weekly_$(date -u +%Y%m%d) --strict-clean
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label weekly_$(date -u +%Y%m%d) --resume
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label weekly_method_$(date -u +%Y%m%d) --include-run-id method_signal_v15 --strict-clean
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label weekly_accountability_$(date -u +%Y%m%d) --include-run-id accountability_tradeoff_v16 --strict-clean
```

Each batch now emits `run_id_summary.csv` (aggregated across repeats/cells per run id), per-cell and batch `duration_seconds`, snapshot hashes in `manifest.json`, and a generated `reproduce.sh` script for one-command reruns. Selection reports/CSV include `planned_samples`, while `--require-min-total-samples`, `--require-min-run-ids`, `--require-min-temperature-count`, and `--require-min-planned-samples-per-run` can hard-fail undersized or too-narrow plans before execution. Manifests also persist `cli_invocation`, merged `manifest_note` text, and `manifest_note_file` context for replayability.

Literature screening reports now include `triage_risk`, `label_gate_conflicts`, `screening_stability` (dedup 라벨 충돌/점수 분산), `confidence_by_label`, a ranked `manual_qc_queue`, and a confidence-aware `manual_qc_queue_balanced` (plus existing `manual_qc_queue_by_label`) to reduce triage bias toward one confidence bucket. Optional CSV handoff now exports the balanced queue via `--manual-qc-csv` with dedup stability columns.

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
