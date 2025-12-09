#!/usr/bin/env python3
"""
Lab 2-2: MLflow 실험 추적
"""

import mlflow
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score

# MLflow 설정
mlflow.set_tracking_uri("http://mlflow-server-service.mlflow-system.svc.cluster.local:5000")
mlflow.set_experiment("california-housing-s3")

# 데이터 로드
data = fetch_california_housing()
X_train, X_test, y_train, y_test = train_test_split(
    data.data, data.target, test_size=0.2, random_state=42
)

print("="*60)
print("  California Housing 실험")
print("="*60)
print()

# 실험 1: LinearRegression
print("[1/2] LinearRegression 학습 중...")
with mlflow.start_run(run_name="linear-baseline"):
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    r2 = r2_score(y_test, predictions)
    
    mlflow.log_params({"model_type": "LinearRegression"})
    mlflow.log_metrics({"r2_score": r2})
    mlflow.sklearn.log_model(model, "model")
    
    print(f"  R2 Score: {r2:.4f}")
    print()

# 실험 2: RandomForest
print("[2/2] RandomForest 학습 중...")
with mlflow.start_run(run_name="rf-baseline"):
    model = RandomForestRegressor(
        n_estimators=100,
        max_depth=10,
        random_state=42
    )
    model.fit(X_train, y_train)
    
    predictions = model.predict(X_test)
    r2 = r2_score(y_test, predictions)
    
    mlflow.log_params({
        "model_type": "RandomForest",
        "n_estimators": 100,
        "max_depth": 10
    })
    mlflow.log_metrics({"r2_score": r2})
    mlflow.sklearn.log_model(model, "model")
    
    print(f"  R2 Score: {r2:.4f}")
    print()

print("="*60)
print("✅ 실험 완료!")
print()
print("MLflow UI 확인:")
print("kubectl port-forward svc/mlflow-server-service -n mlflow-system 5000:5000")
print("브라우저: http://localhost:5000")
print("="*60)
