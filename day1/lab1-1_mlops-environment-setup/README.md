# Lab 1-1: MLOps 환경 구축

## 📋 실습 개요

| 항목 | 내용 |
|------|------|
| **소요시간** | 65분 |
| **난이도** | ⭐⭐ |
| **목표** | AWS EKS 기반 MLOps 플랫폼 구축 및 접속 확인 |

## 🎯 학습 목표

이 실습을 통해 다음을 학습합니다:
- **AWS EKS 클러스터** 연결 및 상태 확인
- **Kubeflow Pipelines** 설치 확인 및 Dashboard 접속
- **MLflow Tracking Server** 배포 확인
- **MinIO & PostgreSQL** 스토리지 구성 확인
- **MLOps 플랫폼** 전체 아키텍처 이해

---

## 🏗️ 실습 구조

```
Lab 1-1: MLOps 환경 구축 (65분)
│
├── 사전 준비 (10분)
│   ├── AWS CLI 설치 확인
│   ├── kubectl 설치 확인
│   ├── AWS 자격 증명 설정
│   └── EKS 클러스터 연결
│
├── Part 1: Kubeflow 설정 (20분)
│   ├── 네임스페이스 확인
│   ├── Kubeflow 파드 상태 확인
│   ├── Kubeflow Dashboard 접속
│   └── Pipelines 페이지 확인
│
├── Part 2: MLflow 배포 (20분)
│   ├── MLflow 네임스페이스 확인
│   ├── MLflow 서비스 확인
│   ├── 포트 포워딩 설정
│   └── MLflow UI 접속 확인
│
└── Part 3: 스토리지 확인 (15분)
    ├── MinIO 상태 확인
    ├── PostgreSQL 상태 확인
    └── 전체 아키텍처 이해
```

---

## 📁 파일 구조

```
lab1-1_mlops-environment-setup/
├── README.md                         # ⭐ 이 파일 (실습 가이드)
├── 1_kubeflow_setup/
│   ├── verify_kubeflow.sh           # Kubeflow 확인 스크립트
│   └── README.md                     # Kubeflow 상세 가이드
├── 2_mlflow_setup/
│   ├── verify_mlflow.sh             # MLflow 확인 스크립트
│   └── README.md                     # MLflow 상세 가이드
└── 3_storage_setup/
    ├── verify_storage.sh            # Storage 확인 스크립트
    └── README.md                     # Storage 상세 가이드
```

---

## 🔧 사전 준비 (10분)

### Step 0-1: 필수 도구 확인

**이 실습을 시작하기 전에 다음 도구가 설치되어 있어야 합니다:**

```bash
# 1. AWS CLI 버전 확인
aws --version
```

**예상 출력:**
```
aws-cli/2.13.x Python/3.11.x Linux/5.x.x
```

**설치되지 않은 경우:**
```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# 설치 확인
aws --version
```

```bash
# 2. kubectl 버전 확인
kubectl version --client
```

**예상 출력:**
```
Client Version: v1.27.x
Kustomize Version: v5.0.x
```

**설치되지 않은 경우:**
```bash
# macOS
brew install kubectl

# Linux
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl

# 설치 확인
kubectl version --client
```

### Step 0-2: 환경 변수 설정

**⚠️ 매우 중요: 본인의 사용자 번호를 정확히 입력하세요!**

```bash
# 사용자 번호 설정 (예: 01, 02, 03...)
export USER_NUM="01"  # ⚠️ 반드시 본인 번호로 변경하세요!

# 환경 변수 확인
echo "사용자 번호: $USER_NUM"
echo "네임스페이스: kubeflow-user$USER_NUM"
```

**예상 출력:**
```
사용자 번호: 01
네임스페이스: kubeflow-user01
```

### Step 0-3: AWS 자격 증명 설정

**강사가 제공한 AWS Access Key와 Secret Key를 준비하세요.**

```bash
# AWS 자격 증명 설정
aws configure
```

**입력 정보 (프롬프트가 나타나면 입력):**
```
AWS Access Key ID [None]: AKIA........................  # 강사가 제공한 키
AWS Secret Access Key [None]: wJalrXUtnF..................  # 강사가 제공한 키
Default region name [None]: ap-northeast-2
Default output format [None]: json
```

