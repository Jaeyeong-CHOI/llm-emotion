# Reproducibility v135

## 변경 요약
1. **선행연구 스크리닝 품질**
   - `scripts/build_screening_triage_plan.py` 개선
   - 실패 gate triage에 `severity_score`, `hotspot_hint` 추가
2. **프롬프트 뱅크 확장**
   - `prompts/prompt_bank_ko.json` 버전: `v134.0 -> v135.0`
   - 시나리오 2개, 페르소나 2개 추가
3. **실험 러너 고도화**
   - `scripts/run_experiments_with_profile.py` 추가
   - `ops/runner_guardrail_profile.json` 추가

## 실행/검증 로그
```bash
python3 -m py_compile scripts/build_screening_triage_plan.py scripts/run_experiments_with_profile.py
python3 scripts/run_experiments_with_profile.py --dry-run
python3 scripts/build_screening_triage_plan.py --in results/screening_quality_report_v75.json --out results/screening_triage_plan_v135.json --out-md results/screening_triage_plan_v135.md
```

## 산출물
- `results/screening_triage_plan_v135.json`
- `results/screening_triage_plan_v135.md`

## 참고
- profile 실행 시 override 인자를 뒤에 붙여서 사용 가능
  - 예: `python3 scripts/run_experiments_with_profile.py -- --run-label weekly_20260323 --plan-only`
