#!/usr/bin/env python3
import json
import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATE_PATH = ROOT / "ops" / "research_state.json"
CRON_STATE_PATH = ROOT / "ops" / "cron_runtime_status.json"
OUT_PATH = ROOT / "LIVE_STATUS.md"


def read_json(path: Path):
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def fmt(v, default="-"):
    return default if v is None else str(v)


def main():
    state = read_json(STATE_PATH)
    cron = read_json(CRON_STATE_PATH)

    stats = state.get("stats", {})
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "# 📡 실시간 연구 진행 현황 (llm-emotion)",
        "",
        f"- 마지막 갱신: **{now} (Asia/Seoul 기준 로컬 실행 시각)**",
        f"- 마지막 실행: **{fmt(state.get('last_run'))}**",
        f"- 마지막 성공: **{fmt(state.get('last_success'))}**",
        f"- 수집 논문 수(후보): **{fmt(stats.get('papers_collected'), '0')}편**",
        f"- Evidence Table 행 수: **{fmt(stats.get('evidence_rows'), '0')}행**",
        f"- 생성 샘플 수(파이프라인 검증용): **{fmt(stats.get('mock_samples_generated'), '0')}개**",
        "",
        "## 자동화 상태",
        f"- 연구 루프(1분): **{fmt((cron.get('continuous') or {}).get('status'), 'unknown')}**",
        f"- 중요상황 상시 보고(1분): **{fmt((cron.get('live_report') or {}).get('status'), 'unknown')}**",
        f"- 최근 연구 루프 결과: **{fmt((cron.get('continuous') or {}).get('lastRunStatus'), 'unknown')}**",
        "",
        "## 현재 단계 요약",
        "- [x] 체계적 선행연구 수집 파이프라인 구축",
        "- [x] 증거표(Evidence Table) 자동 생성",
        "- [x] 연구 자동 루프 + 상태 추적 구축",
        "- [ ] 핵심 논문(코어셋) 정밀 스크리닝 완료",
        "- [ ] 실모델 API 기반 본실험 데이터 수집",
        "- [ ] 통계 검정 + 논문 초안",
        "",
        "> 이 파일은 자동 갱신됩니다. (scripts/research_cycle.py 내부에서 업데이트)",
    ]

    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
