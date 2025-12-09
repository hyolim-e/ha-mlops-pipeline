#!/bin/bash

# Lab 1-1 Part 1: Kubeflow 설정 확인 스크립트
# 이 스크립트는 Kubeflow 환경이 올바르게 설정되었는지 확인합니다.

echo "============================================================"
echo "Lab 1-1 Part 1: Kubeflow 설정 확인"
echo "============================================================"

# 환경 변수 확인
if [ -z "$USER_NUM" ]; then
    echo "⚠️  USER_NUM 환경 변수가 설정되지 않았습니다."
    echo "다음 명령어를 실행하세요: export USER_NUM=\"01\""
    exit 1
fi

NAMESPACE="kubeflow-user${USER_NUM}"

echo ""
echo "사용자 번호: $USER_NUM"
echo "네임스페이스: $NAMESPACE"

# Step 1: 네임스페이스 확인
echo ""
echo "============================================================"
echo "Step 1: 네임스페이스 확인"
echo "============================================================"

if kubectl get namespace $NAMESPACE > /dev/null 2>&1; then
    echo "✅ 네임스페이스 존재: $NAMESPACE"
else
    echo "❌ 네임스페이스를 찾을 수 없습니다: $NAMESPACE"
    exit 1
fi

# Step 2: Kubeflow 파드 확인
echo ""
echo "============================================================"
echo "Step 2: Kubeflow 파드 상태 확인"
echo "============================================================"

POD_COUNT=$(kubectl get pods -n $NAMESPACE | grep -c "Running")

if [ $POD_COUNT -gt 0 ]; then
    echo "✅ Running 상태 파드: $POD_COUNT개"
    kubectl get pods -n $NAMESPACE
else
    echo "❌ Running 상태 파드가 없습니다."
    kubectl get pods -n $NAMESPACE
    exit 1
fi

# Step 3: Kubeflow 서비스 확인
echo ""
echo "============================================================"
echo "Step 3: Kubeflow 서비스 확인"
echo "============================================================"

if kubectl get svc ml-pipeline-ui -n $NAMESPACE > /dev/null 2>&1; then
    echo "✅ ml-pipeline-ui 서비스 존재"
    kubectl get svc -n $NAMESPACE
else
    echo "❌ ml-pipeline-ui 서비스를 찾을 수 없습니다."
    exit 1
fi

# 완료
echo ""
echo "============================================================"
echo "✅ Kubeflow 설정 확인 완료!"
echo "============================================================"
echo ""
echo "다음 단계:"
echo "  kubectl port-forward svc/ml-pipeline-ui -n $NAMESPACE 8080:80"
echo "  브라우저: http://localhost:8080"
