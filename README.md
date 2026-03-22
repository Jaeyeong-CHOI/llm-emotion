# llm-emotion

Research project on whether LLMs show **human-like “regret for what they do not possess”** in language behavior.

## Core idea
We do **behavioral-linguistic comparison**, not claims about machine consciousness.

- Human regret/missingness: affect + self-narrative + counterfactual thought
- LLM output: probabilistic text generation
- Research target: **as-if psychological similarity** in observable text patterns

## Research questions
1. Do LLMs increase counterfactual/regret expressions under loss prompts?
2. Are these patterns similar to human-written regret narratives?
3. How do persona priming and decoding settings (temperature) modulate these behaviors?

## Repository structure
- `docs/lit-review.md`: initial prior-work map
- `docs/systematic-review-protocol.md`: PRISMA-lite review protocol
- `docs/evidence-table.md`: auto-generated evidence table from OpenAlex pulls
- `docs/experiment-plan.md`: hypotheses, design, metrics, stats plan
- `docs/research-ops.md`: continuous research operations playbook
- `queries/search_queries.json`: query groups for ongoing literature scans
- `prompts/`: scenario templates and expanded prompt bank (`prompt_bank_ko.json`, v1.2)
- `scripts/`: data generation + analysis + literature sync + reproducible experiment runner utilities (repeat support + run manifest summary)
- `refs/`: bibliography + machine-collected paper metadata
- `data/`: collected generations + annotation files
- `results/`: metrics and figures

## Quickstart
### 1) Systematic prior-work scan
```bash
python3 scripts/search_openalex.py --config queries/search_queries.json --screening-rules queries/screening_rules.json --out refs/openalex_results.jsonl
python3 scripts/build_evidence_table.py --in refs/openalex_results.jsonl --out docs/evidence-table.md
```

### 2) Experiment pipeline smoke test
```bash
python3 scripts/generate_dataset.py --out data/raw/mock_generations.jsonl --n 30 --seed 42 --prompt-bank prompts/prompt_bank_ko.json
python3 scripts/analyze_regret_markers.py --in data/raw/mock_generations.jsonl --out results/mock_metrics.json

# reproducible multi-run experiment bundle
python3 scripts/run_experiments.py --config ops/experiment_matrix.json --run-label smoke_v12
```

## Initial milestone checklist
- [x] Define operationalized “regret-like” markers
- [x] Draft literature review seed
- [x] Build experimental protocol v0.1
- [x] Add analysis starter scripts
- [ ] Collect real model outputs across 3+ LLMs
- [ ] Human baseline corpus + annotation
- [ ] Statistical testing + report

## Automation
- GitHub Action: `.github/workflows/lit-review-sync.yml`
  - Runs **daily** (UTC)
  - Executes full research cycle (`scripts/research_cycle.py`)
  - Refreshes literature/evidence + smoke-test generation/analysis + state log
  - Auto-commits updates

- Local one-command cycle
```bash
make cycle
make status
```

## Notes
This repository is designed to be iteratively expanded with new models, scenarios, and annotation rounds.
