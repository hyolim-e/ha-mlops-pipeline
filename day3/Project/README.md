# Lab 3-2: E2E MLOps Pipeline & Project

## 📋 실습 개요

| 항목 | 내용 |
|------|------|
| **소요시간** | 140분 (2시간 20분) |
| **난이도** | ⭐⭐⭐⭐ |
| **목표** | 데이터 전처리부터 모델 배포, 모니터링까지 완전한 E2E MLOps 파이프라인 구축 |

## 🎯 학습 목표

이 실습을 통해 다음을 학습합니다:
- **다단계 Kubeflow Pipeline** 구성 및 실행
- **MLflow** 통합을 통한 실험 추적 및 모델 관리
- **조건부 분기**를 활용한 자동 배포 결정
- **KServe**를 사용한 프로덕션 모델 배포
- **Feature Engineering** 기법 적용
- 팀 프로젝트를 통한 실무 역량 강화

---

## 🏗️ 실습 구조

```
Lab 3-2: E2E MLOps Pipeline & Project (140분)
│
├── Part 1: E2E Pipeline 이해 및 실행 (50분)
│   ├── 파이프라인 아키텍처 이해
│   ├── 컴포넌트별 역할 학습
│   ├── E2E 파이프라인 실행
│   └── 결과 확인 (Kubeflow UI, MLflow UI)
│
├── Part 2: 조별 프로젝트 실습 (50분)
│   ├── 팀 구성 및 역할 분담
│   ├── 템플릿 기반 파이프라인 구현
│   ├── Feature Engineering 적용
│   └── KServe 배포 및 테스트
│
└── Part 3: 발표 및 피드백 (40분)
    ├── 팀별 발표 (15분 × 팀)
    ├── Q&A 및 피드백
    └── 실습 결과 공유
```

---

## 📁 파일 구조

```
lab3-2_e2e-project/
├── README.md                         # ⭐ 이 파일 (실습 가이드)
├── requirements.txt                  # Python 패키지
├── scripts/
│   ├── 1_e2e_pipeline.py            # Part 1: E2E 파이프라인 (50분)
│   ├── 2_project_pipeline.py        # Part 2: 프로젝트 파이프라인 
│   └── 3_test_deployment.py         # 배포 테스트 스크립트
├── components/
│   ├── __init__.py                  # 컴포넌트 패키지
│   ├── data_loader.py               # 데이터 로드 컴포넌트
│   ├── preprocessor.py              # 전처리 컴포넌트
│   ├── feature_engineer.py          # 피처 엔지니어링 컴포넌트
│   ├── trainer.py                   # 모델 학습 컴포넌트
│   ├── evaluator.py                 # 모델 평가 컴포넌트
│   └── deployer.py                  # 모델 배포 컴포넌트
├── notebooks/
│   ├── e2e_pipeline.ipynb           # E2E 파이프라인 Notebook
│   └── project_pipeline.ipynb       # 프로젝트 Notebook
└── template/
    ├── project_template.py          # 프로젝트 시작 템플릿
    └── solution/
        └── project_solution.py      # 예제 솔루션 (발표 후 공개)
```

---

## 🔧 사전 요구사항

### 필수 조건
- ✅ Lab 3-1 완료 (Drift Monitoring)
- ✅ Kubeflow Dashboard 접속 가능
- ✅ MLflow Server 접속 가능
- ✅ Python 3.9+ 환경

### 환경 변수 설정

```bash
# 터미널에서 실행
export USER_NUM="01"                          # ⚠️ 본인 번호로 변경!
export NAMESPACE="kubeflow-user${USER_NUM}"
export MLFLOW_TRACKING_URI="http://mlflow-server-service.mlflow-system.svc.cluster.local:5000"

echo "User: ${USER_NUM}"
echo "Namespace: ${NAMESPACE}"
echo "MLflow URI: ${MLFLOW_TRACKING_URI}"
```

### 패키지 설치

```bash
cd lab3-2_e2e-project
pip install -r requirements.txt
```

---

