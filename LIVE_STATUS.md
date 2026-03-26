# 📡 실시간 연구 진행 현황 (llm-emotion)

- 마지막 갱신: **2026-03-26 22:59:51**
- 마지막 실행: **2026-03-26T22:59:00**
- 마지막 성공: **2026-03-26T22:59:00**
- 현재 N: **7,494** (N=7,440 기존 + 54 배치 v38)
- 모델 수: **37 (+ GPT-4o EI 기준조건)**
- 최신 커밋: **5189184** (explicit-instruction baseline 추가)

## 자동화 상태
- 연구 루프(1분): **enabled**
- 중요상황 상시 보고(1분): **enabled**
- 최근 연구 루프 결과: **ok**

## 현재 단계 요약
- [x] 체계적 선행연구 수집 파이프라인 구축
- [x] 증거표(Evidence Table) 자동 생성
- [x] 연구 자동 루프 + 상태 추적 구축
- [x] 실모델 API 기반 본실험 데이터 수집 (N=7,440, 37 모델, 53 배치)
- [x] 통계 검정 + 논문 초안 (31 Critique Cycle 완료)
- [x] **Explicit-instruction baseline (batch v38, N=54)** — 31 사이클 요청 사항 완료
  - EI > CF > Dep > Neutral (임베딩 편향: 0.213 > 0.111 > 0.101 > -0.053)
  - 프레이밍 효과 = 직접 지시 이하 → 순수 instruction-following 아님 확인
  - Marker-type dissociation이 framing 조건 특이적임 확인
- [ ] 2차 인간 주석자 추가 (κ=0.44 개선)
- [ ] Mistral/DeepSeek 복제

> 이 파일은 자동 갱신됩니다.
