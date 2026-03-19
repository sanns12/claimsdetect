# services/document_service.py

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
    Returns structured document verification result.
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

        if mismatches:
            raise HTTPException(
                status_code=400,
                detail={
                    "message": "Document validation failed",
                    "mismatches": mismatches
                }
            )

        # Instead of storing raw extracted text (PHI risk),
        # store only secure hash
        document_hash = hashlib.sha256(
            extracted_text.encode()
        ).hexdigest()

        return {
            "document_verified": True,
            "document_hash": document_hash
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Document processing error: {str(e)}"
        )
    