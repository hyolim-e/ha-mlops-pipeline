#!/bin/bash
# ============================================================
# setup-env.sh - MLOps Training 환경 변수 설정
# ============================================================

# 사용자 번호 설정 (각자 수정!)
# ⚠️ 본인의 번호로 변경하세요! (예: 01, 02, ..., 30)
export USER_NUM="${USER_NUM:-01}"

# ============================================================
# 공통 설정 (수정 불필요)
# ============================================================

# Kubernetes 설정
export NAMESPACE="kubeflow-user${USER_NUM}"
export CLUSTER_NAME="mlops-training-cluster"

# AWS 설정
export AWS_REGION="ap-northeast-2"
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text 2>/dev/null || echo "unknown")

# S3 버킷
export S3_DATA_BUCKET="mlops-training-data"
export S3_MODEL_BUCKET="mlops-training-models"
export S3_ARTIFACT_BUCKET="mlops-training-artifacts"

# ECR 리포지토리
export ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
export ECR_REPO_PREFIX="mlops-training"

# MLflow 설정
export MLFLOW_TRACKING_URI="http://mlflow-server-service.mlflow-system.svc.cluster.local:5000"
export MLFLOW_S3_ENDPOINT_URL="http://minio-service.kubeflow.svc:9000"

# Kubeflow 설정
export KF_PIPELINES_ENDPOINT="http://ml-pipeline-ui.kubeflow.svc.cluster.local"

# ============================================================
# 설정 확인 출력
# ============================================================

echo "============================================================"
echo "  MLOps Training Environment Variables"
echo "============================================================"
echo ""
echo "  👤 User Number:     ${USER_NUM}"
echo "  📁 Namespace:       ${NAMESPACE}"
echo "  ☁️  AWS Region:      ${AWS_REGION}"
echo "  🆔 AWS Account:     ${AWS_ACCOUNT_ID}"
echo ""
echo "  📦 S3 Buckets:"
echo "     - Data:          s3://${S3_DATA_BUCKET}"
echo "     - Models:        s3://${S3_MODEL_BUCKET}"
echo "     - Artifacts:     s3://${S3_ARTIFACT_BUCKET}"
echo ""
echo "  🐳 ECR Registry:    ${ECR_REGISTRY}"
echo ""
echo "  📊 MLflow URI:      ${MLFLOW_TRACKING_URI}"
echo ""
echo "============================================================"
echo "  ✅ Environment setup complete!"
echo "============================================================"
