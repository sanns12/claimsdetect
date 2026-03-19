from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from database import init_db
from app.routes.auth import router as auth_router
from app.routes.claims import router as claims_router
from app.routes.dashboard import router as dashboard_router
from app.routes.companies import router as company_router
# ...existing code...


app = FastAPI(
    title="Insurance Claims API",
    version="1.0.0"
)

# -------------------------------
# CORS
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
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Startup
# -------------------------------
@app.on_event("startup")
async def startup_event():
    init_db()
    print("✅ Database initialized")
    print("🚀 Server running at http://localhost:8000")


# -------------------------------
# Shutdown
# -------------------------------
@app.on_event("shutdown")
async def shutdown_event():
    await Database.close_db()
    print("🛑 Server shutdown complete")


# -------------------------------
# Register Routers
# -------------------------------
app.include_router(auth_router)
app.include_router(claims_router)
app.include_router(dashboard_router)
app.include_router(company_router)


# -------------------------------
# Root
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
# Health
# -------------------------------
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }