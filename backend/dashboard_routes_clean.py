from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from typing import Optional

from auth import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """Get dashboard statistics"""
    
    # Mock data based on user role
    role = current_user.get("role", "user")
    
    if role == "user":
        return {
            "total_claims": 24,
            "approved": 18,
            "flagged": 4,
            "fraud": 2,
            "pending_review": 6,
            "total_amount": 152000,
            "avg_processing_time": 2.4,
            "fraud_probability": 0.38,
            "today_claims": 3
        }
    elif role == "hospital":
        return {
            "total_claims": 156,
            "pending_review": 23,
            "approved": 98,
            "flagged": 28,
            "fraud": 7,
            "total_amount": 1200000,
            "avg_processing_time": 2.4,
            "fraud_probability": 0.38,
            "today_claims": 8
        }
    else:  # insurance
        return {
            "total_claims": 1247,
            "approved": 892,
            "flagged": 47,
            "fraud": 23,
            "pending_review": 156,
            "total_amount": 4200000,
            "avg_processing_time": 2.8,
            "fraud_probability": 0.38,
            "today_claims": 45
        }

@router.get("/fraud-trends")
async def get_fraud_trends():
    """Get fraud trends data"""
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
    """Get recent alerts"""
    return [
        {
            "id": "1",
            "type": "fraud",
            "message": "Potential fraud detected - Claim #CLM2345",
            "time": "10 min ago",
            "severity": "high"
        },
        {
            "id": "2",
            "type": "flag",
            "message": "Claim #CLM2346 flagged for review",
            "time": "25 min ago",
            "severity": "medium"
        },
        {
            "id": "3",
            "type": "risk",
            "message": "City General Hospital risk score increased",
            "time": "1 hour ago",
            "severity": "medium"
        }
    ]