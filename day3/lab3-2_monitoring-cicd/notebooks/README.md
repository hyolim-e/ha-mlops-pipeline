# Jupyter Notebook 실습 가이드

## 📓 모니터링 시스템 대화형 실습

Jupyter Notebook을 통해 대화형으로 모니터링 시스템을 학습할 수 있습니다.

### 실행 방법

```bash
cd lab3-2_monitoring-cicd/notebooks
jupyter notebook monitoring_interactive.ipynb
```

---

## 📚 Notebook 구성

### 1. 환경 설정
- Prometheus Client 라이브러리 import
- 메트릭 정의 및 초기화

### 2. Prometheus 메트릭 생성
- Counter, Gauge, Histogram 실습
- Custom metrics 정의

### 3. 메트릭 시각화
- Matplotlib으로 실시간 차트 생성
- A/B 테스트 결과 비교

### 4. Prometheus 쿼리 (PromQL)
- 기본 쿼리 실습
- 집계 함수 사용
- Rate, Histogram_quantile

### 5. 알림 규칙 테스트
- 임계값 설정
- 알림 조건 시뮬레이션

---

## 💡 학습 목표

- [ ] Prometheus 메트릭 타입 이해
- [ ] Custom metrics 생성
- [ ] PromQL 쿼리 작성
- [ ] 알림 규칙 설정
- [ ] A/B 테스트 분석

---

## 🔗 참고 자료

- [Prometheus Python Client](https://github.com/prometheus/client_python)
- [PromQL 문서](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana 대시보드](../dashboards/model-performance-dashboard.json)

---

## 📝 실습 팁

### Tip 1: 메트릭 확인
```python
# Jupyter에서 메트릭 서버 시작
from prometheus_client import start_http_server, Gauge
start_http_server(8000)

# 브라우저에서 확인: http://localhost:8000/metrics
```

### Tip 2: 실시간 시각화
```python
import matplotlib.pyplot as plt
%matplotlib notebook

# 실시간 업데이트 차트
fig, ax = plt.subplots()
line, = ax.plot([], [])
```

### Tip 3: PromQL 쿼리
```python
import requests

def query_prometheus(query):
    response = requests.get(
        'http://localhost:9090/api/v1/query',
        params={'query': query}
    )
    return response.json()

# 예시
result = query_prometheus('model_mae_score')
print(result)
```

---

© 2025 현대오토에버 MLOps Training - Lab 3-2
