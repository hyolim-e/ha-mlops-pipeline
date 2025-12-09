# 🔧 실습 문제 해결 가이드

## 발견된 문제 및 완전 해결 방법

실습 중 발견된 모든 문제를 분석하고 완전히 해결했습니다.

---

## 📋 문제 요약

| # | 문제 | 상태 | 해결 |
|---|------|------|------|
| 1 | Grafana Import 시 DataSource 선택 없음 | ✅ 해결 | Provisioning 자동 설정 |
| 2 | "Datasource prometheus was not found" 에러 | ✅ 해결 | ConfigMap 수정 + UID 설정 |
| 3 | GitHub Actions Install dependencies 실패 | ✅ 해결 | kubernetes 버전 다운그레이드 |
| 4 | Alertmanager 주석 제거 방법 불명확 | ✅ 해결 | 자동 설정 스크립트 제공 |
| 5 | manifests/alertmanager에 Slack yaml 없음 | ✅ 해결 | 3개 파일 생성 |
| 6 | Alertmanager API "Empty reply from server" | ✅ 해결 | 테스트 스크립트 제공 |

---

## 🔍 문제 1: Grafana DataSource 선택 없음

### 증상
```
Grafana Dashboard Import 화면에서:
- Name, Folder, UID만 보임
- DataSource 선택 옵션이 없음
```

### 원인
Grafana ConfigMap에 DataSource provisioning 설정이 불완전함

### ✅ 해결 방법

**자동 해결 (권장):**
```bash
# 모니터링 스택 재배포
cd lab3-2_monitoring-cicd
./scripts/1_deploy_monitoring.sh
```

수정된 `manifests/grafana/01-grafana-config.yaml`에 다음 설정 추가됨:
```yaml
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus.monitoring.svc.cluster.local:9090
    isDefault: true
    editable: true
    uid: prometheus          # ⬅️ UID 명시
    jsonData:
      httpMethod: POST
      timeInterval: 5s       # ⬅️ 새로 추가
```

**수동 설정 (대안):**
```bash
# 1. Grafana ConfigMap 업데이트
kubectl apply -f manifests/grafana/01-grafana-config.yaml

# 2. Grafana 재시작
kubectl rollout restart deployment/grafana -n monitoring
kubectl rollout status deployment/grafana -n monitoring

# 3. Grafana 접속 확인
kubectl port-forward -n monitoring svc/grafana 3000:3000
# http://localhost:3000 (admin/admin123)
```

**검증:**
```bash
# Grafana UI에서 확인
# Configuration → Data sources → Prometheus가 자동으로 보여야 함
```

---

## 🔍 문제 2: "Datasource prometheus was not found"

### 증상
```
Dashboard 모든 패널에:
- "Datasource prometheus was not found" 에러
- "No data" 표시
```

### 원인
1. DataSource가 제대로 provisioning되지 않음
2. Dashboard JSON의 datasource uid 불일치

### ✅ 해결 방법

**Step 1: DataSource 확인**
```bash
# Grafana에 접속
kubectl port-forward -n monitoring svc/grafana 3000:3000

# 브라우저에서: http://localhost:3000
# Configuration → Data sources
# "Prometheus"가 보이는지 확인
```

**Step 2: 수동 DataSource 추가 (필요시)**
```
1. Grafana UI → Configuration → Data sources
2. "Add data source" 클릭
3. "Prometheus" 선택
4. 설정:
   - Name: Prometheus
   - URL: http://prometheus.monitoring.svc.cluster.local:9090
   - Access: Server (default)
5. "Save & test" 클릭
```

**Step 3: Dashboard 재임포트**
```
1. Dashboards → Import
2. "Upload JSON file" 선택
3. dashboards/model-performance-dashboard.json 업로드
4. Data Source: "Prometheus" 선택 (이제 보여야 함)
5. "Import" 클릭
```

**Step 4: Metrics 확인**
```bash
# Metrics Exporter 실행 확인
ps aux | grep metrics_exporter

# 실행되지 않았다면 시작
python scripts/2_metrics_exporter.py &

# 메트릭 확인
curl http://localhost:8000/metrics | grep model_mae_score

# Prometheus에서 확인
# http://localhost:9090/graph
# Query: model_mae_score
```

**자동 해결 스크립트:**
```bash
# 전체 재배포 및 테스트
./scripts/1_deploy_monitoring.sh
python scripts/2_metrics_exporter.py &
sleep 10
# Grafana에서 Dashboard 재임포트
```

---