**설명:**
- `AWS Access Key ID`: AWS 계정 접근을 위한 공개 키
- `AWS Secret Access Key`: AWS 계정 접근을 위한 비밀 키
- `Default region name`: 서울 리전 (ap-northeast-2)
- `Default output format`: 출력 형식 (json 권장)

### Step 0-4: 자격 증명 확인

```bash
# AWS 자격 증명 테스트
aws sts get-caller-identity
```

**예상 출력:**
```json
{
    "UserId": "AIDAIOSFODNN7EXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/mlops-user01"
}
```

**✅ 성공!** 위와 같은 출력이 나오면 AWS 자격 증명이 올바르게 설정된 것입니다.

**❌ 오류 발생 시:**
```
An error occurred (InvalidClientTokenId) when calling the GetCallerIdentity operation: The security token included in the request is invalid.
```

**해결 방법:**
1. Access Key와 Secret Key를 다시 확인
2. `aws configure`를 다시 실행하여 정확히 입력
3. 강사에게 자격 증명 재확인 요청

### Step 0-5: EKS 클러스터 연결

```bash
# EKS 클러스터 kubeconfig 업데이트
aws eks update-kubeconfig \
    --region ap-northeast-2 \
    --name mlops-training-cluster
```

**예상 출력:**
```
Added new context arn:aws:eks:ap-northeast-2:123456789012:cluster/mlops-training-cluster to /home/user/.kube/config
```

**설명:**
- `--region`: EKS 클러스터가 있는 리전
- `--name`: EKS 클러스터 이름
- 이 명령은 `~/.kube/config` 파일을 업데이트합니다

### Step 0-6: 클러스터 연결 확인

```bash
# 노드 목록 확인
kubectl get nodes
```

**예상 출력:**
```
NAME                                               STATUS   ROLES    AGE   VERSION
ip-10-0-1-234.ap-northeast-2.compute.internal     Ready    <none>   30d   v1.27.9-eks-xxxxx
ip-10-0-2-345.ap-northeast-2.compute.internal     Ready    <none>   30d   v1.27.9-eks-xxxxx
ip-10-0-3-456.ap-northeast-2.compute.internal     Ready    <none>   30d   v1.27.9-eks-xxxxx
```

**✅ 성공!** 위와 같이 노드 목록이 나오고 STATUS가 "Ready"이면 연결 성공입니다.

```bash
# 네임스페이스 목록 확인
kubectl get namespaces
```

**예상 출력:**
```
NAME              STATUS   AGE
default           Active   30d
kube-system       Active   30d
kubeflow          Active   30d
kubeflow-user01   Active   30d
kubeflow-user02   Active   30d
mlflow-system     Active   30d
```

**확인 사항:**
- `kubeflow`: Kubeflow 시스템 네임스페이스
- `kubeflow-user01`: 본인의 네임스페이스 (USER_NUM에 따라 다름)
- `mlflow-system`: MLflow 시스템 네임스페이스

---

## 🚀 Part 1: Kubeflow 설정 (20분)

### Step 1-1: 본인 네임스페이스 확인

```bash
# 네임스페이스 이름 설정
export NAMESPACE="kubeflow-user${USER_NUM}"

# 네임스페이스 확인
kubectl get namespace $NAMESPACE
```

**예상 출력:**
```
NAME               STATUS   AGE
kubeflow-user01    Active   30d
```

**설명:**
- 각 수강생은 독립적인 네임스페이스를 가집니다
- 네임스페이스 이름: `kubeflow-user01`, `kubeflow-user02`, ...
- 이 네임스페이스에서 모든 실습을 진행합니다

### Step 1-2: Kubeflow 파드 확인

```bash
# Kubeflow 파드 목록 확인
kubectl get pods -n $NAMESPACE
```

**예상 출력:**
```
NAME                                   READY   STATUS    RESTARTS   AGE
ml-pipeline-xxxxx-xxxxx               1/1     Running   0          30d
ml-pipeline-persistenceagent-xxxxx    1/1     Running   0          30d
ml-pipeline-scheduledworkflow-xxxxx   1/1     Running   0          30d
ml-pipeline-ui-xxxxx-xxxxx            1/1     Running   0          30d
ml-pipeline-viewer-crd-xxxxx-xxxxx    1/1     Running   0          30d
```

**확인 사항:**
- `READY` 컬럼: `1/1` (파드가 정상 실행 중)
- `STATUS` 컬럼: `Running` (실행 중)
- `RESTARTS` 컬럼: `0` 또는 낮은 숫자 (재시작 횟수)