## 🏛️ 파이프라인 아키텍처

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         E2E ML Pipeline Architecture                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌───────────┐   ┌───────────┐   ┌─────────────┐   ┌───────────┐           │
│  │   Load    │──▶│   Pre-    │──▶│   Feature   │──▶│   Train   │           │
│  │   Data    │   │  process  │   │ Engineering │   │   Model   │           │
│  └───────────┘   └───────────┘   └─────────────┘   └─────┬─────┘           │
│       │               │                │                  │                 │
│       ▼               ▼                ▼                  ▼                 │
│   [sklearn]        [S3/PVC]        [S3/PVC]          [MLflow]               │
│                                                          │                 │
│                                                          ▼                 │
│                                                   ┌─────────────┐          │
│                                                   │  Evaluate   │          │
│                                                   │   Model     │          │
│                                                   └──────┬──────┘          │
│                                                          │                 │
│                                    ┌─────────────────────┴────────────┐    │
│                                    │    Condition: R2 >= threshold    │    │
│                                    └─────────────────────┬────────────┘    │
│                                           │                    │           │
│                                         Yes                   No           │
│                                           ▼                    ▼           │
│                                    ┌─────────────┐     ┌─────────────┐     │
│                                    │   Deploy    │     │   Send      │     │
│                                    │  (KServe)   │     │   Alert     │     │
│                                    └─────────────┘     └─────────────┘     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Part 1: E2E Pipeline 이해 및 실행 (50분)

### 학습 목표
- E2E 파이프라인 아키텍처 이해
- 각 컴포넌트의 역할과 구현 방법 학습
- 파이프라인 실행 및 결과 확인

### Step 1-1: 컴포넌트 이해

각 컴포넌트의 역할:

| 컴포넌트 | 입력 | 출력 | 역할 |
|----------|------|------|------|
| `load_data` | 데이터 소스 | 데이터 경로 | California Housing 데이터 로드 |
| `preprocess` | 데이터 경로 | 전처리 데이터 경로 | Train/Test 분할, 정규화 |
| `feature_engineering` | 전처리 데이터 | 피처 데이터 경로 | 파생 변수 생성 |
| `train_model` | 피처 데이터, MLflow URI | Run ID | 모델 학습 + MLflow 기록 |
| `evaluate_model` | Run ID | 배포 결정 | R2 기준 배포 여부 결정 |
| `deploy_model` | Run ID, namespace | - | KServe InferenceService 배포 |

### Step 1-2: 파이프라인 컴파일

```bash
python scripts/1_e2e_pipeline.py
```

**예상 출력:**
```
============================================================
  E2E ML Pipeline - Compiling
============================================================

✅ Pipeline compiled: e2e_pipeline.yaml

Next steps:
  1. Upload pipeline to Kubeflow UI
  2. Click Create Run
  3. Set parameters:
     - data_source: sklearn
     - experiment_name: e2e-pipeline
     - model_name: california-model
     - namespace: kubeflow-user01
     - n_estimators: 100
     - max_depth: 10
     - r2_threshold: 0.75
  4. Click Start to execute
```

### Step 1-3: Kubeflow UI에서 실행

1. **Kubeflow Dashboard** 접속
2. **Pipelines** → **Upload pipeline**
3. `e2e_pipeline.yaml` 선택 후 업로드
4. **Create Run** 클릭
5. Parameters 설정:
   - `data_source`: sklearn
   - `experiment_name`: e2e-pipeline-user01
   - `model_name`: california-model-user01
   - `namespace`: kubeflow-user01 (본인 네임스페이스)
   - `n_estimators`: 100
   - `max_depth`: 10
   - `r2_threshold`: 0.75
6. **Start** 클릭

### Step 1-4: 결과 확인

**Kubeflow UI:**
- Runs → 실행 상태 확인
- Graph → DAG 시각화
- 각 컴포넌트 로그 확인

**MLflow UI:**
```bash
# Port forward (필요시)
kubectl port-forward svc/mlflow-server-service -n mlflow-system 5000:5000
```
- 브라우저: http://localhost:5000
- Experiments → 실험 결과 확인
- Models → 등록된 모델 확인

