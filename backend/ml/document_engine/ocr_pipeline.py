"""
OCR Pipeline for Document Intelligence Engine
Extracts text from PDFs and images with confidence scoring
"""

import io
import os
import cv2
import numpy as np
import pdfplumber
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
import easyocr
from typing import List, Dict, Any
import tempfile
from datetime import datetime

MAX_FILE_SIZE_MB = 10


def extract_text_from_file(
    file_bytes: bytes,
    filename: str,
    content_type: str
) -> str:
    """Extract text from uploaded document bytes for API claim submission."""
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

    except Exception as exc:
        raise ValueError(f"OCR extraction failed: {str(exc)}") from exc

    return clean_extracted_text(text)


def clean_extracted_text(text: str) -> str:
    """Normalize whitespace in OCR output before validation."""
    if not text:
        return ""

    text = text.replace("\r", " ")
    text = text.replace("\t", " ")
    text = " ".join(text.split())
    return text.strip()


class OCRPipeline:
    def __init__(self, config):
        self.config = config
        # Initialize EasyOCR reader (supports English + medical terms)
        self.reader = easyocr.Reader(['en'], gpu=False)  # Set gpu=True if you have CUDA
        self.supported_formats = ['.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.bmp']
        
    def extract_text(self, document_path: str) -> Dict[str, Any]:
        """
        Extract text from document with confidence scores
        
        Args:
            document_path: Path to PDF or image file
            
        Returns:
            dict: {
                "text": extracted text,
                "confidence": average confidence score,
                "pages": number of pages,
                "word_confidences": list of (word, confidence),
                "processing_time": time taken in seconds
            }
        """
        start_time = datetime.now()
        
        try:
            # Check if file exists
            if not os.path.exists(document_path):
                return self._error_result(f"File not found: {document_path}")
            
            # Check file extension
            file_ext = os.path.splitext(document_path)[1].lower()
            if file_ext not in self.supported_formats:
                return self._error_result(f"Unsupported format: {file_ext}")
            
            # Process based on file type
            if file_ext == '.pdf':
                result = self._process_pdf(document_path)
            else:
                result = self._process_image(document_path)
            
            # Add processing time
            result['processing_time'] = (datetime.now() - start_time).total_seconds()
            
            # Log success
            print(f"✅ OCR successful: {document_path}")
            print(f"   Pages: {result['pages']}, Confidence: {result['confidence']:.2f}")
            
            return result
            
        except Exception as e:
            print(f"❌ OCR failed for {document_path}: {str(e)}")
            return self._low_quality_fallback(document_path)
    
    def _process_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """Process PDF file - convert to images then OCR"""
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300)  # Higher DPI for better OCR
            all_text = []
            all_confidences = []
            all_word_details = []
            
            for page_num, image in enumerate(images, 1):
                # Convert PIL image to numpy array (OpenCV format)
                img_array = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                
                # Preprocess image for better OCR
                processed_img = self._preprocess_image(img_array)
                
                # Perform OCR
                result = self.reader.readtext(processed_img)
                
                # Extract text and confidences
                page_text = []
                page_confidences = []
                page_words = []
                
                for detection in result:
                    text = detection[1]
                    confidence = detection[2]
                    bbox = detection[0]
                    
                    page_text.append(text)
                    page_confidences.append(confidence)
                    page_words.append({
                        'text': text,
                        'confidence': confidence,
                        'bbox': bbox,
                        'page': page_num
                    })
                
                all_text.extend(page_text)
                all_confidences.extend(page_confidences)
                all_word_details.extend(page_words)
            
            # Combine results
            full_text = ' '.join(all_text)
            avg_confidence = np.mean(all_confidences) if all_confidences else 0
            
            return {
                "text": full_text,
                "confidence": float(avg_confidence),
                "pages": len(images),
                "word_confidences": all_word_details,
                "method": "pdf_ocr"
            }
            
        except Exception as e:
            print(f"PDF processing error: {e}")
            raise
    
    def _process_image(self, image_path: str) -> Dict[str, Any]:
        """Process single image file"""
        try:
            # Read image
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"Could not read image: {image_path}")
            
            # Preprocess
            processed_img = self._preprocess_image(img)
            
            # Perform OCR
            result = self.reader.readtext(processed_img)
            
            # Extract text and confidences
            text_pieces = []
            confidences = []
            word_details = []
            
            for detection in result:
                text = detection[1]
                confidence = detection[2]
                bbox = detection[0]
                
                text_pieces.append(text)
                confidences.append(confidence)
                word_details.append({
                    'text': text,
                    'confidence': confidence,
                    'bbox': bbox,
                    'page': 1
                })
            
            full_text = ' '.join(text_pieces)
            avg_confidence = np.mean(confidences) if confidences else 0
            
            return {
                "text": full_text,
                "confidence": float(avg_confidence),
                "pages": 1,
                "word_confidences": word_details,
                "method": "image_ocr"
            }
            
        except Exception as e:
            print(f"Image processing error: {e}")
            raise
    
    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR accuracy"""
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Denoise
            denoised = cv2.fastNlMeansDenoising(gray, h=30)
            
            # Increase contrast
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # Thresholding for better text extraction
            _, thresh = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            return thresh
            
        except Exception as e:
            print(f"Preprocessing error: {e}")
            return image  # Return original if preprocessing fails
    
    def _low_quality_fallback(self, document_path: str) -> Dict[str, Any]:
        """Enhanced fallback for low-quality documents"""
        try:
            print(f"⚠️ Using fallback OCR for: {document_path}")
            
            file_ext = os.path.splitext(document_path)[1].lower()
            
            if file_ext == '.pdf':
                # Try with lower DPI but more preprocessing
                images = convert_from_path(document_path, dpi=200)
                all_text = []
                
                for image in images:
                    img_array = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                    
                    # Aggressive preprocessing for low quality
                    gray = cv2.cvtColor(img_array, cv2.COLOR_BGR2GRAY)
                    _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
                    
                    # Try with different OCR settings
                    result = self.reader.readtext(thresh, paragraph=True)
                    
                    for detection in result:
                        all_text.append(detection[1])
                
                text = ' '.join(all_text)
                
                return {
                    "text": text,
                    "confidence": 0.45,  # Lower confidence for fallback
                    "pages": len(images),
                    "word_confidences": [],
                    "method": "fallback_pdf",
                    "fallback_used": True
                }
            else:
                # Image fallback
                img = cv2.imread(document_path)
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                _, thresh = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY)
                
                result = self.reader.readtext(thresh, paragraph=True)
                text = ' '.join([r[1] for r in result])
                
                return {
                    "text": text,
                    "confidence": 0.4,
                    "pages": 1,
                    "word_confidences": [],
                    "method": "fallback_image",
                    "fallback_used": True
                }
                
        except Exception as e:
            print(f"Fallback OCR failed: {e}")
            return self._error_result("OCR failed completely")
    
    def _error_result(self, error_msg: str) -> Dict[str, Any]:
        """Return error result"""
        return {
            "text": "",
            "confidence": 0.0,
            "pages": 0,
            "word_confidences": [],
            "error": error_msg,
            "method": "error"
        }
    
    def extract_batch(self, document_paths: List[str]) -> List[Dict[str, Any]]:
        """Process multiple documents"""
        results = []
        for path in document_paths:
            result = self.extract_text(path)
            results.append(result)
        return results