# 📡 실시간 연구 진행 현황 (llm-emotion)

- 마지막 갱신: **2026-03-27 04:43 (Asia/Seoul)**
- 현재 단계: **논문 완성 / 제출 준비**

## 데이터 현황
- 전체 N: **7,440** (53 batches, 37 models, 7 organizations)
- Conditions: neutral=2,490 / deprivation=2,436 / counterfactual=2,514 (balanced)
- 모델 수: 37 (GPT-5 family, Gemini-3, Llama-3.3, Qwen3, o1/o3/o4, Groq, Allam 포함)

## 핵심 결과 (LME, N=7,440)
- Embedding regret bias (dep): β=0.179, z=52.21, p<0.001
- Embedding regret bias (CF): β=0.243, z=70.17, p<0.001
- CF rate (dep): β=0.236, z=3.90, p<0.001
- CF rate (CF cond): β=0.656, z=10.83, p<0.001
- Regret-word rate (dep): β=0.220, z=4.80, p<0.001
- 모든 LME 대비 p<0.001 확인됨

## 논문 상태
- paper/main.tex: 684줄, IEEE 8p format — **제출 준비 완료**
- paper/acl_main.tex: ACL/EMNLP 포맷 버전 — 완료
- 빌드: 오류 없음 (overfull hbox 3건, <4pt — 무시 가능)
- Critique Cycle: **53** (완료)

## 완료된 작업
- [x] Embedding metric migration (bag-of-words → sentence-transformer)
- [x] Inter-rater reliability (κ=0.44, N=36)
- [x] 전 조건 balanced (N≥2,436)
- [x] LME 전체 N=7,440 재분석 완료
- [x] Ablation analysis (N=196, CF d=2.52, dep d=0.90)
- [x] LOSO analysis (42 scenarios, stable β)
- [x] Explicit-instruction baseline (batch v38, N=107)
- [x] Length-sensitivity analysis (condition effect <2% attenuated by length)
- [x] CF off-topic audit at scale (22.7%, vs 50% subsample artifact)
- [x] 논문 ACL/EMNLP 포맷 변환
- [x] Korean font warning 제거 (Cycle 50)
- [x] Cycle 53 health check — 모든 stats verified, overfull hbox <4pt (non-blocking)

## 다음 단계 (선택)
- [ ] Venue 결정 후 제출 (ACL 2026 / EMNLP 2026)
- [ ] Mistral/DeepSeek 추가 → 범용성 강화 (optional)
