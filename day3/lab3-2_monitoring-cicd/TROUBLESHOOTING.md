# 트러블슈팅 가이드

## 🔧 Lab 3-2 문제 해결 완벽 가이드

실습 중 발생할 수 있는 모든 문제와 해결 방법을 상세히 설명합니다.

---

## 📊 문제 1: Grafana Dashboard가 비어있음

### 증상
- Dashboard를 Import했는데 패널이 비어있음
- "No data" 또는 "N/A" 표시
- 그래프가 그려지지 않음

### 원인 분석

#### 원인 1-1: Prometheus Data Source 미연결

**확인 방법:**
```bash
# Grafana Pod 로그 확인
kubectl logs -n monitoring deployment/grafana | grep -i datasource
```

**해결 방법:**

1. **Grafana UI에서 수동 설정**
   ```
   1. Grafana 접속 (http://localhost:3000)
   2. 좌측 메뉴 → Configuration → Data sources
   3. "Add data source" 클릭
   4. "Prometheus" 선택
   5. 설정 입력:
      - Name: Prometheus
      - URL: http://prometheus.monitoring.svc.cluster.local:9090
      - Access: Server (default)
   6. "Save & test" 클릭
   ```

2. **ConfigMap 확인 및 수정**
   ```bash
   kubectl get configmap grafana-datasources -n monitoring -o yaml
   
   # URL이 올바른지 확인:
   # url: http://prometheus.monitoring.svc.cluster.local:9090
   ```

3. **Pod 재시작**
   ```bash
   kubectl rollout restart deployment/grafana -n monitoring
   kubectl rollout status deployment/grafana -n monitoring
   ```

#### 원인 1-2: 메트릭이 수집되지 않음

**확인 방법:**
```bash
# Prometheus 타겟 확인
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# 브라우저에서: http://localhost:9090/targets
# 또는 curl:
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'
```

**해결 방법:**

**Step 1: Metrics Exporter 실행 확인**
```bash
# Exporter가 실행 중인지 확인
ps aux | grep metrics_exporter

# 실행되지 않았다면 시작
python scripts/2_metrics_exporter.py
```

**Step 2: 메트릭 엔드포인트 확인**
```bash
# 로컬에서 메트릭 확인
curl http://localhost:8000/metrics | grep model_mae_score

# 출력 예시:
# model_mae_score{model_name="california-housing",version="v1.0"} 0.42
# model_mae_score{model_name="california-housing",version="v2.0"} 0.37
```

**Step 3: Prometheus 설정 확인**
```bash
# Prometheus ConfigMap 확인
kubectl get configmap prometheus-config -n monitoring -o yaml | grep -A 10 "job_name: 'model-metrics-exporter'"
```

#### 원인 1-3: Dashboard UID 불일치

**확인 방법:**
```bash
# Dashboard JSON 확인
cat dashboards/model-performance-dashboard.json | jq '.uid'
```

**해결 방법:**

1. **Dashboard 재임포트**
   ```
   1. Grafana → Dashboards → Import
   2. Upload JSON file 선택
   3. dashboards/model-performance-dashboard.json 선택
   4. Data Source: "Prometheus" 선택
   5. Import 클릭
   ```

2. **Data Source UID 확인**
   ```bash
   # Grafana API로 Data Source UID 확인
   kubectl port-forward -n monitoring svc/grafana 3000:3000
   
   curl -u admin:admin123 http://localhost:3000/api/datasources | jq '.[] | {name: .name, uid: .uid}'
   ```

3. **Dashboard JSON 수정**
   
   `dashboards/model-performance-dashboard.json`에서:
   ```json
   "datasource": {
     "type": "prometheus",
     "uid": "prometheus"  // ← 실제 UID로 변경
   }
   ```

---

## 🔄 문제 2: 실시간 모니터링 불가

### 증상
- Dashboard가 업데이트되지 않음
- 데이터가 고정되어 있음
- Refresh가 작동하지 않음

