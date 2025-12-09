# Lab 2-2: MLflow Tracking & Model Registry

## 📋 실습 개요

| 항목 | 내용 |
|------|------|
| **소요시간** | 60분 |
| **난이도** | ⭐⭐ |
| **목표** | MLflow로 실험 추적 및 모델 관리 |

## 🎯 학습 목표

- MLflow Tracking Server 배포
- 실험 추적 및 파라미터 로깅
- Model Registry 사용
- S3에 모델 저장

## 🚀 실습 단계

### Step 1: MLflow 배포

```bash
cd scripts
./deploy_mlflow.sh
```

### Step 2: 실험 실행

```bash
python mlflow_experiment.py
```

### Step 3: MLflow UI 확인

```bash
kubectl port-forward svc/mlflow-server-service -n mlflow-system 5000:5000
# 브라우저: http://localhost:5000
```

## ✅ 완료 체크리스트

- [ ] MLflow 서버 배포
- [ ] 실험 실행
- [ ] MLflow UI 접속
- [ ] Model Registry 확인
