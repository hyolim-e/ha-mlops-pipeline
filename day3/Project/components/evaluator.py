"""
Lab 3-2: 모델 평가 컴포넌트
===========================

모델 성능을 평가하고 배포 결정을 내리는 컴포넌트

현대오토에버 MLOps Training
"""

from kfp import dsl
from kfp.dsl import component


@component(
    base_image="python:3.9-slim",
    packages_to_install=["mlflow==2.9.2"]
)
def evaluate_model(
    run_id: str,
    mlflow_tracking_uri: str,
    r2_threshold: float = 0.75
) -> str:
    """
    모델 성능 평가 및 배포 결정
    
    Args:
        run_id: MLflow Run ID
        mlflow_tracking_uri: MLflow 서버 URI
        r2_threshold: R2 임계값 (기본값: 0.75)
    
    Returns:
        "deploy" (배포) 또는 "skip" (건너뛰기)
    """
    import mlflow
    import os
    
    print("=" * 60)
    print("  Component: Evaluate Model")
    print("=" * 60)
    
    os.environ['MLFLOW_TRACKING_URI'] = mlflow_tracking_uri
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    
    # Run 정보 가져오기
    print(f"\n  Run ID: {run_id}")
    
    client = mlflow.tracking.MlflowClient()
    run = client.get_run(run_id)
    
    # 메트릭 가져오기
    r2 = float(run.data.metrics.get("r2", 0))
    rmse = float(run.data.metrics.get("rmse", 0))
    mae = float(run.data.metrics.get("mae", 0))
    mse = float(run.data.metrics.get("mse", 0))
    
    print(f"\n  📊 Model Performance:")
    print(f"     - R2 Score: {r2:.4f}")
    print(f"     - RMSE: {rmse:.4f}")
    print(f"     - MAE: {mae:.4f}")
    print(f"     - MSE: {mse:.4f}")
    
    print(f"\n  🎯 Deployment Criteria:")
    print(f"     - R2 Threshold: {r2_threshold}")
    
    # 배포 결정
    if r2 >= r2_threshold:
        decision = "deploy"
        print(f"\n  ✅ Decision: DEPLOY")
        print(f"     Reason: R2 ({r2:.4f}) >= Threshold ({r2_threshold})")
        print(f"\n  📦 Model will be deployed to production")
    else:
        decision = "skip"
        print(f"\n  ⚠️ Decision: SKIP")
        print(f"     Reason: R2 ({r2:.4f}) < Threshold ({r2_threshold})")
        print(f"\n  🔧 Recommendations:")
        print(f"     1. Add more training data")
        print(f"     2. Try different features")
        print(f"     3. Tune hyperparameters")
        print(f"     4. Try different algorithms")
    
    # 결정을 MLflow에 기록
    with mlflow.start_run(run_id=run_id):
        mlflow.set_tag("deployment_decision", decision)
        mlflow.log_metric("r2_threshold", r2_threshold)
        mlflow.set_tag("evaluation_status", "completed")
    
    return decision


# 로컬 테스트용
if __name__ == "__main__":
    print("This component requires MLflow server to run.")
    print("Please use within Kubeflow Pipeline.")
