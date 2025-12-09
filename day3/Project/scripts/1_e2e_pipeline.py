"""
Lab 3-2: End-to-End ML Pipeline (Part 1)
=========================================

데이터 로드 → 전처리 → 피처 엔지니어링 → 학습 → 평가 → 배포
완전 자동화된 MLOps 파이프라인

실행:
    python scripts/1_e2e_pipeline.py

현대오토에버 MLOps Training
"""

import os
from kfp import dsl
from kfp.dsl import component, Input, Output, Dataset, Model, Metrics
from kfp import compiler


# ============================================================
# 환경 변수 설정
# ============================================================
USER_NUM = os.environ.get("USER_NUM", "01")
USER_NAMESPACE = os.environ.get("NAMESPACE", f"kubeflow-user{USER_NUM}")
MLFLOW_TRACKING_URI = os.environ.get(
    "MLFLOW_TRACKING_URI",
    "http://mlflow-server-service.mlflow-system.svc.cluster.local:5000"
)


# ============================================================
# Component 1: 데이터 로드
# ============================================================
@component(
    base_image="python:3.9-slim",
    packages_to_install=["pandas==2.0.3", "scikit-learn==1.3.2"]
)
def load_data(
    data_source: str,
    output_data: Output[Dataset]
):
    """
    California Housing 데이터셋 로드
    
    Args:
        data_source: 데이터 소스 ("sklearn" 또는 S3 경로)
        output_data: 출력 데이터셋
    """
    import pandas as pd
    from sklearn.datasets import fetch_california_housing
    
    print("=" * 60)
    print("  Step 1: Load Data")
    print("=" * 60)
    
    if data_source == "sklearn":
        print("\n  Loading from sklearn...")
        housing = fetch_california_housing(as_frame=True)
        df = housing.frame
    else:
        print(f"\n  Loading from: {data_source}")
        df = pd.read_csv(data_source)
    
    print(f"\n  Data shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
    print(f"\n  First 5 rows:")
    print(df.head())
    
    df.to_csv(output_data.path, index=False)
    print(f"\n  ✅ Data saved to: {output_data.path}")


# ============================================================
# Component 2: 전처리
# ============================================================
@component(
    base_image="python:3.9-slim",
    packages_to_install=["pandas==2.0.3", "scikit-learn==1.3.2", "numpy==1.24.3"]
)
def preprocess(
    input_data: Input[Dataset],
    X_train_out: Output[Dataset],
    X_test_out: Output[Dataset],
    y_train_out: Output[Dataset],
    y_test_out: Output[Dataset],
    test_size: float = 0.2
) -> dict:
    """
    데이터 전처리: Train/Test 분할 및 정규화
    
    Args:
        input_data: 입력 데이터셋
        test_size: 테스트 세트 비율
    
    Returns:
        전처리 메타데이터
    """
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    
    print("=" * 60)
    print("  Step 2: Preprocess")
    print("=" * 60)
    
    df = pd.read_csv(input_data.path)
    print(f"\n  Loaded {len(df)} rows")
    
    # 피처와 타겟 분리
    target_col = "MedHouseVal"
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    print(f"  Features: {list(X.columns)}")
    print(f"  Target: {target_col}")
    
    # Train/Test 분할
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    
    print(f"\n  Train size: {len(X_train)}")
    print(f"  Test size: {len(X_test)}")
    
    # 정규화
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train),
        columns=X_train.columns
    )
    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test),
        columns=X_test.columns
    )
    
    # 저장
    X_train_scaled.to_csv(X_train_out.path, index=False)
    X_test_scaled.to_csv(X_test_out.path, index=False)
    y_train.to_csv(y_train_out.path, index=False)
    y_test.to_csv(y_test_out.path, index=False)
    
    print(f"\n  ✅ Preprocessing completed")
    
    return {
        "n_train": len(X_train),
        "n_test": len(X_test),
        "n_features": X_train.shape[1]
    }


