from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./insurance.db"

# Create engine
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Create session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Mock users collection for auth
users_db = {
    "customer@demo.com": {
        "id": 1,
        "username": "customer@demo.com",
        "email": "customer@demo.com",
        "full_name": "John Doe",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
        "role": "user",
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    "hospital@demo.com": {
        "id": 2,
        "username": "hospital@demo.com",
        "email": "hospital@demo.com",
        "full_name": "City Hospital",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
        "role": "hospital",
        "created_at": datetime.now(timezone.utc).isoformat()
    },
    "insurer@demo.com": {
        "id": 3,
        "username": "insurer@demo.com",
        "email": "insurer@demo.com",
        "full_name": "MediSure Insurance",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
        "role": "insurance",
        "created_at": datetime.now(timezone.utc).isoformat()
    }
}

def get_users_collection():
    """Return mock users collection for authentication"""
    return users_db

def get_db():
    """Dependency to get DB session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)