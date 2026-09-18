from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    File,
    UploadFile,
    Form,
)
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import shutil

from auth import get_current_user
from document_validator import validate_claim_against_document
from ocr_util import extract_text_from_file
from risk_engine import assess_claim


router = APIRouter()


# ============================================================
# Upload configuration
# ============================================================

UPLOAD_DIR = Path(__file__).resolve().parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# Mock claims data
# ============================================================

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
        "risk": 15,
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
        "risk": 8,
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
        "risk": 45,
    },
]


# ============================================================
# GET ALL CLAIMS
# ============================================================

@router.get("/")
async def get_claims(
    limit: int = Query(10, ge=1, le=100),
    role: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get claims list."""

    return {
        "claims": MOCK_CLAIMS[:limit],
        "total": len(MOCK_CLAIMS),
        "limit": limit,
    }


# ============================================================
# DEBUG ENDPOINT
# ============================================================

@router.get("/debug/add-test-claims")
async def add_test_claims(
    current_user: dict = Depends(get_current_user),
) -> Dict[str, str]:
    """Debug endpoint."""

    return {
        "message": "Test claims endpoint is available"
    }


# ============================================================
# GET CLAIM EXPLANATION
# ============================================================

@router.get("/{claim_id}/explain")
async def explain_claim(
    claim_id: str,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get explanation for claim decision."""

    for claim in MOCK_CLAIMS:
        if claim["id"] == claim_id or claim["claim_id"] == claim_id:

            return {
                "claim_id": claim_id,
                "explanation": (
                    "Claim was evaluated using document validation "
                    "and the fraud detection engine."
                ),
                "factors": claim.get(
                    "top_risk_factors",
                    ["No detailed risk factors available"],
                ),
                # SHAP feature contributions of the ML prediction
                # (None for claims that were not scored by the pipeline).
                "explanation_method": "SHAP",
                "shap": claim.get("shap"),
                "evidence": claim.get("evidence"),
                "recommended_action": claim.get("recommended_action"),
                "fraud_score": claim.get("fraud_score", 0),
                "risk_score": claim.get("risk_score", 0),
                "risk_band": claim.get("risk_band"),
                "document_score": claim.get("document_score", 0),
                "mismatch_warnings": claim.get(
                    "mismatch_warnings",
                    [],
                ),
            }

    raise HTTPException(
        status_code=404,
        detail="Claim not found",
    )


# ============================================================
# SUBMIT CLAIM
# ============================================================

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
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Submit a new medical claim.

    Processing pipeline:

        1. Save uploaded document
        2. Extract text using OCR/text extraction
        3. Validate claim against document
        4. Run fraud detection model
        5. Calculate document score
        6. Determine claim status
        7. Store result in MOCK_CLAIMS
        8. Return complete claim result
    """

    print("=" * 60)
    print("SUBMIT CLAIM")
    print("=" * 60)
    print(f"Patient: {patient_name}")
    print(f"Age: {age}")
    print(f"Disease: {disease}")
    print(f"Claim amount: {claim_amount}")
    print(f"Hospital: {hospital_name}")
    print(f"Admission: {admission_date}")
    print(f"Discharge: {discharge_date}")
    print(f"File: {supporting_file.filename}")
    print(f"Content type: {supporting_file.content_type}")

    # --------------------------------------------------------
    # Basic validation
    # --------------------------------------------------------

    if claim_amount < 0:
        raise HTTPException(
            status_code=400,
            detail="Claim amount cannot be negative.",
        )

    if age < 0 or age > 120:
        raise HTTPException(
            status_code=400,
            detail="Invalid patient age.",
        )

    if not supporting_file.filename:
        raise HTTPException(
            status_code=400,
            detail="Supporting document is required.",
        )

    # --------------------------------------------------------
    # Prepare variables
    # --------------------------------------------------------

    file_path: Optional[Path] = None
    extracted_text = ""
    mismatch_warnings = []

    # Default document score
    document_score = 0.85

    # Default fraud result
    fraud_score = 0.12
    risk_band = "low"
    risk_score = 12
    top_risk_factors = []

    try:

        # ====================================================
        # 1. SAVE UPLOADED FILE
        # ====================================================

        safe_filename = Path(supporting_file.filename).name

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")

        file_path = UPLOAD_DIR / f"{timestamp}_{safe_filename}"

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(
                supporting_file.file,
                buffer,
            )

        print(f"File saved: {file_path}")

        # ====================================================
        # 2. READ FILE
        # ====================================================

        file_bytes = file_path.read_bytes()

        print(f"File size: {len(file_bytes)} bytes")

        # ====================================================
        # 3. DETERMINE CONTENT TYPE
        # ====================================================

        file_ext = file_path.suffix.lower()

        if file_ext == ".pdf":
            content_type = "application/pdf"

        elif file_ext in [".jpg", ".jpeg"]:
            content_type = "image/jpeg"

        elif file_ext == ".png":
            content_type = "image/png"

        elif file_ext == ".txt":
            content_type = "text/plain"

        else:
            content_type = supporting_file.content_type

        print(f"Detected content type: {content_type}")

        # ====================================================
        # 4. OCR / TEXT EXTRACTION
        # ====================================================

        try:

            extracted_text = extract_text_from_file(
                file_bytes,
                safe_filename,
                content_type,
            )

            if extracted_text is None:
                extracted_text = ""

            print(
                f"Extracted text length: "
                f"{len(extracted_text)} characters"
            )

            if extracted_text:
                print(
                    "Extracted text preview: "
                    f"{extracted_text[:300]}"
                )

        except Exception as ocr_error:

            print(
                f"OCR/text extraction error: {ocr_error}"
            )

            mismatch_warnings.append(
                f"Document processing error: {str(ocr_error)}"
            )

            extracted_text = ""

        # ====================================================
        # 5. DOCUMENT VALIDATION
        # ====================================================

        if extracted_text.strip():

            if len(extracted_text.strip()) > 10:

                try:

                    mismatch_warnings = (
                        validate_claim_against_document(
                            {
                                "claim_amount": str(
                                    claim_amount
                                ),
                                "admission_date": admission_date,
                                "discharge_date": discharge_date,
                            },
                            extracted_text,
                        )
                    )

                    if mismatch_warnings is None:
                        mismatch_warnings = []

                    print(
                        "Document validation warnings: "
                        f"{mismatch_warnings}"
                    )

                except Exception as validation_error:

                    print(
                        "Document validation error: "
                        f"{validation_error}"
                    )

                    mismatch_warnings = [
                        "Document validation could not be completed."
                    ]

            else:

                print(
                    "Not enough text extracted from document."
                )

                mismatch_warnings = [
                    "Could not extract sufficient text from document"
                ]

        else:

            print("No text extracted from document.")

            mismatch_warnings = [
                "Could not extract text from supporting document"
            ]

        # ====================================================
        # 6. DOCUMENT SCORE
        # ====================================================

        if mismatch_warnings:

            document_score = 0.20

        else:

            document_score = 0.85

        # ====================================================
        # 7. BUILD INPUT FOR FRAUD ENGINE
        # ====================================================

        # risk_engine.assess_claim() builds the canonical feature contract
        # (see fraud_engine/feature_builder.py) from these fields.
        #
        # The claim form does not collect every field the pipeline knows
        # about.  Fields the form does not collect are passed as None
        # (unknown) - the pipeline treats them as missing rather than
        # assuming a value such as a default gender or a claim count of 0.

        fraud_claim_data = {
            "claim_amount": claim_amount,
            "patient_age": age,

            # Current form does not collect gender.
            "gender": None,

            # Current form has hospital name rather than hospital ID.
            # Kept as the provider identifier for the behavior/graph engines.
            "hospital_id": hospital_name,

            # Current form has disease rather than diagnosis code.
            "diagnosis_code": disease,

            "admission_date": admission_date,
            "discharge_date": discharge_date,

            # Current form does not collect item count.
            "billed_items_count": None,

            # Current form does not collect previous claims count.
            "previous_claims_count": None,

            # A document exists, so missing flag is 0.
            "doc_missing_flag": 0 if file_path else 1,

            # Useful metadata for future feature engineering.
            "metadata": {
                "patient_name": patient_name,
                "hospital_name": hospital_name,
                "disease": disease,
                "admission_date": admission_date,
                "discharge_date": discharge_date,
                "document_mismatch_count": len(
                    mismatch_warnings
                ),
            },
        }

        print("Fraud engine input:")
        print(fraud_claim_data)

        # ====================================================
        # 8. RUN FRAUD ENGINE
        # ====================================================

        # The pipeline (risk_engine) builds the feature contract, asks the
        # independent engines for their evidence, runs the ML model + SHAP
        # and fuses everything into one structured assessment.
        #
        # Document evidence comes from the document validation done above,
        # expressed in the document engine's output contract
        # (document_consistency_score: 1 = consistent, 0 = inconsistent).

        assessment = None

        try:

            assessment = assess_claim(
                fraud_claim_data,
                document_features={
                    "document_consistency_score": document_score,
                    "mismatch_flags": mismatch_warnings,
                },
            )

            if not isinstance(assessment, dict):

                raise ValueError(
                    "Fraud engine returned an invalid result."
                )

            # ML model output (0-1).  None when the model is unavailable.
            ml_probability = assessment.get("fraud_probability")

            # Final fused risk (0-100).  None when nothing could be assessed.
            final_risk_score = assessment.get("risk_score")

            if final_risk_score is not None:
                risk_score = int(final_risk_score)
                overall_risk = risk_score / 100
            else:
                risk_score = None
                overall_risk = None

            if ml_probability is not None:
                fraud_score = float(ml_probability)
            elif overall_risk is not None:
                fraud_score = float(overall_risk)
            else:
                fraud_score = None

            risk_band = str(
                assessment.get("risk_band") or "UNKNOWN"
            ).lower()

            top_risk_factors = assessment.get(
                "top_risk_factors",
                [],
            )

            if top_risk_factors is None:
                top_risk_factors = []

            print(
                f"Fraud score: {fraud_score}"
            )

            print(
                f"Risk band: {risk_band}"
            )

            print(
                f"Risk score: {risk_score}"
            )

            print(
                f"Risk factors: {top_risk_factors}"
            )

        except Exception as fraud_error:

            print(
                f"Fraud engine error: {fraud_error}"
            )

            # Keep the API functional if the ML engine fails.
            assessment = None
            fraud_score = 0.12
            overall_risk = 0.12
            risk_band = "low"
            risk_score = 12
            top_risk_factors = [
                "Fraud model could not be evaluated"
            ]

        # ====================================================
        # 9. DETERMINE FINAL CLAIM STATUS
        # ====================================================

        # Document mismatches take priority because the uploaded
        # document directly conflicts with submitted claim data.

        if mismatch_warnings:

            status = "Flagged"

            message = (
                "Claim submitted but document "
                "mismatches were detected."
            )

        elif overall_risk is None:

            # Nothing could be assessed automatically.
            status = "Review"

            message = (
                "Claim submitted, but automated risk assessment "
                "was unavailable. Manual review is required."
            )

        elif overall_risk >= 0.70:

            status = "Flagged"

            message = (
                "Claim submitted successfully, "
                "but the fraud detection model "
                "flagged it for review."
            )

        elif overall_risk >= 0.40:

            status = "Review"

            message = (
                "Claim submitted successfully "
                "and requires additional review."
            )

        else:

            status = "Approved"

            message = (
                "Claim submitted successfully."
            )

        # ====================================================
        # 10. CREATE CLAIM ID
        # ====================================================

        claim_number = len(MOCK_CLAIMS) + 1

        claim_id = f"CLM{claim_number:03d}"

        now = datetime.now()

        # ====================================================
        # 11. BUILD RESPONSE OBJECT
        # ====================================================

        new_claim = {
            "id": claim_id,
            "claim_id": claim_id,
            "claimId": claim_id,

            "amount": claim_amount,
            "claim_amount": claim_amount,
            "claimAmount": claim_amount,

            "age": age,

            "disease": disease,

            "admission_date": admission_date,
            "discharge_date": discharge_date,

            "admissionDate": admission_date,
            "dischargeDate": discharge_date,

            "patient_name": patient_name,
            "patientName": patient_name,

            "hospital_name": hospital_name,
            "hospitalName": hospital_name,

            "status": status,

            "date": now.strftime("%Y-%m-%d"),

            "submitted_at": now.isoformat(),
            "last_updated": now.isoformat(),

            "submittedAt": now.isoformat(),
            "lastUpdated": now.isoformat(),

            "policy_id": "POL-DEFAULT",
            "policyId": "POL-DEFAULT",

            # Fraud engine result
            "fraud_score": fraud_score,
            "fraudScore": fraud_score,

            "risk_score": risk_score,
            "risk": risk_score,

            "risk_band": risk_band,

            "top_risk_factors": top_risk_factors,

            # Evidence-based assessment (see risk_engine.assess_claim).
            # Model score, final fused risk and every evidence layer are
            # kept separate; "shap" explains the ML prediction only.
            "fraud_probability": fraud_score,
            "risk_level": (
                assessment["risk_level"] if assessment else None
            ),
            "recommended_action": (
                assessment["recommended_action"] if assessment else None
            ),
            "component_scores": (
                assessment["component_scores"] if assessment else None
            ),
            "evidence": (
                assessment["evidence"] if assessment else None
            ),
            "evidence_summary": (
                assessment["evidence_summary"] if assessment else None
            ),
            "evidence_quality": (
                assessment["evidence_quality"] if assessment else None
            ),
            "fusion": (
                assessment["fusion"] if assessment else None
            ),
            "engine_status": (
                assessment["engine_status"] if assessment else None
            ),
            "shap": (
                assessment["shap"] if assessment else None
            ),

            # Document validation result
            "document_score": document_score,
            "documentScore": document_score,

            "mismatch_warnings": mismatch_warnings,

            # Document information
            "file_name": safe_filename,
            "fileName": safe_filename,

            "extracted_text_preview": (
                extracted_text[:500]
                if extracted_text
                else ""
            ),

            "message": message,
        }

        # ====================================================
        # 12. STORE CLAIM
        # ====================================================

        MOCK_CLAIMS.append(new_claim)

        print("=" * 60)
        print("CLAIM PROCESSING COMPLETE")
        print(f"Claim ID: {claim_id}")
        print(f"Status: {status}")
        print(f"Fraud score: {fraud_score}")
        print(f"Risk band: {risk_band}")
        print(f"Risk score: {risk_score}")
        print(f"Document score: {document_score}")
        print(f"Mismatches: {mismatch_warnings}")
        print("=" * 60)

        return new_claim

    except HTTPException:
        raise

    except Exception as error:

        print(
            f"Unexpected error submitting claim: {error}"
        )

        import traceback

        traceback.print_exc()

        raise HTTPException(
            status_code=500,
            detail=(
                "An unexpected error occurred while "
                f"processing the claim: {str(error)}"
            ),
        )

    finally:

        try:
            supporting_file.file.close()
        except Exception:
            pass


# ============================================================
# GET SINGLE CLAIM
# ============================================================

@router.get("/{claim_id}")
async def get_claim(
    claim_id: str,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """Get a single claim by ID."""

    for claim in MOCK_CLAIMS:

        if (
            claim["id"] == claim_id
            or claim["claim_id"] == claim_id
        ):
            return claim

    raise HTTPException(
        status_code=404,
        detail="Claim not found",
    )


# ============================================================
# DELETE CLAIM
# ============================================================

@router.delete("/{claim_id}")
async def delete_claim(
    claim_id: str,
    current_user: dict = Depends(get_current_user),
) -> Dict[str, str]:
    """Delete a claim."""

    for index, claim in enumerate(MOCK_CLAIMS):

        if (
            claim["id"] == claim_id
            or claim["claim_id"] == claim_id
        ):

            MOCK_CLAIMS.pop(index)

            return {
                "message": f"Claim {claim_id} deleted"
            }

    raise HTTPException(
        status_code=404,
        detail="Claim not found",
    )