# Reproducibility v123

## 변경 범위
- 스크리닝 품질: `unknown-year known-query query-group top15` 절대 share 및 global 대비 ratio 게이트 추가
- 프롬프트 뱅크: `v123.0`로 갱신하고 top15 countervoice / p99-median tripwire 대응 scenario·persona 추가
- 실험 러너: `--max-planned-sample-temperature-p99-over-median-share-ratio` preflight 가드 추가

## 전제조건
- Python 3.11+ 권장
- 작업 디렉터리: `/Users/jaeyeong_openclaw/.openclaw/workspace/llm-emotion`
- 입력 파일
  - `results/lit_search_report.json`
  - `results/lit_screening_audit.json`
  - `results/manual_qc_queue.csv`
  - `ops/experiment_matrix.json`
  - `prompts/prompt_bank_ko.json`

## 핵심 의사결정
- 스크리닝은 기존 `group top14` 이후에도 남는 누적 과점을 한 단계 더 감시하기 위해 `group top15`를 추가했다.
- 프롬프트 뱅크는 새 게이트를 직접 반영하는 research-ops scenario 3개와 persona 3개를 추가해, 문서상 규칙과 실제 실험 자산 사이의 괴리를 줄였다.
- 러너는 `p95/median` 다음 단계인 `p99/median`을 추가해, top-k 지표와 p95가 통과하더라도 최상단 tail이 과열되는 실패 모드를 조기 차단하도록 했다.

## 실행 커맨드
```bash
python3 -m py_compile scripts/check_screening_quality.py scripts/run_experiments.py

python3 - <<'PY'
import json, pathlib
for path in ['prompts/prompt_bank_ko.json', 'ops/experiment_matrix.json']:
    json.loads(pathlib.Path(path).read_text(encoding='utf-8'))
    print(f'validated {path}')
PY

python3 scripts/check_screening_quality.py \
  --report results/lit_search_report.json \
  --audit results/lit_screening_audit.json \
  --manual-qc-csv results/manual_qc_queue.csv \
  --out results/screening_quality_report_v123.json \
  --out-md results/screening_quality_report_v123.md \
  --run-label screening_qc_v123 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top15-share 1.0 \
  --max-manual-qc-review-traceable-known-query-unknown-year-group-top15-over-global-group-top15-ratio 1.0

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v123_plan \
  --plan-only \
  --include-run-id screening_prompt_runner_unknown_year_group_top15_temperature_p99_median_v123 \
  --fail-on-missing-run-id \
  --print-selection \
  --selection-report results/selection_report_smoke_v123.json \
  --selection-csv results/selection_report_smoke_v123.csv \
  --preflight-markdown \
  --require-prompt-bank-version v123.0 \
  --max-planned-sample-temperature-p99-over-median-share-ratio 1.0 \
  --manifest-note "preflight v123 unknown-year group top15 + temperature p99/median guard"
```

## 산출물
- `results/screening_quality_report_v123.json`
- `results/screening_quality_report_v123.md`
- `results/selection_report_smoke_v123.json`
- `results/selection_report_smoke_v123.csv`
- `results/experiments/smoke_v123_plan/preflight.json`
- `results/experiments/smoke_v123_plan/preflight.md`
- `results/experiments/smoke_v123_plan/manifest.json`

## 검증 결과
- 문법 검사: 통과
- JSON 로드 검증: `prompts/prompt_bank_ko.json`, `ops/experiment_matrix.json` 통과
- `screening_qc_v123`: 전체 상태는 기존 데이터 영향으로 `review`, `quality_score=0.0`
- 신규 top15 게이트:
  - `manual_qc_review_traceable_known_query_unknown_year_group_top15_share_ceiling=pass` (`observed=0.0`, `threshold<=1.0`)
  - `manual_qc_review_traceable_known_query_unknown_year_group_top15_over_global_group_top15_ratio_ceiling=pass` (`observed=0.0`, `threshold<=1.0`)
- `smoke_v123_plan`: plan-only 실행 성공
  - `selected_run_ids=['screening_prompt_runner_unknown_year_group_top15_temperature_p99_median_v123']`
  - `prompt_bank_versions=['v123.0']`
  - `planned_sample_temperature_p95_over_median_share_ratio=1.0`
  - `planned_sample_temperature_p99_over_median_share_ratio=1.0`
  - `min_planned_samples=288`

## 한계
- `screening_qc_v123`의 전체 `review` 상태는 이번 변경으로 새로 발생한 문제가 아니라, 기존 입력 데이터의 다수 게이트 실패가 유지된 결과다.
- `smoke_v123_plan`은 `plan-only` 검증이므로 실제 generation/analysis 실행 경로는 포함하지 않았다.
