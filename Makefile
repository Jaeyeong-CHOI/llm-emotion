.PHONY: lit-sync evidence screening-qc cycle status smoke

lit-sync:
	python3 scripts/search_openalex.py --config queries/search_queries.json --out refs/openalex_results.jsonl

evidence:
	python3 scripts/build_evidence_table.py --in refs/openalex_results.jsonl --out docs/evidence-table.md

screening-qc:
	python3 scripts/check_screening_quality.py --report results/lit_search_report.json --audit results/lit_screening_audit.json --manual-qc-csv results/manual_qc_queue.csv

smoke:
	python3 scripts/generate_dataset.py --out data/raw/mock_generations.jsonl --n 10
	python3 scripts/analyze_regret_markers.py --in data/raw/mock_generations.jsonl --out results/mock_metrics.json

cycle:
	python3 scripts/research_cycle.py

status:
	python3 scripts/research_status.py
