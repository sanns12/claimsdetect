from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, Form
from typing import List, Optional, Dict, Any
from datetime import datetime
from auth import get_current_user
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
        "status": "pending",
        "date": "2026-03-01",
        "policy_id": "POL-12345",
        "fraud_score": 0.15,
        "document_score": 0.72
    },
    {
        "id": "CLM002",
        "claim_id": "CLM002",
        "amount": 3200.00,
        "status": "approved",
        "date": "2026-02-28",
        "policy_id": "POL-12345",
        "fraud_score": 0.08,
        "document_score": 0.85
    },
    {
        "id": "CLM003",
        "claim_id": "CLM003",
        "amount": 850.00,
        "status": "flagged",
        "date": "2026-02-27",
        "policy_id": "POL-67890",
        "fraud_score": 0.45,
        "document_score": 0.34
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
        
        # TODO: Call your Document Engine here
        # from document_engine.main import run as doc_run
        # doc_result = doc_run(f"CLM{len(MOCK_CLAIMS)+1:03d}", [str(file_path)], {"claim_amount": claim_amount})
        
        # TODO: Call Fraud Engine here
        # fraud_result = run_fraud_engine({"claim_id": f"CLM{len(MOCK_CLAIMS)+1:03d}", "claim_amount": claim_amount})
        
        # Mock response
        new_claim = {
            "id": f"CLM{len(MOCK_CLAIMS)+1:03d}",
            "claim_id": f"CLM{len(MOCK_CLAIMS)+1:03d}",
            "amount": claim_amount,
            "status": "pending",
            "date": datetime.now().strftime("%Y-%m-%d"),
            "policy_id": "POL-DEFAULT",
            "fraud_score": 0.15,
            "document_score": 0.72,
            "patient_name": patient_name,
            "hospital_name": hospital_name,
            "message": "Claim submitted successfully",
            "file_name": supporting_file.filename
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