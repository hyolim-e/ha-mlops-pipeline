# Slack 알림 설정 가이드

## 📢 Slack Webhook 연동 완벽 가이드

이 가이드는 Alertmanager와 Slack을 연동하여 모델 성능 알림을 받는 방법을 설명합니다.

---

## 🔧 Step 1: Slack Webhook URL 생성

### 1-1. Slack Workspace 접속

1. [https://api.slack.com/apps](https://api.slack.com/apps) 접속
2. **"Create New App"** 클릭

### 1-2. App 생성

1. **"From scratch"** 선택
2. App 정보 입력:
   - **App Name**: `MLOps Alerts`
   - **Workspace**: 본인의 Workspace 선택
3. **"Create App"** 클릭

### 1-3. Incoming Webhooks 활성화

1. 좌측 메뉴에서 **"Incoming Webhooks"** 클릭
2. **"Activate Incoming Webhooks"** 토글을 **ON**으로 변경
3. 페이지 하단 **"Add New Webhook to Workspace"** 클릭

### 1-4. 채널 선택 및 권한 부여

1. 알림을 받을 채널 선택:
   - 기존 채널 선택 (예: `#ml-alerts`)
   - 또는 새 채널 생성
2. **"Allow"** 클릭

### 1-5. Webhook URL 복사

```
예시:
https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
```

⚠️ **중요**: 이 URL은 절대 공개하지 마세요!

---

## 🔐 Step 2: Kubernetes Secret 생성

### 2-1. Webhook URL을 Secret으로 저장

```bash
# Slack Webhook URL을 환경 변수로 설정
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/YOUR/WEBHOOK/URL"

# Kubernetes Secret 생성
kubectl create secret generic alertmanager-slack \
  --from-literal=webhook-url="${SLACK_WEBHOOK_URL}" \
  -n monitoring
```

### 2-2. Secret 확인

```bash
kubectl get secret alertmanager-slack -n monitoring
```

---

## ⚙️ Step 3: Alertmanager 설정 업데이트

### 3-1. Alertmanager ConfigMap 수정

```bash
kubectl edit configmap alertmanager-config -n monitoring
```

### 3-2. Slack 설정 추가

기존 주석 처리된 부분을 다음과 같이 수정:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-config
  namespace: monitoring
data:
  alertmanager.yml: |
    global:
      resolve_timeout: 5m
      slack_api_url: '<slack_webhook_url>'  # Secret에서 주입됨
    
    route:
      group_by: ['alertname', 'severity']
      group_wait: 10s
      group_interval: 10s
      repeat_interval: 12h
      receiver: 'slack-notifications'
      routes:
        - match:
            severity: critical
          receiver: 'slack-critical'
          continue: true
        - match:
            severity: warning
          receiver: 'slack-warning'
          continue: true
    
    receivers:
      - name: 'slack-notifications'
        slack_configs:
          - channel: '#ml-alerts'
            title: '📊 ML Model Alert'
            text: |
              *Alert:* {{ .GroupLabels.alertname }}
              *Severity:* {{ .GroupLabels.severity }}
              *Description:* {{ range .Alerts }}{{ .Annotations.description }}{{ end }}
              *Status:* {{ .Status }}
            send_resolved: true
      
      - name: 'slack-critical'
        slack_configs:
          - channel: '#ml-alerts-critical'
            title: '🚨 Critical Alert: {{ .GroupLabels.alertname }}'
            text: |
              *Model:* {{ .CommonLabels.model_name }}
              *Severity:* CRITICAL
              
              *Description:*
              {{ range .Alerts }}
              {{ .Annotations.description }}
              {{ end }}
              
              *Time:* {{ .CommonAnnotations.summary }}
            color: 'danger'
            send_resolved: true
      
      - name: 'slack-warning'
        slack_configs:
          - channel: '#ml-alerts-warning'
            title: '⚠️ Warning: {{ .GroupLabels.alertname }}'
            text: |
              *Model:* {{ .CommonLabels.model_name }}
              *Severity:* WARNING
              
              {{ range .Alerts }}
              {{ .Annotations.description }}
              {{ end }}
            color: 'warning'
            send_resolved: true
    
    inhibit_rules:
      - source_match:
          severity: 'critical'
        target_match:
          severity: 'warning'
        equal: ['alertname', 'model_name']
```

### 3-3. Alertmanager Deployment에 Secret 마운트

```bash
kubectl edit deployment alertmanager -n monitoring
```

다음 내용 추가:

```yaml
spec:
  template:
    spec:
      containers:
        - name: alertmanager
          env:
            - name: SLACK_WEBHOOK_URL
              valueFrom:
                secretKeyRef:
                  name: alertmanager-slack
                  key: webhook-url
          # ... 기존 설정 유지
```

또는 새 매니페스트 적용:

```bash
kubectl apply -f manifests/alertmanager/02-alertmanager-deployment-with-slack.yaml
```

---

## 🔄 Step 4: Alertmanager 재시작

```bash
# ConfigMap 변경사항 반영을 위한 재시작
kubectl rollout restart deployment/alertmanager -n monitoring

# 재시작 확인
kubectl rollout status deployment/alertmanager -n monitoring
```

---

## 🧪 Step 5: 알림 테스트

### 5-1. 수동 알림 테스트

```bash
# Alertmanager API로 테스트 알림 전송
kubectl port-forward -n monitoring svc/alertmanager 9093:9093

# 다른 터미널에서
curl -X POST http://localhost:9093/api/v1/alerts -H "Content-Type: application/json" -d '[
  {
    "labels": {
      "alertname": "TestAlert",
      "severity": "warning",
      "model_name": "california-housing"
    },
    "annotations": {
      "summary": "Test alert from Alertmanager",
      "description": "This is a test alert to verify Slack integration"
    }
  }
]'
```

### 5-2. Slack 채널 확인

1. Slack 채널 (#ml-alerts) 접속
2. 다음과 같은 메시지 확인:

```
⚠️ Warning: TestAlert
Model: california-housing
Severity: WARNING