**⚠️ 파드가 보이지 않는 경우:**
```bash
# 모든 네임스페이스에서 Kubeflow 파드 검색
kubectl get pods --all-namespaces | grep pipeline

# 특정 파드 상세 정보 확인
kubectl describe pod <POD_NAME> -n $NAMESPACE
```

### Step 1-3: Kubeflow 서비스 확인

```bash
# Kubeflow 서비스 목록 확인
kubectl get svc -n $NAMESPACE
```

**예상 출력:**
```
NAME                            TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
ml-pipeline                     ClusterIP   10.100.200.100   <none>        8888/TCP   30d
ml-pipeline-ui                  ClusterIP   10.100.200.101   <none>        80/TCP     30d
ml-pipeline-visualizationserver ClusterIP   10.100.200.102   <none>        8888/TCP   30d
```

**설명:**
- `TYPE`: `ClusterIP` (클러스터 내부에서만 접근 가능)
- `CLUSTER-IP`: 클러스터 내부 IP 주소
- `PORT(S)`: 서비스가 리스닝하는 포트

### Step 1-4: Kubeflow Dashboard 접속

**⚠️ 중요: 접속 방법은 강사의 안내에 따라 달라질 수 있습니다.**

#### 방법 1: 포트 포워딩 (로컬 환경)

```bash
# 터미널 1 - 포트 포워딩 시작
kubectl port-forward svc/ml-pipeline-ui -n $NAMESPACE 8080:80
```

**예상 출력:**
```
Forwarding from 127.0.0.1:8080 -> 3000
Forwarding from [::1]:8080 -> 3000
```

**이 터미널은 그대로 두고, 새 터미널을 열어서 다음 단계를 진행하세요.**

```bash
# 브라우저에서 접속
open http://localhost:8080
# 또는 브라우저 주소창에 직접 입력: http://localhost:8080
```

#### 방법 2: Load Balancer (클라우드 환경)

**강사가 제공한 URL로 접속합니다.**

```
https://kubeflow.example.com
```

### Step 1-5: Kubeflow UI 확인

**브라우저에서 다음을 확인하세요:**

1. **메인 Dashboard 화면**
   - 왼쪽 사이드바 메뉴 확인
   - "Pipelines" 메뉴 클릭

2. **Pipelines 페이지**
   - 파이프라인 목록 확인 (비어있을 수 있음)
   - "+ Upload pipeline" 버튼 확인

3. **Experiments 페이지**
   - "Experiments" 메뉴 클릭
   - Experiment 목록 확인

4. **Runs 페이지**
   - "Runs" 메뉴 클릭
   - Run 목록 확인

**✅ 성공!** 위 페이지들이 모두 정상적으로 표시되면 Kubeflow가 올바르게 작동하고 있습니다.

---

## 🚀 Part 2: MLflow 배포 (20분)

### Step 2-1: MLflow 네임스페이스 확인

```bash
# MLflow 시스템 네임스페이스 확인
kubectl get namespace mlflow-system
```

**예상 출력:**
```
NAME            STATUS   AGE
mlflow-system   Active   30d
```

### Step 2-2: MLflow 파드 확인

```bash
# MLflow 파드 목록 확인
kubectl get pods -n mlflow-system
```

**예상 출력:**
```
NAME                             READY   STATUS    RESTARTS   AGE
mlflow-server-xxxxxxxxxx-xxxxx   1/1     Running   0          30d
postgres-xxxxxxxxxx-xxxxx        1/1     Running   0          30d
```

**확인 사항:**
- `mlflow-server`: MLflow Tracking Server
- `postgres`: MLflow 백엔드 데이터베이스
- 모두 `Running` 상태여야 합니다

**파드 상세 정보 확인:**
```bash
# MLflow 서버 파드 상세 정보
kubectl describe pod -l app=mlflow-server -n mlflow-system
```

### Step 2-3: MLflow 서비스 확인

```bash
# MLflow 서비스 목록 확인
kubectl get svc -n mlflow-system
```

**예상 출력:**
```
NAME                    TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
mlflow-server-service   ClusterIP   10.100.150.100   <none>        5000/TCP   30d
postgres-service        ClusterIP   10.100.150.101   <none>        5432/TCP   30d
```

**설명:**
- `mlflow-server-service`: MLflow Tracking Server (포트 5000)
- `postgres-service`: PostgreSQL 데이터베이스 (포트 5432)

