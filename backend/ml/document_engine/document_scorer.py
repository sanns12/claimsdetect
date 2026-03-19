"""
Document Scorer for Document Intelligence
Calculates final document consistency score based on all factors
"""

from typing import List, Dict, Any

class DocumentScorer:
    def __init__(self, config):
        self.config = config
        
        # Base score weights
        self.weights = {
            'ocr_confidence': 0.25,
            'embedding_similarity': 0.35,
            'field_consistency': 0.25,
            'document_completeness': 0.15,
        }
        
        # Penalties for mismatches
        self.mismatch_penalties = {
            # High severity (-30% each)
            'diagnosis_procedure_mismatch': 0.30,
            'amount_mismatch_with_claim': 0.30,
            'missing_signature': 0.25,
            'future_date': 0.30,
            'expired_date': 0.25,
            
            # Medium severity (-20% each)
            'amount_mismatch_across_docs': 0.20,
            'diagnosis_mismatch_across_docs': 0.20,
            'procedure_mismatch_across_docs': 0.20,
            'provider_mismatch_across_docs': 0.15,
            'patient_mismatch_across_docs': 0.20,
            
            # Low severity (-10% each)
            'low_ocr_confidence': 0.10,
            'low_document_similarity': 0.10,
            'date_chronology_mismatch': 0.10,
            'multiple_dates_across_docs': 0.10,
            'amount_unreasonable': 0.15,
        }
    
    def calculate_score(self, 
                       ocr_confidence: float, 
                       embedding_score: float,
                       mismatch_flags: List[str],
                       num_documents: int,
                       extracted_data: List[Dict] = None) -> Dict[str, Any]:
        """
        Calculate final document consistency score
        
        Args:
            ocr_confidence: Average OCR confidence
            embedding_score: Embedding similarity score
            mismatch_flags: List of detected mismatches
            num_documents: Number of documents processed
            extracted_data: Optional extracted structured data
            
        Returns:
            Dictionary with score and breakdown
        """
        # Start with base score from weighted components
        base_score = (
            ocr_confidence * self.weights['ocr_confidence'] +
            embedding_score * self.weights['embedding_similarity']
        )
        
        # Calculate field consistency if we have multiple documents
        field_consistency = self._calculate_field_consistency(extracted_data) if extracted_data else 1.0
        base_score += field_consistency * self.weights['field_consistency']
        
        # Calculate document completeness
        completeness = self._calculate_completeness(extracted_data, num_documents)
        base_score += completeness * self.weights['document_completeness']
        
        # Apply penalties for mismatches
        total_penalty = 0.0
        penalty_breakdown = {}
        
        for flag in mismatch_flags:
            # Remove document number suffix for penalty lookup
            clean_flag = self._clean_flag(flag)
            if clean_flag in self.mismatch_penalties:
                penalty = self.mismatch_penalties[clean_flag]
                total_penalty += penalty
                penalty_breakdown[flag] = penalty
        
        # Cap total penalty at 0.8 (can't reduce score below 0.2)
        total_penalty = min(total_penalty, 0.8)
        
        # Calculate final score
        final_score = base_score * (1 - total_penalty)
        
        # Ensure score is between 0 and 1
        final_score = max(0.0, min(1.0, final_score))
        
        # Determine risk band
        risk_band = self._get_risk_band(final_score, len(mismatch_flags))
        
        return {
            "final_score": round(final_score, 3),
            "base_score": round(base_score, 3),
            "total_penalty": round(total_penalty, 3),
            "penalty_breakdown": penalty_breakdown,
            "risk_band": risk_band,
            "components": {
                "ocr_confidence": round(ocr_confidence, 3),
                "embedding_similarity": round(embedding_score, 3),
                "field_consistency": round(field_consistency, 3),
                "completeness": round(completeness, 3),
            },
            "mismatch_count": len(mismatch_flags)
        }
    
    def _clean_flag(self, flag: str) -> str:
        """Remove document number suffix from flag"""
        import re
        return re.sub(r'_doc\d+$', '', flag)
    
    def _calculate_field_consistency(self, extracted_data: List[Dict]) -> float:
        """Calculate how consistent fields are across documents"""
        if not extracted_data or len(extracted_data) < 2:
            return 1.0
        
        consistency_scores = []
        
        # Check each field type
        fields = ['amounts', 'diagnosis_codes', 'procedure_codes', 'provider_name']
        
        for field in fields:
            values = []
            for data in extracted_data:
                val = data.get(field)
                if val:
                    if isinstance(val, list):
                        values.extend(val)
                    else:
                        values.append(val)
            
            if values:
                # Calculate uniqueness ratio
                unique_ratio = len(set(str(v) for v in values)) / len(values)
                consistency_scores.append(1 - unique_ratio)
        
        if consistency_scores:
            return sum(consistency_scores) / len(consistency_scores)
        return 1.0
    
    def _calculate_completeness(self, extracted_data: List[Dict], num_documents: int) -> float:
        """Calculate how complete the extracted data is"""
        if not extracted_data:
            return 0.0
        
        expected_fields = ['amounts', 'dates', 'diagnosis_codes', 'procedure_codes']
        total_fields = len(expected_fields) * len(extracted_data)
        filled_fields = 0
        
        for data in extracted_data:
            for field in expected_fields:
                if data.get(field):
                    filled_fields += 1
        
        # Also consider number of documents
        doc_factor = min(num_documents / 2, 1.0)  # Cap at 1.0 for 2+ docs
        
        completeness = (filled_fields / total_fields) * doc_factor if total_fields > 0 else 0
        return completeness
    
    def _get_risk_band(self, score: float, mismatch_count: int) -> str:
        """Determine risk band based on score and mismatches"""
        if score >= 0.8 and mismatch_count == 0:
            return "low"
        elif score >= 0.6 and mismatch_count <= 2:
            return "medium"
        elif score >= 0.4:
            return "high"
        else:
            return "critical"
    
    def get_decision(self, score: float, mismatch_flags: List[str]) -> str:
        """Get decision based on score and mismatches"""
        high_risk_flags = [f for f in mismatch_flags if self._get_flag_severity(f) == "high"]
        
        if score >= 0.8 and not high_risk_flags:
            return "auto_approve"
        elif score >= 0.6 and len(high_risk_flags) == 0:
            return "auto_approve"
        elif score >= 0.4 or len(high_risk_flags) <= 1:
            return "manual_review"
        else:
            return "reject"
    
    def _get_flag_severity(self, flag: str) -> str:
        """Get severity of a flag"""
        clean_flag = self._clean_flag(flag)
        penalty = self.mismatch_penalties.get(clean_flag, 0)
        
        if penalty >= 0.25:
            return "high"
        elif penalty >= 0.15:
            return "medium"
        else:
            return "low"