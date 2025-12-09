"""
Lab 3-2: 피처 엔지니어링 컴포넌트
=================================

파생 변수를 생성하는 컴포넌트

현대오토에버 MLOps Training
"""

from kfp import dsl
from kfp.dsl import component, Input, Output, Dataset


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
        - location_score: 위치 점수 (정규화된 좌표 기반)
        - density: 밀집도 지표
    
    Args:
        X_train_in: 학습 피처 입력
        X_test_in: 테스트 피처 입력
        X_train_out: 학습 피처 출력 (피처 추가됨)
        X_test_out: 테스트 피처 출력 (피처 추가됨)
    
    Returns:
        피처 엔지니어링 메타데이터
    """
    import pandas as pd
    import numpy as np
    
    print("=" * 60)
    print("  Component: Feature Engineering")
    print("=" * 60)
    
    # 데이터 로드
    X_train = pd.read_csv(X_train_in.path)
    X_test = pd.read_csv(X_test_in.path)
    
    original_features = list(X_train.columns)
    print(f"\n  Original features ({len(original_features)}):")
    for i, feat in enumerate(original_features, 1):
        print(f"     {i}. {feat}")
    
    def add_features(df):
        """파생 변수 추가"""
        df = df.copy()
        
        # 1. 가구당 방 수
        if 'AveRooms' in df.columns and 'AveOccup' in df.columns:
            df['rooms_per_household'] = df['AveRooms'] / (df['AveOccup'] + 1e-6)
        
        # 2. 방 대비 침실 비율
        if 'AveBedrms' in df.columns and 'AveRooms' in df.columns:
            df['bedrooms_ratio'] = df['AveBedrms'] / (df['AveRooms'] + 1e-6)
        
        # 3. 가구당 인구
        if 'Population' in df.columns and 'AveOccup' in df.columns:
            df['population_per_household'] = df['Population'] / (df['AveOccup'] + 1e-6)
        
        # 4. 위치 점수 (정규화된 좌표 기반)
        if 'Latitude' in df.columns and 'Longitude' in df.columns:
            df['location_score'] = np.sqrt(
                df['Latitude']**2 + df['Longitude']**2
            )
        
        # 5. 밀집도 지표
        if 'Population' in df.columns and 'AveOccup' in df.columns:
            df['density'] = df['Population'] * df['AveOccup']
        
        return df
    
    # 피처 추가
    X_train_fe = add_features(X_train)
    X_test_fe = add_features(X_test)
    
    new_features = [f for f in X_train_fe.columns if f not in original_features]
    
    print(f"\n  New features ({len(new_features)}):")
    for i, feat in enumerate(new_features, 1):
        print(f"     {i}. {feat}")
    
    print(f"\n  Total features: {len(X_train_fe.columns)}")
    
    # 새 피처 통계
    if new_features:
        print(f"\n  New Feature Statistics (Train):")
        for feat in new_features:
            values = X_train_fe[feat]
            print(f"     {feat}:")
            print(f"        Mean: {values.mean():.4f}, Std: {values.std():.4f}")
            print(f"        Min: {values.min():.4f}, Max: {values.max():.4f}")
    
    # 저장
    X_train_fe.to_csv(X_train_out.path, index=False)
    X_test_fe.to_csv(X_test_out.path, index=False)
    
    print(f"\n  ✅ Feature engineering completed")
    
    return {
        "original_features": len(original_features),
        "new_features": len(new_features),
        "total_features": len(X_train_fe.columns),
        "new_feature_names": new_features
    }


# 로컬 테스트용
if __name__ == "__main__":
    import pandas as pd
    import numpy as np
    
    # 테스트 데이터 생성
    np.random.seed(42)
    n_samples = 100
    
    df = pd.DataFrame({
        'MedInc': np.random.randn(n_samples),
        'HouseAge': np.random.randn(n_samples),
        'AveRooms': np.random.randn(n_samples),
        'AveBedrms': np.random.randn(n_samples),
        'Population': np.random.randn(n_samples),
        'AveOccup': np.random.randn(n_samples),
        'Latitude': np.random.randn(n_samples),
        'Longitude': np.random.randn(n_samples)
    })
    
    df.to_csv("/tmp/X_train_in.csv", index=False)
    df.to_csv("/tmp/X_test_in.csv", index=False)
    
    class MockIO:
        def __init__(self, path):
            self.path = path
    
    result = feature_engineering.python_func(
        X_train_in=MockIO("/tmp/X_train_in.csv"),
        X_test_in=MockIO("/tmp/X_test_in.csv"),
        X_train_out=MockIO("/tmp/X_train_out.csv"),
        X_test_out=MockIO("/tmp/X_test_out.csv")
    )
    print(f"\nResult: {result}")