# ============================================================
# Component 3: 피처 엔지니어링
# ============================================================
@component(
    base_image="python:3.9-slim",
    packages_to_install=["pandas==2.0.3", "numpy==1.24.3"]
)
def feature_engineering(
    X_train_in: Input[Dataset],
    X_test_in: Input[Dataset],
    X_train_out: Output[Dataset],
    X_test_out: Output[Dataset]
) -> dict:
    """
    피처 엔지니어링: 파생 변수 생성
    
    생성되는 피처:
    - rooms_per_household: 가구당 방 수
    - bedrooms_ratio: 방 대비 침실 비율
    - population_per_household: 가구당 인구
    """
    import pandas as pd
    import numpy as np
    
    print("=" * 60)
    print("  Step 3: Feature Engineering")
    print("=" * 60)
    
    X_train = pd.read_csv(X_train_in.path)
    X_test = pd.read_csv(X_test_in.path)
    
    original_features = list(X_train.columns)
    print(f"\n  Original features: {original_features}")
    
    def add_features(df):
        """파생 변수 추가"""
        df = df.copy()
        
        # 1. 가구당 방 수 (이미 스케일링됨 - 역스케일링 없이 비율 계산)
        if 'AveRooms' in df.columns and 'AveOccup' in df.columns:
            df['rooms_per_household'] = df['AveRooms'] / (df['AveOccup'] + 1e-6)
        
        # 2. 방 대비 침실 비율
        if 'AveBedrms' in df.columns and 'AveRooms' in df.columns:
            df['bedrooms_ratio'] = df['AveBedrms'] / (df['AveRooms'] + 1e-6)
        
        # 3. 가구당 인구
        if 'Population' in df.columns and 'AveOccup' in df.columns:
            df['population_per_household'] = df['Population'] / (df['AveOccup'] + 1e-6)
        
        return df
    
    X_train_fe = add_features(X_train)
    X_test_fe = add_features(X_test)
    
    new_features = [f for f in X_train_fe.columns if f not in original_features]
    print(f"  New features: {new_features}")
    print(f"  Total features: {len(X_train_fe.columns)}")
    
    X_train_fe.to_csv(X_train_out.path, index=False)
    X_test_fe.to_csv(X_test_out.path, index=False)
    
    print(f"\n  ✅ Feature engineering completed")
    
    return {
        "original_features": len(original_features),
        "new_features": len(new_features),
        "total_features": len(X_train_fe.columns)
    }


# ============================================================
# Component 4: 모델 학습
# ============================================================
@component(
    base_image="python:3.9-slim",
    packages_to_install=[
        "pandas==2.0.3", 
        "scikit-learn==1.3.2", 
        "mlflow==2.9.2",
        "boto3==1.34.0"
    ]
)
def train_model(
    X_train: Input[Dataset],
    X_test: Input[Dataset],
    y_train: Input[Dataset],
    y_test: Input[Dataset],
    mlflow_tracking_uri: str,
    experiment_name: str,
    n_estimators: int = 100,
    max_depth: int = 10
) -> str:
    """
    모델 학습 및 MLflow 기록
    
    Args:
        mlflow_tracking_uri: MLflow 서버 URI
        experiment_name: 실험 이름
        n_estimators: 트리 개수
        max_depth: 최대 깊이
    
    Returns:
        MLflow Run ID
    """
    import pandas as pd
    import numpy as np
    import mlflow
    import mlflow.sklearn
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
    import os
    
    print("=" * 60)
    print("  Step 4: Train Model")
    print("=" * 60)
    
    # 데이터 로드
    X_train_df = pd.read_csv(X_train.path)
    X_test_df = pd.read_csv(X_test.path)
    y_train_df = pd.read_csv(y_train.path)
    y_test_df = pd.read_csv(y_test.path)
    
    print(f"\n  Training data: {X_train_df.shape}")
    print(f"  Test data: {X_test_df.shape}")
    
    # MLflow 설정
    os.environ['MLFLOW_TRACKING_URI'] = mlflow_tracking_uri
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(experiment_name)
    
    print(f"\n  MLflow Tracking URI: {mlflow_tracking_uri}")
    print(f"  Experiment: {experiment_name}")
    
    # 학습
    with mlflow.start_run() as run:
        run_id = run.info.run_id
        print(f"\n  Run ID: {run_id}")
        
        # 파라미터 로깅
        params = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "random_state": 42,
            "n_jobs": -1
        }
        mlflow.log_params(params)
        
        # 모델 학습
        print("\n  Training RandomForest model...")
        model = RandomForestRegressor(**params)
        model.fit(X_train_df, y_train_df.values.ravel())
        
        # 예측 및 평가
        y_pred = model.predict(X_test_df)
        
        mse = mean_squared_error(y_test_df, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test_df, y_pred)
        r2 = r2_score(y_test_df, y_pred)
        
        # 메트릭 로깅
        metrics = {
            "mse": mse,
            "rmse": rmse,
            "mae": mae,
            "r2": r2
        }
        mlflow.log_metrics(metrics)
        
        print(f"\n  Model Performance:")
        print(f"    - R2 Score: {r2:.4f}")
        print(f"    - RMSE: {rmse:.4f}")
        print(f"    - MAE: {mae:.4f}")
        
        # 피처 중요도 로깅
        feature_importance = dict(zip(
            X_train_df.columns,
            model.feature_importances_
        ))
        mlflow.log_dict(feature_importance, "feature_importance.json")
        
        # 모델 저장
        mlflow.sklearn.log_model(
            model,
            "model",
            registered_model_name=f"{experiment_name}-model"
        )
        
        # 태그 추가
        mlflow.set_tags({
            "pipeline": "e2e",
            "stage": "training",
            "n_features": X_train_df.shape[1]
        })
    
    print(f"\n  ✅ Training completed! Run ID: {run_id}")
    
    return run_id


