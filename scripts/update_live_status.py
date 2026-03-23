#!/usr/bin/env python3
import datetime
from typing import Any

from research_ops_common import ROOT, STATE_PATH, get_stats_snapshot, read_json

CRON_STATE_PATH = ROOT / "ops" / "cron_runtime_status.json"
OUT_PATH = ROOT / "LIVE_STATUS.md"


def fmt(v: Any, default: str = "-") -> str:
    return default if v is None else str(v)


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _cron_field(cron: dict[str, Any], section: str, field: str, default: str = "unknown") -> str:
    return fmt(_as_dict(cron.get(section)).get(field), default)


def main() -> None:
    state = _as_dict(read_json(STATE_PATH))
    cron = _as_dict(read_json(CRON_STATE_PATH))

    snapshot = get_stats_snapshot(state)
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        "# 📡 실시간 연구 진행 현황 (llm-emotion)",
        "",
        f"- 마지막 갱신: **{now} (Asia/Seoul 기준 로컬 실행 시각)**",
        f"- 마지막 실행: **{fmt(state.get('last_run'))}**",
        f"- 마지막 성공: **{fmt(state.get('last_success'))}**",
        f"- 수집 논문 수(후보): **{fmt(snapshot.get('papers_collected'), '0')}편**",
        f"- Evidence Table 행 수: **{fmt(snapshot.get('evidence_rows'), '0')}행**",
        f"- 생성 샘플 수(파이프라인 검증용): **{fmt(snapshot.get('mock_samples_generated'), '0')}개**",
        "",
        "## 자동화 상태",
        f"- 연구 루프(1분): **{_cron_field(cron, 'continuous', 'status')}**",
        f"- 중요상황 상시 보고(1분): **{_cron_field(cron, 'live_report', 'status')}**",
        f"- 최근 연구 루프 결과: **{_cron_field(cron, 'continuous', 'lastRunStatus')}**",
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