### 해결 방법

#### 해결 2-1: Auto-refresh 설정 확인

**Grafana UI에서:**
```
1. Dashboard 우측 상단 시계 아이콘 클릭
2. Refresh 간격 설정: "5s" 또는 "10s"
3. Time range: "Last 30 minutes"
```

#### 해결 2-2: Metrics Exporter 지속 실행

**백그라운드 실행:**
```bash
# nohup 사용
nohup python scripts/2_metrics_exporter.py > metrics_exporter.log 2>&1 &

# 실행 확인
ps aux | grep metrics_exporter
tail -f metrics_exporter.log
```

**systemd 서비스로 실행 (선택):**
```bash
# /etc/systemd/system/metrics-exporter.service 생성
cat <<EOF | sudo tee /etc/systemd/system/metrics-exporter.service
[Unit]
Description=ML Model Metrics Exporter
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/lab3-2_monitoring-cicd
ExecStart=/usr/bin/python3 scripts/2_metrics_exporter.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl start metrics-exporter
sudo systemctl enable metrics-exporter
```

#### 해결 2-3: 네트워크 연결 확인

```bash
# Prometheus → Metrics Exporter 연결 확인
kubectl exec -n monitoring deployment/prometheus -- wget -O- http://localhost:8000/metrics

# 타임아웃 발생 시 네트워크 확인
kubectl get svc -n monitoring
kubectl get endpoints -n monitoring
```

---

## ⚠️ 문제 3: GitHub Actions CI 실패

### 증상
- CI Pipeline이 실패함
- "upload-artifact" deprecated 경고

### 해결 방법

#### 해결 3-1: Actions 버전 업데이트

이미 수정된 `.github/workflows/ci-test.yaml` 사용:

```yaml
- name: Upload test artifacts
  if: always()
  uses: actions/upload-artifact@v4  # v3 → v4로 변경
  with:
    name: test-results
    path: |
      htmlcov/
      coverage.xml
    retention-days: 30
```

#### 해결 3-2: Python 환경 문제

**증상:** 패키지 설치 실패

**해결:**
```yaml
- name: Install dependencies
  run: |
    python -m pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
```

#### 해결 3-3: 테스트 파일 누락

**증상:** `tests/` 디렉토리 없음

**해결:**
```bash
# 테스트 디렉토리 생성
mkdir -p tests

# 간단한 테스트 파일 생성
cat <<EOF > tests/test_sample.py
def test_sample():
    assert True
EOF
```

---

## 📦 문제 4: Alertmanager 관련 이슈

### 증상
- Alertmanager Pod이 시작되지 않음
- Alert가 전송되지 않음

### 해결 방법

#### 해결 4-1: Alertmanager 배포 확인

```bash
# Pod 상태 확인
kubectl get pods -n monitoring -l app=alertmanager

# 로그 확인
kubectl logs -n monitoring deployment/alertmanager

# 설정 검증
kubectl exec -n monitoring deployment/alertmanager -- amtool check-config /etc/alertmanager/alertmanager.yml
```

#### 해결 4-2: Prometheus - Alertmanager 연결

**Prometheus ConfigMap 확인:**
```bash
kubectl get configmap prometheus-config -n monitoring -o yaml | grep -A 5 alertmanagers
```

**올바른 설정:**
```yaml
alerting:
  alertmanagers:
    - static_configs:
        - targets:
            - alertmanager.monitoring.svc.cluster.local:9093
```

#### 해결 4-3: Alert Rules 확인

```bash
# Alert rules 확인
kubectl exec -n monitoring deployment/prometheus -- promtool check rules /etc/prometheus/rules/*.yml

# Alert 상태 확인 (Prometheus UI)
# http://localhost:9090/alerts
```

---

## 🔐 문제 5: Slack 알림이 오지 않음

### 해결 방법

**SLACK_SETUP.md 참조** - 상세한 단계별 가이드 제공

