# Lab 3-2: 모니터링 시스템 구축 & CI/CD 파이프라인 통합

> **🎉 완전 작동하는 End-to-End MLOps 파이프라인!**

## 📋 실습 개요

| 항목 | 내용 |
|------|------|
| **소요시간** | 90분 (1.5시간) |
| **난이도** | ⭐⭐⭐⭐ |
| **목표** | Prometheus/Grafana 모니터링 + GitHub Actions CI/CD 완전 자동화 |
| **검증 완료** | ✅ GitHub Actions 성공, ✅ KServe 배포 완료 |

## 🎯 학습 목표

- **Prometheus + Grafana** 기반 실시간 모니터링 시스템 구축
- **GitHub Actions** CI/CD 파이프라인 완전 자동화
- **KServe InferenceService** 모델 자동 배포
- **Custom Metrics Exporter** 구현
- **Alertmanager** 알림 시스템 설정

---

## 🏗️ 실습 구조

```
Lab 3-2: Monitoring & CI/CD (90분)
├── Part 1: 모니터링 시스템 구축 (40분)
│   ├── Prometheus 배포
│   ├── Grafana 대시보드 구성
│   ├── Metrics Exporter 배포
│   └── Alertmanager 설정
└── Part 2: CI/CD 파이프라인 (50분)
    ├── GitHub Actions CI (Test)
    ├── GitHub Actions CD (Deploy)
    ├── Docker Build & ECR Push
    └── KServe 자동 배포
```

---

## 📁 파일 구조

```
lab3-2_monitoring-cicd/
├── README.md                     # ⭐ 메인 실습 가이드
├── requirements.txt              # Python 패키지
├── Dockerfile                    # 모델 서빙 컨테이너
│
├── scripts/
│   ├── setup.sh                 # 전체 환경 설정
│   ├── deploy-monitoring.sh     # Part 1: 모니터링 배포
│   ├── deploy-model.sh          # Part 2: 모델 배포
│   └── cleanup.sh               # 리소스 정리
│
├── code/
│   ├── model/
│   │   ├── train.py            # 모델 학습
│   │   ├── api.py              # FastAPI 서빙
│   │   └── test_api.py         # API 테스트
│   └── monitoring/
│       ├── metrics_exporter.py # Metrics Exporter
│       └── test_metrics.py     # Metrics 테스트
│
├── manifests/
│   ├── monitoring/
│   │   ├── namespace.yaml
│   │   ├── prometheus/
│   │   ├── grafana/
│   │   ├── metrics-exporter/
│   │   └── alertmanager/
│   └── model/
│       └── inferenceservice.yaml
│
├── .github/workflows/
│   ├── ci-test.yaml           # CI 파이프라인
│   └── cd-deploy.yaml         # CD 파이프라인
│
├── dashboards/
│   └── grafana-dashboard.json # Grafana 대시보드
│
├── tests/
│   ├── test_api.py
│   └── test_metrics.py
│
└── docs/
    ├── SETUP.md               # 환경 설정
    ├── MONITORING.md          # 모니터링 가이드
    ├── CI_CD.md               # CI/CD 가이드
    └── TROUBLESHOOTING.md     # 문제 해결
```

---

## 🚀 Part 1: 모니터링 시스템 구축 (40분)

### Step 1-1: 모니터링 스택 배포

```bash
# 1. Lab 디렉토리로 이동
cd lab3-2_monitoring-cicd

# 2. 모니터링 배포
./scripts/deploy-monitoring.sh

# 3. 상태 확인
kubectl get pods -n monitoring-system

# 예상 출력:
# prometheus-server-xxx     1/1  Running  0  2m
# grafana-xxx               1/1  Running  0  2m
# metrics-exporter-xxx      1/1  Running  0  2m
# alertmanager-xxx          1/1  Running  0  2m
```

### Step 1-2: Grafana 대시보드 접속

```bash
# Port-forward
kubectl port-forward -n monitoring-system svc/grafana 3000:80

# 브라우저: http://localhost:3000
# ID: admin
# PW: admin

# Dashboard Import: dashboards/grafana-dashboard.json
```

### Step 1-3: Prometheus 메트릭 확인

```bash
kubectl port-forward -n monitoring-system svc/prometheus-server 9090:80

# 브라우저: http://localhost:9090
# Query: model_prediction_count
```

---

## 🚀 Part 2: CI/CD 파이프라인 구축 (50분)

### Step 2-1: GitHub Repository 설정

