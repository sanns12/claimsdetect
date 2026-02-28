"""
Main entry point for Document Intelligence Engine
"""

from .config import Config
from .document_stub import run_stub, fallback_stub

# Initialize config
config = Config()

def run(claim_id: str, document_paths: list) -> dict:
    """
    Main function called by orchestrator
    
    Args:
        claim_id: The claim ID string
        document_paths: List of paths to document files
    
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
            # Use stub for now
            result = run_stub(claim_id, document_paths)
        else:
            # TODO: Add real implementation here
            # result = real_document_processing(claim_id, document_paths)
            result = run_stub(claim_id, document_paths)
        
        print(f"✅ Document Engine result: {result}")
        return result
        
    except Exception as e:
        print(f"❌ Error in document engine: {e}")
        return fallback_stub(claim_id, document_paths)

# For testing directly
if __name__ == "__main__":
    # Test the module
    test_result = run("TEST-123", ["doc1.pdf", "doc2.jpg"])
    print("\nTest Result:", test_result)