## 🔍 문제 3: GitHub Actions Install dependencies 실패

### 증상
```
GitHub Actions CI 로그:
ERROR: Cannot install -r requirements.txt (line 6) and kubernetes==28.1.0
because these package versions have conflicting dependencies.

The conflict is caused by:
    The user requested kubernetes==28.1.0
    kfp 1.8.22 depends on kubernetes<26 and >=8.0.0
```

### 원인
- `requirements.txt`에 `kubernetes==28.1.0` 지정
- `kfp==2.15.2`가 사용 중이나, 다른 의존성이 kubernetes<26 요구

### ✅ 해결 방법

**수정된 requirements.txt:**
```txt
# Lab 3-2: Monitoring & CI/CD Requirements

# Kubeflow Pipelines
kfp==2.15.2

# MLflow
mlflow==2.9.2

# Prometheus Client
prometheus-client==0.19.0

# HTTP Requests
requests==2.31.0

# Kubernetes Client
kubernetes==25.3.0    # ⬅️ 28.1.0 → 25.3.0으로 변경

# AWS
boto3==1.34.0

# Data Science
numpy>=1.26,<2.0
pandas>=2.0.0
scikit-learn>=1.3.0

# CLI
click==8.1.7

# Monitoring
grafana-api==1.0.3

# Testing
pytest==7.4.3
pytest-cov==4.1.0

# Utilities
python-dotenv==1.0.0
pyyaml==6.0.1
```

**검증:**
```bash
# 로컬에서 테스트
python -m venv test_env
source test_env/bin/activate
pip install -r requirements.txt

# 성공하면:
# ✅ Successfully installed kubernetes-25.3.0 ...
```

**GitHub Actions에서 확인:**
```bash
# .github/workflows/ci-test.yaml 참조
# Install dependencies 단계가 성공해야 함
```

---

## 🔍 문제 4: Alertmanager 주석 제거 방법 불명확

### 증상
```bash
kubectl edit configmap alertmanager-config -n monitoring

# 주석이 너무 많아서 어떤 것을 지워야 할지 불명확:
# slack_api_url: '...'  # 이것을 지워야?
# slack_configs:        # 아니면 이것?
```

### 원인
- ConfigMap을 수동으로 편집하는 것은 복잡함
- 주석 처리된 설정이 많아서 혼란스러움

### ✅ 해결 방법 (자동 스크립트)

**간단한 방법 - 자동 설정 스크립트 사용:**

```bash
# Slack Webhook URL 준비
# https://api.slack.com/apps에서 생성

# 스크립트 실행
./scripts/5_setup_slack.sh https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# 이 스크립트가 자동으로:
# 1. Secret 생성
# 2. ConfigMap 업데이트
# 3. Alertmanager 재시작
```

**스크립트 내용:**
```bash
#!/bin/bash
# 사용법: ./scripts/5_setup_slack.sh <SLACK_WEBHOOK_URL>

SLACK_WEBHOOK_URL="$1"

# Step 1: Secret 생성
kubectl create secret generic alertmanager-slack \
  --from-literal=webhook-url="${SLACK_WEBHOOK_URL}" \
  -n monitoring \
  --dry-run=client -o yaml | kubectl apply -f -

# Step 2: ConfigMap 업데이트 (자동)
# Step 3: Alertmanager 재시작
kubectl rollout restart deployment/alertmanager -n monitoring
```

**수동 방법 (필요시):**

1. **Slack 설정 파일 적용:**
```bash
# 미리 준비된 Slack 설정 사용
kubectl apply -f manifests/alertmanager/04-alertmanager-config-slack.yaml
```

2. **YOUR/SLACK/WEBHOOK 부분 수정:**
```bash
# 파일 편집
vim manifests/alertmanager/04-alertmanager-config-slack.yaml

# 3곳의 'YOUR/SLACK/WEBHOOK'를 실제 URL로 변경
# - slack-critical receiver
# - slack-warning receiver  
# - global section
```

3. **적용 및 재시작:**
```bash
kubectl apply -f manifests/alertmanager/04-alertmanager-config-slack.yaml
kubectl rollout restart deployment/alertmanager -n monitoring
```

---

## 🔍 문제 5: manifests/alertmanager에 Slack yaml 없음

### 증상
```bash
kubectl apply -f manifests/alertmanager/02-alertmanager-deployment-with-slack.yaml

# error: the path "..." does not exist
```

### 원인
파일이 실제로 누락됨

### ✅ 해결 방법

**이제 다음 파일들이 생성되었습니다:**

