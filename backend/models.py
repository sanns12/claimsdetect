from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

from backend.database import Base



# 🚨 CLAIM STATUS ENUM (EXACT VALUES)
class ClaimStatus(str, Enum):
    SUBMITTED = "Submitted"
    AI_PROCESSING = "AI Processing"
    MANUAL_REVIEW = "Manual Review"
    APPROVED = "Approved"
    FLAGGED = "Flagged"
    FRAUD = "Fraud"


# 👤 USER MODEL
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # user, hospital, insurance

    claims = relationship("Claim", back_populates="user")


# 🏢 COMPANY MODEL
class Company(Base):
    __tablename__ = "companies"

    company_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    trust_score = Column(Float, default=0.0)
    flagged_count = Column(Integer, default=0)

    claims = relationship("Claim", back_populates="company")


# 📄 CLAIM MODEL
class Claim(Base):
    __tablename__ = "claims"

    claim_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    company_id = Column(Integer, ForeignKey("companies.company_id"))

    documents = Column(JSON, default={})
    status = Column(String, default=ClaimStatus.SUBMITTED.value)
    risk_score = Column(Float, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="claims")
    company = relationship("Company", back_populates="claims")
