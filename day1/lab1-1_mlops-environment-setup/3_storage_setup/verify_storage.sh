#!/bin/bash

# Lab 1-1 Part 3: 스토리지 확인 스크립트
# 이 스크립트는 MinIO와 PostgreSQL 스토리지가 올바르게 구성되었는지 확인합니다.

echo "============================================================"
echo "Lab 1-1 Part 3: 스토리지 확인"
echo "============================================================"

# Step 1: MinIO 확인
echo ""
echo "============================================================"
echo "Step 1: MinIO 파드 상태 확인"
echo "============================================================"

MINIO_POD=$(kubectl get pods -n kubeflow -l app=minio -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)

if [ -n "$MINIO_POD" ]; then
    echo "✅ MinIO 파드: $MINIO_POD"
    kubectl get pods -n kubeflow -l app=minio
else
    echo "⚠️  MinIO 파드를 찾을 수 없습니다."
    echo "다른 레이블로 검색 중..."
    kubectl get pods -n kubeflow | grep minio
fi

# Step 2: MinIO 서비스 확인
echo ""
echo "============================================================"
echo "Step 2: MinIO 서비스 확인"
echo "============================================================"

if kubectl get svc -n kubeflow | grep -q minio; then
    echo "✅ MinIO 서비스 존재"
    kubectl get svc -n kubeflow | grep minio
else
    echo "❌ MinIO 서비스를 찾을 수 없습니다."
fi

# Step 3: PostgreSQL 확인
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
fi

# Step 4: PostgreSQL 서비스 확인
echo ""
echo "============================================================"
echo "Step 4: PostgreSQL 서비스 확인"
echo "============================================================"

if kubectl get svc postgres-service -n mlflow-system > /dev/null 2>&1; then
    echo "✅ postgres-service 존재"
    kubectl get svc -n mlflow-system | grep postgres
else
    echo "❌ postgres-service를 찾을 수 없습니다."
fi

# Step 5: 전체 스토리지 요약
echo ""
echo "============================================================"
echo "Step 5: 스토리지 아키텍처 요약"
echo "============================================================"

echo ""
echo "📊 스토리지 구성:"
echo ""
echo "  ┌─────────────────────────────────────────────┐"
echo "  │         MLOps Storage Architecture          │"
echo "  ├─────────────────────────────────────────────┤"
echo "  │                                             │"
echo "  │  MinIO (S3-Compatible Object Storage)       │"
echo "  │  ├─ Namespace: kubeflow                     │"
echo "  │  ├─ Port: 9000 (API), 9001 (Console)        │"
echo "  │  └─ 용도: MLflow Artifacts, Pipeline Data   │"
echo "  │                                             │"
echo "  │  PostgreSQL (Relational Database)           │"
echo "  │  ├─ Namespace: mlflow-system                │"
echo "  │  ├─ Port: 5432                              │"
echo "  │  └─ 용도: MLflow Metadata                   │"
echo "  │                                             │"
echo "  └─────────────────────────────────────────────┘"
echo ""

# 완료
echo "============================================================"
echo "✅ 스토리지 확인 완료!"
echo "============================================================"
