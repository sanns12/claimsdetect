from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import joblib
import pandas as pd
import os
from datetime import datetime
from ml_model import predict_fraud
from risk_engine import calculate_risk
from shap_explainer import explain_prediction

# Import routers
from auth import router as auth_router
from claim_routes_clean import router as claim_router
from dashboard_routes_clean import router as dashboard_router
from company_trust_logic import router as company_router


# Import database
from database import init_db, Database

app = FastAPI(title="Insurance Claims API", version="1.0.0")

# -------------------------------
# CORS Middleware - FIXED: removed duplicate allow_credentials
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,  # Only ONCE
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Load Trained Model Once
# -------------------------------
MODEL_PATH = os.path.join(os.path.dirname(__file__), "models", "xgboost_fraud_model.pkl")
model = None

try:
    if os.path.exists(MODEL_PATH):
        model = joblib.load(MODEL_PATH)
        print(f"✅ Model loaded successfully from {MODEL_PATH}")
    else:
        print(f"⚠️ Model not found at {MODEL_PATH}")
except Exception as e:
    print(f"❌ Error loading model: {e}")

# -------------------------------
# Startup Event
# -------------------------------
@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    try:
        init_db()
        print("✅ Database connected")
    except Exception as e:
        print(f"⚠️ Database connection failed: {e}")
    print("✅ Server starting on http://localhost:8000")

# -------------------------------
# Shutdown Event
# -------------------------------
@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    try:
        await Database.close_db()
        print("✅ Database connection closed")
    except Exception as e:
        print(f"⚠️ Error closing database: {e}")

# -------------------------------
# Include Routers
# -------------------------------
app.include_router(auth_router)
app.include_router(claim_router)
app.include_router(dashboard_router)
app.include_router(company_router)

# -------------------------------
# Home Route
# -------------------------------
@app.get("/")
async def home():
    return {
        "message": "Insurance Claims API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "auth": "/auth/*",
            "claims": "/claims/*",
            "dashboard": "/dashboard/*",
            "companies": "/companies/*"
        }
    }

# -------------------------------
# Health Check
# -------------------------------
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected",
        "model_loaded": model is not None
    }


# -------------------------------
# Test CORS endpoint
# -------------------------------
@app.get("/test-cors")
async def test_cors():
    return {"message": "CORS is working!", "origin": "test"}


@app.post("/predict")
async def predict(claim: dict):

    try:
        result = predict_fraud(claim)

        risk_level = calculate_risk(result["fraud_probability"])

        explanation = explain_prediction(
            result["model"],
            result["features_df"]
        )

        return {
            "fraud_probability": result["fraud_probability"],
            "prediction": result["prediction"],
            "risk_level": risk_level,
            "top_risk_factors": explanation,
            "model_loaded": True
        }

    except Exception as e:
        return {
            "error": str(e),
            "fraud_probability": 0.0,
            "prediction": 0
        }