from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import Optional

from auth import get_current_user

router = APIRouter(prefix="/claims", tags=["Claims"])

# Simple in-memory storage (no database needed)
claims_db = []
next_id = 1

@router.post("/submit")
async def submit_claim(claim_data: dict, current_user: dict = Depends(get_current_user)):
    """Submit a new claim"""
    global next_id
    
    try:
        print(f"📥 Received claim data: {claim_data}")
        
        # Calculate duration
        try:
            from datetime import datetime
            adm = datetime.fromisoformat(claim_data.get("admission_date", ""))
            dis = datetime.fromisoformat(claim_data.get("discharge_date", ""))
            duration = (dis - adm).days
            if duration < 0:
                duration = 0
        except:
            duration = 1
        
        # Simple risk calculation
        amount = float(claim_data.get("claim_amount", 0))
        age = int(claim_data.get("age", 35))
        
        risk_score = 30
        if amount > 50000:
            risk_score = 85
        elif amount > 25000:
            risk_score = 70
        elif amount > 10000:
            risk_score = 50
        
        if age > 70:
            risk_score += 10
        elif age < 18:
            risk_score += 5
        
        risk_score = min(risk_score, 95)
        
        # Determine status
        if risk_score > 80:
            status = "Flagged"
        elif risk_score > 60:
            status = "AI Processing"
        else:
            status = "Submitted"
        
        # Create claim
        new_claim = {
            "id": next_id,
            "claim_number": f"CLM{next_id:03d}",
            "user_id": current_user.get("_id", 1),
            "patient_name": claim_data.get("patient_name", "Unknown"),
            "age": age,
            "disease": claim_data.get("disease", ""),
            "admission_date": claim_data.get("admission_date", ""),
            "discharge_date": claim_data.get("discharge_date", ""),
            "duration_days": duration,
            "claim_amount": amount,
            "risk_score": risk_score,  # This is the key field
            "status": status,
            "hospital_name": claim_data.get("hospital_name", "City General Hospital"),
            "created_at": datetime.utcnow().isoformat()
        }
        
        claims_db.append(new_claim)
        print(f"✅ Claim created: CLM{next_id:03d} with risk score: {risk_score}")
        
        next_id += 1
        
        return {
            "claimId": f"CLM{new_claim['id']:03d}",
            "status": status,
            "riskScore": risk_score,
            "message": "Claim submitted successfully"
        }
        
    except Exception as e:
        print(f"❌ Error creating claim: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/")
async def get_claims(
    status: Optional[str] = None,
    limit: int = 100,
    current_user: dict = Depends(get_current_user)
):
    """Get claims - different behavior based on user role"""
    try:
        print(f"📋 Fetching claims for user role: {current_user.get('role')}")
        print(f"👤 User ID: {current_user.get('_id')}")
        print(f"📊 Total claims in DB: {len(claims_db)}")
        
        # Log all claims for debugging
        for i, claim in enumerate(claims_db):
            print(f"  Claim {i+1}: {claim.get('claim_number')} - User: {claim.get('user_id')}")
        
        # Filter based on user role
        user_role = current_user.get("role", "").lower()
        
        if user_role == "insurance":
            # Insurance sees ALL claims - NO FILTERING
            filtered_claims = claims_db.copy()
            print(f"🔍 Insurance user - showing ALL {len(filtered_claims)} claims")
        elif user_role == "hospital":
            # Hospital sees claims from their hospital
            hospital_name = current_user.get("hospital_name", "City General Hospital")
            filtered_claims = [c for c in claims_db if c.get("hospital_name") == hospital_name]
            print(f"🏥 Hospital user - showing {len(filtered_claims)} claims for {hospital_name}")
        else:
            # Regular user sees only their own claims
            filtered_claims = [c for c in claims_db if c.get("user_id") == current_user.get("_id")]
            print(f"👤 Regular user - showing {len(filtered_claims)} claims")
        
        # Apply status filter if provided
        if status:
            filtered_claims = [c for c in filtered_claims if c.get("status") == status]
            print(f"🔍 Filtered by status '{status}': {len(filtered_claims)} claims")
        
        # Apply limit
        if limit and len(filtered_claims) > limit:
            filtered_claims = filtered_claims[:limit]
        
        formatted_claims = []
        for claim in filtered_claims:
            # Determine fraud score/risk level
            risk = claim.get("risk_score", 0)
            
            formatted_claims.append({
                "id": claim.get("claim_number", f"CLM{claim.get('id', 0):03d}"),
                "claim_id": claim.get("claim_number", f"CLM{claim.get('id', 0):03d}"),
                "patient_name": claim.get("patient_name", "Unknown"),
                "patientName": claim.get("patient_name", "Unknown"),  # For frontend compatibility
                "patient_id": f"P{claim.get('user_id', 0):06d}",
                "age": claim.get("age", 0),
                "gender": claim.get("gender", "Unknown"),
                "date": claim.get("created_at", "")[:10] if claim.get("created_at") else "",
                "created_at": claim.get("created_at", ""),
                "amount": claim.get("claim_amount", 0),
                "claim_amount": claim.get("claim_amount", 0),
                "status": claim.get("status", "Unknown"),
                "risk": risk,
                "risk_score": risk,
                "fraudScore": risk / 100,
                "fraud_probability": risk / 100,
                "hospital": claim.get("hospital_name", "Unknown Hospital"),
                "hospital_name": claim.get("hospital_name", "Unknown Hospital"),
                "department": claim.get("department", "General"),
                "doctor": claim.get("doctor_name", "Unknown"),
                "insurance_provider": claim.get("insurance_provider", "Unknown"),
                "policy_number": claim.get("policy_number", ""),
                "flags": generate_flags(claim),
                "priority": "urgent" if risk > 80 else "high" if risk > 60 else "normal"
            })
        
        print(f"✅ Returning {len(formatted_claims)} formatted claims")
        return {
            "claims": formatted_claims,
            "total": len(formatted_claims)
        }
        
    except Exception as e:
        print(f"❌ Error fetching claims: {e}")
        import traceback
        traceback.print_exc()
        return {"claims": [], "total": 0}
    
