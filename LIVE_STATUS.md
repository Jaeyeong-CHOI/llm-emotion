# 📡 실시간 연구 진행 현황 (llm-emotion)

- 마지막 갱신: **2026-03-27 21:52:00 (Asia/Seoul)**
- LME N: **8,317** (65 batches, 39 models)
- 조건별: deprivation=2,758 / counterfactual=2,749 / neutral=2,703

## API 상태 (2026-03-27)
- ❌ OpenAI: **quota exhausted** (insufficient_quota 429)
- ❌ Gemini: **key leaked** (403 PERMISSION_DENIED)
- ✅ Groq: **operational** (llama, qwen, kimi, compound, allam)

## 🐛 버그 수정 (Cycle 89)
> **임베딩 키 버그 수정**: `compute_embedding_bias.py`가 `output`/`text` 키만 읽고 `response` 키를 무시함
> 배치 v36/v40/v45/v46/v47/v49 (8개 배치, 238개 샘플)의 임베딩이 모두 0.0이었음
> 수정 후 gpt-5-pro d_DN: 0.24 → **2.22** (거짓 평탄값 → 실제 효과)
> 전체 d 범위: 0.42–1.86 → **0.42–5.03** 으로 확장

## 핵심 결과 (수정 후 최종값)
- ERB LME: **β_D=0.179** (z=58.13, p<.001), **β_C=0.230** (z=72.45, p<.001)
- Crossed RE: β_D=0.176 (z=64.7), β_C=0.221 (z=80.2) → 강건
- Welch d: dep d=2.11, cf d=2.43 (embedding bias)
- 어휘 마커: LME에서 모두 p<0.001 (cf_rate, regret_rate, negemo_rate)
- 모델별 d 범위: **0.42–5.03** (39모델 전부 D>N)

## 모델 상태
| 항목 | 값 |
|------|-----|
| 전체 모델 수 | 39 |
| 완전 안정 (n≥30/조건) | **39/39** (모두 안정) |
| CF>N with CI\≠0 | 38/39 (예외: GPT-5.4-mini d_CN=0.07) |

## 현재 단계 요약
- [x] 체계적 선행연구 수집 파이프라인 구축
- [x] 실모델 API 기반 본실험 데이터 수집 (N=8,317, 65 batches, 39 models)
- [x] LME + Crossed RE 확인 분석
- [x] Sentence-transformer embedding metric
- [x] Inter-rater reliability (κ=0.44)
- [x] Ablation (minimal-pair N=196, CF d=2.52, dep d=0.90)
- [x] 논문 초안 (paper/main.tex, IEEE 8p) — PDF 컴파일 완료
- [x] **임베딩 키 버그 수정 + LME/모델 d 재계산** (Cycle 89)
- [x] **모든 셀 n≥30 안정** (39/39)
- [ ] OpenAI API 복구 후 추가 확장 (선택 사항)
- [ ] 최종 peer review 제출 준비

> 다음 우선과제: 논문 최종 점검 및 제출 준비 (논문 내 수치 일관성 최종 검토 권장)