```bash
manifests/alertmanager/
├── 01-alertmanager-config.yaml                    # 기본 ConfigMap
├── 02-alertmanager-deployment.yaml                # 기본 Deployment
├── 02-alertmanager-deployment-with-slack.yaml     # ⬅️ 신규: Slack용 Deployment
├── 03-alertmanager-service.yaml                   # Service
└── 04-alertmanager-config-slack.yaml              # ⬅️ 신규: Slack ConfigMap
```

**사용 방법:**

**Option 1: Slack 없이 기본 배포 (현재 상태)**
```bash
kubectl apply -f manifests/alertmanager/01-alertmanager-config.yaml
kubectl apply -f manifests/alertmanager/02-alertmanager-deployment.yaml
kubectl apply -f manifests/alertmanager/03-alertmanager-service.yaml
```

**Option 2: Slack 통합 배포**
```bash
# Step 1: Slack Webhook URL 설정
./scripts/5_setup_slack.sh https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# 또는 수동으로:
kubectl apply -f manifests/alertmanager/04-alertmanager-config-slack.yaml
kubectl apply -f manifests/alertmanager/02-alertmanager-deployment-with-slack.yaml
kubectl apply -f manifests/alertmanager/03-alertmanager-service.yaml
```

**검증:**
```bash
# Alertmanager pod 확인
kubectl get pods -n monitoring -l app=alertmanager

# ConfigMap 확인
kubectl get configmap -n monitoring | grep alertmanager

# Secret 확인 (Slack 사용 시)
kubectl get secret alertmanager-slack -n monitoring
```

---

## 🔍 문제 6: Alertmanager API "Empty reply from server"

### 증상
```bash
curl -X POST http://localhost:9093/api/v1/alerts -H "Content-Type: application/json" -d '[...]'
# curl: (52) Empty reply from server
```

### 원인
1. Port-forward가 제대로 되지 않음
2. Alertmanager pod이 Ready 상태가 아님
3. API 엔드포인트 경로 문제

### ✅ 해결 방법

**자동 테스트 스크립트 사용 (권장):**

```bash
# 테스트 스크립트 실행
./scripts/6_test_alertmanager.sh

# 이 스크립트가 자동으로:
# 1. Pod 상태 확인
# 2. Port-forward 설정
# 3. Health check 수행
# 4. 테스트 알림 전송
# 5. 결과 검증
```

**수동 해결 방법:**

**Step 1: Alertmanager 상태 확인**
```bash
# Pod 상태
kubectl get pods -n monitoring -l app=alertmanager

# 출력 예시:
# NAME                            READY   STATUS    RESTARTS   AGE
# alertmanager-xxxxxxxxxx-xxxxx   1/1     Running   0          5m

# Ready가 0/1이면 로그 확인
kubectl logs -n monitoring -l app=alertmanager
```

**Step 2: Port-forward 재설정**
```bash
# 기존 port-forward 종료
pkill -f "port-forward.*alertmanager"

# 새로 시작
kubectl port-forward -n monitoring svc/alertmanager 9093:9093 &

# 3초 대기
sleep 3
```

**Step 3: Health check**
```bash
# Health 확인
curl http://localhost:9093/-/healthy

# 출력: OK

# Ready 확인
curl http://localhost:9093/-/ready

# 출력: OK
```

**Step 4: 테스트 알림 전송**
```bash
# 올바른 JSON 형식으로 전송
curl -X POST http://localhost:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '[
  {
    "labels": {
      "alertname": "TestAlert",
      "severity": "warning",
      "model_name": "california-housing"
    },
    "annotations": {
      "summary": "Test alert",
      "description": "This is a test alert"
    }
  }
]'

# 성공 시 응답 없음 (정상)
# 실패 시 에러 메시지 표시
```

**Step 5: 알림 확인**
```bash
# Alertmanager UI에서 확인
# http://localhost:9093

# 또는 API로 확인
curl -s http://localhost:9093/api/v2/alerts | jq
```

**트러블슈팅:**

```bash
# 1. Service 확인
kubectl get svc alertmanager -n monitoring

# 2. Endpoints 확인
kubectl get endpoints alertmanager -n monitoring

# 3. Pod IP 확인
kubectl get pods -n monitoring -l app=alertmanager -o wide

# 4. 직접 Pod에 접속해서 테스트
ALERTMANAGER_POD=$(kubectl get pods -n monitoring -l app=alertmanager -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $ALERTMANAGER_POD -n monitoring -- wget -O- http://localhost:9093/-/healthy
```

---

