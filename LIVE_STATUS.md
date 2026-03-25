# 📡 실시간 연구 진행 현황 (llm-emotion)

- 마지막 갱신: **2026-03-26 03:53:00 (Asia/Seoul 기준 로컬 실행 시각)**
- 마지막 실행: **2026-03-26T03:53:00**
- 마지막 성공: **2026-03-26T03:53:00**
- 전체 샘플 수: **N=5,196** (neutral=1,800 / deprivation=1,730 / counterfactual=1,666)
- 모델 수: **25 variants across 7 families** (batch v20: GPT-OSS-Safeguard-20B 추가)
- LME N: **5,196 (34 batches)**

## 자동화 상태
- 연구 루프: **enabled**
- 최근 연구 루프 결과: **ok**

## 현재 단계 요약
- [x] 체계적 선행연구 수집 파이프라인 구축
- [x] 증거표(Evidence Table) 자동 생성
- [x] 실모델 API 기반 본실험 데이터 수집 (N=5,196)
- [x] 통계 검정(LME + Welch t, LOSO)
- [x] embedding metric migration (bag-of-words → sentence-transformer)
- [x] 논문 초안 v5 (IEEE 8p, paper/main.tex + main.pdf)
- [x] Cross-model replication: 25 models, 7 families (OpenAI/Google/Meta/Alibaba/MoonshotAI/Groq/SDAIA)
- [x] batch v20: GPT-OSS-Safeguard-20B (n=49, d_DN=4.73) 추가
- [x] LME 전체 N=5,196 재분석 완료 (34 batches)
- [x] 논문 N/stats 업데이트 + PDF 재컴파일
- [ ] Mistral/DeepSeek 추가 replication (GROQ API 필요)
- [ ] LOSO 재실행 (N=5,196 기준)

## 핵심 결과 요약
- Semantic dissociation confirmed: embedding_regret_bias β=0.148, z=21.83, p<.001
- CF rate (deprivation) n.s. (p=0.286) — 의도적 음성 결과
- Cross-model: D>N in ALL 25 tabulated models
- Welch t: embedding d=1.89 (t=56.16); CF rate d=0.65; regret rate d=0.59; negemo d=0.40
- LOSO: 42 scenarios all positive for embedding bias
- GPT-OSS-Safeguard-20B (safety model): d_DN=4.73 — safety fine-tuning 무관하게 강력한 효과

> 이 파일은 자동 갱신됩니다.
