# 실모델 전환 및 크론 상태 점검 가이드

## 1) 실모델 전환 차단 원인
`ops/real_model_readiness.json` 기준 현재 아래 항목이 누락되어 실모델 전환이 막혀 있습니다.

- `OPENAI_ORG_ID`
- `OPENAI_PROJECT`
- `LLM_EMOTION_REAL_MODEL`
- `LLM_EMOTION_REAL_MODEL_REGION`

`OPENAI_API_KEY`는 이미 존재합니다.

## 2) 실행 환경에서 환경변수 설정 (필수)
아래 4개를 실제 실행 환경에 반드시 export 해야 합니다.

```bash
export OPENAI_ORG_ID="org-xxxxxxxx"
export OPENAI_PROJECT="proj_xxxxxxxxxxxxxxxxxxxxx"
export LLM_EMOTION_REAL_MODEL="gpt-4o"
export LLM_EMOTION_REAL_MODEL_REGION="us-east-1"
```

> 모델명/프로젝트는 본인 환경에 맞게 변경하세요.

## 3) (선택) 크론 재가동 전에 영구 반영
- 터미널/배포 환경별 영구 반영 방법:
  - `~/.zshrc`에 위 export를 추가
  - 또는 cron 실행 전 wrapper script에서 export 후 실행
  - 또는 OpenClaw의 환경 변수 설정 기능(있다면) 사용

## 4) 자동화 상태 missing 원인 및 고치기
`ops/cron_runtime_status.json`가 다음처럼 나오면 크론이 탐색되지 않았다는 의미입니다.

```json
{
  "continuous": {"status":"missing"},
  "live_report": {"status":"missing"}
}
```

이 코드는 고정 ID로 상태를 조회합니다.
- 연속 실행: `33f59b94-c1e7-44f7-ac2b-f2490043bcc6`
- 중요보고: `36361127-9526-4c77-a742-e83d6b4d701e`

실제 cron ID가 바뀌면 2개 중 하나가 missing으로 표시됩니다.

## 5) 점검 절차(복붙 실행)

```bash
cd /Users/jaeyeong_openclaw/.openclaw/workspace/llm-emotion
python3 scripts/check_real_model_readiness.py
python3 scripts/snapshot_cron_status.py
python3 scripts/update_live_status.py
python3 scripts/research_status.py
```

`cron_runtime_status.json`이 `enabled`로 바뀌면 LIVE_STATUS/브리프 로그의 missing이 사라집니다.

## 6) cron ID를 정확히 맞추는 방법
실제 등록된 cron 목록을 확인:

```bash
cd /Users/jaeyeong_openclaw/.openclaw/workspace/llm-emotion
openclaw cron list --json
```

출력의 `id`를 보고 `snapshot_cron_status.py`의 `CONTINUOUS_ID`, `LIVE_REPORT_ID`를 실제 값으로 교체하거나
cron를 다시 생성해 코드 값과 맞추세요.
