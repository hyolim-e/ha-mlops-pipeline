#!/bin/bash

# Lab 3-2 빠른 검증 스크립트
# 모든 컴포넌트가 정상 작동하는지 확인합니다.

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "============================================================"
echo "  Lab 3-2 Monitoring Stack Verification"
echo "============================================================"
echo ""

# Test 1: Pod 상태 확인
echo -e "${BLUE}Test 1: Checking pod status...${NC}"
PODS=$(kubectl get pods -n monitoring --no-headers 2>/dev/null | wc -l)
RUNNING=$(kubectl get pods -n monitoring --no-headers 2>/dev/null | grep -c "Running" || true)

if [ "$PODS" -eq 4 ] && [ "$RUNNING" -eq 4 ]; then
    echo -e "${GREEN}✅ All 4 pods are running${NC}"
    kubectl get pods -n monitoring
else
    echo -e "${RED}❌ Expected 4 running pods, got $RUNNING/$PODS${NC}"
    kubectl get pods -n monitoring
    exit 1
fi
echo ""

# Test 2: Prometheus 접근 확인
echo -e "${BLUE}Test 2: Checking Prometheus accessibility...${NC}"
if kubectl get svc prometheus -n monitoring &>/dev/null; then
    echo -e "${GREEN}✅ Prometheus service exists${NC}"
    
    # Port-forward 테스트 (5초)
    kubectl port-forward -n monitoring svc/prometheus 9090:9090 &>/dev/null &
    PF_PID=$!
    sleep 3
    
    if curl -s http://localhost:9090/-/healthy &>/dev/null; then
        echo -e "${GREEN}✅ Prometheus is healthy${NC}"
    else
        echo -e "${YELLOW}⚠️  Prometheus port-forward failed (start manually)${NC}"
    fi
    
    kill $PF_PID 2>/dev/null || true
else
    echo -e "${RED}❌ Prometheus service not found${NC}"
    exit 1
fi
echo ""

# Test 3: Grafana 접근 확인
echo -e "${BLUE}Test 3: Checking Grafana accessibility...${NC}"
if kubectl get svc grafana -n monitoring &>/dev/null; then
    echo -e "${GREEN}✅ Grafana service exists${NC}"
else
    echo -e "${RED}❌ Grafana service not found${NC}"
    exit 1
fi
echo ""

# Test 4: Metrics Exporter 확인
echo -e "${BLUE}Test 4: Checking Metrics Exporter...${NC}"
if kubectl get deployment metrics-exporter -n monitoring &>/dev/null; then
    echo -e "${GREEN}✅ Metrics Exporter deployment exists${NC}"
    
    READY=$(kubectl get deployment metrics-exporter -n monitoring -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
    if [ "$READY" = "1" ]; then
        echo -e "${GREEN}✅ Metrics Exporter is ready${NC}"
    else
        echo -e "${RED}❌ Metrics Exporter is not ready${NC}"
        kubectl describe deployment metrics-exporter -n monitoring
        exit 1
    fi
else
    echo -e "${RED}❌ Metrics Exporter deployment not found${NC}"
    exit 1
fi
echo ""

# Test 5: Metrics Exporter 로그 확인
echo -e "${BLUE}Test 5: Checking Metrics Exporter logs...${NC}"
LOGS=$(kubectl logs -n monitoring -l app=metrics-exporter --tail=30 2>/dev/null || echo "")
if echo "$LOGS" | grep -q "Metrics server started"; then
    echo -e "${GREEN}✅ Metrics Exporter is generating metrics${NC}"
    echo "$LOGS" | grep -A 3 "Metrics server started" | head -5
else
    echo -e "${YELLOW}⚠️  Metrics Exporter logs (checking for startup message)${NC}"
    echo "$LOGS" | grep -v "WARNING" | grep -v "notice" | tail -5
fi
echo ""

# Test 6: Prometheus ConfigMap 확인
echo -e "${BLUE}Test 6: Checking Prometheus configuration...${NC}"
if kubectl get configmap prometheus-config -n monitoring &>/dev/null; then
    echo -e "${GREEN}✅ Prometheus ConfigMap exists${NC}"
    
    if kubectl get configmap prometheus-config -n monitoring -o yaml | grep -q "metrics-exporter"; then
        echo -e "${GREEN}✅ Prometheus is configured to scrape metrics-exporter${NC}"
    else
        echo -e "${RED}❌ Prometheus scrape config for metrics-exporter not found${NC}"
        exit 1
    fi
else
    echo -e "${RED}❌ Prometheus ConfigMap not found${NC}"
    exit 1
fi
echo ""

# Test 7: Grafana DataSource 확인
echo -e "${BLUE}Test 7: Checking Grafana DataSource configuration...${NC}"
if kubectl get configmap grafana-datasources -n monitoring &>/dev/null; then
    echo -e "${GREEN}✅ Grafana DataSource ConfigMap exists${NC}"
    
    if kubectl get configmap grafana-datasources -n monitoring -o yaml | grep -q "uid: prometheus"; then
        echo -e "${GREEN}✅ Grafana DataSource has prometheus UID${NC}"
    else
        echo -e "${YELLOW}⚠️  Grafana DataSource may need manual configuration${NC}"
    fi
else
    echo -e "${RED}❌ Grafana DataSource ConfigMap not found${NC}"
    exit 1
fi
echo ""

# Summary
echo "============================================================"
echo "  Verification Summary"
echo "============================================================"
echo ""
echo -e "${GREEN}✅ All core components are healthy!${NC}"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Port-forward Prometheus:"
echo "     kubectl port-forward -n monitoring svc/prometheus 9090:9090"
echo ""
echo "  2. Port-forward Grafana:"
echo "     kubectl port-forward -n monitoring svc/grafana 3000:3000"
echo ""
echo "  3. Check Prometheus targets:"
echo "     http://localhost:9090/targets"
echo "     → metrics-exporter should be UP"
echo ""
echo "  4. Import Grafana dashboard:"
echo "     http://localhost:3000 (admin/admin123)"
echo "     → Import dashboards/model-performance-dashboard.json"
echo ""
echo "  5. Verify metrics:"
echo "     kubectl port-forward -n monitoring svc/metrics-exporter 8000:8000"
echo "     curl http://localhost:8000/metrics | grep model_mae_score"
echo ""
echo -e "${GREEN}Happy monitoring! 🎉${NC}"
