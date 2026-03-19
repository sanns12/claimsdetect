"""
Main entry point for Document Intelligence Engine
"""

from .config import Config
from .ocr_pipeline import OCRPipeline
from .text_cleaner import TextCleaner
from .embedding_engine import EmbeddingEngine
from .similarity_checker import SimilarityChecker
from .mismatch_detector import MismatchDetector
from .document_scorer import DocumentScorer
from .document_stub import run_stub, fallback_stub

# Initialize config and components
config = Config()
ocr_pipeline = OCRPipeline(config)
text_cleaner = TextCleaner()
embedding_engine = EmbeddingEngine(config)
similarity_checker = SimilarityChecker(config, embedding_engine)
mismatch_detector = MismatchDetector(config, similarity_checker)
document_scorer = DocumentScorer(config)

def run(claim_id: str, document_paths: list, claim_metadata: dict = None) -> dict:
    """
    Main function called by orchestrator
    
    Args:
        claim_id: The claim ID string
        document_paths: List of paths to document files
        claim_metadata: Optional claim metadata from orchestrator
    
    Returns:
        dict: {
            "document_consistency_score": float,
            "mismatch_flags": list
        }
    """
    try:
        print(f"🔍 Document Engine processing claim: {claim_id}")
        print(f"📄 Documents: {document_paths}")
        
        if config.STUB_MODE:
            # Use stub for initial testing
            print("⚙️ Using STUB mode")
            result = run_stub(claim_id, document_paths)
        else:
            # Use real OCR + Embedding pipeline
            print("⚙️ Using REAL pipeline with full scoring")
            
            # Process all documents
            all_texts = []
            all_confidences = []
            all_structured_data = []
            
            for doc_path in document_paths:
                # Extract text with OCR
                ocr_result = ocr_pipeline.extract_text(doc_path)
                
                if ocr_result['confidence'] > 0:
                    # Clean the extracted text
                    cleaned_text = text_cleaner.normalize(ocr_result['text'])
                    all_texts.append(cleaned_text)
                    all_confidences.append(ocr_result['confidence'])
                    
                    # Extract structured data
                    structured = text_cleaner.extract_structured_data(cleaned_text)
                    all_structured_data.append(structured)
                    
                    print(f"   📝 {doc_path}: Confidence={ocr_result['confidence']:.2f}")
                else:
                    print(f"   ⚠️ {doc_path}: OCR failed")
            
            # Calculate base metrics
            if all_texts:
                # OCR confidence
                avg_confidence = sum(all_confidences) / len(all_confidences)
                
                # Embedding similarity
                if len(all_texts) >= 2:
                    consistency_metrics = similarity_checker.calculate_document_set_consistency(all_texts)
                    embedding_score = consistency_metrics['consistency_score']
                else:
                    embedding_score = avg_confidence  # Fallback for single document
                
                # Detect mismatches
                mismatch_flags = mismatch_detector.detect_all_mismatches(
                    all_structured_data, 
                    claim_metadata or {}
                )
                
                # Calculate final score using document scorer
                scoring_result = document_scorer.calculate_score(
                    ocr_confidence=avg_confidence,
                    embedding_score=embedding_score,
                    mismatch_flags=mismatch_flags,
                    num_documents=len(document_paths),
                    extracted_data=all_structured_data
                )
                
                # Get final consistency score
                document_consistency_score = scoring_result['final_score']
                
                # Add decision info for logging (not part of output contract)
                print(f"\n📊 Score Breakdown:")
                print(f"   Base Score: {scoring_result['base_score']:.3f}")
                print(f"   Penalty: {scoring_result['total_penalty']:.3f}")
                print(f"   Final Score: {scoring_result['final_score']:.3f}")
                print(f"   Risk Band: {scoring_result['risk_band']}")
                print(f"   Decision: {document_scorer.get_decision(scoring_result['final_score'], mismatch_flags)}")
                
            else:
                # No documents processed successfully
                document_consistency_score = 0.0
                mismatch_flags = ["ocr_failed"]
            
            result = {
                "document_consistency_score": round(document_consistency_score, 2),
                "mismatch_flags": mismatch_flags
            }
        
        print(f"✅ Document Engine result: {result}")
        return result
        
    except Exception as e:
        print(f"❌ Error in document engine: {e}")
        import traceback
        traceback.print_exc()
        return fallback_stub(claim_id, document_paths)

# For testing directly
if __name__ == "__main__":
    # Test the module
    test_metadata = {"claim_amount": 1500.00}
    test_result = run("TEST-123", ["claim1.jpg", "claim2.jpg"], test_metadata)
    print("\nTest Result:", test_result)