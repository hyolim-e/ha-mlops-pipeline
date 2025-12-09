#!/bin/bash
# 모델 배포 스크립트

echo "========================================="
echo "모델 배포"
echo "========================================="

NAMESPACE="${KSERVE_NAMESPACE:-kubeflow-user01}"

echo "Namespace: $NAMESPACE"
echo ""

# InferenceService 배포
kubectl apply -f manifests/model/inferenceservice.yaml -n $NAMESPACE

echo ""
echo "✅ 모델 배포 완료!"
echo ""
echo "상태 확인:"
echo "  kubectl get inferenceservice -n $NAMESPACE"
echo ""
echo "API 테스트:"
echo "  kubectl port-forward -n $NAMESPACE svc/california-housing-predictor 8000:80"
echo "  curl http://localhost:8000/health"
