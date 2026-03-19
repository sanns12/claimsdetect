# backend/routes/claims.py

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from typing import Optional

from app.core.security import get_current_user
from app.services.claim_service import process_claim
from database import get_claims_collection

router = APIRouter(prefix="/claims", tags=["Claims"])


# ======================================================
# SUBMIT CLAIM
# ======================================================

@router.post("/submit")
async def submit_claim(
    patient_name: str = Form(...),
    age: int = Form(...),
    gender: str = Form("M"),
    claim_amount: float = Form(...),
    admission_date: str = Form(...),
    discharge_date: str = Form(...),
    billed_items_count: int = Form(0),
    previous_claims_count: int = Form(0),
    doc_missing_flag: int = Form(0),
    supporting_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):

    claim_data = {
        "patient_name": patient_name,
        "age": age,
        "gender": gender,
        "claim_amount": claim_amount,
        "admission_date": admission_date,
        "discharge_date": discharge_date,
        "billed_items_count": billed_items_count,
        "previous_claims_count": previous_claims_count,
        "doc_missing_flag": doc_missing_flag,
        "user_id": current_user["id"]  # from DB user object
    }

    return await process_claim(claim_data, supporting_file)


# ======================================================
# GET CLAIMS (User Scope)
# ======================================================

@router.get("/")
async def get_claims(
    status: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    claims_collection = await get_claims_collection()

    query = {"user_id": current_user["id"]}

    if status:
        query["status"] = status

    claims = claims_collection.find(query, limit=limit)

    formatted = [
        {
            "id": f"CLM{c['id']:03d}",
            "patient_name": c["patient_name"],
            "amount": c["claim_amount"],
            "status": c["status"],
            "risk_score": c.get("risk_score", 0),
            "created_at": c["created_at"]
        }
        for c in claims
    ]

    return {
        "claims": formatted,
        "total": len(formatted)
    }


# ======================================================
# GET SINGLE CLAIM (User Scope)
# ======================================================

@router.get("/{claim_id}")
async def get_claim(
    claim_id: str,
    current_user: dict = Depends(get_current_user)
):
    claims_collection = await get_claims_collection()

    if claim_id.startswith("CLM"):
        try:
            claim_num = int(claim_id[3:])
        except:
            raise HTTPException(status_code=400, detail="Invalid claim ID")
    else:
        try:
            claim_num = int(claim_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid claim ID")

    claim = claims_collection.find_one({
        "id": claim_num,
        "user_id": current_user["id"]
    })

    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found")

    return {
        "id": f"CLM{claim['id']:03d}",
        "patient_name": claim["patient_name"],
        "age": claim["age"],
        "admission_date": claim["admission_date"],
        "discharge_date": claim["discharge_date"],
        "duration_days": claim["duration_days"],
        "claim_amount": claim["claim_amount"],
        "status": claim["status"],
        "risk_score": claim.get("risk_score", 0),
        "fraud_probability": claim.get("fraud_probability", 0),
        "factors": claim.get("lime_explanation", []),
        "created_at": claim["created_at"]
    }