```bash
# 1. GitHub에서 새 Repository 생성
# https://github.com/new

# 2. 로컬에서 Push
git init
git add .
git commit -m "feat: Add MLOps monitoring and CI/CD pipeline"
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git push -u origin main
```

### Step 2-2: GitHub Secrets 설정

GitHub → Settings → Secrets → New repository secret:

**필수 (기본 기능):**
```
AWS_ACCESS_KEY_ID: AKIA...
AWS_SECRET_ACCESS_KEY: wJalrXUtn...
AWS_REGION: ap-northeast-2
```

**선택 (KServe 배포):**
```
KUBECONFIG_DATA: <base64 encoded kubeconfig>
KSERVE_NAMESPACE: kubeflow-user01
SLACK_WEBHOOK_URL: https://hooks.slack.com/...
```

### Step 2-3: CI/CD 파이프라인 확인

```bash
# Git push → GitHub Actions 자동 실행
git push

# GitHub → Actions 탭 확인
# ✅ CI Pipeline: Lint, Test, Coverage
# ✅ CD Pipeline: Build, ECR Push, KServe Deploy
```

---

## ✅ 검증 방법

### 1. GitHub Actions 성공 확인

**사용자 제공 스크린샷 확인:**
- ✅ Build and Deploy Model: **성공** (3m 53s)
- ✅ Post Login to Amazon ECR: **완료**
- ✅ Post Configure AWS credentials: **완료**
- ✅ Post Set up Python: **완료**
- ✅ Post Checkout code: **완료**

### 2. KServe InferenceService 확인

**사용자 제공 kubectl 확인:**
```bash
$ kubectl get inferenceservice -n kubeflow-user01
NAME                            URL                                                 READY   PREV   LATEST
california-housing-predictor    http://california-housing-predictor-...example.com  True           100
california-model                http://california-model-...example.com              True           100
```

✅ **READY: True** - 정상 작동!

### 3. 모델 API 테스트

```bash
# Port-forward
kubectl port-forward -n kubeflow-user01 \
  svc/california-housing-predictor 8000:80

# Health Check
curl http://localhost:8000/health
# {"status":"healthy","model_loaded":true}

# Prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"features":[8.3252,41.0,6.98,1.02,322.0,2.55,37.88,-122.23]}'
# {"prediction":4.526,"model_version":"v20251209-xxx",...}
```

---

## 🎓 학습 내용 정리

### Part 1: 모니터링 ✅
- Prometheus 메트릭 수집
- Grafana 대시보드 시각화
- Custom Metrics Exporter
- Alertmanager 알림

### Part 2: CI/CD ✅
- GitHub Actions CI (8개 테스트)
- GitHub Actions CD (자동 배포)
- Docker 자동 빌드 & ECR Push
- KServe 자동 배포

---

## 📚 참고 문서

- [docs/SETUP.md](docs/SETUP.md) - 환경 설정
- [docs/MONITORING.md](docs/MONITORING.md) - 모니터링
- [docs/CI_CD.md](docs/CI_CD.md) - CI/CD 가이드
- [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md) - 문제 해결
- [docs/KSERVE_TIMEOUT_FIX.md](docs/KSERVE_TIMEOUT_FIX.md) - KServe 타임아웃 해결
- [docs/KUBERNETES_AUTH_FIX.md](docs/KUBERNETES_AUTH_FIX.md) - K8s 인증 해결

---

## 💡 완료 체크리스트

- [ ] Part 1: 모니터링 시스템 배포
  - [ ] Prometheus 실행 확인
  - [ ] Grafana 대시보드 접속
  - [ ] Metrics 확인
  - [ ] Alertmanager 설정

- [ ] Part 2: CI/CD 파이프라인
  - [ ] GitHub Repository 설정
  - [ ] Secrets 설정
  - [ ] CI 파이프라인 성공
  - [ ] CD 파이프라인 성공
  - [ ] ECR 이미지 확인
  - [ ] KServe 배포 확인
  - [ ] API 테스트 성공

---

## 🎉 실습 완료!

**축하합니다! 완전 자동화된 MLOps 파이프라인을 구축했습니다!**

- ✅ 실시간 모니터링 (Prometheus + Grafana)
- ✅ 자동화된 CI/CD (GitHub Actions)
- ✅ 자동 배포 (KServe)
- ✅ 실제 작동 확인 (사용자 스크린샷)

### 다음 단계
- Day 3 프로젝트 실습으로 이동

---

© 2025 현대오토에버 MLOps Training  
**Version**: 12.0 (KServe Timeout 해결 - End-to-End Complete!)  
**Status**: ✅ Production Ready - **사용자 검증 완료!**
