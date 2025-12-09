# 📓 Jupyter Notebook 실습 가이드

## ⚠️ 중요: AWS S3 연결 설정

**실습 시작 전 반드시 AWS 자격 증명을 설정하세요!**

```python
# Cell 0: AWS 자격 증명 설정 (필수!)
import os

# AWS 자격 증명 설정 (여기에 본인의 키를 입력하세요!)
os.environ['AWS_ACCESS_KEY_ID'] = 'YOUR_ACCESS_KEY'          # 변경 필요!
os.environ['AWS_SECRET_ACCESS_KEY'] = 'YOUR_SECRET_KEY'      # 변경 필요!
os.environ['AWS_DEFAULT_REGION'] = 'ap-northeast-2'

# 연결 테스트
import boto3
s3 = boto3.client('s3')

try:
    response = s3.list_buckets()
    print(f"✅ AWS S3 연결 성공! 버킷 개수: {len(response['Buckets'])}")
except Exception as e:
    print(f"❌ AWS S3 연결 실패: {e}")
    print("\n자격 증명을 확인하세요!")
```

---

## 📋 실습 구조 (총 90분)

- **Part 1**: ETL Pipeline (45분)
- **Part 2**: Pandas를 활용한 Batch Processing (45분)

---

## 🎯 Part 1: ETL Pipeline (45분)

### Cell 1: 환경 설정

```python
import os
import pandas as pd
import numpy as np
import awswrangler as wr
from datetime import datetime, timedelta

# 환경 변수 설정
USER_NUM = os.getenv('USER_NUM', '01')  # 본인 번호로 변경!
BUCKET_NAME = f"mlops-training-data-user{USER_NUM}"
AWS_REGION = 'ap-northeast-2'

print(f"사용자: {USER_NUM}")
print(f"버킷: {BUCKET_NAME}")
print(f"리전: {AWS_REGION}")
```

### Cell 2: ETL 파이프라인 전체 실행

```python
# ETL 파이프라인 전체 실행
%run scripts/1_etl_pipeline/etl_pipeline.py
```

**또는 단계별로 실행:**

```python
# Cell 2-1: Data Lake 구조 생성
import boto3

s3_client = boto3.client('s3', region_name=AWS_REGION)

try:
    # S3 버킷 생성
    s3_client.create_bucket(
        Bucket=BUCKET_NAME,
        CreateBucketConfiguration={'LocationConstraint': AWS_REGION}
    )
    print(f"✅ 버킷 생성 완료: {BUCKET_NAME}")
except s3_client.exceptions.BucketAlreadyOwnedByYou:
    print(f"✅ 버킷이 이미 존재함: {BUCKET_NAME}")

print("\n📁 Data Lake 구조:")
print(f"Bronze: s3://{BUCKET_NAME}/raw/")
print(f"Silver: s3://{BUCKET_NAME}/processed/")
print(f"Gold: s3://{BUCKET_NAME}/curated/")
```

```python
# Cell 2-2: 샘플 데이터 생성
np.random.seed(42)

num_customers = 1000
customer_ids = list(range(1, num_customers + 1))
names = [f"Customer_{i}" for i in customer_ids]
ages = np.random.randint(18, 70, num_customers)
emails = [f"user{i}@example.com" for i in customer_ids]
cities = np.random.choice(['Seoul', 'Busan', 'Incheon', 'Daegu'], num_customers)
join_dates = [datetime.now() - timedelta(days=np.random.randint(1, 365)) for _ in range(num_customers)]

# 데이터 품질 이슈 추가 (10%)
issue_indices = np.random.choice(num_customers, size=100, replace=False)

# Null 값 (33개)
for idx in issue_indices[:33]:
    emails[idx] = None

# 중복 (33개)
for idx in issue_indices[33:66]:
    customer_ids[idx] = customer_ids[0]

# 잘못된 형식 (34개)
for idx in issue_indices[66:]:
    emails[idx] = f"invalid_{idx}"

df_customers = pd.DataFrame({
    'customer_id': customer_ids,
    'name': names,
    'age': ages,
    'email': emails,
    'city': cities,
    'join_date': join_dates
})

print(f"✅ 생성 완료: {len(df_customers)}명")
print(f"Null: {df_customers['email'].isnull().sum()}")
print(f"중복: {df_customers['customer_id'].duplicated().sum()}")
df_customers.head()
```

