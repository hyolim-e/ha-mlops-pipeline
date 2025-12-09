#!/bin/bash
# ============================================================
# aws-configure.sh - AWS CLI 및 EKS 설정 스크립트
# ============================================================

set -e

echo "============================================================"
echo "  AWS CLI & EKS Configuration"
echo "============================================================"

# ============================================================
# Step 1: AWS CLI 자격 증명 확인
# ============================================================

echo ""
echo "[Step 1] Checking AWS CLI configuration..."

if aws sts get-caller-identity &> /dev/null; then
    echo "  ✅ AWS CLI is already configured"
    aws sts get-caller-identity
else
    echo "  ⚠️  AWS CLI not configured. Please run 'aws configure'"
    echo ""
    echo "  You will need:"
    echo "    - AWS Access Key ID"
    echo "    - AWS Secret Access Key"
    echo "    - Default region: ap-northeast-2"
    echo "    - Default output format: json"
    echo ""
    read -p "  Configure now? (y/n): " answer
    if [ "$answer" = "y" ]; then
        aws configure
    else
        echo "  Skipping AWS configuration..."
        exit 1
    fi
fi

# ============================================================
# Step 2: EKS 클러스터 연결
# ============================================================

echo ""
echo "[Step 2] Connecting to EKS cluster..."

CLUSTER_NAME="${CLUSTER_NAME:-mlops-training-cluster}"
AWS_REGION="${AWS_REGION:-ap-northeast-2}"

aws eks update-kubeconfig \
    --region ${AWS_REGION} \
    --name ${CLUSTER_NAME}

echo "  ✅ kubeconfig updated for cluster: ${CLUSTER_NAME}"

# ============================================================
# Step 3: 연결 확인
# ============================================================

echo ""
echo "[Step 3] Verifying cluster connection..."

if kubectl cluster-info &> /dev/null; then
    echo "  ✅ Successfully connected to Kubernetes cluster"
    echo ""
    echo "  Cluster Info:"
    kubectl cluster-info | head -2
else
    echo "  ❌ Failed to connect to cluster"
    exit 1
fi

# ============================================================
# Step 4: 노드 확인
# ============================================================

echo ""
echo "[Step 4] Checking cluster nodes..."

kubectl get nodes

# ============================================================
# Step 5: 네임스페이스 확인
# ============================================================

echo ""
echo "[Step 5] Checking your namespace..."

NAMESPACE="${NAMESPACE:-kubeflow-user01}"

if kubectl get namespace ${NAMESPACE} &> /dev/null; then
    echo "  ✅ Namespace '${NAMESPACE}' exists"
    echo ""
    echo "  Resources in your namespace:"
    kubectl get all -n ${NAMESPACE} 2>/dev/null || echo "  (No resources yet)"
else
    echo "  ⚠️  Namespace '${NAMESPACE}' not found"
    echo "  Please check your USER_NUM setting in setup-env.sh"
fi

# ============================================================
# Step 6: ECR 로그인
# ============================================================

echo ""
echo "[Step 6] Logging in to ECR..."

AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

aws ecr get-login-password --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${ECR_REGISTRY} 2>/dev/null && \
    echo "  ✅ ECR login successful" || \
    echo "  ⚠️  ECR login failed (Docker may not be running)"

# ============================================================
# 완료
# ============================================================

echo ""
echo "============================================================"
echo "  ✅ AWS & EKS configuration complete!"
echo "============================================================"
echo ""
echo "  Next steps:"
echo "    1. Access Kubeflow Dashboard:"
echo "       kubectl port-forward svc/istio-ingressgateway -n istio-system 8080:80"
echo "       Then open: http://localhost:8080"
echo ""
echo "    2. Access MLflow:"
echo "       kubectl port-forward svc/mlflow-server-service -n mlflow-system 5000:5000"
echo "       Then open: http://localhost:5000"
echo ""
