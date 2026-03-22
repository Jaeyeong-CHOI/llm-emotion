.PHONY: lit-sync evidence cycle status smoke

lit-sync:
	python3 scripts/search_openalex.py --config queries/search_queries.json --out refs/openalex_results.jsonl

evidence:
	python3 scripts/build_evidence_table.py --in refs/openalex_results.jsonl --out docs/evidence-table.md

smoke:
	python3 scripts/generate_dataset.py --out data/raw/mock_generations.jsonl --n 10
	python3 scripts/analyze_regret_markers.py --in data/raw/mock_generations.jsonl --out results/mock_metrics.json

cycle:
	python3 scripts/research_cycle.py

status:
	python3 scripts/research_status.py