---

## 🎯 Part 2: Batch Processing (45분)

### Cell 3: Batch Processing 실행

```python
# Batch Processing 스크립트 실행
%run scripts/2_batch_processing/pandas_batch_job.py
```

**예상 출력:**
```
============================================================
BATCH 데이터 처리 (Pandas)
============================================================
...
✅ BATCH 데이터 처리 완료!
```

### Cell 4: 결과 확인

```python
# Gold Layer 결과 읽기
gold_path = f"s3://{BUCKET_NAME}/curated/analysis/"

# 도시별 분석
city_df = wr.s3.read_parquet(gold_path + "city_analysis/")
print("📊 도시별 고객 수:")
print(city_df.sort_values('count', ascending=False))
print()

# 나이대별 분석
age_df = wr.s3.read_parquet(gold_path + "age_analysis/")
print("📊 나이대별 분포:")
print(age_df.sort_values('age_group'))
print()

# 통계 요약
stats_df = wr.s3.read_parquet(gold_path + "statistics/")
print("📊 통계 요약:")
print(stats_df)
```

### Cell 5: 시각화 (선택사항) - 영어 라벨만 사용

```python
import matplotlib.pyplot as plt

# ⚠️ 그래프 라벨은 영어만 사용 (한글 폰트 이슈 방지)
plt.rcParams['axes.unicode_minus'] = False

# 차트 생성
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# 1. 도시별 고객 수
city_df_plot = city_df.copy()
axes[0].bar(city_df_plot['city'], city_df_plot['count'], color='steelblue', alpha=0.8)
axes[0].set_title('Customer Count by City', fontsize=13, fontweight='bold', pad=15)
axes[0].set_xlabel('City', fontsize=11)
axes[0].set_ylabel('Count', fontsize=11)
axes[0].grid(axis='y', alpha=0.3, linestyle='--')

# 값 레이블 추가
for i, (city, count) in enumerate(zip(city_df_plot['city'], city_df_plot['count'])):
    axes[0].text(i, count + 10, str(count), ha='center', va='bottom', fontsize=10)

# 2. 나이대별 분포
age_df_plot = age_df.copy()
axes[1].bar(age_df_plot['age_group'], age_df_plot['count'], color='coral', alpha=0.8)
axes[1].set_title('Customer Distribution by Age Group', fontsize=13, fontweight='bold', pad=15)
axes[1].set_xlabel('Age Group', fontsize=11)
axes[1].set_ylabel('Count', fontsize=11)
axes[1].grid(axis='y', alpha=0.3, linestyle='--')

# 값 레이블 추가
for i, (age, count) in enumerate(zip(age_df_plot['age_group'], age_df_plot['count'])):
    axes[1].text(i, count + 5, str(count), ha='center', va='bottom', fontsize=10)

plt.tight_layout()
plt.show()

print("\n✅ 차트 생성 완료!")
print("   - 왼쪽: 도시별 고객 수")
print("   - 오른쪽: 나이대별 분포")
```

---

## 💡 왜 Pandas를 사용하나요?

### ✅ Pandas의 장점
1. **간단하고 직관적** - 추가 인프라 불필요
2. **빠른 개발** - 복잡한 설정 없음
3. **쉬운 디버깅** - 로컬에서 테스트 가능
4. **AWS 통합** - AWS Wrangler와 완벽한 호환

### ⚠️ Spark가 필요한 경우
- 10GB 이상의 대용량 데이터 처리
- 복잡한 분산 처리 작업
- 실시간 스트리밍 처리

**이번 실습(1000행)에서는 Pandas가 최적의 선택입니다!**

---

## 🎉 실습 완료!

축하합니다! 다음을 완료했습니다:

1. ✅ **Part 1**: S3 Data Lake + ETL Pipeline
2. ✅ **Part 2**: Pandas 기반 Batch Processing

### 다음 단계
- **Day 2**: 모델 서빙 & 버전 관리
- **Lab 2-1**: FastAPI 모델 서빙
- **Lab 2-2**: MLflow Tracking & Registry

---

© 2025 현대오토에버 MLOps Training
