"""
Lab 3-2: 프로젝트 솔루션 (예제)
================================

⚠️ 이 파일은 발표 후에 공개됩니다.
팀 프로젝트 완성 예제입니다.

현대오토에버 MLOps Training
"""

import os
from kfp import dsl
from kfp.dsl import component, Input, Output, Dataset, Model
from kfp import compiler


# ============================================================
# 환경 변수 설정
# ============================================================
TEAM_NAME = os.environ.get("TEAM_NAME", "solution-team")
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
    import pandas as pd
    from sklearn.datasets import fetch_california_housing
    
    print("=" * 60)
    print("  Step 1: Load Data")
    print("=" * 60)
    
    housing = fetch_california_housing(as_frame=True)
    df = housing.frame
    
    print(f"\n  Dataset: {dataset_name}")
    print(f"  Shape: {df.shape}")
    print(f"  Columns: {list(df.columns)}")
    print(f"\n  Target statistics:")
    print(f"    Mean: {df['MedHouseVal'].mean():.4f}")
    print(f"    Std: {df['MedHouseVal'].std():.4f}")
    print(f"    Min: {df['MedHouseVal'].min():.4f}")
    print(f"    Max: {df['MedHouseVal'].max():.4f}")
    
    df.to_csv(output_data.path, index=False)
    print(f"\n  ✅ Data saved: {output_data.path}")


# ============================================================
# Component 2: 전처리
# ============================================================
@component(
    base_image="python:3.9-slim",
    packages_to_install=["pandas==2.0.3", "scikit-learn==1.3.2", "numpy==1.24.3", "joblib==1.3.2"]
)
def preprocess(
    input_data: Input[Dataset],
    X_train_out: Output[Dataset],
    X_test_out: Output[Dataset],
    y_train_out: Output[Dataset],
    y_test_out: Output[Dataset],
    scaler_out: Output[Model],
    test_size: float = 0.2
) -> dict:
    """데이터 전처리: 분할 및 정규화"""
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    import joblib
    
    print("=" * 60)
    print("  Step 2: Preprocess")
    print("=" * 60)
    
    df = pd.read_csv(input_data.path)
    print(f"\n  Loaded {len(df)} rows")
    
    # 피처와 타겟 분리
    X = df.drop(columns=['MedHouseVal'])
    y = df['MedHouseVal']
    
    print(f"  Features: {list(X.columns)}")
    
    # Train/Test 분할
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    
    print(f"\n  Train/Test Split:")
    print(f"    Train: {len(X_train)} ({(1-test_size)*100:.0f}%)")
    print(f"    Test: {len(X_test)} ({test_size*100:.0f}%)")
    
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
    joblib.dump(scaler, scaler_out.path)
    
    print(f"\n  ✅ Preprocessing completed")
    
    return {
        "n_train": len(X_train),
        "n_test": len(X_test),
        "n_features": X_train.shape[1]
    }