### Step 2-4: MLflow UI 접속

#### 포트 포워딩 설정

```bash
# 터미널 2 - MLflow 포트 포워딩
kubectl port-forward svc/mlflow-server-service -n mlflow-system 5000:5000
```

**예상 출력:**
```
Forwarding from 127.0.0.1:5000 -> 5000
Forwarding from [::1]:5000 -> 5000
```

**💡 Tip: 백그라운드 실행**
```bash
# 백그라운드로 실행하려면:
nohup kubectl port-forward svc/mlflow-server-service -n mlflow-system 5000:5000 > mlflow-pf.log 2>&1 &

# 프로세스 확인
ps aux | grep "port-forward"

# 종료하려면:
pkill -f "port-forward.*mlflow"
```

#### MLflow UI 접속

```bash
# 브라우저에서 접속
open http://localhost:5000
# 또는 브라우저 주소창에 직접 입력: http://localhost:5000
```

### Step 2-5: MLflow UI 확인

**브라우저에서 다음을 확인하세요:**

1. **MLflow 메인 페이지**
   - "MLflow" 로고 확인
   - 상단 메뉴: "Experiments", "Models", "Traces"

2. **Experiments 탭**
   - 왼쪽에 "Default" Experiment 표시
   - 오른쪽에 Run 목록 (비어있을 수 있음)

3. **Models 탭**
   - Model Registry 페이지
   - 등록된 모델 목록 (비어있을 수 있음)

**✅ 성공!** 위 페이지들이 정상적으로 표시되면 MLflow가 올바르게 작동하고 있습니다.

### Step 2-6: MLflow API 테스트 (선택사항)

```bash
# MLflow API 엔드포인트 테스트
curl http://localhost:5000/api/2.0/mlflow/experiments/list
```

**예상 출력:**
```json
{
  "experiments": [
    {
      "experiment_id": "0",
      "name": "Default",
      "artifact_location": "s3://mlflow/0",
      "lifecycle_stage": "active"
    }
  ]
}
```

---

## 🚀 Part 3: 스토리지 확인 (15분)

### Step 3-1: MinIO 확인

**MinIO는 S3 호환 객체 스토리지로, MLflow의 Artifact Store로 사용됩니다.**

```bash
# MinIO 파드 확인
kubectl get pods -n kubeflow | grep minio
```

**예상 출력:**
```
minio-xxxxxxxxxx-xxxxx   1/1   Running   0   30d
```

```bash
# MinIO 서비스 확인
kubectl get svc -n kubeflow | grep minio
```

**예상 출력:**
```
minio-service   ClusterIP   10.100.180.100   <none>   9000/TCP   30d
```

**설명:**
- MinIO는 `kubeflow` 네임스페이스에 배포됩니다
- 포트 9000: S3 API 엔드포인트
- 포트 9001: MinIO Console (Web UI)

#### MinIO Console 접속 (선택사항)

```bash
# MinIO Console 포트 포워딩
kubectl port-forward svc/minio-service -n kubeflow 9000:9000 9001:9001
```

**브라우저 접속:**
```
http://localhost:9001
```

**로그인 정보:**
- Username: `minio`
- Password: `minio123`

**MinIO Console에서 확인:**
1. **Buckets**: MLflow artifact 버킷 확인
2. **Browse**: 저장된 파일 확인
3. **Monitoring**: 스토리지 사용량 확인

### Step 3-2: PostgreSQL 확인

**PostgreSQL은 MLflow의 백엔드 데이터베이스입니다.**

```bash
# PostgreSQL 파드 확인
kubectl get pods -n mlflow-system | grep postgres
```

**예상 출력:**
```
postgres-xxxxxxxxxx-xxxxx   1/1   Running   0   30d
```

```bash
# PostgreSQL 서비스 확인
kubectl get svc -n mlflow-system | grep postgres
```

**예상 출력:**
```
postgres-service   ClusterIP   10.100.150.101   <none>   5432/TCP   30d
```

**설명:**
- PostgreSQL은 `mlflow-system` 네임스페이스에 배포됩니다
- 포트 5432: PostgreSQL 데이터베이스 포트
- MLflow 메타데이터(Experiments, Runs, Parameters, Metrics) 저장

#### PostgreSQL 연결 테스트 (선택사항)