This is a test alert to verify Slack integration
```

### 5-3. 실제 알림 트리거

```bash
# Metrics Exporter 실행 (MAE 임계값 초과 시뮬레이션)
python scripts/2_metrics_exporter.py

# 5분 후 Slack 알림 확인
```

---

## 📋 Step 6: 알림 채널 구성

### 권장 채널 구조

```
#ml-alerts           → 모든 알림 (warning + critical)
#ml-alerts-critical  → Critical 알림만
#ml-alerts-warning   → Warning 알림만
```

### 채널별 설정

1. **#ml-alerts** (통합 채널)
   - 모든 팀원 참여
   - 모든 알림 수신
   - 알림 빈도: 보통

2. **#ml-alerts-critical** (긴급 채널)
   - On-call 엔지니어만 참여
   - Critical 알림만 수신
   - 알림 빈도: 낮음 (즉시 대응 필요)
   - Slack 알림 설정: **"All new messages"**

3. **#ml-alerts-warning** (모니터링 채널)
   - ML 엔지니어, DevOps 참여
   - Warning 알림만 수신
   - 알림 빈도: 높음 (모니터링 목적)
   - Slack 알림 설정: **"Mentions only"**

---

## 🎨 알림 커스터마이징

### 알림 메시지 포맷 변경

```yaml
slack_configs:
  - channel: '#ml-alerts'
    title: '📊 {{ .GroupLabels.alertname }}'
    text: |
      *환경:* Production
      *모델:* {{ .CommonLabels.model_name }}
      *버전:* {{ .CommonLabels.version }}
      
      *현재 상태:*
      {{ range .Alerts }}
      • {{ .Annotations.description }}
      {{ end }}
      
      *시작 시간:* {{ .StartsAt }}
      *담당자:* @ml-team
    
    # 알림 색상 (good, warning, danger)
    color: '{{ if eq .Status "firing" }}danger{{ else }}good{{ end }}'
    
    # 추가 필드
    fields:
      - title: MAE Score
        value: '{{ .CommonLabels.mae_score }}'
        short: true
      - title: Threshold
        value: '0.40'
        short: true
    
    # 액션 버튼 추가
    actions:
      - type: button
        text: 'View in Grafana'
        url: 'http://grafana.monitoring.svc.cluster.local:3000'
      - type: button
        text: 'Silence Alert'
        url: 'http://alertmanager.monitoring.svc.cluster.local:9093'
```

### 이모지 활용

```yaml
# Severity별 이모지
- Critical: 🚨 🔥 ❌
- Warning: ⚠️ 💡 📊
- Info: ℹ️ 📝 ✅
- Resolved: ✅ 🎉 👍

