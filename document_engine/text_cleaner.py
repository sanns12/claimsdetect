"""
Text Cleaner for Document Intelligence Engine
Normalizes and cleans extracted text from OCR
"""

import re
from typing import List, Dict, Any
import unicodedata

class TextCleaner:
    def __init__(self):
        # Common medical terms and abbreviations
        self.medical_abbreviations = {
            'pt': 'patient',
            'dx': 'diagnosis',
            'rx': 'prescription',
            'hx': 'history',
            'fx': 'fracture',
            'sob': 'shortness of breath',
            'htn': 'hypertension',
            'dm': 'diabetes mellitus',
            'cad': 'coronary artery disease',
            'mi': 'myocardial infarction',
            'cva': 'cerebrovascular accident',
            'tia': 'transient ischemic attack',
            'uti': 'urinary tract infection',
            'copd': 'chronic obstructive pulmonary disease',
            'gerd': 'gastroesophageal reflux disease',
        }
        
        # Patterns to clean
        self.clean_patterns = [
            (r'\s+', ' '),  # Multiple spaces to single
            (r'[^\x00-\x7F]+', ''),  # Remove non-ASCII
            (r'(\d+)[.,](\d+)', r'\1.\2'),  # Fix decimal numbers
            (r'[^\w\s\$\.,\-\(\)/]', ''),  # Keep only useful characters
        ]
    
    def normalize(self, raw_text: str) -> str:
        """
        Clean and normalize extracted text
        
        Args:
            raw_text: Raw text from OCR
            
        Returns:
            Cleaned and normalized text
        """
        if not raw_text:
            return ""
        
        text = raw_text
        
        # Normalize unicode characters
        text = unicodedata.normalize('NFKD', text)
        
        # Apply cleaning patterns
        for pattern, replacement in self.clean_patterns:
            text = re.sub(pattern, replacement, text)
        
        # Convert to uppercase for consistency
        text = text.upper()
        
        # Expand common abbreviations
        text = self._expand_abbreviations(text)
        
        # Fix common OCR errors
        text = self._fix_ocr_errors(text)
        
        return text.strip()
    
    def _expand_abbreviations(self, text: str) -> str:
        """Expand medical abbreviations"""
        words = text.split()
        expanded_words = []
        
        for word in words:
            word_clean = word.lower().strip('.,;:()')
            if word_clean in self.medical_abbreviations:
                # Keep original but add expanded in parentheses
                expanded_words.append(f"{word}({self.medical_abbreviations[word_clean].upper()})")
            else:
                expanded_words.append(word)
        
        return ' '.join(expanded_words)
    
    def _fix_ocr_errors(self, text: str) -> str:
        """Fix common OCR mistakes"""
        # Fix number/letter confusion
        text = re.sub(r'\b0\b', 'O', text)
        text = re.sub(r'\b1\b', 'I', text)
        text = re.sub(r'\b5\b', 'S', text)
        
        # Fix common OCR typos
        replacements = {
            'C1aim': 'Claim',
            'P0licy': 'Policy',
            'D1agnosis': 'Diagnosis',
            'Pr0cedure': 'Procedure',
            'Pat1ent': 'Patient',
            'Phys1cian': 'Physician',
        }
        
        for wrong, correct in replacements.items():
            text = re.sub(wrong, correct, text, flags=re.IGNORECASE)
        
        return text
    
    def extract_structured_data(self, cleaned_text: str) -> Dict[str, Any]:
        """
        Extract structured information from cleaned text
        
        Returns:
            dict: {
                "amounts": list of dollar amounts,
                "dates": list of dates,
                "diagnosis_codes": list of ICD-10 codes,
                "procedure_codes": list of CPT codes,
                "provider_name": extracted provider name,
                "patient_name": extracted patient name,
                "service_date": extracted service date
            }
        """
        data = {
            "amounts": self._extract_amounts(cleaned_text),
            "dates": self._extract_dates(cleaned_text),
            "diagnosis_codes": self._extract_diagnosis_codes(cleaned_text),
            "procedure_codes": self._extract_procedure_codes(cleaned_text),
            "provider_name": self._extract_provider(cleaned_text),
            "patient_name": self._extract_patient(cleaned_text),
            "service_date": self._extract_service_date(cleaned_text),
        }
        
        return data
    
    def _extract_amounts(self, text: str) -> List[float]:
        """Extract dollar amounts"""
        # Pattern: $123.45 or 123.45 or $123
        patterns = [
            r'\$\s*(\d+(?:\.\d{2})?)',
            r'(\d+(?:\.\d{2})?)\s*(?:USD|dollars)',
            r'TOTAL[:\s]*\$?\s*(\d+(?:\.\d{2})?)',
        ]
        
        amounts = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    amounts.append(float(match))
                except:
                    pass
        
        return list(set(amounts))  # Remove duplicates
    
    def _extract_dates(self, text: str) -> List[str]:
        """Extract dates in various formats"""
        patterns = [
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}',
        ]
        
        dates = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        
        return list(set(dates))
    
    def _extract_diagnosis_codes(self, text: str) -> List[str]:
        """Extract ICD-10 diagnosis codes"""
        # ICD-10 pattern: Letter + 2 digits + optional decimal + more digits
        patterns = [
            r'[A-Z][0-9]{2}\.[0-9]{1,2}',  # A00.0
            r'[A-Z][0-9]{2}[0-9]{1,2}',    # A000
            r'ICD10?[:\s]*([A-Z][0-9]{2}\.[0-9]{1,2})',
        ]
        
        codes = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            codes.extend([m.upper() for m in matches])
        
        return list(set(codes))
    
    def _extract_procedure_codes(self, text: str) -> List[str]:
        """Extract CPT procedure codes"""
        # CPT codes are 5 digits
        patterns = [
            r'\b\d{5}\b',
            r'CPT[:\s]*(\d{5})',
            r'PROCEDURE[:\s]*(\d{5})',
        ]
        
        codes = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            codes.extend(matches)
        
        return list(set(codes))
    
    def _extract_provider(self, text: str) -> str:
        """Extract provider/physician name"""
        patterns = [
            r'PROVIDER[:\s]*([A-Z][A-Z\s]+?)(?=\n|$)',
            r'PHYSICIAN[:\s]*([A-Z][A-Z\s]+?)(?=\n|$)',
            r'DR\.?\s*([A-Z][A-Z\s]+?)(?=\n|$)',
            r'DOCTOR[:\s]*([A-Z][A-Z\s]+?)(?=\n|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_patient(self, text: str) -> str:
        """Extract patient name"""
        patterns = [
            r'PATIENT[:\s]*([A-Z][A-Z\s]+?)(?=\n|$)',
            r'NAME[:\s]*([A-Z][A-Z\s]+?)(?=\n|$)',
            r'PT\.?\s*([A-Z][A-Z\s]+?)(?=\n|$)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_service_date(self, text: str) -> str:
        """Extract date of service"""
        patterns = [
            r'DATE OF SERVICE[:\s]*([\d/\-]+)',
            r'SERVICE DATE[:\s]*([\d/\-]+)',
            r'DOS[:\s]*([\d/\-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None