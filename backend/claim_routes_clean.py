from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from datetime import datetime
from typing import Optional
from auth import get_current_user
from ml_model import predict_fraud
from ocr_util import extract_text_from_file
from document_validator import validate_claim_against_document

router = APIRouter(prefix="/claims", tags=["Claims"])

claims_db = []
next_id = 1


# ======================================================
# SUBMIT CLAIM (OCR + VALIDATION + ML)
# ======================================================
@router.post("/submit")
async def submit_claim(
    patient_name: str = Form(...),
    age: int = Form(...),
    claim_amount: float = Form(...),
    admission_date: str = Form(...),
    discharge_date: str = Form(...),
    supporting_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    global next_id

    try:
        # OCR
        file_bytes = await supporting_file.read()

        print("DEBUG filename:", supporting_file.filename)
        print("DEBUG content_type:", supporting_file.content_type)

        extracted_text = extract_text_from_file(
            file_bytes,
            supporting_file.filename,
            supporting_file.content_type
        )

        # ---------------------------
        # 2️⃣ Basic Validation Against OCR
        # ---------------------------
        form_data = {
            "patient_name": patient_name,
            "claim_amount": claim_amount,
            "admission_date": admission_date,
            "discharge_date": discharge_date
        }

        mismatches = validate_claim_against_document(
            form_data,
            extracted_text
        )

        if mismatches:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Document validation failed",
                    "mismatches": mismatches
                }
            )

        # ---------------------------
        # 3️⃣ Safe ML Prediction (No Undefined Variables)
        # ---------------------------
        prediction_result = predict_fraud({
            "patient_age": age,
            "gender": "M",  # temporary default
            "claimed_amount": claim_amount,
            "billed_items_count": 1,
            "previous_claims_count": 0,
            "doc_missing_flag": 0,
            "admission_date": admission_date,
            "discharge_date": discharge_date
        })

        fraud_probability = prediction_result["fraud_probability"]
        risk_score = int(fraud_probability * 100)

        if fraud_probability > 0.8:
            status = "Flagged"
        elif fraud_probability > 0.6:
            status = "AI Processing"
        else:
            status = "Submitted"

        # ---------------------------
        # 4️⃣ Calculate Duration
        # ---------------------------
        try:
            adm = datetime.fromisoformat(admission_date)
            dis = datetime.fromisoformat(discharge_date)
            duration = max((dis - adm).days, 0)
        except:
            duration = 0

        # ---------------------------
        # 5️⃣ Save Claim
        # ---------------------------
        new_claim = {
            "id": next_id,
            "claim_number": f"CLM{next_id:03d}",
            "user_id": current_user.get("_id"),
            "patient_name": patient_name,
            "age": age,
            "admission_date": admission_date,
            "discharge_date": discharge_date,
            "duration_days": duration,
            "claim_amount": claim_amount,
            "fraud_probability": fraud_probability,
            "risk_score": risk_score,
            "status": status,
            "extracted_text": extracted_text,
            "created_at": datetime.utcnow().isoformat()
        }

        claims_db.append(new_claim)
        next_id += 1

        return {
            "claimId": new_claim["claim_number"],
            "status": status,
            "message": "Claim submitted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ======================================================
# GET CLAIMS
# ======================================================
@router.get("/")
async def get_claims(
    status: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):

    user_claims = [
        c for c in claims_db
        if c.get("user_id") == current_user.get("_id")
    ]

    if status:
        user_claims = [c for c in user_claims if c["status"] == status]

    user_claims = user_claims[:limit]

    formatted = []

    for claim in user_claims:
        formatted.append({
            "id": claim["claim_number"],
            "patient_name": claim["patient_name"],
            "amount": claim["claim_amount"],
            "status": claim["status"],
            "created_at": claim["created_at"]
        })

    return {"claims": formatted, "total": len(formatted)}