# 예시
title: '{{ if eq .GroupLabels.severity "critical" }}🚨{{ else }}⚠️{{ end }} {{ .GroupLabels.alertname }}'
```

---

## 🔍 트러블슈팅

### 문제 1: Slack 알림이 오지 않음

**원인 확인:**
```bash
# Alertmanager 로그 확인
kubectl logs -n monitoring deployment/alertmanager

# 설정 확인
kubectl exec -n monitoring deployment/alertmanager -- amtool config show
```

**해결:**
1. Webhook URL이 올바른지 확인
2. Slack App이 채널에 추가되었는지 확인
3. Secret이 올바르게 생성되었는지 확인

### 문제 2: "channel_not_found" 에러

**원인:** Slack App이 채널에 초대되지 않음

**해결:**
```
1. Slack 채널 접속
2. 채널 상단 "Add apps" 클릭
3. "MLOps Alerts" 검색 및 추가
```

### 문제 3: "invalid_payload" 에러

**원인:** Alertmanager 설정 문법 오류

**해결:**
```bash
# 설정 검증
kubectl exec -n monitoring deployment/alertmanager -- amtool check-config /etc/alertmanager/alertmanager.yml
```

### 문제 4: 알림이 너무 많이 옴

**해결 1: Group Wait 조정**
```yaml
route:
  group_wait: 30s      # 30초 → 1분
  group_interval: 5m   # 5분 → 10분
  repeat_interval: 4h  # 4시간 → 12시간
```

**해결 2: Inhibit Rules 활용**
```yaml
inhibit_rules:
  # Critical 발생 시 Warning 억제
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['alertname', 'model_name']
```

---

## 📱 모바일 알림 설정

### iOS/Android Slack 앱 설정

1. Slack 모바일 앱 설치
2. 설정 → 알림 → 채널별 알림 설정
3. **#ml-alerts-critical**: "All new messages"
4. **#ml-alerts-warning**: "Mentions only"

---

## 🔔 알림 예시

### Critical Alert 예시

```
🚨 Critical Alert: ModelPerformanceDegraded

Model: california-housing
Version: v1.0
Severity: CRITICAL

Description:
Model MAE (0.45) exceeded threshold 0.40 for 5 minutes
Performance has degraded significantly and requires immediate attention.

Time: 2025-12-09 14:35:22
Status: firing

[View in Grafana] [Silence Alert]
```

### Resolved Alert 예시

```
✅ Resolved: ModelPerformanceDegraded

Model: california-housing
Status: RESOLVED

The model performance has returned to normal levels.
Current MAE: 0.38 (threshold: 0.40)

Duration: 15 minutes
Resolved at: 2025-12-09 14:50:33
```

---

## 📊 알림 모범 사례

### 1. 알림 피로 방지

- Critical: 즉시 조치 필요한 것만
- Warning: 관찰 필요한 추세
- Info: 로깅 목적

### 2. 명확한 액션 가이드

알림에 다음 정보 포함:
- 무엇이 문제인가?
- 왜 알림이 발생했는가?
- 어떻게 해결하는가?
- 누가 담당자인가?

### 3. Runbook 링크

```yaml
annotations:
  description: 'Model MAE exceeded threshold'
  runbook_url: 'https://wiki.company.com/ml-alerts/mae-degraded'
```

---

## ✅ 완료 체크리스트

- [ ] Slack Workspace에 App 생성
- [ ] Webhook URL 발급
- [ ] Kubernetes Secret 생성
- [ ] Alertmanager ConfigMap 업데이트
- [ ] Slack 채널 생성 및 구성
- [ ] Slack App을 채널에 추가
- [ ] Alertmanager 재시작
- [ ] 테스트 알림 전송
- [ ] Slack에서 알림 수신 확인
- [ ] 실제 알림 트리거 테스트
- [ ] 모바일 알림 설정

---

## 🔗 추가 리소스

- [Alertmanager Slack Configuration](https://prometheus.io/docs/alerting/latest/configuration/#slack_config)
- [Slack API Documentation](https://api.slack.com/messaging/webhooks)
- [Prometheus Alerting Best Practices](https://prometheus.io/docs/practices/alerting/)

---

© 2025 현대오토에버 MLOps Training - Slack 알림 설정 가이드
