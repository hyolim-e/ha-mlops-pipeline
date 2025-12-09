#!/bin/bash
#
# Lab 3-2 Part 1: Deploy Monitoring Stack
# Prometheus와 Grafana를 Kubernetes에 배포합니다.
#

set -e

# 색상 정의
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "============================================================"
echo "  Deploying Monitoring Stack (Prometheus + Grafana)"
echo "============================================================"
echo ""

# Step 1: Namespace 생성
echo -e "${BLUE}Step 1: Creating monitoring namespace...${NC}"
kubectl apply -f manifests/prometheus/01-namespace.yaml
echo -e "${GREEN}✅ Namespace 'monitoring' created${NC}"
echo ""

# Step 2: Prometheus 배포
echo -e "${BLUE}Step 2: Deploying Prometheus...${NC}"
kubectl apply -f manifests/prometheus/02-prometheus-config.yaml
echo -e "${GREEN}✅ ConfigMap 'prometheus-config' created${NC}"

kubectl apply -f manifests/prometheus/03-prometheus-deployment.yaml
echo -e "${GREEN}✅ Deployment 'prometheus' created${NC}"

kubectl apply -f manifests/prometheus/04-prometheus-service.yaml
echo -e "${GREEN}✅ Service 'prometheus' created${NC}"
echo ""

# Step 3: Grafana 배포
echo -e "${BLUE}Step 3: Deploying Grafana...${NC}"
kubectl apply -f manifests/grafana/01-grafana-config.yaml
echo -e "${GREEN}✅ ConfigMap 'grafana-datasources' created${NC}"

kubectl apply -f manifests/grafana/02-grafana-deployment.yaml
echo -e "${GREEN}✅ Deployment 'grafana' created${NC}"

kubectl apply -f manifests/grafana/03-grafana-service.yaml
echo -e "${GREEN}✅ Service 'grafana' created${NC}"
echo ""

# Step 4: Alertmanager 배포
echo -e "${BLUE}Step 4: Deploying Alertmanager...${NC}"
kubectl apply -f manifests/alertmanager/01-alertmanager-config.yaml
echo -e "${GREEN}✅ ConfigMap 'alertmanager-config' created${NC}"

kubectl apply -f manifests/alertmanager/02-alertmanager-deployment.yaml
echo -e "${GREEN}✅ Deployment 'alertmanager' created${NC}"

kubectl apply -f manifests/alertmanager/03-alertmanager-service.yaml
echo -e "${GREEN}✅ Service 'alertmanager' created${NC}"
echo ""

# Step 5: Metrics Exporter 배포
echo -e "${BLUE}Step 5: Deploying Metrics Exporter...${NC}"

# 기존 deployment가 있으면 삭제 (OOM 문제 해결)
if kubectl get deployment metrics-exporter -n monitoring &>/dev/null; then
    echo "  Removing old metrics-exporter deployment..."
    kubectl delete deployment metrics-exporter -n monitoring --wait=true
    sleep 5
fi

kubectl apply -f manifests/metrics-exporter/00-configmap.yaml
echo -e "${GREEN}✅ ConfigMap 'metrics-exporter-script' created${NC}"

kubectl apply -f manifests/metrics-exporter/01-deployment.yaml
echo -e "${GREEN}✅ Deployment 'metrics-exporter' created (lightweight version)${NC}"
echo -e "${GREEN}✅ Service 'metrics-exporter' created${NC}"
echo ""

# Step 6: Prometheus 재시작 (새로운 scrape config 적용)
echo -e "${BLUE}Step 6: Restarting Prometheus to apply new config...${NC}"
kubectl rollout restart deployment/prometheus -n monitoring
echo -e "${GREEN}✅ Prometheus restarted${NC}"
echo ""

# Step 7: Pod 상태 확인
echo -e "${BLUE}Step 7: Waiting for pods to be ready...${NC}"
echo "This may take 1-2 minutes..."
echo ""

# Prometheus Pod 대기
kubectl wait --for=condition=ready pod -l app=prometheus -n monitoring --timeout=300s
echo -e "${GREEN}✅ Prometheus is ready${NC}"

# Grafana Pod 대기
kubectl wait --for=condition=ready pod -l app=grafana -n monitoring --timeout=300s
echo -e "${GREEN}✅ Grafana is ready${NC}"

# Alertmanager Pod 대기
kubectl wait --for=condition=ready pod -l app=alertmanager -n monitoring --timeout=300s
echo -e "${GREEN}✅ Alertmanager is ready${NC}"

# Metrics Exporter Pod 대기
kubectl wait --for=condition=ready pod -l app=metrics-exporter -n monitoring --timeout=300s
echo -e "${GREEN}✅ Metrics Exporter is ready${NC}"
echo ""

# Step 8: 배포 확인
echo "============================================================"
echo "  Monitoring Stack Deployed Successfully!"
echo "============================================================"
echo ""

echo -e "${BLUE}Deployed Resources:${NC}"
kubectl get all -n monitoring
echo ""

echo -e "${YELLOW}Access URLs:${NC}"
echo "  Prometheus:   kubectl port-forward -n monitoring svc/prometheus 9090:9090"
echo "  Grafana:      kubectl port-forward -n monitoring svc/grafana 3000:3000"
echo "  Alertmanager: kubectl port-forward -n monitoring svc/alertmanager 9093:9093"
echo ""

echo -e "${YELLOW}Default Grafana Credentials:${NC}"
echo "  Username: admin"
echo "  Password: admin123"
echo ""

echo -e "${GREEN}Next Steps:${NC}"
echo "  1. Access Prometheus UI: http://localhost:9090"
echo "  2. Access Grafana UI: http://localhost:3000"
echo "  3. Access Alertmanager UI: http://localhost:9093"
echo "  4. Import dashboard from: dashboards/model-performance-dashboard.json"
echo "  5. ✅ Metrics Exporter is already running in Kubernetes!"
echo ""
echo -e "${YELLOW}Check metrics:${NC}"
echo "  kubectl logs -n monitoring -l app=metrics-exporter"
echo "  kubectl port-forward -n monitoring svc/metrics-exporter 8000:8000"
echo "  curl http://localhost:8000/metrics"
echo ""

echo "============================================================"