**KServe 배포 확인:**
```bash
kubectl get inferenceservices -n kubeflow-user01
```

---

## 🎯 Part 2: 조별 프로젝트 실습 (50분)

### 프로젝트 개요

| 항목 | 내용 |
|------|------|
| **시간** | 50분 (구현) |
| **인원** | 5명 × 6조 |
| **목표** | California Housing 가격 예측 E2E 파이프라인 |

### 평가 기준

#### 필수 요구사항 (70점)

| 항목 | 배점 | 설명 |
|------|------|------|
| Kubeflow Pipeline | 40점 | 최소 5개 컴포넌트, Succeeded 상태 |
| MLflow Tracking | 20점 | 최소 2회 Run, 파라미터/메트릭 기록 |
| Feature Engineering | 10점 | 1개 이상 파생 피처 생성 |

#### 선택 요구사항 (30점 + 보너스)

| 항목 | 배점 | 설명 |
|------|------|------|
| KServe 배포 | 25점 | InferenceService 생성 및 API 테스트 |
| Canary 배포 | 5점 (보너스) | 트래픽 분할 적용 |

### Step 2-1: 팀 구성 및 역할 분담

| 역할 | 담당 업무 | 담당자 |
|------|----------|--------|
| **데이터 담당** | load_data, preprocess 컴포넌트 | - |
| **피처 담당** | feature_engineering 컴포넌트 | - |
| **학습 담당** | train_model + MLflow 연동 | - |
| **배포 담당** | evaluate, deploy (KServe) | - |
| **발표 담당** | 발표 자료 준비, 시연 | - |

### Step 2-2: 템플릿으로 시작

```bash
# 템플릿 복사
cp template/project_template.py my_team_pipeline.py

# 팀명으로 수정
sed -i 's/team-XX/team-01/g' my_team_pipeline.py

# 코드 작성 후 실행
python my_team_pipeline.py
```

### Step 2-3: Feature Engineering 아이디어

```python
# 아이디어 1: 방당 침실 비율
df['bedroom_ratio'] = df['AveBedrms'] / df['AveRooms']

# 아이디어 2: 가구당 인구
df['people_per_household'] = df['Population'] / df['AveOccup']

# 아이디어 3: 소득 구간 (범주형)
df['income_category'] = pd.cut(df['MedInc'], bins=5, labels=[1,2,3,4,5])

# 아이디어 4: 위치 기반 피처 (Bay Area 근접도)
bay_area_lat, bay_area_long = 37.77, -122.42
df['dist_to_bay'] = np.sqrt(
    (df['Latitude'] - bay_area_lat)**2 + 
    (df['Longitude'] - bay_area_long)**2
)

# 아이디어 5: 밀집도
df['density'] = df['Population'] / df['AveOccup']
```

### Step 2-4: 배포 테스트

```bash
# 배포 상태 확인
kubectl get inferenceservices -n kubeflow-user01

# API 테스트
python scripts/3_test_deployment.py
```

---

## 🎤 Part 3: 발표 및 피드백 (40분)

### 발표 형식 (15분/조)

1. **팀 소개** (1분)
   - 팀원 및 역할 분담

2. **아키텍처** (2분)
   - 파이프라인 구조 설명
   - 컴포넌트 간 데이터 흐름

3. **구현 하이라이트** (4분)
   - Feature Engineering 설명
   - 핵심 코드 설명

4. **시연** (4분)
   - Kubeflow UI: 파이프라인 실행 결과
   - MLflow UI: 실험 결과 확인
   - KServe: API 테스트

5. **트러블슈팅** (1분)
   - 겪은 문제와 해결 방법

6. **Q&A** (3분)
   - 질의응답

### 발표 체크리스트

- [ ] 발표 자료 준비 완료
- [ ] 시연 화면 공유 준비
- [ ] Q&A 예상 질문 준비
- [ ] 파이프라인 Succeeded 상태 확인
- [ ] MLflow 실험 결과 확인
- [ ] (선택) KServe 배포 상태 확인

