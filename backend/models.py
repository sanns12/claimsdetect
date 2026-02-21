from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# -------------------------------
# Enums
# -------------------------------
class ClaimStatus(str, Enum):
    SUBMITTED = "Submitted"
    AI_PROCESSING = "AI Processing"
    MANUAL_REVIEW = "Manual Review"
    APPROVED = "Approved"
    FLAGGED = "Flagged"
    FRAUD = "Fraud"

class UserRole(str, Enum):
    USER = "User"
    HOSPITAL = "Hospital"
    INSURANCE = "Insurance"

class TrustLevel(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    BLACK = "black"

class DocumentType(str, Enum):
    PDF = "pdf"
    IMAGE = "image"
    TEXT = "text"
    OTHER = "other"

# -------------------------------
# User Models
# -------------------------------
class UserBase(BaseModel):
    email: EmailStr
    name: str
    role: UserRole
    hospital_id: Optional[str] = None
    department: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    role: UserRole

class User(UserBase):
    id: str
    created_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    
    class Config:
        from_attributes = True
        arbitrary_types_allowed = True

class UserInDB(User):
    hashed_password: str

# -------------------------------
# Token Models
# -------------------------------
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[str] = None

# -------------------------------
# Claim Models
# -------------------------------
class ClaimBase(BaseModel):
    patient_id: str
    patient_name: str
    age: int
    gender: str
    admission_date: datetime
    discharge_date: datetime
    diagnosis: str
    procedure: Optional[str] = None
    claim_amount: float
    department: str
    doctor_name: str
    doctor_license: Optional[str] = None
    hospital_id: str
    hospital_name: str
    insurance_provider: str
    policy_number: str

class ClaimCreate(ClaimBase):
    submitted_by: str
    documents: List[str] = []

class ClaimUpdate(BaseModel):
    status: Optional[ClaimStatus] = None
    notes: Optional[str] = None

class ClaimDocument(BaseModel):
    filename: str
    file_type: DocumentType
    file_size: int
    uploaded_at: datetime
    verified: bool = False
    verification_issues: List[str] = []

class ClaimNote(BaseModel):
    text: str
    author: str
    author_id: str
    created_at: datetime

class ClaimFlag(BaseModel):
    type: str
    severity: str  # low, medium, high
    description: str
    created_at: datetime

class Claim(ClaimBase):
    id: str
    claim_number: str
    status: ClaimStatus
    risk_score: float
    fraud_probability: float
    submitted_by: str
    submitted_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    processed_by: Optional[str] = None
    documents: List[ClaimDocument] = []
    notes: List[ClaimNote] = []
    flags: List[ClaimFlag] = []
    
    class Config:
        from_attributes = True

# -------------------------------
# Risk Models
# -------------------------------
class RiskFactor(BaseModel):
    name: str
    impact: float
    description: str
    category: str
    color: Optional[str] = None

class RiskAnalysis(BaseModel):
    claim_id: str
    risk_score: float
    fraud_probability: float
    factors: List[RiskFactor]
    model_confidence: float
    analyzed_at: datetime

class FraudPrediction(BaseModel):
    fraud_probability: float
    prediction: int  # 0 or 1
    risk_level: str  # low, medium, high
    model_loaded: bool
    timestamp: datetime

# -------------------------------
# Company Trust Models
# -------------------------------
class CompanyBase(BaseModel):
    hospital_id: str
    hospital_name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class CompanyTrust(CompanyBase):
    trust_score: float
    trust_level: TrustLevel
    total_claims: int
    fraud_cases: int
    flagged_cases: int
    approved_cases: int
    total_amount: float
    fraud_rate: float
    avg_risk_score: float
    risk_factors: List[Dict[str, Any]]
    last_incident: Optional[datetime] = None
    trend: str  # 'increasing', 'decreasing', 'stable'
    
    class Config:
        from_attributes = True

class CompanyTrustUpdate(BaseModel):
    trust_level: TrustLevel
    reason: str

# -------------------------------
# Dashboard Models
# -------------------------------
class DashboardStats(BaseModel):
    total_claims: int
    total_amount: float
    pending_review: int
    approved: int
    flagged: int
    fraud: int
    avg_processing_time: float
    fraud_probability: float
    today_claims: Optional[int] = 0

class FraudTrend(BaseModel):
    month: str
    amount: int

class Alert(BaseModel):
    id: str
    type: str  # 'fraud', 'flag', 'risk', 'approval'
    message: str
    time: str
    severity: str  # 'high', 'medium', 'low'

# -------------------------------
# Document Verification Models
# -------------------------------
class DocumentVerification(BaseModel):
    filename: str
    verified: bool
    hash: Optional[str] = None
    size: Optional[int] = None
    mime_type: Optional[str] = None
    issues: List[str] = []
    authenticity_score: Optional[float] = None

class BatchVerificationResult(BaseModel):
    results: List[DocumentVerification]
    total_verified: int
    total_failed: int

# -------------------------------
# Response Models
# -------------------------------
class ResponseModel(BaseModel):
    message: str
    success: bool = True
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    message: str
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[Any] = None
    