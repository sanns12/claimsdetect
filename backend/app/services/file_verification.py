"""
File Verification Module
Verifies uploaded documents for authenticity and integrity
"""

from fastapi import UploadFile
import hashlib
import os
import magic
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import asyncio
from PIL import Image
import io
import PyPDF2

# Constants
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.txt', '.csv', '.xlsx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_MIME_TYPES = {
    '.pdf': 'application/pdf',
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.png': 'image/png',
    '.txt': 'text/plain',
    '.csv': 'text/csv',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
}

async def verify_document(file: UploadFile) -> Dict:
    """
    Verify a document for authenticity and integrity
    
    Args:
        file: UploadFile object
        
    Returns:
        Dictionary with verification results
    """
    issues = []
    
    # Check filename and extension
    filename = file.filename
    if not filename:
        issues.append("File has no name")
        return {
            "verified": False,
            "issues": issues
        }
    
    ext = os.path.splitext(filename)[1].lower()
    
    # Check file extension
    if ext not in ALLOWED_EXTENSIONS:
        issues.append(f"File type {ext} not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")
        return {
            "verified": False,
            "issues": issues
        }
    
    # Read file content
    try:
        content = await file.read()
        file_size = len(content)
    except Exception as e:
        issues.append(f"Could not read file: {str(e)}")
        return {
            "verified": False,
            "issues": issues
        }
    
    # Check file size
    if file_size > MAX_FILE_SIZE:
        issues.append(f"File size exceeds {MAX_FILE_SIZE//(1024*1024)}MB limit")
    
    # Calculate file hash for integrity
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Check file type using magic numbers
    try:
        mime = magic.from_buffer(content[:2048], mime=True)
        expected_mime = ALLOWED_MIME_TYPES.get(ext, '')
        
        if mime != expected_mime and expected_mime:
            issues.append(f"File extension {ext} does not match actual file type {mime}")
    except Exception as e:
        issues.append(f"MIME type detection failed: {str(e)}")
    
    # Specific file type verification
    if ext == '.pdf':
        pdf_issues = await verify_pdf(content)
        issues.extend(pdf_issues)
    elif ext in ['.jpg', '.jpeg', '.png']:
        image_issues = await verify_image(content, ext)
        issues.extend(image_issues)
    elif ext == '.txt':
        text_issues = verify_text(content)
        issues.extend(text_issues)
    
    # Reset file cursor for later use
    await file.seek(0)
    
    # Calculate authenticity score
    authenticity_score = calculate_authenticity_score(issues, file_size)
    
    return {
        "verified": len(issues) == 0,
        "hash": file_hash,
        "size": file_size,
        "mime_type": mime if 'mime' in locals() else 'unknown',
        "issues": issues,
        "authenticity_score": authenticity_score,
        "filename": filename,
        "extension": ext
    }

async def verify_pdf(content: bytes) -> List[str]:
    """Verify PDF file integrity"""
    issues = []
    
    # Check PDF header
    if not content.startswith(b'%PDF'):
        issues.append("Invalid PDF format - missing PDF header")
        return issues
    
    # Check PDF structure
    try:
        pdf_file = io.BytesIO(content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        # Check if PDF is readable
        num_pages = len(pdf_reader.pages)
        if num_pages == 0:
            issues.append("PDF has no pages")
        
        # Check for encryption
        if pdf_reader.is_encrypted:
            issues.append("PDF is encrypted - cannot verify content")
            
    except Exception as e:
        issues.append(f"PDF structure verification failed: {str(e)}")
    
    return issues

async def verify_image(content: bytes, ext: str) -> List[str]:
    """Verify image file integrity"""
    issues = []
    
    try:
        img = Image.open(io.BytesIO(content))
        img.verify()  # Verify image integrity
        
        # Check image mode
        if img.mode not in ['RGB', 'RGBA', 'L']:
            issues.append(f"Unusual image color mode: {img.mode}")
            
    except Exception as e:
        issues.append(f"Image verification failed: {str(e)}")
    
    return issues

def verify_text(content: bytes) -> List[str]:
    """Verify text file integrity"""
    issues = []
    
    try:
        # Try to decode as UTF-8
        text = content.decode('utf-8')
        
        # Check for null bytes (potential binary data)
        if '\x00' in text:
            issues.append("File contains null bytes - may contain binary data")
        
        # Check for excessive special characters
        special_chars = sum(1 for c in text if ord(c) > 127)
        if special_chars > len(text) * 0.3:
            issues.append("High proportion of special characters - may be corrupted")
            
    except UnicodeDecodeError:
        issues.append("File is not valid UTF-8 text")
    except Exception as e:
        issues.append(f"Text verification failed: {str(e)}")
    
    return issues

def calculate_authenticity_score(issues: List[str], file_size: int) -> float:
    """Calculate authenticity score based on issues and file size"""
    base_score = 1.0
    
    # Deduct for issues
    base_score -= len(issues) * 0.1
    
    # Deduct for very small files (potential tampering)
    if file_size < 1024:  # Less than 1KB
        base_score -= 0.2
    elif file_size > MAX_FILE_SIZE * 0.9:  # Near size limit
        base_score -= 0.1
    
    return max(0.0, min(1.0, base_score))

async def batch_verify_documents(files: List[UploadFile]) -> Dict:
    """Verify multiple documents"""
    tasks = [verify_document(file) for file in files]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    verified_results = []
    total_verified = 0
    total_failed = 0
    
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            verified_results.append({
                "filename": files[i].filename if i < len(files) else "unknown",
                "verified": False,
                "issues": [str(result)]
            })
            total_failed += 1
        else:
            verified_results.append(result)
            if result["verified"]:
                total_verified += 1
            else:
                total_failed += 1
    
    return {
        "results": verified_results,
        "total_verified": total_verified,
        "total_failed": total_failed,
        "total_files": len(files)
    }

async def check_document_authenticity(file: UploadFile) -> Dict:
    """
    Advanced authenticity check for documents
    Detects potential forgery and tampering
    """
    
    # Basic verification first
    basic_check = await verify_document(file)
    
    if not basic_check["verified"]:
        return basic_check
    
    # Read content
    content = await file.read()
    await file.seek(0)
    
    issues = basic_check.get("issues", [])
    authenticity_indicators = []
    
    # Check for metadata that might indicate forgery
    content_str = str(content[:10000])  # Check first 10KB
    
    # Common forgery indicators
    forgery_indicators = [
        "Adobe Photoshop", "GIMP", "Canva", "Edited", "Modified",
        "Microsoft Word", "LibreOffice", "OpenOffice"
    ]
    
    for indicator in forgery_indicators:
        if indicator.encode() in content[:5000]:
            authenticity_indicators.append(f"Document may have been created/modified with {indicator}")
    
    # Check for PDF-specific forgery signs
    if file.filename.endswith('.pdf'):
        if b'/Creator (Microsoft' in content:
            authenticity_indicators.append("PDF appears to be converted from Word document")
        if b'/Producer (iText' in content or b'/Producer (iTextSharp' in content:
            authenticity_indicators.append("PDF generated by iText library - may be programmatically created")
    
    # Calculate final score
    authenticity_score = basic_check.get("authenticity_score", 1.0)
    authenticity_score -= len(authenticity_indicators) * 0.15
    
    return {
        **basic_check,
        "authenticity_indicators": authenticity_indicators,
        "authenticity_score": max(0.0, authenticity_score),
        "is_authentic": authenticity_score > 0.7
    }