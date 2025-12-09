# 🚀 MLOps Training Labs - 현대오토에버

> **MLOps 파이프라인 구현 [고급]** - 3일 24시간 실습 자료

## 📋 교육 개요

| 항목 | 내용 |
|------|------|
| **교육명** | MLOps 파이프라인 구현 [고급] |
| **기간** | 3일 (24시간) |
| **대상** | 데이터사이언티스트 & 데이터엔지니어 |
| **환경** | AWS EKS + Kubeflow + MLflow + KServe |

## 📁 Repository 구조

```
mlops-training-labs/
├── README.md                    # 이 파일
├── docs/                        # 문서
│   ├── SETUP.md                # 환경 설정 가이드
│   └── TROUBLESHOOTING.md      # 트러블슈팅 가이드
├── scripts/                     # 설정 스크립트
│   ├── setup-env.sh            # 환경 변수 설정
│   ├── aws-configure.sh        # AWS CLI 설정
│   └── cleanup.sh              # 리소스 정리
├── day1/                        # 1일차 실습
│   ├── lab1-1_aws-eks-setup/   # AWS EKS 환경 설정
│   ├── lab1-2_kubeflow-access/ # Kubeflow 대시보드 접속
│   ├── lab1-3_jupyter-setup/   # Jupyter Notebook 설정
│   └── lab1-4_hello-pipeline/  # Hello World 파이프라인
├── day2/                        # 2일차 실습
│   ├── lab2-1_fastapi-serving/ # FastAPI 모델 서빙
│   ├── lab2-2_mlflow-tracking/ # MLflow Tracking & Registry
│   └── lab2-3_kserve-deploy/   # KServe 배포
├── day3/                        # 3일차 실습
│   ├── lab3-1_monitoring/      # Prometheus/Grafana 모니터링
│   └── lab3-2_e2e-pipeline/    # E2E 파이프라인 통합
├── project/                     # 조별 프로젝트
│   ├── template/               # 프로젝트 템플릿
│   └── examples/               # 예제 솔루션
└── manifests/                   # Kubernetes YAML
    ├── deployments/            # Deployment 매니페스트
    ├── services/               # Service 매니페스트
    └── kserve/                 # KServe InferenceService
```

## 🛠️ 사전 준비

### 필수 설치 도구

| 도구 | 최소 버전 | 설치 확인 |
|------|----------|----------|
| AWS CLI | 2.x | `aws --version` |
| kubectl | 1.24+ | `kubectl version --client` |
| Docker | 20.x+ | `docker --version` |
| Python | 3.9+ | `python --version` |
| Git | 2.x+ | `git --version` |

### 환경 설정

```bash
# 1. Repository 클론
git clone https://github.com/[org]/mlops-training-labs.git
cd mlops-training-labs

# 2. 환경 변수 설정 (사용자 번호 수정!)
export USER_NUM="01"  # 본인 번호로 변경
source scripts/setup-env.sh

# 3. AWS 자격 증명 설정
./scripts/aws-configure.sh

# 4. EKS 클러스터 연결
aws eks update-kubeconfig --name mlops-training-cluster --region ap-northeast-2
```

## 📅 실습 목록

### Day 1: MLOps 엔지니어링 심화 & 데이터 파이프라인

| 실습 | 제목 | 소요시간 | 난이도 |
|------|------|----------|--------|
| Lab 1-1 | AWS EKS 환경 설정 | 30분 | ⭐ |
| Lab 1-2 | Kubeflow 대시보드 접속 | 15분 | ⭐ |
| Lab 1-3 | Jupyter Notebook 설정 | 20분 | ⭐ |
| Lab 1-4 | Hello World 파이프라인 | 40분 | ⭐⭐ |

### Day 2: 모델 서빙 & 버전 관리

| 실습 | 제목 | 소요시간 | 난이도 |
|------|------|----------|--------|
| Lab 2-1 | FastAPI 모델 서빙 | 50분 | ⭐⭐ |
| Lab 2-2 | MLflow Tracking & Registry | 60분 | ⭐⭐ |
| Lab 2-3 | KServe 배포 | 40분 | ⭐⭐⭐ |

### Day 3: 모니터링 & 프로젝트

| 실습 | 제목 | 소요시간 | 난이도 |
|------|------|----------|--------|
| Lab 3-1 | Prometheus/Grafana 모니터링 | 40분 | ⭐⭐ |
| Lab 3-2 | E2E 파이프라인 통합 | 60분 | ⭐⭐⭐ |
| Project | 조별 프로젝트 | 50분 | ⭐⭐⭐⭐ |

## 🔧 빠른 시작

```bash
# Day 1 - Hello World 파이프라인
cd day1/lab1-4_hello-pipeline
python hello_pipeline.py

# Day 2 - MLflow Tracking
cd day2/lab2-2_mlflow-tracking
python mlflow_experiment.py

# Day 3 - E2E 파이프라인
cd day3/lab3-2_e2e-pipeline
python e2e_pipeline.py
```

## 📚 추가 자료

- [Kubeflow 공식 문서](https://www.kubeflow.org/docs/)
- [MLflow 공식 문서](https://mlflow.org/docs/latest/index.html)
- [KServe 공식 문서](https://kserve.github.io/website/)
- [AWS EKS 사용 가이드](https://docs.aws.amazon.com/eks/)

## ⚠️ 주의사항

1. **네임스페이스**: 항상 자신의 네임스페이스(`kubeflow-userXX`)에서 작업
2. **리소스 정리**: 실습 후 반드시 리소스 정리 (`scripts/cleanup.sh`)
3. **비용**: AWS 리소스는 비용이 발생하므로 미사용 시 정리


---

© 2025 현대오토에버 MLOps Training
