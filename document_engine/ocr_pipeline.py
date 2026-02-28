"""
OCR Pipeline - Will be implemented in Day 2
"""

class OCRPipeline:
    def __init__(self, config):
        self.config = config
    
    def extract_text(self, document_path: str) -> dict:
        """Placeholder for OCR extraction"""
        return {
            "text": "Sample extracted text",
            "confidence": 0.85,
            "pages": 1
        }