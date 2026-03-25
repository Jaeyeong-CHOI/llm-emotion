# 📡 실시간 연구 진행 현황 (llm-emotion)

- 마지막 갱신: **2026-03-25 20:30:09 (Asia/Seoul 기준 로컬 실행 시각)**
- 마지막 실행: **2026-03-25T20:30:09**
- 마지막 성공: **2026-03-25T20:30:09**
- 전체 샘플 수: **N=4,381** (neutral=1,500 / deprivation=1,460 / counterfactual=1,421) (neutral=1,439 / deprivation=1,423 / counterfactual=1,386)
- 모델 수: **18 variants across 5 families**
- LME N: **4,381 (29 batches)**

## 자동화 상태
- 연구 루프: **enabled**
- 최근 연구 루프 결과: **ok**

## 현재 단계 요약
- [x] 체계적 선행연구 수집 파이프라인 구축
- [x] 증거표(Evidence Table) 자동 생성
- [x] 실모델 API 기반 본실험 데이터 수집 (N=4,248)
- [x] 통계 검정(LME + Welch t, LOSO)
- [x] embedding metric migration (bag-of-words → sentence-transformer)
- [x] 논문 초안 v4 (IEEE 8p, paper/main.tex + main.pdf)
- [x] Cross-model replication: 18 models, 5 families
- [ ] Mistral/DeepSeek 추가 replication (GROQ API 필요)

## 핵심 결과 요약
- Semantic dissociation confirmed: embedding_regret_bias β=0.142, z=12.69, p<.001
- CF rate (deprivation) n.s. (p=0.204) — 의도적 음성 결과
- Cross-model: D>N in ALL 17 tabulated models
- LOSO: 42 scenarios all positive for embedding bias

> 이 파일은 자동 갱신됩니다.
