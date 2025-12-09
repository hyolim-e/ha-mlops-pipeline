#!/bin/bash
# 전체 환경 설정 스크립트

echo "========================================="
echo "Lab 3-2: 환경 설정"
echo "========================================="

# 환경 변수 확인
if [ -z "$USER_NUM" ]; then
  echo "⚠️  USER_NUM 환경 변수가 설정되지 않았습니다"
  echo "   export USER_NUM=\"01\"  # 본인 번호로 설정"
  exit 1
fi

echo "✅ 사용자 번호: $USER_NUM"

# Namespace 생성
kubectl create namespace monitoring-system --dry-run=client -o yaml | kubectl apply -f -
echo "✅ Namespace 생성: monitoring-system"

# 모니터링 스택 배포
echo ""
echo "모니터링 스택을 배포하시겠습니까? (y/n)"
read -p "> " answer
if [ "$answer" = "y" ]; then
  ./scripts/deploy-monitoring.sh
fi

echo ""
echo "✅ 환경 설정 완료!"
