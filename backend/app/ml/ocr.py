# backend/ml/ocr.py

import io
from typing import Optional
import pdfplumber
from PIL import Image
import pytesseract


MAX_FILE_SIZE_MB = 10


def extract_text_from_file(
    file_bytes: bytes,
    filename: str,
    content_type: str
) -> str:
    """
    Extract text from uploaded document.
    Supports:
        - PDF
        - PNG / JPEG
        - Plain text
    """

    if not file_bytes:
        raise ValueError("Empty file")

    file_size_mb = len(file_bytes) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise ValueError("File too large")

    text = ""

    try:
        if content_type == "application/pdf":
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

        elif content_type in ["image/png", "image/jpeg", "image/jpg"]:
            image = Image.open(io.BytesIO(file_bytes))
            text = pytesseract.image_to_string(image)

        elif content_type == "text/plain":
            text = file_bytes.decode("utf-8", errors="ignore")

        else:
            raise ValueError(f"Unsupported file format: {content_type}")

    except Exception as e:
        raise ValueError(f"OCR extraction failed: {str(e)}")

    return clean_extracted_text(text)


def clean_extracted_text(text: str) -> str:
    """
    Basic cleanup to normalize OCR output.
    """
    if not text:
        return ""

    # Normalize whitespace
    text = text.replace("\r", " ")
    text = text.replace("\t", " ")
    text = " ".join(text.split())

    return text.strip()
