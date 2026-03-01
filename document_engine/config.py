"""
Configuration for Document Intelligence Engine
"""

class Config:
    # OCR settings
    OCR_ENGINE = "tesseract"
    OCR_CONFIDENCE_THRESHOLD = 0.6
    
    # Embedding settings
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    SIMILARITY_THRESHOLD = 0.75
    
    # Mismatch categories
    MISMATCH_TYPES = [
        "amount_mismatch",
        "diagnosis_procedure_mismatch", 
        "date_inconsistency",
        "missing_signature",
        "low_ocr_confidence",
        "provider_mismatch"
    ]
    
    # Scoring weights
    OCR_WEIGHT = 0.3
    SIMILARITY_WEIGHT = 0.5
    MISMATCH_PENALTY = 0.2
    
    # Stub mode flag (set to False when real implementation is ready)
    STUB_MODE = False
