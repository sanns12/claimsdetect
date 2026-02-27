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

# Import database and ML model
from database import init_db, Database, seed_database
from ml_model import load_model, predict_fraud, get_model

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
# Load Trained Model Once (using ml_model.py)
# -------------------------------
model = None

@app.on_event("startup")
async def startup_event():
    """Initialize database and load model on startup"""
    global model
    
    # Initialize database tables (init_db is synchronous)
    try:
        init_db()  # Remove await, it's not async
        print("✅ Database initialized with schema")
        
        # Seed the database with initial data
        seed_database()
        print("✅ Database seeded with sample data")
        print("✅ Database connected")
    except Exception as e:
        print(f"⚠️ Database initialization failed: {e}")
    
    # Load ML model using ml_model.py
    try:
        load_model()  # This loads the model into ml_model._model
        model = get_model()  # Get the loaded model instance
        if model is not None:
            print("✅ ML Model loaded successfully via ml_model.py")
        else:
            print("⚠️ ML Model could not be loaded")
    except Exception as e:
        print(f"❌ Error loading ML model: {e}")
        model = None
    
    print("✅ Server starting on http://localhost:8000")

# -------------------------------
# Shutdown Event
# -------------------------------
@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    try:
        # Run the synchronous close_db in a thread pool
        import asyncio
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, Database.close_db)
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
    # Get current model status from ml_model
    from ml_model import _model
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected",
        "model_loaded": _model is not None
    }

# -------------------------------
# Test CORS endpoint
# -------------------------------
@app.get("/test-cors")
async def test_cors():
    return {"message": "CORS is working!", "origin": "test"}

# -------------------------------
# Prediction Route - Now using ml_model.py
# -------------------------------
@app.post("/predict")
async def predict(claim: dict):
    """Predict fraud probability using ml_model.py"""
    try:
        # Use the predict_fraud function from ml_model.py
        result = predict_fraud({
            "patient_age": claim.get("patient_age", claim.get("age", 35)),
            "claimed_amount": claim.get("claimed_amount", claim.get("amount", 5000))
        })
        return result
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        return {
            "error": str(e),
            "fraud_probability": 0.0,
            "prediction": 0,
            "risk_level": "unknown",
            "model_loaded": False
        }

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