**빠른 체크리스트:**
```bash
# 1. Secret 확인
kubectl get secret alertmanager-slack -n monitoring

# 2. Webhook URL 확인
kubectl get secret alertmanager-slack -n monitoring -o jsonpath='{.data.webhook-url}' | base64 -d

# 3. 테스트 알림 전송
curl -X POST https://hooks.slack.com/services/YOUR/WEBHOOK/URL \
  -H 'Content-Type: application/json' \
  -d '{"text": "Test alert from Alertmanager"}'

# 4. Alertmanager 로그 확인
kubectl logs -n monitoring deployment/alertmanager | grep -i slack
```

---

## 🐳 문제 6: Docker 관련 이슈

### 증상
- Docker 빌드 실패
- Architecture 불일치 (ARM64 vs AMD64)

### 해결 방법

#### 해결 6-1: Multi-platform 빌드

```bash
# Docker buildx 설정
docker buildx create --use

# Multi-platform 빌드
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t your-image:tag \
  --push \
  .
```

#### 해결 6-2: 로컬 테스트 시 플랫폼 지정

```bash
# AMD64 플랫폼으로 강제 빌드
docker build --platform linux/amd64 -t test-image .

# 실행 시에도 플랫폼 지정
docker run --platform linux/amd64 test-image
```

---

## 🔍 문제 7: Prometheus 메트릭 수집 안됨

### 증상
- Targets가 "Down" 상태
- Scrape errors 발생

### 해결 방법

#### 해결 7-1: ServiceMonitor 확인

```bash
# ServiceMonitor 확인
kubectl get servicemonitor -n monitoring

# ServiceMonitor 상세 확인
kubectl describe servicemonitor model-metrics-monitor -n monitoring
```

#### 해결 7-2: 라벨 매칭 확인

```bash
# Service 라벨 확인
kubectl get svc -n monitoring --show-labels

# ServiceMonitor selector 확인
kubectl get servicemonitor model-metrics-monitor -n monitoring -o yaml | grep -A 5 selector
```

#### 해결 7-3: 네트워크 정책 확인

```bash
# NetworkPolicy 확인
kubectl get networkpolicy -n monitoring

# Pod 간 통신 테스트
kubectl exec -n monitoring deployment/prometheus -- wget -O- http://grafana.monitoring.svc.cluster.local:3000
```

---

## 🚫 문제 8: RBAC 권한 부족

### 증상
- "Forbidden" 에러
- Pipeline 생성 실패
- InferenceService 배포 실패

### 해결 방법

#### 해결 8-1: ServiceAccount 확인

```bash
# 현재 사용 중인 ServiceAccount 확인
kubectl get sa -n monitoring

# Prometheus ServiceAccount 확인
kubectl get sa prometheus -n monitoring -o yaml
```

#### 해결 8-2: ClusterRole 권한 확인

```bash
# ClusterRole 확인
kubectl get clusterrole prometheus -o yaml

# ClusterRoleBinding 확인
kubectl get clusterrolebinding prometheus -o yaml
```

#### 해결 8-3: 권한 테스트

```bash
# Prometheus ServiceAccount로 권한 테스트
kubectl auth can-i list pods --as=system:serviceaccount:monitoring:prometheus
kubectl auth can-i get services --as=system:serviceaccount:monitoring:prometheus
```

---

## 📋 종합 진단 스크립트

실습 환경을 전체적으로 점검하는 스크립트:

