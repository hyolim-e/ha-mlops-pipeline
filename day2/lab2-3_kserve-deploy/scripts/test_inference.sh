#!/bin/bash

NAMESPACE="kubeflow-user01"  # 변경 필요
MODEL_NAME="california-model"

echo "============================================================"
echo "  추론 테스트"
echo "============================================================"

# Pod 찾기
POD=$(kubectl get pods -n $NAMESPACE \
  -l serving.kserve.io/inferenceservice=$MODEL_NAME \
  --no-headers | head -1 | awk '{print $1}')

if [ -z "$POD" ]; then
    echo "ERROR: Pod를 찾을 수 없습니다"
    exit 1
fi

echo "Pod: $POD"
echo ""

# 포트 포워딩
echo "포트 포워딩 중..."
kubectl port-forward -n $NAMESPACE pod/$POD 8081:8080 &
PF_PID=$!
sleep 3

# 추론 테스트
echo "추론 테스트..."
RESPONSE=$(curl -s -X POST http://localhost:8081/v1/models/$MODEL_NAME:predict \
  -H "Content-Type: application/json" \
  -d '{"instances": [[8.3252, 41.0, 6.984, 1.024, 322.0, 2.556, 37.88, -122.23]]}')

echo "$RESPONSE" | python3 -m json.tool

# 정리
kill $PF_PID 2>/dev/null

echo ""
echo "✅ 테스트 완료"
