"""
Lab 3-2: 모델 학습 컴포넌트
===========================

모델 학습 및 MLflow 연동을 수행하는 컴포넌트

현대오토에버 MLOps Training
"""

from kfp import dsl
from kfp.dsl import component, Input, Dataset


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
    n_estimators: int = 100,
    max_depth: int = 10
) -> str:
    """
    모델 학습 및 MLflow에 기록
    
    Args:
        X_train: 학습 피처 데이터
        X_test: 테스트 피처 데이터
        y_train: 학습 타겟 데이터
        y_test: 테스트 타겟 데이터
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
    print("  Component: Train Model")
    print("=" * 60)
    
    # 환경 변수 설정
    os.environ['MLFLOW_TRACKING_URI'] = mlflow_tracking_uri
    
    # 데이터 로드
    print(f"\n  Loading data...")
    X_train_df = pd.read_csv(X_train.path)
    X_test_df = pd.read_csv(X_test.path)
    y_train_df = pd.read_csv(y_train.path)
    y_test_df = pd.read_csv(y_test.path)
    
    print(f"     - X_train: {X_train_df.shape}")
    print(f"     - X_test: {X_test_df.shape}")
    print(f"     - Features: {list(X_train_df.columns)}")
    
    # MLflow 설정
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    mlflow.set_experiment(experiment_name)
    
    print(f"\n  📊 MLflow Configuration:")
    print(f"     - Tracking URI: {mlflow_tracking_uri}")
    print(f"     - Experiment: {experiment_name}")
    
    # 학습 및 기록
    with mlflow.start_run() as run:
        run_id = run.info.run_id
        print(f"\n  🏃 Run ID: {run_id}")
        
        # 파라미터 기록
        params = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "random_state": 42,
            "n_jobs": -1,
            "n_features": X_train_df.shape[1],
            "n_train_samples": len(X_train_df)
        }
        mlflow.log_params(params)
        print(f"  ✅ Parameters logged")
        
        # 모델 학습
        print(f"\n  🔄 Training RandomForest model...")
        print(f"     - n_estimators: {n_estimators}")
        print(f"     - max_depth: {max_depth}")
        
        model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            random_state=42,
            n_jobs=-1
        )
        model.fit(X_train_df, y_train_df.values.ravel())
        print(f"  ✅ Model trained")
        
        # 예측 및 평가
        y_pred = model.predict(X_test_df)
        
        mse = mean_squared_error(y_test_df, y_pred)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test_df, y_pred)
        r2 = r2_score(y_test_df, y_pred)
        
        # 메트릭 기록
        metrics = {
            "mse": mse,
            "rmse": rmse,
            "mae": mae,
            "r2": r2
        }
        mlflow.log_metrics(metrics)
        print(f"  ✅ Metrics logged")
        
        print(f"\n  📈 Model Performance:")
        print(f"     - R2 Score: {r2:.4f}")
        print(f"     - RMSE: {rmse:.4f}")
        print(f"     - MAE: {mae:.4f}")
        print(f"     - MSE: {mse:.4f}")
        
        # 피처 중요도 기록
        feature_importance = dict(zip(
            X_train_df.columns,
            model.feature_importances_
        ))
        mlflow.log_dict(feature_importance, "feature_importance.json")
        
        print(f"\n  🔝 Top 5 Important Features:")
        sorted_importance = sorted(
            feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        for i, (feat, imp) in enumerate(sorted_importance, 1):
            print(f"     {i}. {feat}: {imp:.4f}")
        
        # 모델 저장
        mlflow.sklearn.log_model(
            model,
            "model",
            registered_model_name=f"{experiment_name}-model"
        )
        print(f"  ✅ Model registered")
        
        # 태그 추가
        mlflow.set_tags({
            "pipeline": "e2e",
            "stage": "training",
            "algorithm": "RandomForest",
            "n_features": X_train_df.shape[1]
        })
    
    print(f"\n  ✅ Training completed! Run ID: {run_id}")
    
    return run_id


# 로컬 테스트용
if __name__ == "__main__":
    print("This component requires MLflow server to run.")
    print("Please use within Kubeflow Pipeline.")
