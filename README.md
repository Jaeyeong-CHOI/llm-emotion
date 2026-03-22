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
- `docs/lit-review.md`: prior work map
- `docs/experiment-plan.md`: hypotheses, design, metrics, stats plan
- `prompts/`: scenario templates and model prompts
- `scripts/`: data generation + analysis utilities
- `data/`: collected generations + annotation files
- `results/`: metrics and figures

## Quickstart
```bash
python3 scripts/generate_dataset.py --out data/raw/mock_generations.jsonl --n 30
python3 scripts/analyze_regret_markers.py --in data/raw/mock_generations.jsonl --out results/mock_metrics.json
```

## Initial milestone checklist
- [x] Define operationalized “regret-like” markers
- [x] Draft literature review seed
- [x] Build experimental protocol v0.1
- [x] Add analysis starter scripts
- [ ] Collect real model outputs across 3+ LLMs
- [ ] Human baseline corpus + annotation
- [ ] Statistical testing + report

## Notes
This repository is designed to be iteratively expanded with new models, scenarios, and annotation rounds.
