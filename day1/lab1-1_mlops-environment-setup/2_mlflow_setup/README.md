# Lab 1-1 Part 2: MLflow 배포 확인

## 📋 개요

이 섹션에서는 MLflow Tracking Server가 올바르게 배포되었는지 확인합니다.

**소요시간:** 20분

---

## 🎯 확인 항목

- MLflow 네임스페이스 (`mlflow-system`)
- MLflow Server 파드 상태
- PostgreSQL 파드 상태 (MLflow 백엔드)
- MLflow 서비스 확인
- MLflow UI 접속

---

## 🚀 단계별 실행

### Step 1: 자동 검증 스크립트 실행

```bash
# 검증 스크립트 실행
./2_mlflow_setup/verify_mlflow.sh
```

**예상 출력:**
```
============================================================
Lab 1-1 Part 2: MLflow 배포 확인
============================================================

============================================================
Step 1: MLflow 네임스페이스 확인
============================================================
✅ mlflow-system 네임스페이스 존재

============================================================
Step 2: MLflow 파드 상태 확인
============================================================
✅ MLflow 서버 파드: mlflow-server-xxxxxxxxxx-xxxxx
NAME                             READY   STATUS    RESTARTS   AGE
mlflow-server-xxxxxxxxxx-xxxxx   1/1     Running   0          30d

============================================================
Step 3: PostgreSQL 파드 상태 확인
============================================================
✅ PostgreSQL 파드: postgres-xxxxxxxxxx-xxxxx
NAME                        READY   STATUS    RESTARTS   AGE
postgres-xxxxxxxxxx-xxxxx   1/1     Running   0          30d

============================================================
Step 4: MLflow 서비스 확인
============================================================
✅ mlflow-server-service 존재
NAME                    TYPE        CLUSTER-IP       EXTERNAL-IP   PORT(S)    AGE
mlflow-server-service   ClusterIP   10.100.150.100   <none>        5000/TCP   30d
postgres-service        ClusterIP   10.100.150.101   <none>        5432/TCP   30d

============================================================
✅ MLflow 배포 확인 완료!
============================================================

다음 단계:
  kubectl port-forward svc/mlflow-server-service -n mlflow-system 5000:5000
  브라우저: http://localhost:5000
```

### Step 2: 포트 포워딩

```bash
# MLflow UI 접속을 위한 포트 포워딩
kubectl port-forward svc/mlflow-server-service -n mlflow-system 5000:5000
```

**백그라운드 실행:**
```bash
nohup kubectl port-forward svc/mlflow-server-service -n mlflow-system 5000:5000 > mlflow-pf.log 2>&1 &
```

### Step 3: MLflow UI 접속

```bash
# 브라우저에서 접속
open http://localhost:5000
```

**확인 사항:**
- ✅ MLflow 메인 페이지 표시
- ✅ "Experiments" 탭 확인
- ✅ "Models" 탭 확인
- ✅ "Default" Experiment 존재

---

## 🧪 API 테스트

```bash
# MLflow API 엔드포인트 테스트
curl http://localhost:5000/api/2.0/mlflow/experiments/list
```

**예상 출력:**
```json
{
  "experiments": [
    {
      "experiment_id": "0",
      "name": "Default",
      "artifact_location": "s3://mlflow/0",
      "lifecycle_stage": "active"
    }
  ]
}
```

---

## 💡 문제 해결

### 문제: 파드가 Pending 상태

**확인:**
```bash
kubectl describe pod -l app=mlflow-server -n mlflow-system
```

**일반적인 원인:**
- 리소스 부족
- 이미지 Pull 오류
- PVC 마운트 실패

### 문제: 포트 포워딩 실패

**확인:**
```bash
# 파드 상태 확인
kubectl get pods -n mlflow-system

# 포트 사용 확인
lsof -ti:5000 | xargs kill -9
```

---

## ✅ 완료 체크리스트

- [ ] mlflow-system 네임스페이스 확인
- [ ] MLflow Server 파드 Running
- [ ] PostgreSQL 파드 Running
- [ ] MLflow 서비스 확인
- [ ] 포트 포워딩 성공
- [ ] MLflow UI 접속 성공
- [ ] Experiments 페이지 확인

---

## 📚 다음 단계

**Part 3: 스토리지 확인** - MinIO와 PostgreSQL 스토리지 구성 확인
