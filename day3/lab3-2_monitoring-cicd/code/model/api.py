"""
FastAPI Model Serving
California Housing 모델을 서빙하는 API
"""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import numpy as np
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="California Housing Model API",
    description="ML model for California Housing price predictions",
    version=os.getenv("MODEL_VERSION", "v1.0")
)

model = None
feature_names = None

class PredictionRequest(BaseModel):
    features: List[float] = Field(..., description="8 features for California Housing")

class PredictionResponse(BaseModel):
    prediction: float
    model_version: str
    features_used: List[str]

@app.on_event("startup")
async def load_model():
    global model, feature_names
    logger.info("Loading California Housing dataset...")
    housing = fetch_california_housing()
    X, y = housing.data, housing.target
    feature_names = housing.feature_names
    
    logger.info("Training Random Forest model...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    
    score = model.score(X_test, y_test)
    logger.info(f"Model trained! R² score: {score:.4f}")

@app.get("/")
async def root():
    return {"message": "California Housing Model API", "version": os.getenv("MODEL_VERSION", "v1.0")}

@app.get("/health")
async def health():
    return {"status": "healthy" if model else "unhealthy", "model_loaded": model is not None}

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    if len(request.features) != 8:
        raise HTTPException(status_code=400, detail=f"Expected 8 features, got {len(request.features)}")
    
    features_array = np.array(request.features).reshape(1, -1)
    prediction = model.predict(features_array)[0]
    
    return PredictionResponse(
        prediction=float(prediction),
        model_version=os.getenv("MODEL_VERSION", "v1.0"),
        features_used=list(feature_names)
    )

@app.get("/metrics")
async def metrics():
    return {"model_loaded": model is not None, "model_version": os.getenv("MODEL_VERSION", "v1.0")}
