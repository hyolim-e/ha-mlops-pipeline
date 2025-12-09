"""
Lab 3-2: Deployment Test Script
================================

배포된 KServe InferenceService를 테스트합니다.

사용법:
    python scripts/3_test_deployment.py
    python scripts/3_test_deployment.py --model-name my-model --namespace kubeflow-user01

현대오토에버 MLOps Training
"""

import argparse
import json
import requests
import subprocess
import sys
import os


def get_args():
    """커맨드라인 인자 파싱"""
    parser = argparse.ArgumentParser(description="Test KServe deployment")
    parser.add_argument(
        "--model-name",
        default=os.environ.get("MODEL_NAME", "california-model"),
        help="Model name (default: california-model)"
    )
    parser.add_argument(
        "--namespace",
        default=os.environ.get("NAMESPACE", "kubeflow-user01"),
        help="Kubernetes namespace (default: kubeflow-user01)"
    )
    parser.add_argument(
        "--local-port",
        type=int,
        default=8080,
        help="Local port for port-forward (default: 8080)"
    )
    return parser.parse_args()


def check_inferenceservice(model_name: str, namespace: str) -> bool:
    """InferenceService 상태 확인"""
    print("=" * 60)
    print("  Checking InferenceService Status")
    print("=" * 60)
    
    cmd = [
        "kubectl", "get", "inferenceservice",
        model_name, "-n", namespace,
        "-o", "jsonpath={.status.conditions[?(@.type=='Ready')].status}"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        status = result.stdout.strip()
        
        print(f"\n  Model: {model_name}")
        print(f"  Namespace: {namespace}")
        print(f"  Ready: {status}")
        
        if status == "True":
            print("\n  ✅ InferenceService is READY")
            return True
        else:
            print("\n  ⚠️ InferenceService is NOT READY")
            print("\n  Run the following to check status:")
            print(f"    kubectl describe inferenceservice {model_name} -n {namespace}")
            return False
            
    except Exception as e:
        print(f"\n  ❌ Error checking status: {e}")
        return False


def get_service_url(model_name: str, namespace: str) -> str:
    """서비스 URL 가져오기"""
    cmd = [
        "kubectl", "get", "inferenceservice",
        model_name, "-n", namespace,
        "-o", "jsonpath={.status.url}"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip()
    except:
        return None


def test_prediction_internal(model_name: str, namespace: str) -> bool:
    """내부 클러스터에서 예측 테스트 (kubectl run 사용)"""
    print("\n" + "=" * 60)
    print("  Testing Prediction (Internal)")
    print("=" * 60)
    
    # California Housing 샘플 데이터 (정규화된 값)
    # MedInc, HouseAge, AveRooms, AveBedrms, Population, AveOccup, Latitude, Longitude
    sample_data = {
        "instances": [
            [0.5, 0.2, -0.1, -0.15, 0.3, 0.1, 0.8, -0.5],  # Sample 1
            [-0.3, 0.5, 0.2, 0.1, -0.2, -0.1, -0.3, 0.2]   # Sample 2
        ]
    }
    
    url = f"http://{model_name}.{namespace}.svc.cluster.local/v1/models/{model_name}:predict"
    
    print(f"\n  URL: {url}")
    print(f"\n  Request data:")
    print(f"    {json.dumps(sample_data, indent=4)}")
    
    # kubectl run을 사용하여 클러스터 내부에서 테스트
    curl_cmd = f"curl -s -X POST {url} -H 'Content-Type: application/json' -d '{json.dumps(sample_data)}'"
    
    cmd = [
        "kubectl", "run", "curl-test", "--rm", "-i", "--restart=Never",
        f"--namespace={namespace}",
        "--image=curlimages/curl:latest",
        "--", "sh", "-c", curl_cmd
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            response = result.stdout
            print(f"\n  Response:")
            print(f"    {response}")
            print("\n  ✅ Prediction test PASSED")
            return True
        else:
            print(f"\n  ❌ Prediction test FAILED")
            print(f"    Error: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n  ⚠️ Test timed out")
        # Clean up
        subprocess.run(["kubectl", "delete", "pod", "curl-test", f"-n={namespace}", "--ignore-not-found"], 
                      capture_output=True)
        return False
    except Exception as e:
        print(f"\n  ❌ Error: {e}")
        return False


def test_prediction_portforward(model_name: str, namespace: str, local_port: int) -> bool:
    """Port-forward를 통한 예측 테스트"""
    print("\n" + "=" * 60)
    print("  Testing Prediction (Port-Forward)")
    print("=" * 60)
    
    print(f"\n  To test manually:")
    print(f"\n  1. Start port-forward:")
    print(f"     kubectl port-forward svc/{model_name}-predictor -n {namespace} {local_port}:80")
    print(f"\n  2. Send prediction request:")
    print(f"""     curl -X POST http://localhost:{local_port}/v1/models/{model_name}:predict \\
       -H 'Content-Type: application/json' \\
       -d '{{
         "instances": [
           [0.5, 0.2, -0.1, -0.15, 0.3, 0.1, 0.8, -0.5]
         ]
       }}'""")
    
    return True


def test_with_python_client(model_name: str, namespace: str) -> bool:
    """Python requests를 사용한 테스트 (로컬에서 직접 실행 시)"""
    print("\n" + "=" * 60)
    print("  Python Client Test Example")
    print("=" * 60)
    
    code_example = f'''
# Python 코드 예제
import requests
import json

# 클러스터 내부에서 실행하거나 port-forward 사용
url = "http://{model_name}.{namespace}.svc.cluster.local/v1/models/{model_name}:predict"
# 또는 port-forward 사용 시:
# url = "http://localhost:8080/v1/models/{model_name}:predict"

# California Housing 샘플 데이터
data = {{
    "instances": [
        [0.5, 0.2, -0.1, -0.15, 0.3, 0.1, 0.8, -0.5],
        [-0.3, 0.5, 0.2, 0.1, -0.2, -0.1, -0.3, 0.2]
    ]
}}

response = requests.post(url, json=data)
print(f"Status: {{response.status_code}}")
print(f"Predictions: {{response.json()}}")
'''
    
    print(code_example)
    return True


def main():
    """메인 함수"""
    args = get_args()
    
    print("\n" + "=" * 60)
    print("  KServe Deployment Test")
    print("=" * 60)
    print(f"\n  Model: {args.model_name}")
    print(f"  Namespace: {args.namespace}")
    
    # 1. InferenceService 상태 확인
    is_ready = check_inferenceservice(args.model_name, args.namespace)
    
    if not is_ready:
        print("\n⚠️ InferenceService is not ready. Please wait or check the status.")
        print("\n  Useful commands:")
        print(f"    kubectl get inferenceservice -n {args.namespace}")
        print(f"    kubectl describe inferenceservice {args.model_name} -n {args.namespace}")
        print(f"    kubectl logs -l serving.kserve.io/inferenceservice={args.model_name} -n {args.namespace}")
        sys.exit(1)
    
    # 2. 서비스 URL 확인
    service_url = get_service_url(args.model_name, args.namespace)
    if service_url:
        print(f"\n  Service URL: {service_url}")
    
    # 3. 내부 테스트 시도
    test_prediction_internal(args.model_name, args.namespace)
    
    # 4. Port-forward 안내
    test_prediction_portforward(args.model_name, args.namespace, args.local_port)
    
    # 5. Python 클라이언트 예제
    test_with_python_client(args.model_name, args.namespace)
    
    print("\n" + "=" * 60)
    print("  Test Complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
