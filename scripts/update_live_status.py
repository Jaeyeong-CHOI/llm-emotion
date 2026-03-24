#!/usr/bin/env python3
import datetime
from zoneinfo import ZoneInfo

from research_ops_common import ROOT, STATE_PATH, display_value, get_nested_field, get_stats_snapshot, read_json_dict

CRON_STATE_PATH = ROOT / "ops" / "cron_runtime_status.json"
OUT_PATH = ROOT / "LIVE_STATUS.md"

fmt = display_value


def _build_status_lines(cron: dict[str, object]) -> list[str]:
    status_fields = [
        ("연구 루프(1분)", get_nested_field(cron, "continuous", "status")),
        ("중요상황 상시 보고(1분)", get_nested_field(cron, "live_report", "status")),
        ("최근 연구 루프 결과", get_nested_field(cron, "continuous", "lastRunStatus")),
    ]

    return [f"- {label}: **{value}**" for label, value in status_fields]


def main() -> None:
    state = read_json_dict(STATE_PATH)
    cron = read_json_dict(CRON_STATE_PATH)

    snapshot = get_stats_snapshot(state)
    now = datetime.datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M:%S")

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
        *_build_status_lines(cron),
        "",
        "## 현재 단계 요약",
        "- [x] 체계적 선행연구 수집 파이프라인 구축",
        "- [x] 증거표(Evidence Table) 자동 생성",
        "- [x] 연구 자동 루프 + 상태 추적 구축",
        "- [ ] 핵심 논문(코어셋) 정밀 스크리닝 완료",
        "- [ ] 실모델 API 기반 본실험 데이터 수집",
        "- [ ] 통계 검정 + 논문 초안",
        "",
        "> 이 파일은 자동 갱신됩니다. (scripts/update_live_status.py가 최근 상태/크론 결과를 갱신)",
    ]

    OUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
