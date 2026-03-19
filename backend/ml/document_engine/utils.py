"""
Utility functions for Document Engine
"""

import json
from datetime import datetime

def log_processing(claim_id: str, stage: str, details: dict):
    """Simple logging utility"""
    timestamp = datetime.now().isoformat()
    log_entry = {
        "timestamp": timestamp,
        "claim_id": claim_id,
        "stage": stage,
        "details": details
    }
    print(f"📝 LOG: {json.dumps(log_entry)}")
    return log_entry

def validate_document_path(path: str) -> bool:
    """Check if document path exists and is supported"""
    import os
    supported_formats = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp']
    
    if not os.path.exists(path):
        return False
    
    ext = os.path.splitext(path)[1].lower()
    return ext in supported_formats