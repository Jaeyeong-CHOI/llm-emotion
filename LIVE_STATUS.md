# 📡 실시간 연구 진행 현황 (llm-emotion)

- 마지막 갱신: **2026-03-27 17:37:47 (Asia/Seoul)**
- LME N: **8,299** (65 batches, 39 models)
- 조건별: deprivation=2,755 / counterfactual=2,737 / neutral=2,700

## API 상태 (2026-03-27)
- ❌ OpenAI: **quota exhausted** (insufficient_quota 429)
- ❌ Gemini: **key leaked** (403 PERMISSION_DENIED)
- ✅ Groq: **operational** (llama, qwen, kimi, compound, allam)

## Thin Cell 상태 (2026-03-27 재검증)
> ✅ **모든 셀 n≥30 확인** — gpt-5-pro CF (n=65), gpt-5.3-chat-latest (n=57/조건) 포함
> 이전 LIVE_STATUS의 thin cell 경고는 오래된 스냅샷 기준이었음. 실제 데이터 재집계 결과 0개.

| 모델 | 조건 | n | 상태 |
|------|------|---|------|
| gpt-5-pro | counterfactual | 65 | ✅ |
| gpt-5.3-chat-latest | deprivation | 57 | ✅ |
| gpt-5.3-chat-latest | counterfactual | 57 | ✅ |
| gpt-5.3-chat-latest | neutral | 57 | ✅ |

> batch v52 스크립트는 더 이상 필요하지 않음 (모든 셀 이미 안정)

## 핵심 결과 (현재 안정)
- ERB LME: β_D=0.172 (p<0.001), β_C=0.229 (p<0.001)
- Crossed RE: β_D=0.169 (z=61.2), β_C=0.216 (z=77.3) → 강건
- Welch t (dep vs neutral): d=2.06 (embedding bias)
- 어휘 마커: LME에서 모두 p<0.001 (cf_rate, regret_rate, negemo_rate)

## 현재 단계 요약
- [x] 체계적 선행연구 수집 파이프라인 구축
- [x] 실모델 API 기반 본실험 데이터 수집 (N=8,299, 65 batches, 39 models)
- [x] LME + Crossed RE 확인 분석
- [x] Sentence-transformer embedding metric
- [x] Inter-rater reliability (κ=0.44)
- [x] Ablation (minimal-pair N=196, CF d=2.52, dep d=0.90)
- [x] 논문 초안 (paper/main.tex, IEEE 8p) — PDF 컴파일 완료
- [x] **모든 셀 n≥30 안정** (2026-03-27 재검증)
- [ ] OpenAI API 복구 후 추가 확장 (선택 사항)
- [ ] 최종 peer review 제출 준비

> 다음 우선과제: 논문 최종 점검 및 제출 준비