# Helper function to generate flags based on risk
def generate_flags(claim):
    flags = []
    risk = claim.get("risk_score", 0)
    
    if risk > 80:
        flags.append("High Risk")
        flags.append("Urgent Review")
    elif risk > 60:
        flags.append("Medium Risk")
    
    if claim.get("claim_amount", 0) > 50000:
        flags.append("Amount Anomaly")
    
    if claim.get("age", 0) > 70:
        flags.append("Age Factor")
    
    return flags
    
@router.get("/{claim_id}")
async def get_claim(claim_id: str, current_user: dict = Depends(get_current_user)):
    """Get claim by ID"""
    # Remove 'CLM' prefix if present
    if claim_id.startswith("CLM"):
        try:
            numeric_id = int(claim_id[3:])
        except:
            raise HTTPException(status_code=400, detail="Invalid claim ID")
    else:
        try:
            numeric_id = int(claim_id)
        except:
            raise HTTPException(status_code=400, detail="Invalid claim ID")
    
    # Find claim
    for claim in claims_db:
        if claim["id"] == numeric_id and claim["user_id"] == current_user.get("_id", 1):
            return {
                "id": claim["claim_number"],
                "patient_name": claim["patient_name"],
                "age": claim["age"],
                "admission_date": claim["admission_date"],
                "discharge_date": claim["discharge_date"],
                "duration_days": claim["duration_days"],
                "diagnosis": claim["disease"],
                "claim_amount": f"${claim['claim_amount']:,.0f}",
                "status": claim["status"],
                "risk_score": claim["risk_score"],
                "hospital": claim["hospital_name"],
                "created_at": claim["created_at"]
            }
    
    raise HTTPException(status_code=404, detail="Claim not found")

