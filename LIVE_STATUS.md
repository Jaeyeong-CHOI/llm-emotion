# 📡 실시간 연구 진행 현황 (llm-emotion)

- 마지막 갱신: **2026-03-27 06:47:26 (Asia/Seoul 기준 로컬 실행 시각)**
- 마지막 실행: **2026-03-26T21:47:26Z**
- 마지막 성공: **2026-03-26T21:47:26Z**
- 수집 논문 수(후보): **279편**
- Evidence Table 행 수: **279행**
- 생성 샘플 수(전체 파이프라인 누계): **14,262개**

## 자동화 상태
- 연구 루프(1분): **enabled**
- 중요상황 상시 보고(1분): **missing**
- 최근 연구 루프 결과: **ok**

## 현재 단계 요약
- [x] 체계적 선행연구 수집 파이프라인 구축
- [x] 증거표(Evidence Table) 자동 생성
- [x] 연구 자동 루프 + 상태 추적 구축
- [x] 실모델 API 기반 본실험 데이터 수집 (N=14,262 누계)
- [x] LME 통계 검정 완료 (N=7,524, 56 batches, β_D=0.179 p<.001, β_C=0.242 p<.001)
- [x] 논문 초안 작성 및 PDF 컴파일 (paper/main.pdf, 8p IEEE)
- [x] batch v39 임베딩 계산 + LME 편입 완료 (N 7,440→7,524)
- [ ] 핵심 논문(코어셋) 정밀 스크리닝 완료
- [ ] 추가 모델 확장 및 재현 검증

## 주요 통계 (최신)
- N_total: 14,262 samples / 38+ models
- LME core (N=7,524): embedding regret bias — cond_D β=0.179 z=53.41, cond_C β=0.242 z=71.58, both p<.001
- Ruminative persona: regret_rate β=0.259 z=10.42 (strongest predictor)
- Inter-rater κ=0.44 (human vs GPT-4o, N=36)
- Ablation (N=196): combined d=2.52 (CF), d=0.90 (dep)

> 이 파일은 자동 갱신됩니다. (scripts/update_live_status.py가 최근 상태/크론 결과를 갱신)
