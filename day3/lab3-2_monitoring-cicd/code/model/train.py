"""
Model Training Script
California Housing 모델 학습
"""
from sklearn.datasets import fetch_california_housing
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train_model(n_estimators=100, max_depth=10, random_state=42):
    """
    California Housing 모델 학습
    """
    logger.info("Loading data...")
    housing = fetch_california_housing()
    X, y = housing.data, housing.target
    
    logger.info("Splitting data...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=random_state
    )
    
    logger.info(f"Training Random Forest (n_estimators={n_estimators}, max_depth={max_depth})...")
    model = RandomForestRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        random_state=random_state,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    
    logger.info("Evaluating model...")
    y_pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    logger.info(f"Results - MAE: {mae:.4f}, R²: {r2:.4f}")
    
    return model, {"mae": mae, "r2": r2}

if __name__ == "__main__":
    model, metrics = train_model()
    
    # Save model
    joblib.dump(model, "california_housing_model.pkl")
    logger.info("✅ Model saved to california_housing_model.pkl")
    logger.info(f"   MAE: {metrics['mae']:.4f}")
    logger.info(f"   R²: {metrics['r2']:.4f}")