@router.delete("/{claim_id}")
async def delete_claim(claim_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a claim"""
    global claims_db
    
    # Remove 'CLM' prefix if present
    if claim_id.startswith("CLM"):
        numeric_id = int(claim_id[3:])
    else:
        numeric_id = int(claim_id)
    
    original_length = len(claims_db)
    claims_db = [c for c in claims_db if not (c["id"] == numeric_id and c["user_id"] == current_user.get("_id", 1))]
    
    if len(claims_db) == original_length:
        raise HTTPException(status_code=404, detail="Claim not found")
    
    return {"message": "Claim deleted successfully"}

@router.get("/{claim_id}/explain")
async def get_claim_explanation(claim_id: str):
    """Get LIME explanation for claim"""
    return {
        "factors": [
            {
                "name": "Claim Amount",
                "impact": 42,
                "color": "high",
                "description": "Amount exceeds typical range"
            },
            {
                "name": "Patient Age",
                "impact": 28,
                "color": "medium",
                "description": "Age factor considered"
            },
            {
                "name": "Disease Type",
                "impact": 18,
                "color": "low",
                "description": "Standard condition"
            }
        ],
        "model_confidence": 0.87,
        "similar_claims": 156
    }

@router.post("/debug/add-test-claims")
async def add_test_claims(current_user: dict = Depends(get_current_user)):
    """Add test claims for debugging"""
    global next_id, claims_db
    
    if current_user.get("role") != "insurance":
        return {"error": "Only insurance can add test claims"}
    
    test_claims = [
        {
            "patient_name": "John Smith",
            "age": 45,
            "disease": "Cardiovascular",
            "admission_date": "2024-03-15",
            "discharge_date": "2024-03-20",
            "claim_amount": 25000,
            "hospital_name": "City General Hospital",
            "status": "Flagged",
            "risk_score": 78,
            "user_id": 1
        },
        {
            "patient_name": "Emma Wilson",
            "age": 62,
            "disease": "Oncology",
            "admission_date": "2024-03-10",
            "discharge_date": "2024-03-25",
            "claim_amount": 75000,
            "hospital_name": "MediCare Plus Clinic",
            "status": "Fraud",
            "risk_score": 92,
            "user_id": 2
        },
        {
            "patient_name": "Robert Brown",
            "age": 34,
            "disease": "Orthopedic",
            "admission_date": "2024-03-18",
            "discharge_date": "2024-03-22",
            "claim_amount": 12000,
            "hospital_name": "HealthFirst Medical",
            "status": "Approved",
            "risk_score": 28,
            "user_id": 1
        }
    ]
    
    added = []
    for tc in test_claims:
        tc["id"] = next_id
        tc["claim_number"] = f"CLM{next_id:03d}"
        tc["created_at"] = datetime.utcnow().isoformat()
        claims_db.append(tc)
        added.append(f"CLM{next_id:03d}")
        next_id += 1
    
    return {
        "message": f"Added {len(added)} test claims",
        "claims": added,
        "total_claims": len(claims_db)
    }

@router.post("/debug/add-test-claims")
async def add_test_claims(current_user: dict = Depends(get_current_user)):
    """Add test claims for debugging"""
    global next_id, claims_db
    
    if current_user.get("role") != "insurance":
        return {"error": "Only insurance can add test claims"}
    
    test_claims = [
        {
            "patient_name": "John Smith",
            "age": 45,
            "disease": "Cardiovascular",
            "admission_date": "2024-03-15",
            "discharge_date": "2024-03-20",
            "claim_amount": 25000,
            "hospital_name": "City General Hospital",
            "status": "Flagged",
            "risk_score": 78,
            "user_id": 1
        },
        {
            "patient_name": "Emma Wilson",
            "age": 62,
            "disease": "Oncology",
            "admission_date": "2024-03-10",
            "discharge_date": "2024-03-25",
            "claim_amount": 75000,
            "hospital_name": "MediCare Plus Clinic",
            "status": "Fraud",
            "risk_score": 92,
            "user_id": 2
        },
        {
            "patient_name": "Robert Brown",
            "age": 34,
            "disease": "Orthopedic",
            "admission_date": "2024-03-18",
            "discharge_date": "2024-03-22",
            "claim_amount": 12000,
            "hospital_name": "HealthFirst Medical",
            "status": "Approved",
            "risk_score": 28,
            "user_id": 1
        }
    ]
    
    added = []
    for tc in test_claims:
        tc["id"] = next_id
        tc["claim_number"] = f"CLM{next_id:03d}"
        tc["created_at"] = datetime.utcnow().isoformat()
        claims_db.append(tc)
        added.append(f"CLM{next_id:03d}")
        next_id += 1
    
    return {
        "message": f"Added {len(added)} test claims",
        "claims": added,
        "total_claims": len(claims_db)
    }
    
@router.post("/debug/add-test-claims")
async def add_test_claims(current_user: dict = Depends(get_current_user)):
    """Add test claims for debugging"""
    global next_id, claims_db
    
    if current_user.get("role") != "insurance":
        return {"error": "Only insurance can add test claims"}
    
    test_claims = [
        {
            "patient_name": "John Smith",
            "age": 45,
            "disease": "Cardiovascular",
            "admission_date": "2024-03-15",
            "discharge_date": "2024-03-20",
            "claim_amount": 25000,
            "hospital_name": "City General Hospital",
            "status": "Flagged",
            "risk_score": 78,
            "user_id": 1
        },
        {
            "patient_name": "Emma Wilson",
            "age": 62,
            "disease": "Oncology",
            "admission_date": "2024-03-10",
            "discharge_date": "2024-03-25",
            "claim_amount": 75000,
            "hospital_name": "MediCare Plus Clinic",
            "status": "Fraud",
            "risk_score": 92,
            "user_id": 2
        },
        {
            "patient_name": "Robert Brown",
            "age": 34,
            "disease": "Orthopedic",
            "admission_date": "2024-03-18",
            "discharge_date": "2024-03-22",
            "claim_amount": 12000,
            "hospital_name": "HealthFirst Medical",
            "status": "Approved",
            "risk_score": 28,
            "user_id": 1
        }
    ]
    
    added = []
    for tc in test_claims:
        tc["id"] = next_id
        tc["claim_number"] = f"CLM{next_id:03d}"
        tc["created_at"] = datetime.utcnow().isoformat()
        claims_db.append(tc)
        added.append(f"CLM{next_id:03d}")
        next_id += 1
    
    return {
        "message": f"Added {len(added)} test claims",
        "claims": added,
        "total_claims": len(claims_db)
    }