```bash
# PostgreSQL 파드에 접속
kubectl exec -it deployment/postgres -n mlflow-system -- psql -U mlflow

# 데이터베이스 목록 확인
\l

# 테이블 목록 확인
\dt

# 종료
\q
```

### Step 3-3: 전체 아키텍처 확인

**스토리지 구성 요약:**

```
┌─────────────────────────────────────────────────────────┐
│                   MLOps Platform                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────────┐         ┌──────────────────┐     │
│  │   Kubeflow      │         │     MLflow       │     │
│  │   Pipeline      │────────▶│  Tracking Server │     │
│  │                 │         │    (Port 5000)   │     │
│  └─────────────────┘         └─────────┬────────┘     │
│          │                              │              │
│          │                    ┌─────────▼────────┐    │
│          │                    │   PostgreSQL     │    │
│          │                    │   (Metadata)     │    │
│          │                    │    Port 5432     │    │
│          │                    └──────────────────┘    │
│          │                                             │
│  ┌───────▼────────┐                                   │
│  │     MinIO      │◀─────────────────────────────────│
│  │  (Artifacts)   │         (Artifact Store)          │
│  │   Port 9000    │                                   │
│  └────────────────┘                                   │
│                                                        │
└────────────────────────────────────────────────────────┘
```

**각 컴포넌트 역할:**

1. **Kubeflow Pipeline**
   - ML 워크플로우 오케스트레이션
   - 파이프라인 실행 및 관리

2. **MLflow Tracking Server**
   - 실험 추적 (Experiments, Runs)
   - 모델 레지스트리 (Model Registry)
   - 메트릭 및 파라미터 로깅

3. **PostgreSQL**
   - MLflow 메타데이터 저장
   - Experiments, Runs, Parameters, Metrics

4. **MinIO**
   - MLflow Artifacts 저장
   - 모델 파일, 그래프, 데이터 파일

---

## ✅ 완료 체크리스트

### 사전 준비 (10분)
- [ ] AWS CLI 설치 확인 (`aws --version`)
- [ ] kubectl 설치 확인 (`kubectl version --client`)
- [ ] 사용자 번호 설정 (`export USER_NUM="01"`)
- [ ] AWS 자격 증명 설정 (`aws configure`)
- [ ] 자격 증명 확인 (`aws sts get-caller-identity`)
- [ ] EKS 클러스터 연결 (`aws eks update-kubeconfig`)
- [ ] 노드 목록 확인 (`kubectl get nodes`)

### Part 1: Kubeflow (20분)
- [ ] 네임스페이스 확인 (`kubectl get namespace`)
- [ ] Kubeflow 파드 Running 상태 (`kubectl get pods -n $NAMESPACE`)
- [ ] Kubeflow 서비스 확인 (`kubectl get svc -n $NAMESPACE`)
- [ ] 포트 포워딩 성공 (`kubectl port-forward`)
- [ ] Kubeflow Dashboard 접속 성공
- [ ] Pipelines 페이지 확인
- [ ] Experiments 페이지 확인

### Part 2: MLflow (20분)
- [ ] MLflow 네임스페이스 확인
- [ ] MLflow 파드 Running 상태
- [ ] PostgreSQL 파드 Running 상태
- [ ] MLflow 서비스 확인
- [ ] 포트 포워딩 성공 (localhost:5000)
- [ ] MLflow UI 접속 성공
- [ ] Experiments 탭 확인
- [ ] Models 탭 확인

### Part 3: 스토리지 (15분)
- [ ] MinIO 파드 Running 상태
- [ ] MinIO 서비스 확인
- [ ] PostgreSQL 파드 Running 상태
- [ ] PostgreSQL 서비스 확인
- [ ] 전체 아키텍처 이해

---

## 🎯 학습 성과

이 실습을 완료하면:

1. ✅ **Kubernetes 클러스터 관리** - kubectl 명령어 사용
2. ✅ **Kubeflow 플랫폼 이해** - Pipeline 오케스트레이션
3. ✅ **MLflow Tracking** - 실험 추적 시스템
4. ✅ **스토리지 아키텍처** - MinIO (S3) + PostgreSQL
5. ✅ **MLOps 인프라** - 전체 구조 파악
6. ✅ **포트 포워딩** - 로컬에서 서비스 접근

---

## 💡 문제 해결

### 문제 1: kubectl 명령어 "connection refused"

**증상:**
```
The connection to the server localhost:8080 was refused
```

**원인:** kubectl 설정이 올바르지 않음

