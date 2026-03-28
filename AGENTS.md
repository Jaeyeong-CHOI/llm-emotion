# AGENTS.md

## Setup
uv venv && source .venv/bin/activate && uv sync
cp .env.example .env  # API 키 설정 필요

## Test
pytest tests/ -v

## Run
python scripts/run_experiment.py --dry-run  # 항상 dry-run 먼저

## Boundaries
- 🚫 .env 수정 금지 (API 키)
- 🚫 results/real_experiments/ 덮어쓰기 금지
- ⚠️ API 호출 전 budget_report.md 확인
