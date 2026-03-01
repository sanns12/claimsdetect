"""
Mismatch Detector for Document Intelligence
Detects inconsistencies across documents and with claim data
"""

import re
from datetime import datetime
from typing import List, Dict, Any, Tuple
from difflib import SequenceMatcher

class MismatchDetector:
    def __init__(self, config, similarity_checker=None):
        self.config = config
        self.similarity_checker = similarity_checker
        
        # Common procedure-diagnosis pairs (simplified)
        self.valid_procedure_diagnosis_pairs = {
            # Hypertension with office visit
            ('I10', '99213'): True,
            ('I10', '99214'): True,
            ('I10', '99215'): True,
            # Diabetes with HbA1c test
            ('E11', '83036'): True,
            ('E10', '83036'): True,
            # Routine checkup
            ('Z00.00', '99385'): True,
            ('Z00.00', '99386'): True,
            # Urinary tract infection
            ('N39.0', '81000'): True,
            ('N39.0', '87086'): True,
        }
        
        # Date validation
        self.max_future_days = 30  # Can't be more than 30 days in future
        self.max_past_years = 2    # Can't be more than 2 years old
    
    def detect_all_mismatches(self, extracted_data_list: List[Dict], claim_metadata: Dict) -> List[str]:
        """
        Run all mismatch detectors on multiple documents
        
        Args:
            extracted_data_list: List of extracted data from each document
            claim_metadata: Claim metadata from orchestrator
            
        Returns:
            List of mismatch flags
        """
        mismatches = []
        
        if not extracted_data_list:
            return ["no_document_data"]
        
        # Check each document individually
        for i, data in enumerate(extracted_data_list):
            doc_mismatches = self._check_document_mismatches(data, claim_metadata)
            mismatches.extend([f"{flag}_doc{i+1}" for flag in doc_mismatches])
        
        # Check across documents
        if len(extracted_data_list) > 1:
            cross_mismatches = self._check_cross_document_mismatches(extracted_data_list)
            mismatches.extend(cross_mismatches)
        
        # Check with claim metadata
        if claim_metadata:
            claim_mismatches = self._check_with_claim_metadata(extracted_data_list, claim_metadata)
            mismatches.extend(claim_mismatches)
        
        # Remove duplicates and sort
        return sorted(list(set(mismatches)))
    
    def _check_document_mismatches(self, data: Dict, claim_metadata: Dict) -> List[str]:
        """Check mismatches within a single document"""
        mismatches = []
        
        # Check diagnosis-procedure consistency
        if self._check_diagnosis_procedure_mismatch(data):
            mismatches.append("diagnosis_procedure_mismatch")
        
        # Check date consistency
        date_mismatch = self._check_date_consistency(data)
        if date_mismatch:
            mismatches.append(date_mismatch)
        
        # Check for missing signature (simplified - check for signature keywords)
        if not self._check_signature_present(data):
            mismatches.append("missing_signature")
        
        # Check amount reasonability
        if self._check_amount_unreasonable(data, claim_metadata):
            mismatches.append("amount_unreasonable")
        
        return mismatches
    
    def _check_cross_document_mismatches(self, data_list: List[Dict]) -> List[str]:
        """Check inconsistencies across multiple documents"""
        mismatches = []
        
        # Check amounts across documents
        amounts = []
        for data in data_list:
            amounts.extend(data.get('amounts', []))
        
        if len(set(amounts)) > 1:
            mismatches.append("amount_mismatch_across_docs")
        
        # Check diagnosis codes across documents
        diag_codes = []
        for data in data_list:
            diag_codes.extend(data.get('diagnosis_codes', []))
        
        if len(set(diag_codes)) > 1:
            mismatches.append("diagnosis_mismatch_across_docs")
        
        # Check procedure codes across documents
        proc_codes = []
        for data in data_list:
            proc_codes.extend(data.get('procedure_codes', []))
        
        if len(set(proc_codes)) > 1:
            mismatches.append("procedure_mismatch_across_docs")
        
        # Check provider names across documents
        providers = [d.get('provider_name') for d in data_list if d.get('provider_name')]
        if len(set(providers)) > 1:
            mismatches.append("provider_mismatch_across_docs")
        
        # Check patient names across documents
        patients = [d.get('patient_name') for d in data_list if d.get('patient_name')]
        if len(set(patients)) > 1:
            mismatches.append("patient_mismatch_across_docs")
        
        # Check dates across documents
        all_dates = []
        for data in data_list:
            all_dates.extend(data.get('dates', []))
        
        if len(set(all_dates)) > 2:  # More than 2 different dates
            mismatches.append("multiple_dates_across_docs")
        
        return mismatches
    
    def _check_with_claim_metadata(self, data_list: List[Dict], claim_metadata: Dict) -> List[str]:
        """Check extracted data against claim metadata"""
        mismatches = []
        
        claim_amount = claim_metadata.get('claim_amount')
        if claim_amount:
            # Check if claim amount matches any extracted amount
            amounts_found = []
            for data in data_list:
                amounts_found.extend(data.get('amounts', []))
            
            if amounts_found:
                # Allow small tolerance (e.g., within 1%)
                tolerance = 0.01
                matches = any(
                    abs(amt - claim_amount) / claim_amount < tolerance 
                    for amt in amounts_found
                )
                if not matches:
                    mismatches.append("amount_mismatch_with_claim")
        
        return mismatches
    
    def _check_diagnosis_procedure_mismatch(self, data: Dict) -> bool:
        """Check if diagnosis and procedure codes are clinically consistent"""
        diagnosis_codes = data.get('diagnosis_codes', [])
        procedure_codes = data.get('procedure_codes', [])
        
        if not diagnosis_codes or not procedure_codes:
            return False
        
        # Check each diagnosis-procedure pair
        for diag in diagnosis_codes:
            for proc in procedure_codes:
                # Check if this pair is valid
                if (diag, proc) not in self.valid_procedure_diagnosis_pairs:
                    # If not in valid list, check if they're at least somewhat related
                    # This is simplified - in production, use medical code database
                    if not self._codes_related(diag, proc):
                        return True
        
        return False
    
    def _codes_related(self, diag: str, proc: str) -> bool:
        """Check if diagnosis and procedure codes might be related"""
        # Simplified - check first characters
        # e.g., I codes (circulatory) with certain procedure ranges
        diag_prefix = diag[0] if diag else ''
        proc_prefix = proc[0] if proc else ''
        
        # Very basic check - in production, use proper medical coding database
        related_pairs = {
            'I': ['9', '8'],  # Circulatory with certain procedures
            'E': ['8'],        # Endocrine with lab tests
            'J': ['9'],        # Respiratory with certain procedures
        }
        
        return proc_prefix in related_pairs.get(diag_prefix, [])
    
    def _check_date_consistency(self, data: Dict) -> str:
        """Check if dates are logical"""
        dates = data.get('dates', [])
        if not dates:
            return None
        
        try:
            current_date = datetime.now()
            
            for date_str in dates:
                # Try to parse date
                parsed_date = self._parse_date(date_str)
                if parsed_date:
                    # Check if date is in future
                    if parsed_date > current_date:
                        days_in_future = (parsed_date - current_date).days
                        if days_in_future > self.max_future_days:
                            return "future_date"
                    
                    # Check if date is too old
                    days_old = (current_date - parsed_date).days
                    if days_old > self.max_past_years * 365:
                        return "expired_date"
            
            # Check chronological order if multiple dates
            if len(dates) > 1:
                parsed_dates = [self._parse_date(d) for d in dates if self._parse_date(d)]
                if len(parsed_dates) > 1 and parsed_dates[0] > parsed_dates[1]:
                    return "date_chronology_mismatch"
            
        except:
            return "date_parsing_error"
        
        return None
    
    def _parse_date(self, date_str: str):
        """Try to parse date in various formats"""
        formats = [
            '%m/%d/%Y',
            '%m-%d-%Y',
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%b %d, %Y',
            '%B %d, %Y',
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        return None
    
    def _check_signature_present(self, data: Dict) -> bool:
        """Check if document appears to have a signature"""
        # In production, this would use image analysis
        # For now, check text for signature indicators
        text_combined = ' '.join([
            str(data.get('provider_name', '')),
            str(data.get('patient_name', '')),
        ]).upper()
        
        signature_indicators = ['SIGNATURE', 'SIGNED', 'ELECTRONICALLY SIGNED']
        
        return any(ind in text_combined for ind in signature_indicators)
    
    def _check_amount_unreasonable(self, data: Dict, claim_metadata: Dict) -> bool:
        """Check if amount seems unreasonable"""
        amounts = data.get('amounts', [])
        if not amounts:
            return False
        
        max_amount = max(amounts)
        
        # Basic reasonability checks
        if max_amount > 1000000:  # More than $1M
            return True
        
        if max_amount < 0:  # Negative amount
            return True
        
        # Check against claim amount if available
        claim_amount = claim_metadata.get('claim_amount')
        if claim_amount:
            if max_amount > claim_amount * 2:  # More than double claim
                return True
        
        return False
    
    def get_mismatch_severity(self, mismatch_flag: str) -> str:
        """Get severity level of mismatch"""
        high_severity = [
            "diagnosis_procedure_mismatch",
            "amount_mismatch_with_claim",
            "missing_signature",
            "future_date",
            "expired_date",
        ]
        
        medium_severity = [
            "amount_mismatch_across_docs",
            "diagnosis_mismatch_across_docs",
            "procedure_mismatch_across_docs",
            "provider_mismatch_across_docs",
        ]
        
        if mismatch_flag in high_severity:
            return "high"
        elif mismatch_flag in medium_severity:
            return "medium"
        else:
            return "low"