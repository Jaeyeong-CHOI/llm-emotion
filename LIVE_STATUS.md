# 📡 실시간 연구 진행 현황 (llm-emotion)

- 마지막 갱신: **2026-03-27 17:15:35 (Asia/Seoul)**
- LME N: **8,299** (65 batches, 39 models)
- 조건별: deprivation=2,755 / counterfactual=2,737 / neutral=2,700

## API 상태 (2026-03-27)
- ❌ OpenAI: **quota exhausted** (insufficient_quota 429)
- ❌ Gemini: **key leaked** (403 PERMISSION_DENIED)
- ✅ Groq: **operational** (llama, qwen, kimi, compound, allam)

## 잔여 thin cells (n<30)
| 모델 | 조건 | n |
|------|------|---|
| gpt-5-pro | counterfactual | 25 |
| gpt-5.3-chat-latest | deprivation | 27 |
| gpt-5.3-chat-latest | counterfactual | 27 |
| gpt-5.3-chat-latest | neutral | 27 |

> ⚠️ 위 셀 보충은 OpenAI API 복구 후 batch v52로 진행 예정 (+14 samples → N=8,313)

## 핵심 결과 (현재 안정)
- ERB LME: β_D=0.172 (p<0.001), β_C=0.229 (p<0.001)
- Crossed RE: β_D=0.169 (z=61.2), β_C=0.216 (z=77.3) → 강건
- Welch t (dep vs neutral): d=2.06 (embedding bias)
- 어휘 마커: LME에서 n.s. → semantic-layer dissociation 확인

## 현재 단계 요약
- [x] 체계적 선행연구 수집 파이프라인 구축
- [x] 실모델 API 기반 본실험 데이터 수집 (N=8,299)
- [x] LME + Crossed RE 확인 분석
- [x] Sentence-transformer embedding metric
- [x] Inter-rater reliability (κ=0.44)
- [x] 논문 초안 (paper/main.tex, IEEE 8p)
- [ ] Thin cell 보충 (OpenAI API 복구 대기)
- [ ] 최종 peer review 제출 준비

> batch v52 스크립트 준비 완료 (scripts/run_batch_v52_thin_cell_fill.py)
> OpenAI API 복구 후 즉시 실행 가능
