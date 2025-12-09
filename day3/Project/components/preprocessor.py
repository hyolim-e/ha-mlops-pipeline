"""
Lab 3-2: 전처리 컴포넌트
========================

데이터 분할 및 정규화를 수행하는 컴포넌트

현대오토에버 MLOps Training
"""

from kfp import dsl
from kfp.dsl import component, Input, Output, Dataset


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
        X_train_out: 학습 피처 출력
        X_test_out: 테스트 피처 출력
        y_train_out: 학습 타겟 출력
        y_test_out: 테스트 타겟 출력
        test_size: 테스트 세트 비율 (기본값: 0.2)
    
    Returns:
        전처리 메타데이터 (샘플 수, 피처 수)
    """
    import pandas as pd
    import numpy as np
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    
    print("=" * 60)
    print("  Component: Preprocess")
    print("=" * 60)
    
    # 데이터 로드
    df = pd.read_csv(input_data.path)
    print(f"\n  Loaded {len(df)} rows")
    
    # 타겟 컬럼 확인
    target_col = "MedHouseVal"
    if target_col not in df.columns:
        # 마지막 컬럼을 타겟으로 가정
        target_col = df.columns[-1]
    
    print(f"  Target column: {target_col}")
    
    # 피처와 타겟 분리
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    print(f"  Features: {list(X.columns)}")
    
    # Train/Test 분할
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=42
    )
    
    print(f"\n  Train/Test Split:")
    print(f"     - Train size: {len(X_train)} ({(1-test_size)*100:.0f}%)")
    print(f"     - Test size: {len(X_test)} ({test_size*100:.0f}%)")
    
    # 정규화
    print(f"\n  Applying StandardScaler...")
    scaler = StandardScaler()
    X_train_scaled = pd.DataFrame(
        scaler.fit_transform(X_train),
        columns=X_train.columns
    )
    X_test_scaled = pd.DataFrame(
        scaler.transform(X_test),
        columns=X_test.columns
    )
    
    # 정규화 통계
    print(f"\n  Scaling Statistics (Train):")
    print(f"     - Mean: {scaler.mean_[:3]}... (first 3 features)")
    print(f"     - Std: {np.sqrt(scaler.var_[:3])}... (first 3 features)")
    
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


# 로컬 테스트용
if __name__ == "__main__":
    from sklearn.datasets import fetch_california_housing
    import pandas as pd
    
    # 테스트 데이터 생성
    housing = fetch_california_housing(as_frame=True)
    df = housing.frame
    df.to_csv("/tmp/input_data.csv", index=False)
    
    class MockInput:
        def __init__(self, path):
            self.path = path
    
    class MockOutput:
        def __init__(self, name):
            self.path = f"/tmp/{name}.csv"
    
    result = preprocess.python_func(
        input_data=MockInput("/tmp/input_data.csv"),
        X_train_out=MockOutput("X_train"),
        X_test_out=MockOutput("X_test"),
        y_train_out=MockOutput("y_train"),
        y_test_out=MockOutput("y_test")
    )
    print(f"\nResult: {result}")