---

## ✅ 완료 체크리스트

### Part 1 체크리스트
- [ ] E2E 파이프라인 아키텍처 이해
- [ ] 컴포넌트 코드 분석 완료
- [ ] 파이프라인 컴파일 성공
- [ ] Kubeflow UI에서 파이프라인 실행
- [ ] 파이프라인 Succeeded 상태
- [ ] MLflow UI에서 실험 확인
- [ ] (조건 충족 시) KServe 배포 확인

### Part 2 체크리스트
- [ ] 팀 구성 및 역할 분담
- [ ] load_data 컴포넌트 구현
- [ ] preprocess 컴포넌트 구현
- [ ] feature_engineering 컴포넌트 구현 (파생 피처 1개+)
- [ ] train_model 컴포넌트 구현 (MLflow 연동)
- [ ] evaluate_model 컴포넌트 구현
- [ ] 파이프라인 컴파일 성공
- [ ] 파이프라인 실행 Succeeded
- [ ] MLflow UI에서 실험 확인
- [ ] (선택) KServe 배포 성공
- [ ] (선택) API 테스트 성공

---

## 📊 데이터셋 정보

### California Housing Dataset

| 항목 | 값 |
|------|------|
| 샘플 수 | 20,640 |
| 피처 수 | 8 |
| 타겟 | MedHouseVal (중간 주택 가격) |

### 피처 설명

| 피처 | 설명 | 단위 |
|------|------|------|
| MedInc | 블록 그룹의 중간 소득 | 만 달러 |
| HouseAge | 블록 그룹의 중간 주택 연령 | 년 |
| AveRooms | 가구당 평균 방 수 | 개 |
| AveBedrms | 가구당 평균 침실 수 | 개 |
| Population | 블록 그룹 인구 | 명 |
| AveOccup | 가구당 평균 거주자 수 | 명 |
| Latitude | 블록 그룹 위도 | 도 |
| Longitude | 블록 그룹 경도 | 도 |
| **MedHouseVal** | 중간 주택 가격 (타겟) | 10만 달러 |

---

## ❓ 트러블슈팅

### 문제: 컴포넌트 간 데이터 전달 실패

```python
# ✅ 올바른 방법: .output 사용
step2 = component_b(input=step1.output)

# ❌ 잘못된 방법
step2 = component_b(input=step1)
```

### 문제: MLflow 연결 실패

```python
# 환경 변수 확인
import os
os.environ['MLFLOW_TRACKING_URI'] = 'http://mlflow-server-service.mlflow-system.svc.cluster.local:5000'

# 연결 테스트
import mlflow
mlflow.set_tracking_uri(os.environ['MLFLOW_TRACKING_URI'])
print(mlflow.get_tracking_uri())
```

### 문제: KServe 배포 실패

```bash
# RBAC 권한 확인
kubectl auth can-i create inferenceservices -n kubeflow-user01

# InferenceService 상태 확인
kubectl describe inferenceservice <model-name> -n kubeflow-user01

# Pod 로그 확인
kubectl logs -l serving.kserve.io/inferenceservice=<model-name> -n kubeflow-user01
```

### 문제: 파이프라인 컴파일 오류

```python
# KFP 버전 확인
import kfp
print(kfp.__version__)  # 2.0.0 이상 권장

# 컴포넌트 데코레이터 확인
from kfp import dsl

@dsl.component(base_image="python:3.9-slim")
def my_component(...) -> str:
    # 함수 내부에서 import
    import pandas as pd
    ...
```

---

## 📚 참고 자료

- [Kubeflow Pipelines v2 SDK](https://www.kubeflow.org/docs/components/pipelines/sdk/v2/)
- [MLflow Model Deployment](https://mlflow.org/docs/latest/models.html)
- [KServe Python SDK](https://kserve.github.io/website/0.10/sdk_docs/sdk_doc/)
- [California Housing Dataset](https://scikit-learn.org/stable/datasets/real_world.html#california-housing-dataset)

---

© 2025 현대오토에버 MLOps Training - Lab 3-2
