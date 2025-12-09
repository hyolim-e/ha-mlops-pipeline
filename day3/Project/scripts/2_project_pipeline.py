"""
Lab 3-2: Project Pipeline (Part 2)
===================================

조별 프로젝트용 파이프라인 예제
팀에서 이 파일을 수정하여 자신만의 파이프라인을 구축하세요.

실행:
    python scripts/2_project_pipeline.py

현대오토에버 MLOps Training
"""

import os
from kfp import dsl
from kfp.dsl import component, Input, Output, Dataset, Model
from kfp import compiler


# ============================================================
# 환경 변수 설정 (팀 설정으로 변경하세요!)
# ============================================================
TEAM_NAME = os.environ.get("TEAM_NAME", "team-01")
USER_NAMESPACE = os.environ.get("NAMESPACE", "kubeflow-user01")
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
    dataset_name: str,
    output_data: Output[Dataset]
):
    """California Housing 데이터셋 로드"""
    from sklearn.datasets import fetch_california_housing
    import pandas as pd
    
    print("=" * 60)
    print(f"  {dataset_name.upper()} Dataset Loading")
    print("=" * 60)
    
    housing = fetch_california_housing(as_frame=True)
    df = housing.frame
    
    print(f"\n  Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
    print(f"\n  Statistics:")
    print(df.describe())
    
    df.to_csv(output_data.path, index=False)
    print(f"\n  ✅ Saved to: {output_data.path}")


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
):
    """데이터 전처리: 분할 및 정규화"""
    import pandas as pd
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    
    print("=" * 60)
    print("  Preprocessing")
    print("=" * 60)
    
    df = pd.read_csv(input_data.path)
    
    X = df.drop(columns=['MedHouseVal'])
    y = df['MedHouseVal']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train),
        columns=X_train.columns
    )
    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test),
        columns=X_test.columns
    )
    
    X_train_scaled.to_csv(X_train_out.path, index=False)
    X_test_scaled.to_csv(X_test_out.path, index=False)
    y_train.to_csv(y_train_out.path, index=False)
    y_test.to_csv(y_test_out.path, index=False)
    
    print(f"\n  Train: {len(X_train)}, Test: {len(X_test)}")
    print(f"  ✅ Preprocessing completed")


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
) -> int:
    """
    피처 엔지니어링
    
    TODO: 팀에서 추가 피처를 구현하세요!
    
    아이디어:
    - bedroom_ratio: 방 대비 침실 비율
    - people_per_household: 가구당 인구
    - dist_to_bay: Bay Area까지 거리
    - income_category: 소득 구간
    """
    import pandas as pd
    import numpy as np
    
    print("=" * 60)
    print("  Feature Engineering")
    print("=" * 60)
    
    X_train = pd.read_csv(X_train_in.path)
    X_test = pd.read_csv(X_test_in.path)
    
    original_cols = list(X_train.columns)
    
    def add_features(df):
        """파생 변수 추가"""
        df = df.copy()
        
        # 1. 방 대비 침실 비율
        df['bedroom_ratio'] = df['AveBedrms'] / (df['AveRooms'] + 1e-6)
        
        # 2. 가구당 인구
        df['people_per_household'] = df['Population'] / (df['AveOccup'] + 1e-6)
        
        # 3. Bay Area까지 거리 (정규화된 데이터에서 상대적 거리)
        # 실제 Bay Area 좌표: (37.77, -122.42)
        # 정규화 후에는 상대적 위치만 의미 있음
        df['location_score'] = np.sqrt(
            df['Latitude']**2 + df['Longitude']**2
        )
        
        # 4. 밀집도 지표
        df['density'] = df['Population'] * df['AveOccup']
        
        return df
    
    X_train_fe = add_features(X_train)
    X_test_fe = add_features(X_test)
    
    new_cols = [c for c in X_train_fe.columns if c not in original_cols]
    print(f"\n  Original features: {len(original_cols)}")
    print(f"  New features: {new_cols}")
    print(f"  Total features: {len(X_train_fe.columns)}")
    
    X_train_fe.to_csv(X_train_out.path, index=False)
    X_test_fe.to_csv(X_test_out.path, index=False)
    
    print(f"\n  ✅ Feature engineering completed")
    
    return len(new_cols)


