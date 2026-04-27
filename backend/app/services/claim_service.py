# backend/app/services/claim_service.py

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
    try:
        db_claims = await get_claims_collection()
        db_files = await get_claim_files_collection()
        db_history = await get_status_history_collection()

        # ------------------------------------
        # 1. Document Processing
        # ------------------------------------
        form_data = {
            "patient_name": claim_data["patient_name"],
            "claim_amount": claim_data["claim_amount"],
            "admission_date": claim_data["admission_date"],
            "discharge_date": claim_data["discharge_date"]
        }
        document_result = await process_document(supporting_file, form_data)

        # ------------------------------------
        # 2. ML Evaluation
        # ------------------------------------
        ml_result = evaluate_claim(claim_data)

        # ------------------------------------
        # 3. Insert Claim Record
        # ------------------------------------
        now = datetime.utcnow().isoformat()
        claim_number = f"CLM-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{claim_data['user_id']}"

        cursor = await db_claims.execute(
            """INSERT INTO claims (
                claim_number, user_id, patient_name, hospital_name, age, disease,
                admission_date, discharge_date, duration_days,
                claim_amount, risk_score, fraud_probability,
                status, lime_explanation, mismatch_flag,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?)""",
            (
                claim_number,
                claim_data["user_id"],
                claim_data["patient_name"],
                claim_data.get("hospital_name"),
                claim_data["age"],
                claim_data.get("disease", "General"),
                claim_data["admission_date"],
                claim_data["discharge_date"],
                ml_result["duration_days"],
                claim_data["claim_amount"],
                ml_result["risk_score"],
                ml_result["fraud_probability"],
                ml_result["status"],
                str(ml_result.get("factors", [])),
                0,
                now,
                now
            )
        )
        await db_claims.commit()
        claim_id = cursor.lastrowid

        # ------------------------------------
        # 4. Save File Metadata
        # ------------------------------------
        await db_files.execute(
            """INSERT INTO claim_files (claim_id, filename, file_path, created_at)
               VALUES (?, ?, ?, ?)""",
            (
                claim_id,
                supporting_file.filename,
                f"local_storage/{supporting_file.filename}",
                now
            )
        )
        await db_files.commit()

        # ------------------------------------
        # 5. Status History Log
        # ------------------------------------
        await db_history.execute(
            """INSERT INTO status_history (claim_id, status, changed_at)
               VALUES (?, ?, ?)""",
            (claim_id, ml_result["status"], now)
        )
        await db_history.commit()

        # ------------------------------------
        # 6. Return Response
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
    