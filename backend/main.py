from fastapi import FastAPI

from backend.database import engine
from backend.models import Base
from backend.claim_routes import router as claim_router
from backend.dashboard_routes import router as dashboard_router
from backend.auth import router as auth_router

app = FastAPI(title="Insurance Claim Management Platform")

# Create DB tables
Base.metadata.create_all(bind=engine)

# Register routes
app.include_router(auth_router)
app.include_router(claim_router)
app.include_router(dashboard_router)

@app.get("/")
def root():
    return {"status": "Backend running successfully"}
