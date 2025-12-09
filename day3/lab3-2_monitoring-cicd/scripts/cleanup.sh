#!/bin/bash
# 리소스 정리 스크립트

echo "========================================="
echo "리소스 정리"
echo "========================================="

echo "⚠️  모든 리소스를 삭제합니다!"
echo "계속하시겠습니까? (y/n)"
read -p "> " answer

if [ "$answer" != "y" ]; then
  echo "취소되었습니다"
  exit 0
fi

# 모니터링 스택 삭제
echo ""
echo "모니터링 스택 삭제 중..."
kubectl delete namespace monitoring-system

# 모델 삭제
echo ""
echo "모델 삭제 중..."
kubectl delete inferenceservice --all -n kubeflow-user01

echo ""
echo "✅ 리소스 정리 완료!"
