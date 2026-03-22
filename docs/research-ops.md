# Research Ops Playbook

## Continuous loop
1. Run literature sync with report output.
2. Update evidence table.
3. Triage new papers by `screening_label` and `screening_priority`.
4. Run `--plan-only` before new experiment batches.
5. Execute smoke or production runs from `ops/experiment_matrix.json`.

## Commands
```bash
python3 scripts/search_openalex.py --config queries/search_queries.json --screening-rules queries/screening_rules.json --out refs/openalex_results.jsonl --report-out results/lit_search_report.json
python3 scripts/build_evidence_table.py --in refs/openalex_results.jsonl --out docs/evidence-table.md

python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label weekly_$(date -u +%Y%m%d) --plan-only --manifest-note "weekly preflight"
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label weekly_$(date -u +%Y%m%d) --strict-clean
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label weekly_$(date -u +%Y%m%d) --resume
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label weekly_method_$(date -u +%Y%m%d) --include-run-id method_signal_v15 --strict-clean
```

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
