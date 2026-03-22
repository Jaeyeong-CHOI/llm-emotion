# Research Ops Playbook

## Continuous loop (recommended weekly)
1. Run literature sync (`scripts/search_openalex.py`)
2. Update evidence table (`scripts/build_evidence_table.py`)
3. Triage new papers into: cite now / later / discard
4. Open or update GitHub issues for next experiment tasks
5. Run pilot/production experiments and append logs

## Commands
```bash
python3 scripts/search_openalex.py --config queries/search_queries.json --screening-rules queries/screening_rules.json --out refs/openalex_results.jsonl
python3 scripts/build_evidence_table.py --in refs/openalex_results.jsonl --out docs/evidence-table.md
python3 scripts/run_experiments.py --config ops/experiment_matrix.json
```

## Branching convention
- `lit/*` for prior-work updates
- `exp/*` for experiments
- `analysis/*` for model/statistical analysis

## Definition of done (per cycle)
- Evidence table updated
- Bibliography updated (or TODO filed)
- At least one actionable research issue advanced
- Commit + push + concise changelog
