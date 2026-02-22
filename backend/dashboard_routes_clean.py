from fastapi import APIRouter, Depends
from auth import get_current_user
from database import get_claims_collection

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
async def get_dashboard_stats(current_user = Depends(get_current_user)):
    claims_collection = await get_claims_collection()

    user_claims = claims_collection.find({
        "user_id": current_user["id"]
    }, limit=None)

    total = len(user_claims)

    approved = len([c for c in user_claims if c["status"] == "Approved"])
    flagged = len([c for c in user_claims if c["status"] == "Flagged"])
    fraud = len([c for c in user_claims if c["status"] == "Fraud"])
    pending = len([
        c for c in user_claims
        if c["status"] in ["Submitted", "AI Processing", "Manual Review"]
    ])

    return {
        "total_claims": total,
        "approved": approved,
        "flagged": flagged,
        "fraud": fraud,
        "pending_review": pending
    }

@router.get("/fraud-trends")
async def get_fraud_trends():
    return [
        {"month": "Jan", "amount": 45},
        {"month": "Feb", "amount": 52},
        {"month": "Mar", "amount": 38},
        {"month": "Apr", "amount": 65},
        {"month": "May", "amount": 48},
        {"month": "Jun", "amount": 72}
    ]

@router.get("/alerts")
async def get_recent_alerts():
    return [
        {
            "id": "1",
            "type": "fraud",
            "message": "Potential fraud detected - Claim #CLM2345",
            "time": "10 min ago",
            "severity": "high"
        }
    ]
