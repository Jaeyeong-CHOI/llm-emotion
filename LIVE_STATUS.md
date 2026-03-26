# 📡 실시간 연구 진행 현황 (llm-emotion)

- 마지막 갱신: **2026-03-27 05:11:37 (Asia/Seoul 기준 로컬 실행 시각)**
- 마지막 실행: **2026-03-26T20:11:37Z**
- 마지막 성공: **2026-03-26T20:11:37Z**
- 실험 샘플 수(실모델): **7,440 (53 batches, 37 models)**
- 수집 논문 수(후보): **279편**

## 핵심 통계 요약
- N=7,440 | 조건: neutral=2,490 / deprivation=2,436 / counterfactual=2,514
- 모델 수: 37 (7개 기관)
- LME (embedding_regret_bias): cond_D β=0.179 (z=52.21, p<0.001), cond_C β=0.243 (z=70.17, p<0.001)
- Crossed-RE 검증: cond_D β=0.172 (z=58.6), cond_C β=0.228 (z=77.1) — 견고성 확인됨
- Ablation: minimal-pair combined d=2.52 (CF), d=0.90 (dep), N=196
- Inter-rater: Cohen κ=0.44 (human vs GPT-4o, N=36)

## 논문 상태
- paper/main.tex: IEEE 8p, 최신 통계 반영 완료
- paper/main.pdf: 정상 컴파일 (155KB, 경미한 layout warning만 존재)
- 핵심 발견: semantic-layer dissociation (embedding bias p<0.001; lexical divergence by framing type)

## 자동화 상태
- 연구 루프: **completed (Cycle 55)**
- LME 재검증: **2026-03-27 완료**
- PDF 재컴파일: **2026-03-27 완료**

## 완료 단계
- [x] 실험 데이터 수집 (N=7,440, 37 models)
- [x] LME 확인적 분석 (scenario random intercept + crossed RE)
- [x] Embedding metric (sentence-transformer)
- [x] Inter-rater reliability (κ=0.44)
- [x] Ablation (minimal-pair N=196)
- [x] Explicit-instruction baseline (batch v38, N=107)
- [x] LOSO 분석 (42 scenarios, mean β=0.165)
- [x] 논문 초안 완성 (IEEE 8p)

> 이 파일은 자동 갱신됩니다.
