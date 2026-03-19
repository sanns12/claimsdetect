# backend/schemas/models.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# =====================================================
# ENUMS (Aligned with SQLite)
# =====================================================

class ClaimStatus(str, Enum):
    SUBMITTED = "Submitted"
    AI_PROCESSING = "AI Processing"
    MANUAL_REVIEW = "Manual Review"
    APPROVED = "Approved"
    FLAGGED = "Flagged"
    FRAUD = "Fraud"


class UserRole(str, Enum):
    USER = "user"
    HOSPITAL = "hospital"
    INSURANCE = "insurance"


class TrustLevel(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    BLACK = "black"


class DocumentType(str, Enum):
    PDF = "pdf"
    IMAGE = "image"
    TEXT = "text"
    OTHER = "other"


# =====================================================
# USER MODELS (Matches users table)
# =====================================================

class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    role: UserRole


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str
    role: UserRole


class UserResponse(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# TOKEN MODELS
# =====================================================

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[int] = None
    role: Optional[str] = None


# =====================================================
# CLAIM MODELS (Aligned with claims table)
# =====================================================

class ClaimBase(BaseModel):
    patient_name: str
    hospital_name: Optional[str] = None
    age: int
    disease: str
    admission_date: datetime
    discharge_date: datetime
    claim_amount: float


class ClaimCreate(ClaimBase):
    pass


class ClaimUpdate(BaseModel):
    status: Optional[ClaimStatus] = None


class ClaimResponse(ClaimBase):
    id: int
    claim_number: str
    user_id: int
    company_id: Optional[int] = None
    duration_days: Optional[int] = None
    risk_score: Optional[float] = None
    fraud_probability: Optional[float] = None
    status: ClaimStatus
    lime_explanation: Optional[str] = None
    mismatch_flag: Optional[bool] = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# RISK MODELS
# =====================================================

class RiskFactor(BaseModel):
    name: str
    impact: float
    description: str
    color: Optional[str] = None


class FraudPrediction(BaseModel):
    fraud_probability: float
    prediction: int
    risk_score: float
    model_loaded: bool
    timestamp: datetime


# =====================================================
# COMPANY TRUST MODELS (Matches companies table)
# =====================================================

class CompanyTrustResponse(BaseModel):
    id: int
    name: str
    type: str
    trust_status: TrustLevel
    fraud_percentage: float
    total_claims: int
    flagged_claims: int
    created_at: datetime

    class Config:
        from_attributes = True


# =====================================================
# DASHBOARD MODELS
# =====================================================

class DashboardStats(BaseModel):
    total_claims: int
    total_amount: float
    pending_review: int
    approved: int
    flagged: int
    fraud: int
    avg_processing_time: float


class FraudTrend(BaseModel):
    month: str
    amount: int


class Alert(BaseModel):
    id: str
    type: str
    message: str
    time: str
    severity: str


# =====================================================
# DOCUMENT VERIFICATION MODELS
# =====================================================

class DocumentVerification(BaseModel):
    filename: str
    verified: bool
    hash: Optional[str] = None
    size: Optional[int] = None
    mime_type: Optional[str] = None
    issues: List[str] = Field(default_factory=list)
    authenticity_score: Optional[float] = None


class BatchVerificationResult(BaseModel):
    results: List[DocumentVerification] = Field(default_factory=list)
    total_verified: int
    total_failed: int


# =====================================================
# GENERIC RESPONSE MODELS
# =====================================================

class ResponseModel(BaseModel):
    message: str
    success: bool = True
    data: Optional[Dict[str, Any]] = None


class ErrorResponse(BaseModel):
    message: str
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    