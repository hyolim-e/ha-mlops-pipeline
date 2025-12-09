"""
Lab 3-2: 데이터 로드 컴포넌트
============================

데이터셋을 로드하고 저장하는 컴포넌트

현대오토에버 MLOps Training
"""

from kfp import dsl
from kfp.dsl import component, Output, Dataset


@component(
    base_image="python:3.9-slim",
    packages_to_install=["pandas==2.0.3", "scikit-learn==1.3.2"]
)
def load_data(
    data_source: str,
    output_data: Output[Dataset]
):
    """
    데이터를 로드하고 CSV로 저장합니다.
    
    Args:
        data_source: 데이터 소스 ("sklearn" 또는 S3/파일 경로)
        output_data: 출력 데이터셋
    
    지원하는 데이터 소스:
        - "sklearn": California Housing 데이터셋 (기본)
        - S3 또는 로컬 파일 경로
    """
    import pandas as pd
    from sklearn.datasets import fetch_california_housing
    
    print("=" * 60)
    print("  Component: Load Data")
    print("=" * 60)
    
    # 데이터 로드
    if data_source == "sklearn":
        print("\n  Data source: sklearn (California Housing)")
        housing = fetch_california_housing(as_frame=True)
        df = housing.frame
    else:
        print(f"\n  Data source: {data_source}")
        df = pd.read_csv(data_source)
    
    # 데이터 정보 출력
    print(f"\n  📊 Data Information:")
    print(f"     - Rows: {len(df)}")
    print(f"     - Columns: {len(df.columns)}")
    print(f"     - Features: {list(df.columns[:-1])}")
    print(f"     - Target: {df.columns[-1]}")
    
    print(f"\n  📈 Data Statistics:")
    print(df.describe().to_string())
    
    # 저장
    df.to_csv(output_data.path, index=False)
    print(f"\n  ✅ Data saved: {output_data.path}")


# 로컬 테스트용
if __name__ == "__main__":
    class MockOutput:
        def __init__(self):
            self.path = "/tmp/test_data.csv"
    
    output = MockOutput()
    load_data.python_func(
        data_source="sklearn",
        output_data=output
    )
    print(f"\nTest completed. Output: {output.path}")
