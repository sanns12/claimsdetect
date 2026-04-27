# backend/app/routes/dashboard.py

from fastapi import APIRouter, Depends
from datetime import datetime
from collections import defaultdict

from app.core.security import get_current_user
from database import get_claims_collection

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


# ======================================================
# DASHBOARD STATS (Role-Aware)
# ======================================================

@router.get("/stats")
async def get_dashboard_stats(
    current_user: dict = Depends(get_current_user)
):
    db = await get_claims_collection()

    if current_user["role"] == "user":
        async with db.execute(
            "SELECT * FROM claims WHERE user_id = ?",
            (current_user["id"],)
        ) as cursor:
            claims = await cursor.fetchall()
    else:
        async with db.execute("SELECT * FROM claims") as cursor:
            claims = await cursor.fetchall()

    total = len(claims)
    approved = sum(1 for c in claims if c["status"] == "Approved")
    flagged = sum(1 for c in claims if c["status"] == "Flagged")
    fraud = sum(1 for c in claims if c["status"] == "Fraud")
    pending = sum(1 for c in claims if c["status"] in ["Submitted", "AI Processing", "Manual Review"])
    total_amount = sum(c["claim_amount"] or 0 for c in claims)
    today = datetime.utcnow().date().isoformat()
    today_claims = sum(1 for c in claims if c["created_at"] and c["created_at"].startswith(today))

    return {
        "total_claims": total,
        "total_amount": total_amount,
        "approved": approved,
        "flagged": flagged,
        "fraud": fraud,
        "pending_review": pending,
        "today_claims": today_claims,
        "avg_processing_time": 0,
        "fraud_probability": round(fraud / total, 2) if total else 0
    }


# ======================================================
# FRAUD TRENDS
# ======================================================

@router.get("/fraud-trends")
async def get_fraud_trends(
    current_user: dict = Depends(get_current_user)
):
    db = await get_claims_collection()

    if current_user["role"] == "user":
        async with db.execute(
            "SELECT status, created_at FROM claims WHERE user_id = ? AND status IN ('Flagged', 'Fraud')",
            (current_user["id"],)
        ) as cursor:
            claims = await cursor.fetchall()
    else:
        async with db.execute(
            "SELECT status, created_at FROM claims WHERE status IN ('Flagged', 'Fraud')"
        ) as cursor:
            claims = await cursor.fetchall()

    monthly_counts = defaultdict(int)
    for claim in claims:
        if claim["created_at"]:
            month_label = datetime.fromisoformat(claim["created_at"]).strftime("%b")
            monthly_counts[month_label] += 1

    ordered_months = ["Jan","Feb","Mar","Apr","May","Jun",
                      "Jul","Aug","Sep","Oct","Nov","Dec"]

    return [
        {"month": m, "amount": monthly_counts.get(m, 0)}
        for m in ordered_months
    ]


# ======================================================
# ALERTS
# ======================================================

@router.get("/alerts")
async def get_recent_alerts(
    current_user: dict = Depends(get_current_user)
):
    db = await get_claims_collection()

    if current_user["role"] == "user":
        async with db.execute(
            """SELECT * FROM claims WHERE user_id = ?
               AND status IN ('Flagged', 'Fraud')
               ORDER BY created_at DESC LIMIT 10""",
            (current_user["id"],)
        ) as cursor:
            claims = await cursor.fetchall()
    else:
        async with db.execute(
            """SELECT * FROM claims WHERE status IN ('Flagged', 'Fraud')
               ORDER BY created_at DESC LIMIT 10"""
        ) as cursor:
            claims = await cursor.fetchall()

    return [
        {
            "id": str(c["id"]),
            "type": "fraud",
            "message": f"High risk detected - Claim CLM{c['id']:03d}",
            "time": c["created_at"],
            "severity": "high" if c["status"] == "Fraud" else "medium"
        }
        for c in claims
    ]
