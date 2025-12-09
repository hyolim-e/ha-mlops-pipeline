#!/bin/bash
# ============================================================
# cleanup.sh - 실습 리소스 정리 스크립트
# ============================================================

set -e

echo "============================================================"
echo "  🧹 MLOps Training Resource Cleanup"
echo "============================================================"

# 환경 변수 확인
NAMESPACE="${NAMESPACE:-kubeflow-user01}"

echo ""
echo "  Target Namespace: ${NAMESPACE}"
echo ""
read -p "  ⚠️  Are you sure you want to delete all resources? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "  Cleanup cancelled."
    exit 0
fi

# ============================================================
# Step 1: Jupyter Notebook 삭제
# ============================================================

echo ""
echo "[Step 1] Deleting Jupyter Notebooks..."

kubectl delete notebooks --all -n ${NAMESPACE} 2>/dev/null && \
    echo "  ✅ Notebooks deleted" || \
    echo "  ℹ️  No notebooks found"

# ============================================================
# Step 2: InferenceService 삭제
# ============================================================

echo ""
echo "[Step 2] Deleting KServe InferenceServices..."

kubectl delete inferenceservices --all -n ${NAMESPACE} 2>/dev/null && \
    echo "  ✅ InferenceServices deleted" || \
    echo "  ℹ️  No InferenceServices found"

# ============================================================
# Step 3: Deployments 삭제
# ============================================================

echo ""
echo "[Step 3] Deleting Deployments..."

kubectl delete deployments --all -n ${NAMESPACE} 2>/dev/null && \
    echo "  ✅ Deployments deleted" || \
    echo "  ℹ️  No deployments found"

# ============================================================
# Step 4: Services 삭제
# ============================================================

echo ""
echo "[Step 4] Deleting Services..."

# 시스템 서비스 제외하고 삭제
kubectl get svc -n ${NAMESPACE} -o name 2>/dev/null | \
    grep -v "kubernetes" | \
    xargs -r kubectl delete -n ${NAMESPACE} 2>/dev/null && \
    echo "  ✅ Services deleted" || \
    echo "  ℹ️  No services found"

# ============================================================
# Step 5: PVC 삭제
# ============================================================

echo ""
echo "[Step 5] Deleting PersistentVolumeClaims..."

kubectl delete pvc --all -n ${NAMESPACE} 2>/dev/null && \
    echo "  ✅ PVCs deleted" || \
    echo "  ℹ️  No PVCs found"

# ============================================================
# Step 6: Pods 삭제 (남은 것들)
# ============================================================

echo ""
echo "[Step 6] Deleting remaining Pods..."

kubectl delete pods --all -n ${NAMESPACE} 2>/dev/null && \
    echo "  ✅ Pods deleted" || \
    echo "  ℹ️  No pods found"

# ============================================================
# Step 7: 정리 확인
# ============================================================

echo ""
echo "[Step 7] Verifying cleanup..."

echo ""
echo "  Remaining resources in ${NAMESPACE}:"
kubectl get all -n ${NAMESPACE} 2>/dev/null || echo "  (No resources)"

# ============================================================
# 완료
# ============================================================

echo ""
echo "============================================================"
echo "  ✅ Cleanup complete!"
echo "============================================================"
echo ""
echo "  💡 Tip: Run this script before leaving each day"
echo "  💰 Reminder: Unused resources incur AWS costs!"
echo ""
