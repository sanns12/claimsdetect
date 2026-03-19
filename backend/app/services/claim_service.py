# services/claim_service.py

from datetime import datetime
from fastapi import UploadFile, HTTPException

from database import (
    get_claims_collection,
    get_claim_files_collection,
    get_status_history_collection
)

from app.services.document_service import process_document
from app.services.ml_service import evaluate_claim


async def process_claim(
    claim_data: dict,
    supporting_file: UploadFile
) -> dict:
    """
    Full claim processing pipeline:
    - OCR + Validation
    - ML Risk Evaluation
    - DB persistence
    - Status history logging
    """

    try:
        claims_collection = await get_claims_collection()
        files_collection = await get_claim_files_collection()
        history_collection = await get_status_history_collection()

        # ------------------------------------
        # 1️⃣ Document Processing
        # ------------------------------------
        form_data = {
            "patient_name": claim_data["patient_name"],
            "claim_amount": claim_data["claim_amount"],
            "admission_date": claim_data["admission_date"],
            "discharge_date": claim_data["discharge_date"]
        }

        document_result = await process_document(
            supporting_file,
            form_data
        )

        # ------------------------------------
        # 2️⃣ ML Evaluation
        # ------------------------------------
        ml_result = evaluate_claim(claim_data)

        # ------------------------------------
        # 3️⃣ Create Claim Record
        # ------------------------------------
        now = datetime.utcnow().isoformat()

        claim_record = {
            "user_id": claim_data["user_id"],
            "company_id": claim_data.get("company_id"),
            "patient_name": claim_data["patient_name"],
            "hospital_name": claim_data.get("hospital_name"),
            "age": claim_data["age"],
            "disease": claim_data.get("disease", "General"),
            "admission_date": claim_data["admission_date"],
            "discharge_date": claim_data["discharge_date"],
            "duration_days": ml_result["duration_days"],
            "claim_amount": claim_data["claim_amount"],
            "risk_score": ml_result["risk_score"],
            "fraud_probability": ml_result["fraud_probability"],
            "status": ml_result["status"],
            "lime_explanation": str(ml_result.get("factors", [])),
            "mismatch_flag": 0,
            "created_at": now,
            "updated_at": now
        }

        insert_result = claims_collection.insert_one(claim_record)
        claim_id = insert_result.inserted_id

        # ------------------------------------
        # 4️⃣ Save File Metadata
        # ------------------------------------
        file_record = {
            "claim_id": claim_id,
            "file_name": supporting_file.filename,
            "file_url": f"local_storage/{supporting_file.filename}",
            "file_type": supporting_file.content_type,
            "extracted_text": document_result["document_hash"],  # store hash not raw text
            "uploaded_at": now
        }

        files_collection.insert_one(file_record)

        # ------------------------------------
        # 5️⃣ Status History Log
        # ------------------------------------
        history_collection.insert_one({
            "claim_id": claim_id,
            "old_status": "N/A",
            "new_status": ml_result["status"],
            "changed_by": claim_data["user_id"],
            "changed_at": now
        })

        # ------------------------------------
        # 6️⃣ Return API Response
        # ------------------------------------
        return {
            "claimId": f"CLM{claim_id:03d}",
            "status": ml_result["status"],
            "riskScore": ml_result["risk_score"],
            "message": "Claim submitted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Claim processing failed: {str(e)}"
        )
    