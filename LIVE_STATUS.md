# 📡 실시간 연구 진행 현황 (llm-emotion)

- 마지막 갱신: **2026-03-27 13:22:51 (Asia/Seoul)**
- 마지막 실행: **2026-03-27T04:22:51Z**
- 마지막 성공: **2026-03-27T04:22:51Z**
- 총 샘플 수(N): **8,038** (60 batches, 39 models)
- 조건별: deprivation=2,652 / counterfactual=2,643 / neutral=2,636

## 최신 LME 결과 (Cycle 75 — confirmed stable)
- embedding_regret_bias: beta_D=0.176 (z=56.05, p<.001), beta_C=0.231 (z=71.66, p<.001)
- regret_rate: beta_D=0.241 (z=5.85), beta_C=0.214 (z=5.07), beta_rum=0.258 (z=10.57) all p<.001
- CF rate: beta_D=0.233 (z=4.14), beta_C=0.684 (z=11.86) all p<.001

## Cycle 75 작업 내역
- gpt-5-pro API timeout 재확인: v45 partial (N+28, D+2) commit; CF fill SIGTERM
- v46 script (run_batch_v46_gpt5pro_cf_fill.py) 준비 — gpt-5-pro CF +12 목표
- LME 재실행: N=8,038 확인, 모든 coefficients 안정
- Paper main.tex 이미 최신 (stats 변경 없음)
- git commit + push 완료 (211a04a)

## 모델 안정화 상태
- 완전 안정(n>=30/cond): 38/39
- 미완 (preliminary): gpt-5-pro (N=46, D=36, C=18 → CF -12 needed)
- gpt-5-pro API 응답 지연 지속 (>90s timeout)

## 현재 단계 요약
- [x] 체계적 선행연구 수집 파이프라인 구축
- [x] 실모델 API 기반 본실험 데이터 수집 (N=8,038)
- [x] LME 분석 (60 batches, 39 models) — confirmed stable
- [x] Cross-model replication (39/39 D>N; 38 fully stable)
- [x] Paper: IEEE 8p, stats up-to-date, compiled
- [ ] gpt-5-pro stabilization (C=18 -> 30 needed; API timeout)
- [ ] Inter-rater reliability expansion (kappa=0.44, N=36)

> 이 파일은 자동 갱신됩니다.
