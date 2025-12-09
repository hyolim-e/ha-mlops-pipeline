#!/bin/bash
set -e

echo "============================================================"
echo "  MLflow 배포"
echo "============================================================"

kubectl apply -f manifests/00-namespace.yaml
kubectl apply -f manifests/01-postgres.yaml
kubectl apply -f manifests/02-minio.yaml
kubectl apply -f manifests/03-mlflow-server.yaml

echo "배포 대기 중..."
kubectl wait --for=condition=ready pod -l app=postgres -n mlflow-system --timeout=300s
kubectl wait --for=condition=ready pod -l app=mlflow-server -n mlflow-system --timeout=300s

echo ""
echo "✅ MLflow 배포 완료!"
echo ""
echo "MLflow UI 접속:"
echo "kubectl port-forward svc/mlflow-server-service -n mlflow-system 5000:5000"
echo "브라우저: http://localhost:5000"