# ============================================================
# Component 4: 모델 학습
# ============================================================
@component(
    base_image="python:3.9-slim",
    packages_to_install=[
        "pandas==2.0.3",
        "scikit-learn==1.3.2",
        "mlflow==2.9.2",
        "numpy==1.24.3"
    ]
)
def train_model(
    X_train: Input[Dataset],
    X_test: Input[Dataset],
    y_train: Input[Dataset],
    y_test: Input[Dataset],
    mlflow_tracking_uri: str,
    experiment_name: str,
    team_name: str,
    n_estimators: int = 100,
    max_depth: int = 10
) -> str:
    """모델 학습 및 MLflow 기록"""
    import pandas as pd
    import numpy as np
    import mlflow
    import mlflow.sklearn
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
    import os
    
    print("=" * 60)
    print(f"  Model Training - {team_name}")
    print("=" * 60)
    
    X_train_df = pd.read_csv(X_train.path)
    X_test_df = pd.read_csv(X_test.path)
    y_train_df = pd.read_csv(y_train.path)
    y_test_df = pd.read_csv(y_test.path)
    
    os.environ['MLFLOW_TRACKING_URI'] = mlflow_tracking_uri
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(experiment_name)
    
    with mlflow.start_run(run_name=f"{team_name}-run") as run:
        run_id = run.info.run_id
        
        params = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "random_state": 42
        }
        mlflow.log_params(params)
        mlflow.set_tag("team", team_name)
        
        model = RandomForestRegressor(**params)
        model.fit(X_train_df, y_train_df.values.ravel())
        
        y_pred = model.predict(X_test_df)
        
        r2 = r2_score(y_test_df, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test_df, y_pred))
        mae = mean_absolute_error(y_test_df, y_pred)
        
        mlflow.log_metrics({"r2": r2, "rmse": rmse, "mae": mae})
        
        print(f"\n  R2: {r2:.4f}")
        print(f"  RMSE: {rmse:.4f}")
        print(f"  MAE: {mae:.4f}")
        
        mlflow.sklearn.log_model(
            model,
            "model",
            registered_model_name=f"{team_name}-california-model"
        )
        
        print(f"\n  ✅ Model trained! Run ID: {run_id}")
    
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
    """모델 평가 및 배포 결정"""
    import mlflow
    import os
    
    print("=" * 60)
    print("  Model Evaluation")
    print("=" * 60)
    
    os.environ['MLFLOW_TRACKING_URI'] = mlflow_tracking_uri
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    
    client = mlflow.tracking.MlflowClient()
    run = client.get_run(run_id)
    
    r2 = float(run.data.metrics.get("r2", 0))
    
    print(f"\n  Run ID: {run_id}")
    print(f"  R2 Score: {r2:.4f}")
    print(f"  Threshold: {r2_threshold}")
    
    if r2 >= r2_threshold:
        decision = "deploy"
        print(f"\n  ✅ Decision: DEPLOY")
    else:
        decision = "skip"
        print(f"\n  ⚠️ Decision: SKIP")
    
    return decision


# ============================================================
# Component 6: 모델 배포
# ============================================================
@component(
    base_image="python:3.9-slim",
    packages_to_install=["kubernetes==28.1.0"]
)
def deploy_model(
    run_id: str,
    model_name: str,
    namespace: str
):
    """KServe 배포"""
    from kubernetes import client, config
    from kubernetes.client.rest import ApiException
    import time
    
    print("=" * 60)
    print("  Model Deployment (KServe)")
    print("=" * 60)
    
    print(f"\n  Model: {model_name}")
    print(f"  Namespace: {namespace}")
    
    try:
        config.load_incluster_config()
    except:
        config.load_kube_config()
    
    api = client.CustomObjectsApi()
    
    isvc = {
        "apiVersion": "serving.kserve.io/v1beta1",
        "kind": "InferenceService",
        "metadata": {
            "name": model_name,
            "namespace": namespace
        },
        "spec": {
            "predictor": {
                "sklearn": {
                    "storageUri": f"mlflow-artifacts:/{run_id}/model",
                    "resources": {
                        "requests": {"cpu": "100m", "memory": "256Mi"},
                        "limits": {"cpu": "500m", "memory": "512Mi"}
                    }
                }
            }
        }
    }
    
    try:
        api.delete_namespaced_custom_object(
            group="serving.kserve.io",
            version="v1beta1",
            namespace=namespace,
            plural="inferenceservices",
            name=model_name
        )
        time.sleep(5)
    except ApiException:
        pass
    
    api.create_namespaced_custom_object(
        group="serving.kserve.io",
        version="v1beta1",
        namespace=namespace,
        plural="inferenceservices",
        body=isvc
    )
    
    print(f"\n  ✅ InferenceService created: {model_name}")
    print(f"\n  Endpoint:")
    print(f"    http://{model_name}.{namespace}.svc.cluster.local/v1/models/{model_name}:predict")


# ============================================================
# Component 7: 알림
# ============================================================
@component(base_image="python:3.9-slim")
def send_alert(run_id: str, team_name: str):
    """성능 미달 알림"""
    print("=" * 60)
    print(f"  Alert - {team_name}")
    print("=" * 60)
    
    print(f"\n  ⚠️ Model did not meet performance threshold")
    print(f"  Run ID: {run_id}")
    print(f"\n  Recommendations:")
    print(f"    1. Add more features")
    print(f"    2. Tune hyperparameters")
    print(f"    3. Try different algorithms")


# ============================================================
# 파이프라인 정의
# ============================================================
@dsl.pipeline(
    name="Project Pipeline",
    description="Team Project: E2E ML Pipeline"
)
def project_pipeline(
    dataset_name: str = "california",
    team_name: str = "team-01",
    experiment_name: str = "team-01-experiment",
    model_name: str = "team-01-model",
    namespace: str = "kubeflow-user01",
    mlflow_tracking_uri: str = "http://mlflow-server-service.mlflow-system.svc.cluster.local:5000",
    n_estimators: int = 100,
    max_depth: int = 10,
    r2_threshold: float = 0.75
):
    """프로젝트 파이프라인"""
    
    # Step 1: 데이터 로드
    load_task = load_data(dataset_name=dataset_name)
    
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
        team_name=team_name,
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
            namespace=namespace
        )
    
    with dsl.If(evaluate_task.output == "skip"):
        send_alert(run_id=train_task.output, team_name=team_name)


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print(f"  Project Pipeline - {TEAM_NAME}")
    print("=" * 60)
    
    pipeline_file = f"{TEAM_NAME}_pipeline.yaml"
    
    compiler.Compiler().compile(
        pipeline_func=project_pipeline,
        package_path=pipeline_file
    )
    
    print(f"\n✅ Pipeline compiled: {pipeline_file}")
    print(f"\nParameters:")
    print(f"  - team_name: {TEAM_NAME}")
    print(f"  - experiment_name: {TEAM_NAME}-experiment")
    print(f"  - model_name: {TEAM_NAME}-model")
    print(f"  - namespace: {USER_NAMESPACE}")
    print("=" * 60)
