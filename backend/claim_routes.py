from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Security
from sqlalchemy.orm import Session
from typing import List

from backend.database import get_db
from backend.models import Claim, ClaimStatus, User
from backend.auth import get_current_user, require_role, security
from backend.ml_model import predict_fraud
from backend.risk_engine import calculate_risk
from backend.lime_explainer import explain_decision

router = APIRouter(
    prefix="/claims",
    tags=["Claims"],
    dependencies=[Security(security)]
)

# 1️⃣ SUBMIT NEW CLAIM
@router.post("/submit")
def submit_claim(
    company_id: int,
    documents: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["user"]))
):
    new_claim = Claim(
        user_id=current_user.id,
        company_id=company_id,
        documents=documents,
        status=ClaimStatus.SUBMITTED.value
    )

    db.add(new_claim)
    db.commit()
    db.refresh(new_claim)

    return {
        "message": "Claim submitted successfully",
        "claim_id": new_claim.claim_id,
        "status": new_claim.status
    }