```bash
#!/bin/bash
# diagnose.sh - 모니터링 스택 진단 스크립트

echo "=========================================="
echo "Lab 3-2 Monitoring Stack Diagnosis"
echo "=========================================="
echo ""

# 1. Namespace 확인
echo "1. Checking namespace..."
kubectl get ns monitoring > /dev/null 2>&1 && echo "✅ Namespace OK" || echo "❌ Namespace missing"
echo ""

# 2. Pods 상태
echo "2. Checking pods..."
kubectl get pods -n monitoring
echo ""

# 3. Services 상태
echo "3. Checking services..."
kubectl get svc -n monitoring
echo ""

# 4. ConfigMaps 확인
echo "4. Checking ConfigMaps..."
kubectl get configmap -n monitoring
echo ""

# 5. Prometheus Targets
echo "5. Checking Prometheus targets..."
kubectl port-forward -n monitoring svc/prometheus 9090:9090 > /dev/null 2>&1 &
PF_PID=$!
sleep 3
curl -s http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'
kill $PF_PID
echo ""

# 6. Metrics Exporter 확인
echo "6. Checking Metrics Exporter..."
ps aux | grep metrics_exporter | grep -v grep && echo "✅ Exporter running" || echo "⚠️  Exporter not running"
echo ""

# 7. Grafana Data Source
echo "7. Checking Grafana datasource..."
kubectl exec -n monitoring deployment/grafana -- grafana-cli admin reset-admin-password admin123 > /dev/null 2>&1
kubectl port-forward -n monitoring svc/grafana 3000:3000 > /dev/null 2>&1 &
GF_PID=$!
sleep 3
curl -s -u admin:admin123 http://localhost:3000/api/datasources | jq '.[] | {name: .name, type: .type, url: .url}'
kill $GF_PID
echo ""

echo "=========================================="
echo "Diagnosis complete!"
echo "=========================================="
```

**실행:**
```bash
chmod +x diagnose.sh
./diagnose.sh
```

---

## 💡 예방 조치

### 1. 정기적인 헬스 체크

```bash
# 매일 아침 실행
kubectl get pods -n monitoring
kubectl top pods -n monitoring
```

### 2. 로그 모니터링

```bash
# 에러 로그 확인
kubectl logs -n monitoring deployment/prometheus | grep -i error
kubectl logs -n monitoring deployment/grafana | grep -i error
kubectl logs -n monitoring deployment/alertmanager | grep -i error
```

### 3. 리소스 사용량 확인

```bash
# CPU/Memory 사용량
kubectl top pods -n monitoring

# 리소스 제한 확인
kubectl describe deployment prometheus -n monitoring | grep -A 5 "Limits:"
```

---

## 📞 추가 지원

### 문제가 해결되지 않을 때

1. **로그 수집**
   ```bash
   # 모든 로그를 파일로 저장
   kubectl logs -n monitoring deployment/prometheus > prometheus.log
   kubectl logs -n monitoring deployment/grafana > grafana.log
   kubectl logs -n monitoring deployment/alertmanager > alertmanager.log
   ```

2. **전체 상태 Export**
   ```bash
   kubectl get all -n monitoring -o yaml > monitoring-state.yaml
   kubectl describe all -n monitoring > monitoring-describe.txt
   ```

3. **커뮤니티 지원**
   - Slack: #mlops-training
   - 이메일: support@company.com
   - GitHub Issues: [링크]

---

## ✅ 체크리스트

**실습 전 확인사항:**
- [ ] Kubernetes 클러스터 접근 가능
- [ ] kubectl 설치 및 설정 완료
- [ ] Python 3.9+ 설치
- [ ] 필요한 패키지 설치 (`pip install -r requirements.txt`)
- [ ] 충분한 리소스 (CPU: 4 cores, Memory: 8GB)

**배포 후 확인사항:**
- [ ] 모든 Pod이 Running 상태
- [ ] Prometheus UI 접속 가능 (localhost:9090)
- [ ] Grafana UI 접속 가능 (localhost:3000)
- [ ] Alertmanager UI 접속 가능 (localhost:9093)
- [ ] Metrics Exporter 실행 중
- [ ] Dashboard에 데이터 표시됨

**테스트 완료:**
- [ ] A/B 테스트 시뮬레이션 실행
- [ ] 실시간 메트릭 업데이트 확인
- [ ] Alert 발생 테스트
- [ ] Slack 알림 수신 (선택)

---

© 2025 현대오토에버 MLOps Training - 트러블슈팅 가이드
