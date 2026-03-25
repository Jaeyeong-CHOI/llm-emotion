# 📡 실시간 연구 진행 현황 (llm-emotion)

- 마지막 갱신: **2026-03-26 02:33:00 (Asia/Seoul 기준 로컬 실행 시각)**
- 마지막 실행: **2026-03-26T02:33:00**
- 마지막 성공: **2026-03-26T02:33:00**
- 전체 샘플 수: **N=5,147** (neutral=1,784 / deprivation=1,712 / counterfactual=1,651)
- 모델 수: **24 variants across 7 families** (batch v19: Llama-3.1-8B, GPT-OSS-20B, Kimi/Allam fill-up)
- LME N: **5,147 (33 batches)**

## 자동화 상태
- 연구 루프: **enabled**
- 최근 연구 루프 결과: **ok**

## 현재 단계 요약
- [x] 체계적 선행연구 수집 파이프라인 구축
- [x] 증거표(Evidence Table) 자동 생성
- [x] 실모델 API 기반 본실험 데이터 수집 (N=5,147)
- [x] 통계 검정(LME + Welch t, LOSO)
- [x] embedding metric migration (bag-of-words → sentence-transformer)
- [x] 논문 초안 v5 (IEEE 8p, paper/main.tex + main.pdf)
- [x] Cross-model replication: 24 models, 7 families (OpenAI/Google/Meta/Alibaba/MoonshotAI/Groq/SDAIA)
- [x] batch v19 embedding 계산 완료 (N=437 → emb.jsonl)
- [x] LME 전체 N=5,147 재분석 완료
- [ ] Mistral/DeepSeek 추가 replication (GROQ API 필요)
- [ ] LOSO 재실행 (N=5,147 기준)

## 핵심 결과 요약
- Semantic dissociation confirmed: embedding_regret_bias β=0.146, z=21.06, p<.001
- CF rate (deprivation) n.s. (p=0.339) — 의도적 음성 결과 (이전 p=0.382에서 업데이트)
- Cross-model: D>N in ALL 24 tabulated models
- Welch t: embedding d=1.88 (t=55.51); CF rate d=0.65; regret rate d=0.58; negemo d=0.40
- LOSO: 42 scenarios all positive for embedding bias

> 이 파일은 자동 갱신됩니다.
