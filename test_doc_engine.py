"""
Test script for document engine
Run this from the root folder: python test_doc_engine.py
"""

from document_engine import run

print("=" * 60)
print("📄 DOCUMENT INTELLIGENCE ENGINE TEST")
print("=" * 60)

# Test with sample data
claim_id = "TEST-001"
documents = ["sample_claim.pdf", "supporting_doc.jpg"]

print(f"Claim ID: {claim_id}")
print(f"Documents: {documents}")
print("-" * 60)

# Run the engine
result = run(claim_id, documents)

print("-" * 60)
print("✅ OUTPUT:")
print(f"   Document Consistency Score: {result['document_consistency_score']}")
print(f"   Mismatch Flags: {result['mismatch_flags']}")
print("=" * 60)

# Verify contract
expected_keys = ["document_consistency_score", "mismatch_flags"]
actual_keys = list(result.keys())

print("📋 CONTRACT VALIDATION:")
if actual_keys == expected_keys:
    print("   ✅ PASSED - Correct output keys")
else:
    print("   ❌ FAILED - Wrong output keys")
    print(f"      Expected: {expected_keys}")
    print(f"      Got: {actual_keys}")

print("=" * 60)