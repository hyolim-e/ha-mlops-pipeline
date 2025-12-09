# California Housing Model Serving Dockerfile
# Lab 3-2: Monitoring & CI/CD Pipeline

FROM python:3.9-slim

# Build arguments
ARG MODEL_VERSION=latest
ARG BUILD_DATE
ARG VCS_REF

# Labels for metadata
LABEL maintainer="MLOps Team" \
      version="${MODEL_VERSION}" \
      description="California Housing Model API" \
      build-date="${BUILD_DATE}" \
      vcs-ref="${VCS_REF}"

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir fastapi uvicorn[standard] pydantic

# Copy application code
COPY scripts/2_metrics_exporter.py /app/model_server.py

# Create model directory
RUN mkdir -p /app/models

# Create a simple FastAPI server for the model
RUN cat > /app/api.py << 'EOF'
"""
California Housing Model API
FastAPI server for model inference
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Dict
import numpy as np
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="California Housing Model API",
    description="API for California Housing price predictions",
    version=os.getenv("MODEL_VERSION", "v1.0")
)

# Global model variable
model = None
feature_names = None

# Pydantic models for request/response
class PredictionRequest(BaseModel):
    """Request model for predictions"""
    features: List[float] = Field(..., description="8 features for California Housing")
    
    class Config:
        schema_extra = {
            "example": {
                "features": [8.3252, 41.0, 6.984127, 1.023810, 322.0, 2.555556, 37.88, -122.23]
            }
        }

class PredictionResponse(BaseModel):
    """Response model for predictions"""
    prediction: float = Field(..., description="Predicted house price")
    model_version: str = Field(..., description="Model version")
    features_used: List[str] = Field(..., description="Feature names")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    model_loaded: bool
    model_version: str

@app.on_event("startup")
async def load_model():
    """Load and train model on startup"""
    global model, feature_names
    
    try:
        logger.info("Loading California Housing dataset...")
        housing = fetch_california_housing()
        X, y = housing.data, housing.target
        feature_names = housing.feature_names
        
        logger.info("Training Random Forest model...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
        model.fit(X_train, y_train)
        
        score = model.score(X_test, y_test)
        logger.info(f"Model trained successfully! R² score: {score:.4f}")
        
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint"""
    return {
        "message": "California Housing Model API",
        "version": os.getenv("MODEL_VERSION", "v1.0"),
        "docs": "/docs"
    }

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy" if model is not None else "unhealthy",
        model_loaded=model is not None,
        model_version=os.getenv("MODEL_VERSION", "v1.0")
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """Make prediction endpoint"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    if len(request.features) != 8:
        raise HTTPException(
            status_code=400, 
            detail=f"Expected 8 features, got {len(request.features)}"
        )
    
    try:
        # Make prediction
        features_array = np.array(request.features).reshape(1, -1)
        prediction = model.predict(features_array)[0]
        
        logger.info(f"Prediction made: {prediction:.4f}")
        
        return PredictionResponse(
            prediction=float(prediction),
            model_version=os.getenv("MODEL_VERSION", "v1.0"),
            features_used=feature_names
        )
    
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return {
        "model_loaded": model is not None,
        "model_version": os.getenv("MODEL_VERSION", "v1.0"),
        "feature_count": len(feature_names) if feature_names else 0
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Expose port
EXPOSE 8000

# Set environment variables
ENV MODEL_VERSION=${MODEL_VERSION} \
    PYTHONUNBUFFERED=1

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
