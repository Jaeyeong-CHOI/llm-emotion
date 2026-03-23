# Reproducibility v121

## 변경 요약

우선순위 기준으로 다음 3가지를 반영했다.

1. **선행연구 스크리닝 품질 개선**
   - `scripts/build_screening_triage_plan.py` 추가
   - `results/screening_quality_report.json`의 gate 실패 항목을 우선순위별 액션으로 자동 정리
2. **프롬프트 뱅크 확장**
   - `prompts/prompt_bank_ko.json`에 v118 계열 시나리오 보강(누락 항목 자동 추가)
   - 버전 메타데이터를 `v118.0`으로 갱신
3. **실험 러너 고도화**
   - `scripts/run_experiments.py`에 `planned_sample_temperature_gini` 지표 추가
   - 새 preflight 게이트: `--max-planned-sample-temperature-gini`
   - preflight/manifest 요약에 gini 및 관련 설정 기록
   - 누락되어 있던 `max_planned_sample_temperature_top20_over_uniform_ratio` manifest 기록 포함

---

## 재현 절차

```bash
python3 -m py_compile scripts/run_experiments.py scripts/build_screening_triage_plan.py

python3 scripts/build_screening_triage_plan.py \
  --in results/screening_quality_report.json \
  --out results/screening_triage_plan_v121.json \
  --out-md results/screening_triage_plan_v121.md

python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --run-label smoke_v121_plan \
  --plan-only \
  --selection-report results/selection_report_smoke_v121.json \
  --selection-csv results/selection_report_smoke_v121.csv \
  --preflight-markdown
```

---

## 산출물

- `results/screening_triage_plan_v121.json`
- `results/screening_triage_plan_v121.md`
- `results/selection_report_smoke_v121.json`
- `results/selection_report_smoke_v121.csv`
- `results/experiments/smoke_v121_plan/manifest.json`

---

## 운영 메모

- screening triage 계획은 gate fail이 없으면 빈 액션 목록을 출력한다.
- 온도 분포는 기존 top-k / HHI / gap 지표에 더해 **Gini 계수**로 추가 감시한다.
- `--max-planned-sample-temperature-gini`를 0보다 크게 주면 fail-fast가 활성화된다.
