#!/bin/bash

# Slack Integration Setup Script for Alertmanager
# This script helps you configure Slack notifications for ML model alerts

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "============================================================"
echo "  Alertmanager Slack Integration Setup"
echo "============================================================"
echo ""

# Check if Slack webhook URL is provided
if [ -z "$1" ]; then
    echo -e "${YELLOW}Usage: $0 <SLACK_WEBHOOK_URL>${NC}"
    echo ""
    echo "Example:"
    echo "  $0 https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK"
    echo ""
    echo -e "${BLUE}To get your Slack Webhook URL:${NC}"
    echo "  1. Go to https://api.slack.com/apps"
    echo "  2. Create a new app or select existing one"
    echo "  3. Enable 'Incoming Webhooks'"
    echo "  4. Add webhook to workspace"
    echo "  5. Copy the webhook URL"
    echo ""
    exit 1
fi

SLACK_WEBHOOK_URL="$1"

echo -e "${BLUE}Step 1: Creating Kubernetes Secret for Slack Webhook...${NC}"
kubectl create secret generic alertmanager-slack \
  --from-literal=webhook-url="${SLACK_WEBHOOK_URL}" \
  -n monitoring \
  --dry-run=client -o yaml | kubectl apply -f -

echo -e "${GREEN}✅ Secret created${NC}"
echo ""

echo -e "${BLUE}Step 2: Updating Alertmanager ConfigMap with Slack configuration...${NC}"

# Create temporary file with updated config
cat > /tmp/alertmanager-config-slack.yaml <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: alertmanager-config
  namespace: monitoring
data:
  alertmanager.yml: |
    global:
      resolve_timeout: 5m
      slack_api_url: '${SLACK_WEBHOOK_URL}'
    
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
            send_resolved: true
      
      - name: 'slack-critical'
        slack_configs:
          - channel: '#ml-alerts-critical'
            title: '🚨 Critical Alert: {{ .GroupLabels.alertname }}'
            text: |
              *Model:* {{ .CommonLabels.model_name }}
              *Severity:* CRITICAL
              
              {{ range .Alerts }}
              {{ .Annotations.description }}
              {{ end }}
            color: 'danger'
            send_resolved: true
      
      - name: 'slack-warning'
        slack_configs:
          - channel: '#ml-alerts-warning'
            title: '⚠️ Warning: {{ .GroupLabels.alertname }}'
            text: |
              *Model:* {{ .CommonLabels.model_name }}
              
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
EOF

kubectl apply -f /tmp/alertmanager-config-slack.yaml
rm /tmp/alertmanager-config-slack.yaml

echo -e "${GREEN}✅ ConfigMap updated${NC}"
echo ""

echo -e "${BLUE}Step 3: Restarting Alertmanager to apply changes...${NC}"
kubectl rollout restart deployment/alertmanager -n monitoring
kubectl rollout status deployment/alertmanager -n monitoring --timeout=60s

echo -e "${GREEN}✅ Alertmanager restarted${NC}"
echo ""

echo "============================================================"
echo "  Slack Integration Configured Successfully!"
echo "============================================================"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "  1. Create Slack channels: #ml-alerts, #ml-alerts-critical, #ml-alerts-warning"
echo "  2. Invite the Slack app to these channels"
echo "  3. Test alert with: scripts/test_alert.sh"
echo ""
echo -e "${GREEN}Slack notifications are now enabled!${NC}"
