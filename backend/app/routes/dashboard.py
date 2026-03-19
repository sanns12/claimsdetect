datetime# backend/routes/dashboard.py

from fastapi import APIRouter, Depends
from typing import List
from datetime import datetime
from collections import defaultdict

from app.core.security import get_current_user
from backend.app.routes import claims
from database import get_claims_collection

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# ======================================================
# DASHBOARD STATS (Role-Aware)
# ======================================================

@router.get("/stats")
async def get_dashboard_stats(
    current_user: dict = Depends(get_current_user)
):
    claims_collection = await get_claims_collection()

    # ------------------------------------
    # Scope Claims Based on Role
    # ------------------------------------
    if current_user["role"] == "user":
        query = {"user_id": current_user["id"]}
    else:
        # hospital or insurance → see all
        query = {}

    claims = list(claims_collection.find(query))
    total = len(claims)
    approved = len([c for c in claims if c["status"] == "Approved"])
    flagged = len([c for c in claims if c["status"] == "Flagged"])
    fraud = len([c for c in claims if c["status"] == "Fraud"])

    pending = len([
        c for c in claims
        if c["status"] in ["Submitted", "AI Processing", "Manual Review"]
    ])

    total_amount = sum(c.get("claim_amount", 0) for c in claims)
    today = datetime.utcnow().date().isoformat()
    today_claims = len([c for c in claims if c["created_at"].startswith(today)])
    avg_processing_time = 0  # compute from admission/discharge or leave as 0
    return {
        "total_claims": total,
        "total_amount": total_amount,
        "approved": approved,
        "flagged": flagged,
        "fraud": fraud,
        "pending_review": pending,
        "today_claims": today_claims,
        "avg_processing_time": 0,       # placeholder until you compute it
        "fraud_probability": round(fraud / total, 2) if total else 0
    }


# ======================================================
# FRAUD TRENDS (DB-Based Monthly Aggregation)
# ======================================================

@router.get("/fraud-trends")
async def get_fraud_trends(
    current_user: dict = Depends(get_current_user)
):
    claims_collection = await get_claims_collection()

    if current_user["role"] == "user":
        query = {"user_id": current_user["id"]}
    else:
        query = {}

    claims = claims_collection.find(query, limit=None)

    monthly_counts = defaultdict(int)

    for claim in claims:
        if claim["status"] in ["Flagged", "Fraud"]:
            created = datetime.fromisoformat(claim["created_at"])
            month_label = created.strftime("%b")
            monthly_counts[month_label] += 1

    # Sort months chronologically
    ordered_months = [
        "Jan","Feb","Mar","Apr","May","Jun",
        "Jul","Aug","Sep","Oct","Nov","Dec"
    ]

    result = [
        {"month": m, "amount": monthly_counts.get(m, 0)}
        for m in ordered_months
    ]

    return result


# ======================================================
# ALERTS (Dynamic)
# ======================================================

@router.get("/alerts")
async def get_recent_alerts(
    current_user: dict = Depends(get_current_user)
):
    claims_collection = await get_claims_collection()

    if current_user["role"] == "user":
        query = {"user_id": current_user["id"]}
    else:
        query = {}

    claims = claims_collection.find(query, limit=10)

    alerts = []

    for claim in claims:
        if claim["status"] in ["Flagged", "Fraud"]:
            alerts.append({
                "id": str(claim["id"]),
                "type": "fraud",
                "message": f"High risk detected - Claim CLM{claim['id']:03d}",
                "time": claim["created_at"],
                "severity": "high" if claim["status"] == "Fraud" else "medium"
            })

    return alerts