# Lab 3-2 빠른 시작 가이드

## 🚀 5분 안에 시작하기

### 1. 사전 준비

```bash
# 환경 변수 설정
export USER_NUM="01"  # 본인 번호로 변경
export USER_NAMESPACE="kubeflow-user${USER_NUM}"

# 디렉토리 이동
cd lab3-2_monitoring-cicd
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 모니터링 스택 배포

```bash
chmod +x scripts/*.sh
./scripts/1_deploy_monitoring.sh
```

### 4. UI 접속

**터미널 1 - Prometheus:**
```bash
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# http://localhost:9090
```

**터미널 2 - Grafana:**
```bash
kubectl port-forward -n monitoring svc/grafana 3000:3000
# http://localhost:3000
# Username: admin / Password: admin123
```

### 5. 메트릭 수집 시작

**터미널 3:**
```bash
python scripts/2_metrics_exporter.py
```

### 6. A/B 테스트 실행

**터미널 4:**
```bash
python scripts/3_ab_test_simulator.py --duration 300
```

### 7. Grafana 대시보드 확인

1. Grafana 로그인 (admin/admin123)
2. Dashboards → Import
3. `dashboards/model-performance-dashboard.json` 업로드
4. Data Source: Prometheus 선택
5. Import 클릭

### 8. 자동 재학습 모니터링

**터미널 5:**
```bash
python scripts/4_trigger_pipeline.py
```

---

## 📊 실습 흐름도

```
┌─────────────────┐
│ 1. Deploy Stack │
│   (Prometheus + │
│    Grafana)     │
└────────┬────────┘
         ↓
┌─────────────────┐
│ 2. Start Metrics│
│    Exporter     │
└────────┬────────┘
         ↓
┌─────────────────┐
│ 3. Run A/B Test │
│    Simulator    │
└────────┬────────┘
         ↓
┌─────────────────┐
│ 4. Monitor in   │
│    Grafana      │
└────────┬────────┘
         ↓
┌─────────────────┐
│ 5. Auto Trigger │
│    Retraining   │
└─────────────────┘
```

---

## ✅ 체크리스트

- [ ] Prometheus 배포 완료
- [ ] Grafana 배포 완료
- [ ] Prometheus UI 접속 (localhost:9090)
- [ ] Grafana UI 접속 (localhost:3000)
- [ ] 대시보드 임포트 완료
- [ ] Metrics Exporter 실행 중
- [ ] A/B 테스트 시뮬레이터 실행 중
- [ ] 실시간 메트릭 확인
- [ ] 재학습 트리거 테스트 완료

---

## 🆘 문제 해결

### Prometheus Pod이 시작되지 않음
```bash
kubectl get pods -n monitoring
kubectl logs -n monitoring <prometheus-pod-name>
```

### Grafana에 데이터가 표시되지 않음
```bash
# Prometheus 타겟 확인
curl http://localhost:9090/api/v1/targets

# Data Source 재설정
# Grafana → Configuration → Data Sources → Add Prometheus
# URL: http://prometheus.monitoring.svc.cluster.local:9090
```

### Metrics Exporter 연결 실패
```bash
# 포트 확인
netstat -an | grep 8000

# 재시작
python scripts/2_metrics_exporter.py
```

---

## 📚 다음 단계

- [ ] GitHub Actions CI/CD 설정
- [ ] Slack 알림 구성
- [ ] 실제 모델로 교체
- [ ] Canary 배포 테스트
- [ ] 성능 튜닝

---

상세한 내용은 `README.md`를 참고하세요.
