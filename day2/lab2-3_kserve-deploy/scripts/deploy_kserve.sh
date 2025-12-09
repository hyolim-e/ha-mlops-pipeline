#!/bin/bash
set -e

NAMESPACE="kubeflow-user01"  # 변경 필요

echo "============================================================"
echo "  KServe InferenceService 배포"
echo "============================================================"

echo "InferenceService 배포 중..."
kubectl apply -f manifests/inferenceservice.yaml

echo "배포 대기 중 (2-3분 소요)..."
kubectl wait --for=condition=Ready \
  inferenceservice/california-model \
  -n $NAMESPACE \
  --timeout=300s

echo ""
echo "✅ 배포 완료!"
kubectl get inferenceservice -n $NAMESPACE
kubectl get pods -n $NAMESPACE -l serving.kserve.io/inferenceservice=california-model
