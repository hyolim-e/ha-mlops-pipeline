"""
Lab 3-2: 모델 배포 컴포넌트
===========================

KServe InferenceService로 모델을 배포하는 컴포넌트

현대오토에버 MLOps Training
"""

from kfp import dsl
from kfp.dsl import component


@component(
    base_image="python:3.9-slim",
    packages_to_install=["kubernetes==28.1.0", "mlflow==2.9.2"]
)
def deploy_model(
    run_id: str,
    model_name: str,
    namespace: str,
    mlflow_tracking_uri: str
):
    """
    KServe InferenceService로 모델 배포
    
    Args:
        run_id: MLflow Run ID
        model_name: 모델/InferenceService 이름
        namespace: Kubernetes 네임스페이스
        mlflow_tracking_uri: MLflow 서버 URI
    """
    from kubernetes import client, config
    from kubernetes.client.rest import ApiException
    import time
    import os
    
    print("=" * 60)
    print("  Component: Deploy Model (KServe)")
    print("=" * 60)
    
    print(f"\n  Configuration:")
    print(f"     - Model Name: {model_name}")
    print(f"     - Namespace: {namespace}")
    print(f"     - Run ID: {run_id}")
    print(f"     - MLflow URI: {mlflow_tracking_uri}")
    
    # Kubernetes 클라이언트 설정
    try:
        config.load_incluster_config()
        print(f"\n  ✅ Using in-cluster config")
    except:
        config.load_kube_config()
        print(f"\n  ✅ Using kubeconfig")
    
    api = client.CustomObjectsApi()
    
    # InferenceService 정의
    model_uri = f"mlflow-artifacts:/{run_id}/model"
    
    isvc = {
        "apiVersion": "serving.kserve.io/v1beta1",
        "kind": "InferenceService",
        "metadata": {
            "name": model_name,
            "namespace": namespace,
            "annotations": {
                "sidecar.istio.io/inject": "false"
            }
        },
        "spec": {
            "predictor": {
                "sklearn": {
                    "storageUri": model_uri,
                    "resources": {
                        "requests": {
                            "cpu": "100m",
                            "memory": "256Mi"
                        },
                        "limits": {
                            "cpu": "500m",
                            "memory": "512Mi"
                        }
                    }
                }
            }
        }
    }
    
    # 기존 InferenceService 삭제 (있으면)
    print(f"\n  🗑️ Checking existing InferenceService...")
    try:
        api.delete_namespaced_custom_object(
            group="serving.kserve.io",
            version="v1beta1",
            namespace=namespace,
            plural="inferenceservices",
            name=model_name
        )
        print(f"  ✅ Deleted existing InferenceService: {model_name}")
        time.sleep(5)
    except ApiException as e:
        if e.status == 404:
            print(f"  ✅ No existing InferenceService found")
        else:
            raise
    
    # 새로 생성
    print(f"\n  🚀 Creating InferenceService...")
    try:
        result = api.create_namespaced_custom_object(
            group="serving.kserve.io",
            version="v1beta1",
            namespace=namespace,
            plural="inferenceservices",
            body=isvc
        )
        print(f"  ✅ InferenceService created: {model_name}")
        
    except ApiException as e:
        print(f"  ❌ Failed to create InferenceService: {e.reason}")
        raise
    
    # 상태 확인
    print(f"\n  ⏳ Waiting for deployment (max 60s)...")
    for i in range(6):
        time.sleep(10)
        try:
            isvc_status = api.get_namespaced_custom_object(
                group="serving.kserve.io",
                version="v1beta1",
                namespace=namespace,
                plural="inferenceservices",
                name=model_name
            )
            
            conditions = isvc_status.get("status", {}).get("conditions", [])
            ready_condition = next(
                (c for c in conditions if c.get("type") == "Ready"),
                None
            )
            
            if ready_condition and ready_condition.get("status") == "True":
                print(f"  ✅ InferenceService READY!")
                break
            else:
                status = ready_condition.get("status", "Unknown") if ready_condition else "Unknown"
                message = ready_condition.get("message", "") if ready_condition else ""
                print(f"  ⏳ Status: {status} ({(i+1)*10}s)")
                if message:
                    print(f"      Message: {message[:50]}...")
                
        except Exception as e:
            print(f"  ⚠️ Status check failed: {e}")
    
    # 엔드포인트 정보
    internal_url = f"http://{model_name}.{namespace}.svc.cluster.local/v1/models/{model_name}:predict"
    
    print(f"\n  📡 Deployment Information:")
    print(f"     - Internal URL: {internal_url}")
    print(f"\n  🧪 Test Command:")
    print(f"""     curl -X POST {internal_url} \\
       -H 'Content-Type: application/json' \\
       -d '{{"instances": [[0.5, 0.2, -0.1, -0.15, 0.3, 0.1, 0.8, -0.5]]}}'""")
    
    print(f"\n  ✅ Deployment completed!")


# 로컬 테스트용
if __name__ == "__main__":
    print("This component requires Kubernetes cluster to run.")
    print("Please use within Kubeflow Pipeline.")
