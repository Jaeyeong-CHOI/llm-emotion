# 📡 실시간 연구 진행 현황 (llm-emotion)

- 마지막 갱신: **2026-03-27 07:28:44 (Asia/Seoul 기준 로컬 실행 시각)**
- 마지막 실행: **2026-03-26T22:28:44Z**
- 마지막 성공: **2026-03-26T22:28:44Z**
- LME N (core): **7,524** (D=2,463 / CF=2,541 / N=2,520)
- 총 데이터(EI 포함): **7,631**
- 모델 수: **38개** (37 stable + GPT-5.3-Chat preliminary; GPT-5-Pro n=8 미포함)
- 배치 수: **55 배치** (batch_v1~v39 포함)
- Key LME: embedding β_D=0.179, z=53.41, p<.001 / β_C=0.242, z=71.58, p<.001

## 자동화 상태
- 연구 루프: **enabled**
- 최근 LME 실행: **ok (Cycle 64 tick)**

## 현재 단계 요약
- [x] 체계적 선행연구 수집 파이프라인 구축
- [x] 증거표(Evidence Table) 자동 생성
- [x] 연구 자동 루프 + 상태 추적 구축
- [x] 실모델 API 기반 본실험 데이터 수집 (39개 모델 / 7,631 샘플)
- [x] LME 확인적 분석 완료 (N=7,524; 모든 대조 p<.001)
- [x] 임베딩 메트릭 마이그레이션 (sentence-transformer cosine bias)
- [x] 인터레이터 신뢰도 (Cohen κ=0.44, N=36)
- [x] Ablation 분석 (N=196, combined d=2.52 CF / d=0.90 dep)
- [x] 논문 초안 (paper/main.tex, IEEE 8p; ACL format도 보유)
- [ ] GPT-5-Pro 안정화 (현재 n=8; 목표 n≥30)

> 이 파일은 자동 갱신됩니다.