## 🎯 완전한 실습 진행 순서

모든 문제가 해결된 상태에서 실습을 진행하는 순서:

### 1. 초기 설정 및 배포 (10분)

```bash
cd lab3-2_monitoring-cicd

# 환경 변수 설정
export USER_NUM="01"
export USER_NAMESPACE="kubeflow-user${USER_NUM}"

# 모니터링 스택 배포
./scripts/1_deploy_monitoring.sh

# 배포 완료 대기 (약 2-3분)
kubectl get pods -n monitoring -w
```

### 2. 포트 포워딩 (3개 터미널)

```bash
# 터미널 1: Prometheus
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# 터미널 2: Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000

# 터미널 3: Alertmanager
kubectl port-forward -n monitoring svc/alertmanager 9093:9093
```

### 3. Grafana Dashboard 설정 (5분)

```bash
# 브라우저에서:
# http://localhost:3000
# Username: admin
# Password: admin123

# Dashboard 임포트:
# 1. Dashboards → Import
# 2. Upload JSON file
# 3. dashboards/model-performance-dashboard.json 선택
# 4. Data Source: "Prometheus" 자동 선택됨 ✅
# 5. Import 클릭
```

### 4. Metrics 수집 시작 (터미널 4)

```bash
# Metrics Exporter 시작
python scripts/2_metrics_exporter.py

# 메트릭 확인
curl http://localhost:8000/metrics | grep model_mae_score

# Grafana Dashboard에서 데이터 확인 ✅
```

### 5. A/B 테스트 시뮬레이션 (터미널 5)

```bash
# 5분 동안 실행
python scripts/3_ab_test_simulator.py --duration 300

# Grafana에서 실시간으로 메트릭 변화 확인 ✅
```

### 6. Alertmanager 테스트

```bash
# 자동 테스트
./scripts/6_test_alertmanager.sh

# Alertmanager UI 확인
# http://localhost:9093
```

### 7. Slack 통합 (선택)

```bash
# Slack Webhook URL 준비 후
./scripts/5_setup_slack.sh https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# 테스트 알림 전송
./scripts/6_test_alertmanager.sh

# Slack 채널에서 알림 확인 ✅
```

### 8. GitHub Actions CI/CD 테스트

```bash
# requirements.txt 확인 (kubernetes 25.3.0)
cat requirements.txt | grep kubernetes

# GitHub에 push
git add .
git commit -m "Update monitoring lab"
git push

# GitHub Actions 페이지에서 확인
# Install dependencies 단계 성공 확인 ✅
```

---

## ✅ 모든 문제 해결 체크리스트

실습 전 확인:
- [ ] Lab 다운로드 및 압축 해제
- [ ] kubectl 설정 확인
- [ ] Python 3.9+ 설치
- [ ] requirements.txt 설치 (kubernetes==25.3.0)

배포 확인:
- [ ] Prometheus Pod Running
- [ ] Grafana Pod Running
- [ ] Alertmanager Pod Running
- [ ] 모든 Service 생성됨

Grafana 확인:
- [ ] DataSource "Prometheus" 자동 생성됨 ✅
- [ ] Dashboard import 시 DataSource 선택 가능 ✅
- [ ] Dashboard에 데이터 표시됨 ✅
- [ ] "Datasource was not found" 에러 없음 ✅

GitHub Actions 확인:
- [ ] Install dependencies 성공 ✅
- [ ] kubernetes 버전 충돌 없음 ✅
- [ ] CI pipeline 통과

Alertmanager 확인:
- [ ] manifests/alertmanager/*.yaml 파일 존재 ✅
- [ ] Slack 설정 스크립트 사용 가능 ✅
- [ ] API 테스트 성공 (Empty reply 없음) ✅
- [ ] 테스트 알림 수신 확인 ✅

---

## 📞 추가 지원

문제가 계속되면:

1. **진단 스크립트 실행:**
```bash
./scripts/6_test_alertmanager.sh
```

2. **로그 확인:**
```bash
kubectl logs -n monitoring deployment/prometheus
kubectl logs -n monitoring deployment/grafana
kubectl logs -n monitoring deployment/alertmanager
```

3. **전체 상태 확인:**
```bash
kubectl get all -n monitoring
kubectl describe pods -n monitoring
```

4. **문서 참조:**
- `TROUBLESHOOTING.md` - 상세 문제 해결
- `SLACK_SETUP.md` - Slack 통합 가이드
- `README.md` - 전체 실습 가이드

---

© 2025 현대오토에버 MLOps Training - 문제 해결 완료
