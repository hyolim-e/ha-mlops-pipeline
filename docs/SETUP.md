# 🔧 환경 설정 가이드

## 📋 목차

1. [사전 준비](#1-사전-준비)
2. [AWS CLI 설정](#2-aws-cli-설정)
3. [kubectl 설정](#3-kubectl-설정)
4. [Docker 설정](#4-docker-설정)
5. [Python 환경](#5-python-환경)
6. [Kubeflow 접속](#6-kubeflow-접속)

---

## 1. 사전 준비

### 필수 도구 설치

| 도구 | Windows | macOS | Linux |
|------|---------|-------|-------|
| AWS CLI | [설치 링크](https://aws.amazon.com/cli/) | `brew install awscli` | `apt install awscli` |
| kubectl | [설치 링크](https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/) | `brew install kubectl` | `snap install kubectl` |
| Docker | [Docker Desktop](https://www.docker.com/products/docker-desktop/) | [Docker Desktop](https://www.docker.com/products/docker-desktop/) | `apt install docker.io` |
| Python | [python.org](https://www.python.org/) | `brew install python` | `apt install python3` |
| Git | [git-scm.com](https://git-scm.com/) | `brew install git` | `apt install git` |

### 버전 확인

```bash
# AWS CLI
aws --version
# 예상: aws-cli/2.x.x ...

# kubectl
kubectl version --client
# 예상: Client Version: v1.28.x

# Docker
docker --version
# 예상: Docker version 24.x.x

# Python
python --version
# 예상: Python 3.9.x 이상

# Git
git --version
# 예상: git version 2.x.x
```

---

## 2. AWS CLI 설정

### Step 1: 자격 증명 설정

```bash
aws configure
```

입력 값:
```
AWS Access Key ID: [제공된 Access Key]
AWS Secret Access Key: [제공된 Secret Key]
Default region name: ap-northeast-2
Default output format: json
```

### Step 2: 확인

```bash
aws sts get-caller-identity
```

예상 출력:
```json
{
    "UserId": "AIDAXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/mlops-userXX"
}
```

---

## 3. kubectl 설정

### Step 1: EKS 클러스터 연결

```bash
aws eks update-kubeconfig \
    --region ap-northeast-2 \
    --name mlops-training-cluster
```

### Step 2: 연결 확인

```bash
# 클러스터 정보
kubectl cluster-info

# 노드 목록
kubectl get nodes

# 네임스페이스 목록
kubectl get namespaces
```

### Step 3: 기본 네임스페이스 설정 (선택)

```bash
# 본인의 네임스페이스를 기본으로 설정
kubectl config set-context --current --namespace=kubeflow-userXX
```

---

## 4. Docker 설정

### Step 1: Docker 실행 확인

```bash
docker info
```

### Step 2: ECR 로그인

```bash
# 환경 변수 설정
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
export AWS_REGION=ap-northeast-2

# ECR 로그인
aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin \
    ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
```

### Step 3: 테스트 빌드 (선택)

```bash
# 간단한 Dockerfile 테스트
echo 'FROM python:3.9-slim' > test.Dockerfile
docker build -f test.Dockerfile -t test .
rm test.Dockerfile
```

---

## 5. Python 환경

### Step 1: 가상 환경 생성 (권장)

```bash
# venv 사용
python -m venv mlops-env
source mlops-env/bin/activate  # Linux/macOS
# mlops-env\Scripts\activate   # Windows

# 또는 conda 사용
conda create -n mlops python=3.9
conda activate mlops
```

### Step 2: 필수 패키지 설치

```bash
pip install kfp==1.8.22 mlflow==2.9.2 scikit-learn pandas numpy
```

### Step 3: 설치 확인

```python
python -c "import kfp; print(f'KFP: {kfp.__version__}')"
python -c "import mlflow; print(f'MLflow: {mlflow.__version__}')"
python -c "import sklearn; print(f'sklearn: {sklearn.__version__}')"
```

---

## 6. Kubeflow 접속

### Step 1: 포트 포워딩

터미널 1 (열어둔 상태 유지):
```bash
kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80
```

터미널 2 (MLflow용, 선택):
```bash
kubectl port-forward svc/mlflow-server-service -n mlflow-system 5000:5000
```

### Step 2: 브라우저 접속

- **Kubeflow Dashboard**: http://localhost:8080
- **MLflow UI**: http://localhost:5000

### Step 3: 로그인

```
Email: userXX@example.com
Password: [제공된 비밀번호]
```

---

## 🔍 환경 검증 스크립트

모든 설정을 한번에 확인하려면:

```bash
#!/bin/bash

echo "=== Environment Verification ==="

# AWS CLI
echo -n "AWS CLI: "
aws --version 2>/dev/null && echo "✅" || echo "❌"

# kubectl
echo -n "kubectl: "
kubectl version --client 2>/dev/null && echo "✅" || echo "❌"

# Docker
echo -n "Docker: "
docker --version 2>/dev/null && echo "✅" || echo "❌"

# Python
echo -n "Python: "
python --version 2>/dev/null && echo "✅" || echo "❌"

# EKS Connection
echo -n "EKS Connection: "
kubectl get nodes 2>/dev/null && echo "✅" || echo "❌"

echo "=== Verification Complete ==="
```

---

## ⚠️ 주의사항

1. **네임스페이스**: 항상 자신의 네임스페이스(`kubeflow-userXX`)에서 작업
2. **포트 충돌**: 이미 사용 중인 포트가 있다면 다른 포트 사용
3. **VPN**: 회사 VPN 연결 필요 여부 확인
4. **방화벽**: 필요한 포트가 열려있는지 확인

---

