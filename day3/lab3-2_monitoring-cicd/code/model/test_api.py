"""
API Test Script
FastAPI 엔드포인트 테스트
"""
import requests
import pytest

BASE_URL = "http://localhost:8000"

def test_health():
    """Health 엔드포인트 테스트"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"

def test_root():
    """Root 엔드포인트 테스트"""
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data

def test_predict():
    """Prediction 엔드포인트 테스트"""
    payload = {
        "features": [8.3252, 41.0, 6.98, 1.02, 322.0, 2.55, 37.88, -122.23]
    }
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert "model_version" in data
    assert isinstance(data["prediction"], float)

def test_predict_invalid_features():
    """잘못된 Feature 개수 테스트"""
    payload = {"features": [1, 2, 3]}  # 8개가 아닌 3개
    response = requests.post(f"{BASE_URL}/predict", json=payload)
    assert response.status_code == 400

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
