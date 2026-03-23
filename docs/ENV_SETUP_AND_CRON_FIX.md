# 실모델 전환 및 크론 상태 점검 가이드

## 0) 지금 왜 막혀 있나 (요약)
- 실모델 전환은 현재 **필수 변수 3개**가 준비되지 않으면 block됨.
- `OPENAI_ORG_ID`, `OPENAI_PROJECT`는 지금은 보조 변수로 분류 (없어도 실행 전환은 허용).
- 크론 상태가 missing인 이유는 cron id/name 매칭이 점검 스크립트와 일치하지 않거나 cron 실행 환경에서 job 조회가 실패했을 때.

필수 체크 항목:
- `OPENAI_API_KEY`
- `LLM_EMOTION_REAL_MODEL`
- `LLM_EMOTION_REAL_MODEL_REGION`

권장(안전/추적):
- `OPENAI_ORG_ID`
- `OPENAI_PROJECT`

`OPENAI_API_KEY`는 실존 여부만 확인(형식은 최소 `sk-` 접두사 체크).

---

## 1) 30초 One-liner (Local 실행 + 상태 갱신)
```bash
cd /Users/jaeyeong_openclaw/.openclaw/workspace/llm-emotion && \
export LLM_EMOTION_REAL_MODEL='gpt-4o' \
export LLM_EMOTION_REAL_MODEL_REGION='us-east-1' \
python3 scripts/check_real_model_readiness.py && \
python3 scripts/snapshot_cron_status.py && \
python3 scripts/update_live_status.py && \
python3 scripts/research_status.py
```

> 위 값은 본인 계정값으로 바꿔 넣으세요.

---

## 2) 실모델 env를 한 번에 적용하는 영구 설정
```bash
cat <<'ENV_EOF' >> ~/.zshrc
export LLM_EMOTION_REAL_MODEL='gpt-4o'
export LLM_EMOTION_REAL_MODEL_REGION='us-east-1'
# 권장: 추적/오류추적 용도
# export OPENAI_ORG_ID='org-XXXXXXXX'
# export OPENAI_PROJECT='proj_XXXXXXXX'
ENV_EOF
source ~/.zshrc
```

cron에서 실행되는 환경도 동일해야 하므로, cron wrapper 사용이 더 안전합니다.

---

## 3) cron wrapper 예시 (권장)
`LLM_EMOTION_ROOT` 기준으로 env 주입 후 확인 스크립트를 실행합니다.

```bash
cat >/Users/jaeyeong_openclaw/.openclaw/workspace/llm-emotion/scripts/run_realtime_check_via_env.sh <<'WRAP_EOF'
#!/usr/bin/env bash
set -euo pipefail

export LLM_EMOTION_ROOT="${LLM_EMOTION_ROOT:-/Users/jaeyeong_openclaw/.openclaw/workspace/llm-emotion}"
export LLM_EMOTION_REAL_MODEL="${LLM_EMOTION_REAL_MODEL:?missing}"
export LLM_EMOTION_REAL_MODEL_REGION="${LLM_EMOTION_REAL_MODEL_REGION:?missing}"

cd "$LLM_EMOTION_ROOT"
python3 scripts/check_real_model_readiness.py
python3 scripts/snapshot_cron_status.py
python3 scripts/update_live_status.py
python3 scripts/research_status.py
WRAP_EOF
chmod +x /Users/jaeyeong_openclaw/.openclaw/workspace/llm-emotion/scripts/run_realtime_check_via_env.sh
```

cron payload는 wrapper를 실행하도록 바꾸면 됩니다.

---

## 4) 현재 cron ID 동기화(자동 탐지)
`snapshot_cron_status.py`가 이제는 다음 순서로 찾습니다.
1) `LLM_EMOTION_CONTINUOUS_CRON_ID`, `LLM_EMOTION_LIVE_CRON_ID` env가 있으면 그 ID 사용
2) 이름으로 매칭 (`llm-emotion-continuous-research`, `llm-emotion-important-live-report`)
3) 최종 fallback로 legacy hardcoded ID 사용

현재 실제 등록된 job id 확인:
```bash
cd /Users/jaeyeong_openclaw/.openclaw/workspace/llm-emotion
openclaw cron list --json
```

필요 시 고정 ID를 강제 설정:
```bash
export LLM_EMOTION_CONTINUOUS_CRON_ID="5774a9df-01a2-4de3-8016-710120693fef"
export LLM_EMOTION_LIVE_CRON_ID="2a4cf4a2-8b68-4661-8b57-52ff0829cf71"
```

---

## 5) 빠른 헬프 점검 (문제 진단 순서)
```bash
cd /Users/jaeyeong_openclaw/.openclaw/workspace/llm-emotion
python3 scripts/check_real_model_readiness.py
cat ops/real_model_readiness.json

python3 scripts/snapshot_cron_status.py
cat ops/cron_runtime_status.json

python3 scripts/research_status.py
```

- `ops/real_model_readiness.json.ready == true` 가 되면 실모델 전환 조건 통과.
- `ops/cron_runtime_status.json`의 `continuous`/`live_report` 상태가 `enabled`로 보이면 상태 missing이 사라집니다.


## 7) avrtg 연구 키 1회성 동기화 (요청 반영)
아래 스크립트는 **AVRTG_QUERY_GEN/.env**에서 키를 가져와 `llm-emotion/.env.real_model`에 넣습니다.
값은 출력하지 않습니다.

```bash
cd /Users/jaeyeong_openclaw/.openclaw/workspace/llm-emotion
AVRTG_ENV_FILE=/Users/jaeyeong_openclaw/.openclaw/workspace/AVRTG_QUERY_GEN/.env \
  LLM_EMOTION_REAL_MODEL='gpt-4o' \
  LLM_EMOTION_REAL_MODEL_REGION='us-east-1' \
  bash scripts/sync_keys_from_avrtg.sh
```

필요 시 org/project는 기존 `.env.real_model`의 값이 남아 있으면 유지되고, 없으면 빈 상태로 남습니다.

`source .env.real_model` 후 `check_real_model_readiness.py`에서 missing 변수를 추가로 채워야 합니다.
