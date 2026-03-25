# 📡 실시간 연구 진행 현황 (llm-emotion)

- 마지막 갱신: **2026-03-25 22:43:00 (Asia/Seoul 기준 로컬 실행 시각)**
- 마지막 실행: **2026-03-25T22:43:00**
- 마지막 성공: **2026-03-25T22:43:00**
- 전체 샘플 수: **N=4,539** (neutral=1,572 / deprivation=1,513 / counterfactual=1,454)
- 모델 수: **20 variants across 6 families** (Groq Compound/Compound-Mini 추가)
- LME N: **4,539 (30 batches)**

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
- Semantic dissociation confirmed: embedding_regret_bias β=0.148, z=18.34, p<.001
- CF rate (deprivation) n.s. (p=0.382) — 의도적 음성 결과
- Cross-model: D>N in ALL 19 tabulated models (incl. Groq Compound d=4.23, Compound-Mini d=4.78)
- LOSO: 42 scenarios all positive for embedding bias

> 이 파일은 자동 갱신됩니다.
