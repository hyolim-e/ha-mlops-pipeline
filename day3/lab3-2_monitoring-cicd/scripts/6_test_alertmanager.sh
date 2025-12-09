#!/bin/bash

# Test Alertmanager Script
# This script tests Alertmanager by sending a test alert

set -e

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

echo "============================================================"
echo "  Alertmanager Test Script"
echo "============================================================"
echo ""

echo -e "${BLUE}Step 1: Checking Alertmanager status...${NC}"

# Check if Alertmanager pod is running
ALERTMANAGER_POD=$(kubectl get pods -n monitoring -l app=alertmanager -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || echo "")

if [ -z "$ALERTMANAGER_POD" ]; then
    echo -e "${RED}❌ Alertmanager pod not found${NC}"
    echo "Please deploy Alertmanager first: ./scripts/1_deploy_monitoring.sh"
    exit 1
fi

POD_STATUS=$(kubectl get pod $ALERTMANAGER_POD -n monitoring -o jsonpath='{.status.phase}')
if [ "$POD_STATUS" != "Running" ]; then
    echo -e "${RED}❌ Alertmanager pod is not running (Status: $POD_STATUS)${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Alertmanager pod is running${NC}"
echo ""

echo -e "${BLUE}Step 2: Setting up port-forward...${NC}"

# Kill any existing port-forward
pkill -f "port-forward.*alertmanager" || true
sleep 2

# Start port-forward in background
kubectl port-forward -n monitoring svc/alertmanager 9093:9093 > /dev/null 2>&1 &
PF_PID=$!
sleep 3

# Cleanup function
cleanup() {
    echo ""
    echo -e "${YELLOW}Cleaning up port-forward...${NC}"
    kill $PF_PID 2>/dev/null || true
}
trap cleanup EXIT

echo -e "${GREEN}✅ Port-forward established${NC}"
echo ""

echo -e "${BLUE}Step 3: Checking Alertmanager health...${NC}"

# Check health endpoint
HEALTH=$(curl -s http://localhost:9093/-/healthy || echo "failed")
if [ "$HEALTH" != "OK" ]; then
    echo -e "${RED}❌ Alertmanager health check failed${NC}"
    echo "Response: $HEALTH"
    exit 1
fi

echo -e "${GREEN}✅ Alertmanager is healthy${NC}"
echo ""

echo -e "${BLUE}Step 4: Sending test alert...${NC}"

# Send test alert
RESPONSE=$(curl -s -X POST http://localhost:9093/api/v1/alerts \
  -H "Content-Type: application/json" \
  -d '[
  {
    "labels": {
      "alertname": "TestAlert",
      "severity": "warning",
      "model_name": "california-housing",
      "version": "v1.0"
    },
    "annotations": {
      "summary": "Test alert from Alertmanager test script",
      "description": "This is a test alert to verify Alertmanager and Slack integration are working correctly"
    },
    "startsAt": "'"$(date -u +%Y-%m-%dT%H:%M:%S.%3NZ)"'",
    "endsAt": "'"$(date -u -d '+5 minutes' +%Y-%m-%dT%H:%M:%S.%3NZ)"'"
  }
]' 2>&1)

if echo "$RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✅ Test alert sent successfully${NC}"
elif [ -z "$RESPONSE" ]; then
    echo -e "${GREEN}✅ Test alert sent (no response body is normal)${NC}"
else
    echo -e "${YELLOW}⚠️  Alert sent, response: $RESPONSE${NC}"
fi
echo ""

echo -e "${BLUE}Step 5: Verifying alert in Alertmanager...${NC}"
sleep 2

# Check if alert is visible in Alertmanager
ALERTS=$(curl -s http://localhost:9093/api/v2/alerts || echo "[]")
ALERT_COUNT=$(echo "$ALERTS" | grep -o '"alertname"' | wc -l)

if [ "$ALERT_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ Alert is visible in Alertmanager (Total alerts: $ALERT_COUNT)${NC}"
    echo ""
    echo "Alert details:"
    echo "$ALERTS" | jq '.[] | {alertname: .labels.alertname, status: .status.state, severity: .labels.severity}' 2>/dev/null || echo "$ALERTS"
else
    echo -e "${YELLOW}⚠️  No alerts visible yet (may take a few seconds)${NC}"
fi
echo ""

echo "============================================================"
echo "  Test Complete!"
echo "============================================================"
echo ""
echo -e "${YELLOW}Access Alertmanager UI:${NC}"
echo "  http://localhost:9093"
echo ""
echo -e "${YELLOW}Check Slack notifications in:${NC}"
echo "  #ml-alerts-warning (if Slack is configured)"
echo ""
echo -e "${GREEN}Tip: Keep port-forward running and visit the UI to see the alert${NC}"
echo ""

# Keep port-forward running for 30 seconds
echo "Port-forward will remain active for 30 seconds..."
sleep 30
