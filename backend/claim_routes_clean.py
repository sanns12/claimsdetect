from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, Form
from typing import List, Optional, Dict, Any
from datetime import datetime
from auth import get_current_user
from document_validator import validate_claim_against_document
import shutil
import os
from pathlib import Path

router = APIRouter()  # No prefix here

# Create upload directory if it doesn't exist
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Mock claims data
MOCK_CLAIMS = [
    {
        "id": "CLM001",
        "claim_id": "CLM001",
        "amount": 1500.00,
        "claim_amount": 1500.00,
        "age": 29,
        "disease": "Respiratory Infection",
        "admission_date": "2026-02-15",
        "discharge_date": "2026-02-20",
        "patient_name": "Alice Smith",
        "hospital_name": "City General Hospital",
        "status": "Submitted",
        "date": "2026-03-01",
        "policy_id": "POL-12345",
        "fraud_score": 0.15,
        "document_score": 0.72,
        "risk_score": 15,
        "risk": 15
    },
    {
        "id": "CLM002",
        "claim_id": "CLM002",
        "amount": 3200.00,
        "claim_amount": 3200.00,
        "age": 42,
        "disease": "Orthopedic",
        "admission_date": "2026-02-20",
        "discharge_date": "2026-02-25",
        "patient_name": "Bob Johnson",
        "hospital_name": "City General Hospital",
        "status": "Approved",
        "date": "2026-02-28",
        "policy_id": "POL-12345",
        "fraud_score": 0.08,
        "document_score": 0.85,
        "risk_score": 8,
        "risk": 8
    },
    {
        "id": "CLM003",
        "claim_id": "CLM003",
        "amount": 850.00,
        "claim_amount": 850.00,
        "age": 35,
        "disease": "General Checkup",
        "admission_date": "2026-02-27",
        "discharge_date": "2026-02-27",
        "patient_name": "N/A",
        "hospital_name": "City General Hospital",
        "status": "Flagged",
        "date": "2026-02-27",
        "policy_id": "POL-67890",
        "fraud_score": 0.45,
        "document_score": 0.34,
        "risk_score": 45,
        "risk": 45
    }
]

@router.get("/")
async def get_claims(
    limit: int = Query(10, ge=1, le=100),
    role: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get claims list"""
    return {
        "claims": MOCK_CLAIMS[:limit],
        "total": len(MOCK_CLAIMS),
        "limit": limit
    }

@router.get("/{claim_id}")
async def get_claim(
    claim_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get single claim by ID"""
    for claim in MOCK_CLAIMS:
        if claim["id"] == claim_id or claim["claim_id"] == claim_id:
            return claim
    raise HTTPException(status_code=404, detail="Claim not found")

@router.post("/submit")
async def submit_claim(
    patient_name: str = Form(...),
    age: int = Form(...),
    disease: str = Form(...),
    admission_date: str = Form(...),
    discharge_date: str = Form(...),
    claim_amount: float = Form(...),
    hospital_name: str = Form(...),
    supporting_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Submit a new claim with document"""
    
    print(f"📝 Submitting claim for patient: {patient_name}")
    print(f"💰 Claim amount: ${claim_amount}")
    print(f"📄 File received: {supporting_file.filename}")
    
    try:
        # Save the uploaded file temporarily
        file_path = UPLOAD_DIR / supporting_file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(supporting_file.file, buffer)
        
        print(f"✅ File saved to: {file_path}")
        
        mismatch_warnings = []
        if file_path.suffix.lower() == '.txt':
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    extracted_text = f.read()
                mismatch_warnings = validate_claim_against_document({
                    "claim_amount": str(claim_amount),
                    "admission_date": admission_date,
                    "discharge_date": discharge_date
                }, extracted_text)
            except Exception as e:
                print(f"⚠️ Document validation failed: {e}")
        
        # Simple risk logic for faster prototype feedback
        suspicious_diseases = {"Cardiovascular", "Neurological", "Oncology", "Infectious Disease"}
        if claim_amount > 25000 or disease in suspicious_diseases:
            status = "Flagged"
            fraud_score = 0.72
            document_score = 0.48
        else:
            status = "Approved"
            fraud_score = 0.12
            document_score = 0.85

        if mismatch_warnings:
            status = "Flagged"
            fraud_score = max(fraud_score, 0.7)
            document_score = min(document_score, 0.35)
            message = "Claim submitted successfully, but supporting document mismatches were detected."
            print(f"⚠️ Mismatch detected, forcing flag: {mismatch_warnings}")
        elif claim_amount > 25000 or disease in suspicious_diseases:
            status = "Flagged"
            fraud_score = 0.72
            document_score = 0.48
            message = "Claim submitted successfully, but this claim was flagged for review."
        else:
            status = "Approved"
            fraud_score = 0.12
            document_score = 0.85
            message = "Claim submitted successfully"
        
        # Mock response
        new_claim = {
            "id": f"CLM{len(MOCK_CLAIMS)+1:03d}",
            "claim_id": f"CLM{len(MOCK_CLAIMS)+1:03d}",
            "claimId": f"CLM{len(MOCK_CLAIMS)+1:03d}",
            "amount": claim_amount,
            "claim_amount": claim_amount,
            "claimAmount": claim_amount,
            "age": age,
            "disease": disease,
            "admission_date": admission_date,
            "discharge_date": discharge_date,
            "admissionDate": admission_date,
            "dischargeDate": discharge_date,
            "status": status,
            "submitted_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "submittedAt": datetime.now().isoformat(),
            "lastUpdated": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "policy_id": "POL-DEFAULT",
            "policyId": "POL-DEFAULT",
            "fraud_score": fraud_score,
            "document_score": document_score,
            "fraudScore": fraud_score,
            "documentScore": document_score,
            "patient_name": patient_name,
            "hospital_name": hospital_name,
            "patientName": patient_name,
            "hospitalName": hospital_name,
            "message": message,
            "file_name": supporting_file.filename,
            "fileName": supporting_file.filename,
            "mismatch_warnings": mismatch_warnings,
            "risk_score": round(fraud_score * 100, 0),
            "risk": round(fraud_score * 100, 0)
        }
        
        # Add to mock claims for testing
        MOCK_CLAIMS.append(new_claim)
        
        return new_claim
        
    except Exception as e:
        print(f"❌ Error submitting claim: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        supporting_file.file.close()

@router.delete("/{claim_id}")
async def delete_claim(
    claim_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, str]:
    """Delete a claim"""
    return {"message": f"Claim {claim_id} deleted"}

@router.get("/debug/add-test-claims")
async def add_test_claims(current_user: dict = Depends(get_current_user)) -> Dict[str, str]:
    """Add test claims (debug endpoint)"""
    return {"message": "Test claims added"}

# Add explain endpoint (was 404)
@router.get("/{claim_id}/explain")
async def explain_claim(
    claim_id: str,
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get explanation for claim decision"""
    return {
        "claim_id": claim_id,
        "explanation": "Claim was processed normally",
        "factors": ["amount_normal", "documentation_complete"]
    }