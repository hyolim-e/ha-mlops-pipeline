# Lab 2-3: KServe 배포

## 📋 실습 개요

| 항목 | 내용 |
|------|------|
| **소요시간** | 40분 |
| **난이도** | ⭐⭐⭐ |
| **목표** | KServe로 프로덕션 모델 서빙 |

## 🎯 학습 목표

- KServe InferenceService 이해
- S3에서 모델 로드
- REST API를 통한 추론

## 🚀 실습 단계

### Step 1: AWS 자격증명 설정

```bash
export AWS_ACCESS_KEY_ID="<YOUR_KEY>"
export AWS_SECRET_ACCESS_KEY="<YOUR_SECRET>"

cd scripts
./setup_credentials.sh
```

### Step 2: InferenceService 배포

```bash
./deploy_kserve.sh
```

### Step 3: 추론 테스트

```bash
./test_inference.sh
```

## ✅ 완료 체크리스트

- [ ] AWS 자격증명 설정
- [ ] InferenceService 배포
- [ ] Pod Running 확인
- [ ] 추론 테스트 성공
