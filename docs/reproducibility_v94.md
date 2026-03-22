# Reproducibility v94

## 요약

v9.4에서는 우선순위 3축을 동시에 보강했다.

1. **선행연구 스크리닝 품질 개선**
   - `check_screening_quality.py`에 review known-query의 **query-group 분포 지표**(entropy/coverage/top1/top2 share)를 추가.
   - 쿼리 그룹화는 `canonical_query_group()`으로 수행(`||`, `::`, `//` 접두 그룹 정규화).
   - 신규 gate(하한/상한)를 추가해 review 큐가 특정 query-group으로 재쏠릴 때 조기 탐지 가능.

2. **프롬프트 뱅크 확장**
   - `prompts/prompt_bank_ko.json` 버전 `v9.4`로 상향.
   - 시나리오 3개 추가:
     - `screening_query_group_entropy_recovery_v94`
     - `prompt_bank_countervoice_query_group_ladder_v94`
     - `runner_timeout_stage_rebalance_drill_v94`
   - 페르소나 3개 추가:
     - `query_group_entropy_triager_v94`
     - `countervoice_group_ladder_curator_v94`
     - `timeout_share_governor_v94`

3. **실험 러너 고도화**
   - `run_experiments.py`에서 timeout 실패를 일반 실패와 분리:
     - `failed_generation_timeout`
     - `failed_analysis_timeout`
   - 기존 timeout-share/failure-over-selection budget 규칙이 실제 상태코드와 직접 연결되도록 정합성 개선.

---

## 재현 절차

### 1) 문법 체크

```bash
python3 -m py_compile scripts/check_screening_quality.py scripts/run_experiments.py
```

### 2) v9.4 스모크 플랜 실행 (실행 없이 계획/manifest 생성)

```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --include-run-id screening_prompt_runner_query_group_timeout_v94 \
  --plan-only \
  --run-label smoke_v94 \
  --manifest-markdown \
  --preflight-markdown
```

생성 아티팩트:

- `results/experiments/smoke_v94/manifest.json`
- `results/experiments/smoke_v94/manifest.md`
- `results/experiments/smoke_v94/preflight.json`
- `results/experiments/smoke_v94/preflight.md`
- `results/experiments/smoke_v94/runs.csv`

### 3) 실제 실행 예시 (필요 시)

```bash
python3 scripts/run_experiments.py \
  --config ops/experiment_matrix.json \
  --include-run-id screening_prompt_runner_query_group_timeout_v94 \
  --run-label v94_exec \
  --continue-on-error \
  --max-retries 1 \
  --generation-timeout-seconds 180 \
  --analysis-timeout-seconds 180 \
  --manifest-markdown \
  --preflight-markdown
```

---

## 변경 파일

- `scripts/check_screening_quality.py`
- `scripts/run_experiments.py`
- `prompts/prompt_bank_ko.json`
- `ops/experiment_matrix.json`
- `docs/reproducibility_v94.md`