**해결 방법:**
```bash
# Kubeconfig 재설정
aws eks update-kubeconfig --region ap-northeast-2 --name mlops-training-cluster

# 컨텍스트 확인
kubectl config current-context

# 컨텍스트 변경 (필요한 경우)
kubectl config use-context <CONTEXT_NAME>
```

### 문제 2: 파드가 "Pending" 상태

**증상:**
```
NAME              READY   STATUS    RESTARTS   AGE
mlflow-xxxxx     0/1     Pending   0          5m
```

**원인:** 리소스 부족 또는 스케줄링 실패

**해결 방법:**
```bash
# 파드 상세 정보 확인
kubectl describe pod <POD_NAME> -n <NAMESPACE>

# Events 섹션 확인
# 일반적인 원인:
# - Insufficient CPU/Memory
# - Node not ready
# - Image pull error

# 노드 리소스 확인
kubectl top nodes
```

### 문제 3: 포트 포워딩 실패

**증상:**
```
error: unable to forward port because pod is not running
```

**원인:** 대상 파드가 실행 중이 아님

**해결 방법:**
```bash
# 파드 상태 확인
kubectl get pods -n <NAMESPACE>

# 파드가 Running 상태인지 확인
# Pending, CrashLoopBackOff 등의 상태면 파드 문제 해결 필요

# 포트가 이미 사용 중인 경우
lsof -ti:5000 | xargs kill -9  # 포트 5000 사용 중인 프로세스 종료
```

### 문제 4: MLflow UI 접속 불가

**증상:**
브라우저에서 "This site can't be reached"

**원인:** 포트 포워딩 실패 또는 MLflow 서비스 문제

**해결 방법:**
```bash
# 1. 포트 포워딩 상태 확인
ps aux | grep "port-forward"

# 2. MLflow 서비스 확인
kubectl get svc mlflow-server-service -n mlflow-system

# 3. MLflow 파드 로그 확인
kubectl logs -l app=mlflow-server -n mlflow-system --tail=50

# 4. 포트 포워딩 재시작
pkill -f "port-forward.*mlflow"
kubectl port-forward svc/mlflow-server-service -n mlflow-system 5000:5000
```

### 문제 5: AWS 자격 증명 오류

**증상:**
```
An error occurred (UnrecognizedClientException) when calling the GetCallerIdentity operation
```

**원인:** 잘못된 Access Key 또는 Secret Key

**해결 방법:**
```bash
# 자격 증명 파일 확인
cat ~/.aws/credentials

# 자격 증명 재설정
aws configure

# 환경 변수 확인
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY

# 환경 변수로 설정 (임시)
export AWS_ACCESS_KEY_ID="your_access_key"
export AWS_SECRET_ACCESS_KEY="your_secret_key"
```

---

## 📚 다음 단계

**Lab 1-2: Hello World Pipeline**
- Kubeflow Pipeline 첫 실습
- 간단한 ML Workflow 작성
- Pipeline 컴파일 및 업로드
- Pipeline 실행 및 모니터링

**Lab 1-3: Batch Data Pipeline**
- S3 Data Lake 구축
- ETL Pipeline 구현
- Batch 데이터 처리
- Gold Layer 생성

---

## 🔗 참고 자료

### 공식 문서
- [Kubeflow 공식 문서](https://www.kubeflow.org/docs/)
- [MLflow 공식 문서](https://mlflow.org/docs/latest/)
- [AWS EKS 사용 가이드](https://docs.aws.amazon.com/eks/)
- [MinIO 문서](https://min.io/docs/minio/linux/index.html)
- [PostgreSQL 문서](https://www.postgresql.org/docs/)

### 유용한 명령어 모음

```bash
# Kubernetes 리소스 확인
kubectl get all -n <NAMESPACE>
kubectl describe <RESOURCE_TYPE> <RESOURCE_NAME> -n <NAMESPACE>
kubectl logs <POD_NAME> -n <NAMESPACE> --tail=100

# 포트 포워딩
kubectl port-forward svc/<SERVICE_NAME> -n <NAMESPACE> <LOCAL_PORT>:<REMOTE_PORT>

# 파드 접속
kubectl exec -it <POD_NAME> -n <NAMESPACE> -- /bin/bash

# 리소스 사용량
kubectl top nodes
kubectl top pods -n <NAMESPACE>
```

---

© 2025 현대오토에버 MLOps Training
