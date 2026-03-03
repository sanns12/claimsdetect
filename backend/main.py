import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth import router as auth_router
from database import engine, Base
from models import User, Claim
from claim_routes_clean import router as claim_router
from dashboard_routes_clean import router as dashboard_router

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app FIRST
app = FastAPI(title="MediSecure API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (app is now defined)
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(claim_router, prefix="/claims", tags=["Claims"])
app.include_router(dashboard_router, prefix="/dashboard", tags=["Dashboard"])

@app.get("/")
def root():
    return {"message": "MediSecure API is running", "status": "healthy"}

@app.get("/health")
def health_check():
    return {"status": "ok"}