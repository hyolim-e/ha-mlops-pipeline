"""
Metrics Test Script
Prometheus 메트릭 테스트
"""
import requests
import pytest

METRICS_URL = "http://localhost:8080/metrics"

def test_metrics_endpoint():
    """Metrics 엔드포인트 테스트"""
    response = requests.get(METRICS_URL)
    assert response.status_code == 200
    content = response.text
    
    # Check metrics existence
    assert "model_mae_score" in content
    assert "model_r2_score" in content
    assert "model_prediction_count" in content
    assert "model_prediction_latency_seconds" in content

def test_metrics_labels():
    """Metrics 레이블 테스트"""
    response = requests.get(METRICS_URL)
    content = response.text
    
    # Check labels
    assert 'model_version="v1.0"' in content
    assert 'model_version="v2.0"' in content

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
