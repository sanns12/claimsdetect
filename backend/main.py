from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import joblib
import pandas as pd
import os
from datetime import datetime

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
        await init_db()
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

# -------------------------------
# Prediction Route
# -------------------------------
@app.post("/predict")
async def predict(claim: dict):
    """Predict fraud probability"""
    global model
    
    try:
        age = claim.get("patient_age", claim.get("age", 35))
        amount = claim.get("claimed_amount", claim.get("amount", 5000))
        
        if model is not None:
            df = pd.DataFrame([{"patient_age": age, "claimed_amount": amount}])
            prob = model.predict_proba(df)[0][1]
            pred = int(model.predict(df)[0])
        else:
            prob = min(amount / 100000, 0.5)
            pred = 1 if prob > 0.5 else 0
        
        return {
            "fraud_probability": float(prob),
            "prediction": pred,
            "risk_level": "high" if prob > 0.7 else "medium" if prob > 0.3 else "low",
            "model_loaded": model is not None
        }
    except Exception as e:
        return {"error": str(e), "fraud_probability": 0.0, "prediction": 0}

# -------------------------------
# Run Server
# -------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )