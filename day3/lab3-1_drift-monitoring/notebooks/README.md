# Jupyter Notebook 실습

## 📓 drift_analysis.ipynb

Jupyter Notebook을 통한 대화형 Drift 분석 실습입니다.

### 실행 방법

```bash
cd lab3-1_drift-monitoring/notebooks
jupyter notebook drift_analysis.ipynb
```

### 학습 내용

1. **데이터 로드**: California Housing 데이터셋
2. **Drift 시뮬레이션**: MedInc feature에 의도적 변화 추가
3. **Statistical Test**: KS Test로 Drift 감지
4. **시각화**: Feature 분포 비교
5. **HTML 리포트**: Evidently를 사용한 리포트 생성

### 주요 코드

```python
from scipy.stats import ks_2samp

# Drift Detection
for col in reference_data.columns:
    _, p_value = ks_2samp(reference_data[col], current_data[col])
    if p_value < 0.05:
        print(f"{col}: Drift detected!")
```

---

© 2025 MLOps Training Lab 3-1
