from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, Form
from typing import List, Optional, Dict, Any
from datetime import datetime
from auth import get_current_user
from document_validator import validate_claim_against_document
from ocr_util import extract_text_from_file
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
    patient_id: str = Form(...),
    patient_name: str = Form(...),
    age: int = Form(...),
    gender: str = Form(...),
    disease: str = Form(...),
    procedure: str = Form(...),
    admission_date: str = Form(...),
    discharge_date: str = Form(...),
    claim_amount: float = Form(...),
    hospital_name: str = Form(...),
    doctor_name: str = Form(...),
    insurance_provider: str = Form(...),
    policy_number: str = Form(...),
    supporting_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    
    """Submit a new claim with document"""
    
    print(f"📝 Submitting claim for patient: {patient_name}")
    print(f"💰 Claim amount: ${claim_amount}")
    print(f"📄 File received: {supporting_file.filename}")
    print(f"📄 Content type: {supporting_file.content_type}")
    
    try:
        # Save the uploaded file temporarily
        file_path = UPLOAD_DIR / supporting_file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(supporting_file.file, buffer)
        
        print(f"✅ File saved to: {file_path}")
        
        # Read file bytes for OCR
        file_bytes = file_path.read_bytes()
        
        # Extract text from the uploaded file using OCR utility
        extracted_text = ""
        mismatch_warnings = []
        
        try:
            # Determine content type from file extension
            file_ext = file_path.suffix.lower()
            
            # Map extensions to content types
            if file_ext == '.pdf':
                content_type = 'application/pdf'
            elif file_ext in ['.jpg', '.jpeg']:
                content_type = 'image/jpeg'
            elif file_ext == '.png':
                content_type = 'image/png'
            elif file_ext == '.txt':
                content_type = 'text/plain'
            else:
                content_type = supporting_file.content_type
            
            # Extract text using the OCR utility
            extracted_text = extract_text_from_file(file_bytes, supporting_file.filename, content_type)
            print(f"✅ Extracted text length: {len(extracted_text)} characters")
            print(f"📝 Extracted text preview: {extracted_text[:200]}...")
            
            # Only validate if we got some text
            if extracted_text and len(extracted_text.strip()) > 10:
                mismatch_warnings = validate_claim_against_document({
                    "claim_amount": str(claim_amount),
                    "admission_date": admission_date,
                    "discharge_date": discharge_date
                }, extracted_text)
                print(f"⚠️ Mismatch warnings: {mismatch_warnings}")
            else:
                print(f"⚠️ Not enough text extracted from document (length: {len(extracted_text)})")
                mismatch_warnings.append("Could not extract sufficient text from document")
                
        except Exception as e:
            print(f"❌ OCR/Validation failed: {e}")
            mismatch_warnings.append(f"Document processing error: {str(e)}")
        
        # Simple risk logic for faster prototype feedback
        suspicious_diseases = {"Cardiovascular", "Neurological", "Oncology", "Infectious Disease"}
        
        # Start with default risk
        risk_score = 0.0
        status = "Approved"
        fraud_score = 0.12
        document_score = 0.85
        
        # Check if there are any mismatches
        if mismatch_warnings:
            # If any mismatch warnings exist, flag the claim
            status = "Flagged"
            fraud_score = 0.8
            document_score = 0.2
            risk_score = 80
            message = "Claim submitted but document mismatches detected!"
            print(f"🚨 Mismatch detected, flagging claim: {mismatch_warnings}")
        elif claim_amount > 25000 or disease in suspicious_diseases:
            status = "Flagged"
            fraud_score = 0.72
            document_score = 0.48
            risk_score = 72
            message = "Claim submitted successfully, but this claim was flagged for review."
        else:
            status = "Approved"
            fraud_score = 0.12
            document_score = 0.85
            risk_score = 12
            message = "Claim submitted successfully"
        
        # Mock response
        new_claim = {
            "id": f"CLM{len(MOCK_CLAIMS)+1:03d}",
            "claim_id": f"CLM{len(MOCK_CLAIMS)+1:03d}",
            "claimId": f"CLM{len(MOCK_CLAIMS)+1:03d}",

            # Raw claim data
            "patient_id": patient_id,
            "patient_name": patient_name,
            "patientName": patient_name,
            "age": age,
            "gender": gender,

            "hospital_name": hospital_name,
            "hospitalName": hospital_name,
            "doctor_name": doctor_name,
            "doctorName": doctor_name,

            "insurance_provider": insurance_provider,
            "insuranceProvider": insurance_provider,
            "policy_number": policy_number,
            "policyNumber": policy_number,

            "disease": disease,
            "procedure": procedure,

            "admission_date": admission_date,
            "discharge_date": discharge_date,
            "admissionDate": admission_date,
            "dischargeDate": discharge_date,

            "amount": claim_amount,
            "claim_amount": claim_amount,
            "claimAmount": claim_amount,

            # Existing status/risk fields
            "status": status,
            "submitted_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "submittedAt": datetime.now().isoformat(),
            "lastUpdated": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d"),

            "policy_id": policy_number,
            "policyId": policy_number,

            "fraud_score": fraud_score,
            "document_score": document_score,
            "fraudScore": fraud_score,
            "documentScore": document_score,

            "message": message,
            "file_name": supporting_file.filename,
            "fileName": supporting_file.filename,
            "mismatch_warnings": mismatch_warnings,
            "risk_score": risk_score,
            "risk": risk_score,
            "extracted_text_preview": extracted_text[:500] if extracted_text else ""
        }
        # Add to mock claims for testing
        MOCK_CLAIMS.append(new_claim)
        
        return new_claim
        
    except Exception as e:
        print(f"❌ Error submitting claim: {e}")
        import traceback
        traceback.print_exc()
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