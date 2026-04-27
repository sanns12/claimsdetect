# backend/app/services/document_service.py

import hashlib
from fastapi import UploadFile, HTTPException
from ml.document_engine.ocr_pipeline import extract_text_from_file
from app.services.document_validator import validate_claim_against_document


async def process_document(
    supporting_file: UploadFile,
    form_data: dict
) -> dict:
    """
    Handles OCR extraction + validation against submitted form data.
    Mismatches are flagged but do NOT block claim submission.
    """

    try:
        # Read file bytes
        file_bytes = await supporting_file.read()

        # Extract text using OCR utility
        extracted_text = extract_text_from_file(
            file_bytes,
            supporting_file.filename,
            supporting_file.content_type
        )

        # Validate form data against OCR text
        mismatches = validate_claim_against_document(
            form_data,
            extracted_text
        )

        # Flag mismatches but don't block the claim
        mismatch_flag = 1 if mismatches else 0

        if mismatches:
            print(f"⚠️ Document mismatches detected: {mismatches}")

        # Store secure hash instead of raw text (PHI risk)
        document_hash = hashlib.sha256(
            extracted_text.encode()
        ).hexdigest()

        return {
            "document_verified": len(mismatches) == 0,
            "document_hash": document_hash,
            "mismatches": mismatches,
            "mismatch_flag": mismatch_flag
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Document processing error: {str(e)}"
        )