# ============================================================
# Component 3: 피처 엔지니어링 (완성 버전)
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
    피처 엔지니어링 - 완성 버전
    
    생성되는 피처:
    1. rooms_per_household: 가구당 방 수
    2. bedrooms_ratio: 방 대비 침실 비율
    3. population_per_household: 가구당 인구
    4. location_score: 위치 점수
    5. density: 밀집도 지표
    6. income_rooms_interaction: 소득 × 방 수 상호작용
    """
    import pandas as pd
    import numpy as np
    
    print("=" * 60)
    print("  Step 3: Feature Engineering")
    print("=" * 60)
    
    X_train = pd.read_csv(X_train_in.path)
    X_test = pd.read_csv(X_test_in.path)
    
    original_features = list(X_train.columns)
    print(f"\n  Original features ({len(original_features)}):")
    for feat in original_features:
        print(f"    - {feat}")
    
    def add_features(df):
        """파생 변수 추가"""
        df = df.copy()
        
        # 1. 가구당 방 수
        df['rooms_per_household'] = df['AveRooms'] / (df['AveOccup'] + 1e-6)
        
        # 2. 방 대비 침실 비율
        df['bedrooms_ratio'] = df['AveBedrms'] / (df['AveRooms'] + 1e-6)
        
        # 3. 가구당 인구
        df['population_per_household'] = df['Population'] / (df['AveOccup'] + 1e-6)
        
        # 4. 위치 점수 (정규화된 좌표 기반)
        df['location_score'] = np.sqrt(
            df['Latitude']**2 + df['Longitude']**2
        )
        
        # 5. 밀집도 지표
        df['density'] = df['Population'] * df['AveOccup']
        
        # 6. 소득과 방 수의 상호작용
        df['income_rooms_interaction'] = df['MedInc'] * df['AveRooms']
        
        # 7. 주택 연령 그룹 (범주형 → 수치형)
        df['house_age_group'] = pd.cut(
            df['HouseAge'], 
            bins=[-np.inf, -0.5, 0, 0.5, np.inf], 
            labels=[1, 2, 3, 4]
        ).astype(float)
        
        return df
    
    X_train_fe = add_features(X_train)
    X_test_fe = add_features(X_test)
    
    new_features = [f for f in X_train_fe.columns if f not in original_features]
    
    print(f"\n  New features ({len(new_features)}):")
    for feat in new_features:
        stats = X_train_fe[feat].describe()
        print(f"    - {feat}: mean={stats['mean']:.4f}, std={stats['std']:.4f}")
    
    print(f"\n  Total features: {len(X_train_fe.columns)}")
    
    X_train_fe.to_csv(X_train_out.path, index=False)
    X_test_fe.to_csv(X_test_out.path, index=False)
    
    print(f"\n  ✅ Feature engineering completed")
    
    return {
        "original_features": len(original_features),
        "new_features": len(new_features),
        "total_features": len(X_train_fe.columns),
        "new_feature_names": new_features
    }


# ============================================================
# Component 4: 모델 학습 (완성 버전)
# ============================================================
@component(
    base_image="python:3.9-slim",
    packages_to_install=[
        "pandas==2.0.3",
        "scikit-learn==1.3.2",
        "mlflow==2.9.2",
        "numpy==1.24.3",
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
    team_name: str,
    n_estimators: int = 100,
    max_depth: int = 10
) -> str:
    """모델 학습 및 MLflow 기록"""
    import pandas as pd
    import numpy as np
    import mlflow
    import mlflow.sklearn
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
    import os
    
    print("=" * 60)
    print(f"  Step 4: Model Training - {team_name}")
    print("=" * 60)
    
    # 데이터 로드
    X_train_df = pd.read_csv(X_train.path)
    X_test_df = pd.read_csv(X_test.path)
    y_train_df = pd.read_csv(y_train.path)
    y_test_df = pd.read_csv(y_test.path)
    
    print(f"\n  Data shapes:")
    print(f"    X_train: {X_train_df.shape}")
    print(f"    X_test: {X_test_df.shape}")
    
    # MLflow 설정
    os.environ['MLFLOW_TRACKING_URI'] = mlflow_tracking_uri
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(experiment_name)
    
    print(f"\n  MLflow Configuration:")
    print(f"    URI: {mlflow_tracking_uri}")
    print(f"    Experiment: {experiment_name}")
    
    with mlflow.start_run(run_name=f"{team_name}-run") as run:
        run_id = run.info.run_id
        print(f"\n  Run ID: {run_id}")
        
        # 파라미터 로깅
        params = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "random_state": 42,
            "n_jobs": -1,
            "model_type": "RandomForestRegressor"
        }
        mlflow.log_params(params)
        mlflow.set_tag("team", team_name)
        mlflow.set_tag("pipeline", "e2e-project")
        
        # 모델 학습
        print(f"\n  Training RandomForest...")
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train_df, y_train_df.values.ravel())
        
        # 예측 및 평가
        y_pred = model.predict(X_test_df)
        
        r2 = r2_score(y_test_df, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test_df, y_pred))
        mae = mean_absolute_error(y_test_df, y_pred)
        mse = mean_squared_error(y_test_df, y_pred)
        
        # 메트릭 로깅
        metrics = {"r2": r2, "rmse": rmse, "mae": mae, "mse": mse}
        mlflow.log_metrics(metrics)
        
        print(f"\n  Model Performance:")
        print(f"    R2 Score: {r2:.4f}")
        print(f"    RMSE: {rmse:.4f}")
        print(f"    MAE: {mae:.4f}")
        
        # 피처 중요도 로깅
        feature_importance = dict(zip(
            X_train_df.columns,
            model.feature_importances_
        ))
        mlflow.log_dict(feature_importance, "feature_importance.json")
        
        print(f"\n  Top 5 Important Features:")
        sorted_importance = sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        for i, (feat, imp) in enumerate(sorted_importance, 1):
            print(f"    {i}. {feat}: {imp:.4f}")
        
        # 모델 저장
        mlflow.sklearn.log_model(
            model,
            "model",
            registered_model_name=f"{team_name}-california-model"
        )
        
        print(f"\n  ✅ Model training completed")
    
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
    print("  Step 5: Model Evaluation")
    print("=" * 60)
    
    os.environ['MLFLOW_TRACKING_URI'] = mlflow_tracking_uri
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    
    client = mlflow.tracking.MlflowClient()
    run = client.get_run(run_id)
    
    r2 = float(run.data.metrics.get("r2", 0))
    rmse = float(run.data.metrics.get("rmse", 0))
    mae = float(run.data.metrics.get("mae", 0))
    
    print(f"\n  Run ID: {run_id}")
    print(f"\n  Model Metrics:")
    print(f"    R2 Score: {r2:.4f}")
    print(f"    RMSE: {rmse:.4f}")
    print(f"    MAE: {mae:.4f}")
    print(f"\n  Deployment Threshold: R2 >= {r2_threshold}")
    
    if r2 >= r2_threshold:
        decision = "deploy"
        print(f"\n  ✅ Decision: DEPLOY")
        print(f"     Reason: R2 ({r2:.4f}) >= Threshold ({r2_threshold})")
    else:
        decision = "skip"
        print(f"\n  ⚠️ Decision: SKIP")
        print(f"     Reason: R2 ({r2:.4f}) < Threshold ({r2_threshold})")
    
    with mlflow.start_run(run_id=run_id):
        mlflow.set_tag("deployment_decision", decision)
    
    return decision


# ============================================================
# Component 6: 모델 배포
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
    """KServe InferenceService로 모델 배포"""
    from kubernetes import client, config
    from kubernetes.client.rest import ApiException
    import time
    
    print("=" * 60)
    print("  Step 6: Model Deployment (KServe)")
    print("=" * 60)
    
    print(f"\n  Configuration:")
    print(f"    Model Name: {model_name}")
    print(f"    Namespace: {namespace}")
    print(f"    Run ID: {run_id}")
    
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
            "namespace": namespace,
            "annotations": {
                "sidecar.istio.io/inject": "false"
            }
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
    
    # 기존 삭제
    try:
        api.delete_namespaced_custom_object(
            group="serving.kserve.io",
            version="v1beta1",
            namespace=namespace,
            plural="inferenceservices",
            name=model_name
        )
        print(f"\n  Deleted existing InferenceService")
        time.sleep(5)
    except ApiException as e:
        if e.status != 404:
            raise
    
    # 생성
    api.create_namespaced_custom_object(
        group="serving.kserve.io",
        version="v1beta1",
        namespace=namespace,
        plural="inferenceservices",
        body=isvc
    )
    
    print(f"\n  ✅ InferenceService created: {model_name}")
    
    # 상태 확인
    print(f"\n  Waiting for deployment...")
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
            ready = next((c for c in conditions if c.get("type") == "Ready"), None)
            if ready and ready.get("status") == "True":
                print(f"  ✅ InferenceService READY!")
                break
            print(f"  ⏳ Status: {ready.get('status') if ready else 'Unknown'} ({(i+1)*10}s)")
        except:
            pass
    
    print(f"\n  Endpoint:")
    print(f"    http://{model_name}.{namespace}.svc.cluster.local/v1/models/{model_name}:predict")
    print(f"\n  ✅ Deployment completed!")


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
    print(f"    1. Add more training data")
    print(f"    2. Create additional features")
    print(f"    3. Tune hyperparameters")
    print(f"    4. Try different algorithms")


# ============================================================
# 파이프라인 정의
# ============================================================
@dsl.pipeline(
    name="Project Pipeline (Solution)",
    description="Team Project Solution: Complete E2E ML Pipeline"
)
def project_pipeline(
    dataset_name: str = "california",
    team_name: str = "solution-team",
    experiment_name: str = "solution-experiment",
    model_name: str = "solution-model",
    namespace: str = "kubeflow-user01",
    mlflow_tracking_uri: str = "http://mlflow-server-service.mlflow-system.svc.cluster.local:5000",
    n_estimators: int = 100,
    max_depth: int = 10,
    r2_threshold: float = 0.75
):
    """프로젝트 솔루션 파이프라인"""
    
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
            namespace=namespace,
            mlflow_tracking_uri=mlflow_tracking_uri
        )
    
    with dsl.If(evaluate_task.output == "skip"):
        send_alert(run_id=train_task.output, team_name=team_name)


# ============================================================
# Main
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("  Project Pipeline Solution")
    print("=" * 60)
    
    pipeline_file = "project_solution_pipeline.yaml"
    
    compiler.Compiler().compile(
        pipeline_func=project_pipeline,
        package_path=pipeline_file
    )
    
    print(f"\n✅ Pipeline compiled: {pipeline_file}")
    print(f"\n📋 This solution includes:")
    print(f"  - 7 new engineered features")
    print(f"  - Complete MLflow integration")
    print(f"  - Feature importance logging")
    print(f"  - KServe deployment with status check")
    print("=" * 60)