# ============================================================
# Component 5: 모델 평가
# ============================================================
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
        r2_threshold: R2 임계값
    
    Returns:
        "deploy" 또는 "skip"
    """
    import mlflow
    import os
    
    print("=" * 60)
    print("  Step 5: Evaluate Model")
    print("=" * 60)
    
    os.environ['MLFLOW_TRACKING_URI'] = mlflow_tracking_uri
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    
    client = mlflow.tracking.MlflowClient()
    run = client.get_run(run_id)
    
    # 메트릭 가져오기
    r2 = float(run.data.metrics.get("r2", 0))
    rmse = float(run.data.metrics.get("rmse", 0))
    mae = float(run.data.metrics.get("mae", 0))
    
    print(f"\n  Run ID: {run_id}")
    print(f"\n  Model Metrics:")
    print(f"    - R2 Score: {r2:.4f}")
    print(f"    - RMSE: {rmse:.4f}")
    print(f"    - MAE: {mae:.4f}")
    print(f"\n  Deployment Threshold:")
    print(f"    - R2 >= {r2_threshold}")
    
    # 배포 결정
    if r2 >= r2_threshold:
        decision = "deploy"
        print(f"\n  ✅ Decision: DEPLOY")
        print(f"     R2 ({r2:.4f}) >= Threshold ({r2_threshold})")
    else:
        decision = "skip"
        print(f"\n  ⚠️ Decision: SKIP")
        print(f"     R2 ({r2:.4f}) < Threshold ({r2_threshold})")
    
    # MLflow에 결정 기록
    with mlflow.start_run(run_id=run_id):
        mlflow.set_tag("deployment_decision", decision)
        mlflow.log_metric("r2_threshold", r2_threshold)
    
    return decision


# ============================================================
# Component 6: 모델 배포 (KServe)
# ============================================================
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
        model_name: 모델 이름
        namespace: Kubernetes 네임스페이스
        mlflow_tracking_uri: MLflow 서버 URI
    """
    from kubernetes import client, config
    from kubernetes.client.rest import ApiException
    import time
    
    print("=" * 60)
    print("  Step 6: Deploy Model (KServe)")
    print("=" * 60)
    
    print(f"\n  Model Name: {model_name}")
    print(f"  Namespace: {namespace}")
    print(f"  Run ID: {run_id}")
    
    try:
        config.load_incluster_config()
        print("\n  Using in-cluster config")
    except:
        config.load_kube_config()
        print("\n  Using kubeconfig")
    
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
    try:
        api.delete_namespaced_custom_object(
            group="serving.kserve.io",
            version="v1beta1",
            namespace=namespace,
            plural="inferenceservices",
            name=model_name
        )
        print(f"\n  Deleted existing InferenceService: {model_name}")
        time.sleep(5)
    except ApiException as e:
        if e.status != 404:
            raise
    
    # 새 InferenceService 생성
    print(f"\n  Creating InferenceService...")
    try:
        api.create_namespaced_custom_object(
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
    print(f"\n  Waiting for deployment (max 60s)...")
    for i in range(6):
        time.sleep(10)
        try:
            status = api.get_namespaced_custom_object(
                group="serving.kserve.io",
                version="v1beta1",
                namespace=namespace,
                plural="inferenceservices",
                name=model_name
            )
            conditions = status.get("status", {}).get("conditions", [])
            ready = next(
                (c for c in conditions if c.get("type") == "Ready"),
                None
            )
            if ready and ready.get("status") == "True":
                print(f"  ✅ InferenceService READY!")
                break
            print(f"  ⏳ Status: {ready.get('status') if ready else 'Unknown'} ({(i+1)*10}s)")
        except Exception as e:
            print(f"  ⚠️ Status check failed: {e}")
    
    print(f"\n  Endpoint:")
    print(f"    http://{model_name}.{namespace}.svc.cluster.local/v1/models/{model_name}:predict")
    print(f"\n  ✅ Deployment completed!")


# ============================================================
# Component 7: 알림 (성능 미달 시)
# ============================================================
@component(base_image="python:3.9-slim")
def send_alert(
    run_id: str,
    message: str = "Model did not meet performance threshold"
):
    """
    성능 미달 알림 전송
    
    Args:
        run_id: MLflow Run ID
        message: 알림 메시지
    """
    print("=" * 60)
    print("  Step 6 (Alt): Send Alert")
    print("=" * 60)
    
    print(f"\n  ⚠️ ALERT: {message}")
    print(f"  Run ID: {run_id}")
    print(f"\n  Actions required:")
    print(f"    1. Review model performance in MLflow")
    print(f"    2. Check data quality")
    print(f"    3. Tune hyperparameters")
    print(f"    4. Re-run pipeline")


# ============================================================
# 파이프라인 정의
# ============================================================
@dsl.pipeline(
    name="E2E ML Pipeline",
    description="End-to-End Machine Learning Pipeline with MLflow and KServe"
)
def e2e_ml_pipeline(
    data_source: str = "sklearn",
    experiment_name: str = "e2e-pipeline",
    model_name: str = "california-model",
    namespace: str = "kubeflow-user01",
    mlflow_tracking_uri: str = "http://mlflow-server-service.mlflow-system.svc.cluster.local:5000",
    n_estimators: int = 100,
    max_depth: int = 10,
    r2_threshold: float = 0.75
):
    """
    E2E ML 파이프라인
    
    Args:
        data_source: 데이터 소스 ("sklearn" 또는 S3 경로)
        experiment_name: MLflow 실험 이름
        model_name: 모델/InferenceService 이름
        namespace: Kubernetes 네임스페이스
        mlflow_tracking_uri: MLflow 서버 URI
        n_estimators: RandomForest 트리 개수
        max_depth: RandomForest 최대 깊이
        r2_threshold: 배포 결정 R2 임계값
    """
    # Step 1: 데이터 로드
    load_task = load_data(data_source=data_source)
    
    # Step 2: 전처리
    preprocess_task = preprocess(input_data=load_task.outputs["output_data"])
    
    # Step 3: 피처 엔지니어링
    feature_task = feature_engineering(
        X_train_in=preprocess_task.outputs["X_train_out"],
        X_test_in=preprocess_task.outputs["X_test_out"]
    )
    
    # Step 4: 모델 학습
    train_task = train_model(
        X_train=feature_task.outputs["X_train_out"],
        X_test=feature_task.outputs["X_test_out"],
        y_train=preprocess_task.outputs["y_train_out"],
        y_test=preprocess_task.outputs["y_test_out"],
        mlflow_tracking_uri=mlflow_tracking_uri,
        experiment_name=experiment_name,
        n_estimators=n_estimators,
        max_depth=max_depth
    )
    
    # Step 5: 평가
    evaluate_task = evaluate_model(
        run_id=train_task.output,
        mlflow_tracking_uri=mlflow_tracking_uri,
        r2_threshold=r2_threshold
    )
    
    # Step 6: 조건부 배포
    with dsl.If(evaluate_task.output == "deploy"):
        deploy_model(
            run_id=train_task.output,
            model_name=model_name,
            namespace=namespace,
            mlflow_tracking_uri=mlflow_tracking_uri
        )
    
    with dsl.If(evaluate_task.output == "skip"):
        send_alert(
            run_id=train_task.output,
            message=f"Model R2 score below threshold ({r2_threshold})"
        )


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  E2E ML Pipeline - Compiling")
    print("=" * 60)
    
    pipeline_file = "e2e_pipeline.yaml"
    
    compiler.Compiler().compile(
        pipeline_func=e2e_ml_pipeline,
        package_path=pipeline_file
    )
    
    print(f"\n✅ Pipeline compiled: {pipeline_file}")
    print(f"\nNext steps:")
    print(f"  1. Upload pipeline to Kubeflow UI")
    print(f"  2. Click Create Run")
    print(f"  3. Set parameters:")
    print(f"     - data_source: sklearn")
    print(f"     - experiment_name: e2e-pipeline-{USER_NUM}")
    print(f"     - model_name: california-model-{USER_NUM}")
    print(f"     - namespace: {USER_NAMESPACE}")
    print(f"     - n_estimators: 100")
    print(f"     - max_depth: 10")
    print(f"     - r2_threshold: 0.75")
    print(f"  4. Click Start to execute")
    print("=" * 60)
