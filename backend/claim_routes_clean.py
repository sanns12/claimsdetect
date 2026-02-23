from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from datetime import datetime
from typing import Optional
from auth import get_current_user
from ml_model import predict_fraud
from ocr_util import extract_text_from_file
from document_validator import validate_claim_against_document
from database import get_claims_collection

router = APIRouter(prefix="/claims", tags=["Claims"])


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
    disease: str = Form(""),
    hospital_name: str = Form(""),
    supporting_file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
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
        except Exception:
            duration = 0

        # ---------------------------
        # 5️⃣ Save Claim
        # ---------------------------
        claims_collection = await get_claims_collection()
        now = datetime.utcnow().isoformat()

        new_claim = {
            "user_id": current_user["id"],
            "patient_name": patient_name,
            "hospital_name": hospital_name,
            "age": age,
            "disease": disease,
            "admission_date": admission_date,
            "discharge_date": discharge_date,
            "duration_days": duration,
            "claim_amount": claim_amount,
            "fraud_probability": fraud_probability,
            "risk_score": risk_score,
            "status": status,
            "mismatch_flag": 1 if mismatches else 0,
            "created_at": now,
            "updated_at": now
        }

        insert_result = claims_collection.insert_one(new_claim)
        saved_claim = claims_collection.find_one({"id": insert_result.inserted_id})
        claim_number = f"CLM{saved_claim['id']:03d}"

        return {
            "claimId": claim_number,
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
    claims_collection = await get_claims_collection()

    query = {}
    if current_user.get("role") != "insurance":
        query["user_id"] = current_user["id"]
    if status:
        query["status"] = status

    user_claims = claims_collection.find(query, limit=limit)

    formatted = []

    for claim in user_claims:
        claim_number = f"CLM{claim['id']:03d}"
        formatted.append({
            "id": claim_number,
            "claim_id": claim["id"],
            "patient_name": claim.get("patient_name", ""),
            "hospital_name": claim.get("hospital_name", ""),
            "disease": claim.get("disease", ""),
            "admission_date": claim.get("admission_date"),
            "discharge_date": claim.get("discharge_date"),
            "claim_amount": claim.get("claim_amount", 0),
            "amount": claim.get("claim_amount", 0),
            "status": claim.get("status", "Submitted"),
            "risk_score": claim.get("risk_score", 0),
            "fraud_probability": claim.get("fraud_probability", 0),
            "date": (claim.get("created_at") or "").split("T")[0],
            "created_at": claim.get("created_at", ""),
            "updated_at": claim.get("updated_at", "")
        })

    return {"claims": formatted, "total": len(formatted)}