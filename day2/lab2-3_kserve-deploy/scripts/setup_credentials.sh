#!/bin/bash
set -e

NAMESPACE="kubeflow-user01"  # 변경 필요

echo "============================================================"
echo "  AWS 자격증명 설정"
echo "============================================================"

if [ -z "$AWS_ACCESS_KEY_ID" ] || [ -z "$AWS_SECRET_ACCESS_KEY" ]; then
    echo "ERROR: AWS 환경 변수를 설정하세요"
    echo "export AWS_ACCESS_KEY_ID='<YOUR_KEY>'"
    echo "export AWS_SECRET_ACCESS_KEY='<YOUR_SECRET>'"
    exit 1
fi

echo "Secret 생성 중..."
kubectl create secret generic aws-s3-credentials \
  --from-literal=AWS_ACCESS_KEY_ID="$AWS_ACCESS_KEY_ID" \
  --from-literal=AWS_SECRET_ACCESS_KEY="$AWS_SECRET_ACCESS_KEY" \
  --from-literal=AWS_DEFAULT_REGION="ap-northeast-2" \
  -n $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

echo "ConfigMap 생성 중..."
kubectl create configmap s3-config \
  --from-literal=S3_ENDPOINT="s3.amazonaws.com" \
  --from-literal=S3_USE_HTTPS="1" \
  --from-literal=AWS_REGION="ap-northeast-2" \
  -n $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

echo ""
echo "✅ 자격증명 설정 완료"
