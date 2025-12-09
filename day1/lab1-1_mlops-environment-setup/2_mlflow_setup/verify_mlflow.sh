#!/bin/bash

# Lab 1-1 Part 2: MLflow 배포 확인 스크립트
# 이 스크립트는 MLflow 환경이 올바르게 배포되었는지 확인합니다.

echo "============================================================"
echo "Lab 1-1 Part 2: MLflow 배포 확인"
echo "============================================================"

# Step 1: MLflow 네임스페이스 확인
echo ""
echo "============================================================"
echo "Step 1: MLflow 네임스페이스 확인"
echo "============================================================"

if kubectl get namespace mlflow-system > /dev/null 2>&1; then
    echo "✅ mlflow-system 네임스페이스 존재"
else
    echo "❌ mlflow-system 네임스페이스를 찾을 수 없습니다."
    exit 1
fi

# Step 2: MLflow 파드 확인
echo ""
echo "============================================================"
echo "Step 2: MLflow 파드 상태 확인"
echo "============================================================"

MLFLOW_POD=$(kubectl get pods -n mlflow-system -l app=mlflow-server -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -n "$MLFLOW_POD" ]; then
    echo "✅ MLflow 서버 파드: $MLFLOW_POD"
    kubectl get pods -n mlflow-system -l app=mlflow-server
else
    echo "❌ MLflow 서버 파드를 찾을 수 없습니다."
    kubectl get pods -n mlflow-system
    exit 1
fi

# Step 3: PostgreSQL 파드 확인
echo ""
echo "============================================================"
echo "Step 3: PostgreSQL 파드 상태 확인"
echo "============================================================"

POSTGRES_POD=$(kubectl get pods -n mlflow-system -l app=postgres -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -n "$POSTGRES_POD" ]; then
    echo "✅ PostgreSQL 파드: $POSTGRES_POD"
    kubectl get pods -n mlflow-system -l app=postgres
else
    echo "❌ PostgreSQL 파드를 찾을 수 없습니다."
    kubectl get pods -n mlflow-system
    exit 1
fi

# Step 4: MLflow 서비스 확인
echo ""
echo "============================================================"
echo "Step 4: MLflow 서비스 확인"
echo "============================================================"

if kubectl get svc mlflow-server-service -n mlflow-system > /dev/null 2>&1; then
    echo "✅ mlflow-server-service 존재"
    kubectl get svc -n mlflow-system
else
    echo "❌ mlflow-server-service를 찾을 수 없습니다."
    exit 1
fi

# 완료
echo ""
echo "============================================================"
echo "✅ MLflow 배포 확인 완료!"
echo "============================================================"
echo ""
echo "다음 단계:"
echo "  kubectl port-forward svc/mlflow-server-service -n mlflow-system 5000:5000"
echo "  브라우저: http://localhost:5000"
