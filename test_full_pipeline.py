"""
Full pipeline test for Document Intelligence Engine
"""

from document_engine.main import run

def test_full_pipeline():
    print("=" * 60)
    print("🧪 TESTING FULL DOCUMENT PIPELINE")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        {
            "name": "Two similar documents",
            "claim_id": "TEST-001",
            "documents": ["claim1.jpg", "claim2.jpg"],
            "metadata": {"claim_amount": 1500.00}
        },
        {
            "name": "Single document",
            "claim_id": "TEST-002",
            "documents": ["claim1.jpg"],
            "metadata": {"claim_amount": 1500.00}
        }
    ]
    
    for test in test_cases:
        print(f"\n📋 Test: {test['name']}")
        print("-" * 40)
        
        result = run(
            test['claim_id'],
            test['documents'],
            test['metadata']
        )
        
        print(f"\n✅ Result: {result}")
        print("-" * 40)
    
    print("\n" + "=" * 60)
    print("✅ All tests complete")
    print("=" * 60)

if __name__ == "__main__":
    test_full_pipeline()