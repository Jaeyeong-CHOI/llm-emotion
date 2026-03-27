# 📡 실시간 연구 진행 현황 (llm-emotion)

- 마지막 갱신: **2026-03-27 12:59:26 (Asia/Seoul)**
- 마지막 실행: **2026-03-27T03:59:26Z**
- 마지막 성공: **2026-03-27T03:59:26Z**
- 총 샘플 수(N): **8,038** (60 batches, 39 models)
- 조건별: deprivation=2,652 / counterfactual=2,643 / neutral=2,636

## 최신 LME 결과 (Cycle 74 — confirmed stable)
- embedding_regret_bias: beta_D=0.176 (z=56.05, p<.001), beta_C=0.231 (z=71.66, p<.001)
- regret_rate: beta_D=0.241 (z=5.85), beta_C=0.214 (z=5.07), beta_rum=0.258 (z=10.57) all p<.001
- CF rate: beta_D=0.233 (z=4.14), beta_C=0.684 (z=11.86) all p<.001

## Cycle 74 작업 내역
- LME re-run on N=8,038: all coefficients confirmed stable (identical to Cycle 73)
- Batch v45 partial: gpt-5-pro neutral 23/21 samples collected; deprivation/counterfactual API timeout (gpt-5-pro slow)
- v45 partial data committed; embedding computation deferred (conditions incomplete)
- Paper main.tex: already up-to-date (no changes needed)

## 모델 안정화 상태
- 완전 안정(n>=30/cond): 37/39
- 미완 (preliminary): gpt-5-pro (n_N=32+, n_D=15), gpt-5.3-chat-latest (n_D=27)
- gpt-5-pro API 응답 지연으로 v45 deprivation/counterfactual 수집 실패

## 현재 단계 요약
- [x] 체계적 선행연구 수집 파이프라인 구축
- [x] 실모델 API 기반 본실험 데이터 수집 (N=8,038)
- [x] LME 분석 (60 batches, 39 models) — confirmed stable
- [x] Cross-model replication (39/39 D>N; 37 fully stable)
- [x] Paper: IEEE 8p, stats up-to-date, compiled
- [ ] gpt-5-pro stabilization (n_D=15 -> 30 needed; API timeout issue)
- [ ] Inter-rater reliability expansion (kappa=0.44, N=36)

> 이 파일은 자동 갱신됩니다.
