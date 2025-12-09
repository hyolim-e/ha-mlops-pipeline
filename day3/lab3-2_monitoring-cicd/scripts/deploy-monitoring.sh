#!/bin/bash
# 모니터링 스택 배포 스크립트

echo "========================================="
echo "모니터링 스택 배포"
echo "========================================="

# Namespace
kubectl apply -f manifests/monitoring/namespace.yaml

# Prometheus
echo ""
echo "📊 Prometheus 배포 중..."
kubectl apply -f manifests/monitoring/prometheus/

# Grafana
echo ""
echo "📈 Grafana 배포 중..."
kubectl apply -f manifests/monitoring/grafana/

# Metrics Exporter
echo ""
echo "📉 Metrics Exporter 배포 중..."
kubectl apply -f manifests/monitoring/metrics-exporter/

# Alertmanager
echo ""
echo "🔔 Alertmanager 배포 중..."
kubectl apply -f manifests/monitoring/alertmanager/

echo ""
echo "✅ 모니터링 스택 배포 완료!"
echo ""
echo "상태 확인:"
echo "  kubectl get pods -n monitoring-system"
echo ""
echo "Grafana 접속:"
echo "  kubectl port-forward -n monitoring-system svc/grafana 3000:80"
echo "  http://localhost:3000 (admin/admin)"
