from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, timedelta
#from bson import ObjectId

from database import get_companies_collection, get_claims_collection
from auth import get_current_user
from models import CompanyTrust, TrustLevel
# Import ML model
from ml_model import predict_fraud

router = APIRouter(prefix="/companies", tags=["Companies"])

async def calculate_trust_score(hospital_id: str) -> dict:
    """Calculate trust score for a hospital"""
    claims = await get_claims_collection()
    
    # Get all claims for this hospital in last 12 months
    year_ago = datetime.utcnow() - timedelta(days=365)
    
    pipeline = [
        {
            "$match": {
                "hospital_id": hospital_id,
                "submitted_at": {"$gte": year_ago}
            }
        },
        {
            "$group": {
                "_id": None,
                "total_claims": {"$sum": 1},
                "fraud_cases": {
                    "$sum": {"$cond": [{"$eq": ["$status", "Fraud"]}, 1, 0]}
                },
                "flagged_cases": {
                    "$sum": {"$cond": [{"$eq": ["$status", "Flagged"]}, 1, 0]}
                },
                "approved_cases": {
                    "$sum": {"$cond": [{"$eq": ["$status", "Approved"]}, 1, 0]}
                },
                "total_amount": {"$sum": "$claim_amount"},
                "avg_risk": {"$avg": "$risk_score"},
                "avg_ml_fraud_probability": {"$avg": "$fraud_probability"}  # Add ML average
            }
        }
    ]
    
    cursor = claims.aggregate(pipeline)
    stats = await cursor.to_list(length=1)
    
    if not stats or not stats[0]:
        # No claims in last year
        return {
            "total_claims": 0,
            "fraud_cases": 0,
            "flagged_cases": 0,
            "approved_cases": 0,
            "total_amount": 0,
            "avg_risk": 0,
            "avg_ml_fraud_probability": 0
        }
    
    return stats[0]

def determine_trust_level(trust_score: float) -> TrustLevel:
    """Determine trust level based on score"""
    if trust_score >= 80:
        return TrustLevel.GREEN
    elif trust_score >= 60:
        return TrustLevel.YELLOW
    else:
        return TrustLevel.BLACK

def calculate_trend(historical_scores: List[float]) -> str:
    """Calculate trend based on historical scores"""
    if len(historical_scores) < 2:
        return "stable"
    
    recent_avg = sum(historical_scores[-3:]) / len(historical_scores[-3:])
    previous_avg = sum(historical_scores[:-3]) / len(historical_scores[:-3]) if historical_scores[:-3] else recent_avg
    
    if recent_avg > previous_avg * 1.1:
        return "increasing"
    elif recent_avg < previous_avg * 0.9:
        return "decreasing"
    else:
        return "stable"

@router.get("/")
async def get_all_companies(
    limit: int = 50,
    skip: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get all companies with trust scores"""
    companies = await get_companies_collection()
    
    cursor = companies.find().skip(skip).limit(limit)
    results = await cursor.to_list(length=limit)
    
    formatted_companies = []
    for company in results:
        # Calculate trust score based on claims
        stats = await calculate_trust_score(company["hospital_id"])
        
        fraud_rate = (stats["fraud_cases"] / stats["total_claims"] * 100) if stats["total_claims"] > 0 else 0
        
        # Calculate trust score - now using ML probabilities
        base_score = 100
        
        # Deduct based on actual fraud cases
        base_score -= fraud_rate * 2
        
        # Deduct based on flagged cases
        base_score -= (stats["flagged_cases"] / max(stats["total_claims"], 1)) * 10
        
        # Deduct based on average ML fraud probability
        if stats.get("avg_ml_fraud_probability", 0) > 0:
            ml_deduction = stats["avg_ml_fraud_probability"] * 30  # Scale ML impact
            base_score -= ml_deduction
        
        base_score = max(min(base_score, 100), 0)  # Clamp between 0-100
        
        trust_level = determine_trust_level(base_score)
        
        # Get historical scores for trend (mock data for now)
        historical_scores = [base_score * (0.9 + i * 0.02) for i in range(5)]
        trend = calculate_trend(historical_scores)
        
        formatted_companies.append({
            "id": company["hospital_id"],
            "name": company["hospital_name"],
            "address": company.get("address", ""),
            "trustScore": round(base_score, 1),
            "trustLevel": trust_level.value,
            "totalClaims": stats["total_claims"],
            "totalAmount": f"${stats['total_amount']:,.0f}" if stats['total_amount'] else "$0",
            "fraudCases": stats["fraud_cases"],
            "fraudRate": f"{fraud_rate:.1f}%",
            "flaggedClaims": stats["flagged_cases"],
            "approvedClaims": stats["approved_cases"],
            "avgMLFraudProbability": f"{stats.get('avg_ml_fraud_probability', 0)*100:.1f}%" if stats.get('avg_ml_fraud_probability') else "0%",
            "avgProcessingTime": "2.4 days",  # Mock data
            "riskTrend": trend,
            "lastIncident": (datetime.utcnow() - timedelta(days=7)).strftime("%Y-%m-%d") if stats["fraud_cases"] > 0 else None,
            "riskFactors": [
                {"name": "ML Fraud Score", "score": round((1 - stats.get('avg_ml_fraud_probability', 0)) * 100, 1)},
                {"name": "Documentation Quality", "score": round(base_score * 0.95, 1)},
                {"name": "Billing Accuracy", "score": round(base_score * 0.92, 1)},
                {"name": "Claim Pattern", "score": round(base_score * 0.88, 1)}
            ]
        })
    
    return formatted_companies

@router.get("/{company_id}")
async def get_company_by_id(
    company_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get company by ID with detailed trust info"""
    companies = await get_companies_collection()
    
    company = await companies.find_one({"hospital_id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    stats = await calculate_trust_score(company_id)
    
    fraud_rate = (stats["fraud_cases"] / stats["total_claims"] * 100) if stats["total_claims"] > 0 else 0
    
    # Calculate trust score - now using ML probabilities
    base_score = 100
    base_score -= fraud_rate * 2
    base_score -= (stats["flagged_cases"] / max(stats["total_claims"], 1)) * 10
    
    if stats.get("avg_ml_fraud_probability", 0) > 0:
        ml_deduction = stats["avg_ml_fraud_probability"] * 30
        base_score -= ml_deduction
    
    base_score = max(min(base_score, 100), 0)
    
    trust_level = determine_trust_level(base_score)
    
    # Get monthly history
    claims = await get_claims_collection()
    year_ago = datetime.utcnow() - timedelta(days=365)
    
    monthly_pipeline = [
        {
            "$match": {
                "hospital_id": company_id,
                "submitted_at": {"$gte": year_ago}
            }
        },
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$submitted_at"},
                    "month": {"$month": "$submitted_at"}
                },
                "claims": {"$sum": 1},
                "fraud": {
                    "$sum": {"$cond": [{"$eq": ["$status", "Fraud"]}, 1, 0]}
                },
                "flagged": {
                    "$sum": {"$cond": [{"$eq": ["$status", "Flagged"]}, 1, 0]}
                },
                "avg_ml_prob": {"$avg": "$fraud_probability"}
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1}}
    ]
    
    monthly_cursor = claims.aggregate(monthly_pipeline)
    monthly_stats = await monthly_cursor.to_list(length=12)
    
    months_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    history = []
    
    for stat in monthly_stats:
        history.append({
            "month": months_names[stat["_id"]["month"] - 1],
            "claims": stat["claims"],
            "fraud": stat["fraud"],
            "flagged": stat["flagged"],
            "avgMLProbability": f"{stat.get('avg_ml_prob', 0)*100:.1f}%"
        })
    
    return {
        "id": company["hospital_id"],
        "name": company["hospital_name"],
        "address": company.get("address", ""),
        "trustScore": round(base_score, 1),
        "trustLevel": trust_level.value,
        "totalClaims": stats["total_claims"],
        "totalAmount": f"${stats['total_amount']:,.0f}" if stats['total_amount'] else "$0",
        "fraudCases": stats["fraud_cases"],
        "fraudRate": f"{fraud_rate:.1f}%",
        "flaggedClaims": stats["flagged_cases"],
        "approvedClaims": stats["approved_cases"],
        "avgMLFraudProbability": f"{stats.get('avg_ml_fraud_probability', 0)*100:.1f}%" if stats.get('avg_ml_fraud_probability') else "0%",
        "avgProcessingTime": "2.4 days",
        "monthlyHistory": history,
        "riskFactors": [
            {"name": "ML Fraud Score", "score": round((1 - stats.get('avg_ml_fraud_probability', 0)) * 100, 1)},
            {"name": "Documentation Quality", "score": round(base_score * 0.95, 1)},
            {"name": "Billing Accuracy", "score": round(base_score * 0.92, 1)},
            {"name": "Claim Pattern", "score": round(base_score * 0.88, 1)}
        ]
    }

@router.get("/{company_id}/trust-score")
async def get_company_trust_score(
    company_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get just the trust score for a company"""
    companies = await get_companies_collection()
    
    company = await companies.find_one({"hospital_id": company_id})
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    
    stats = await calculate_trust_score(company_id)
    
    fraud_rate = (stats["fraud_cases"] / stats["total_claims"] * 100) if stats["total_claims"] > 0 else 0
    
    # Calculate trust score
    base_score = 100
    base_score -= fraud_rate * 2
    base_score -= (stats["flagged_cases"] / max(stats["total_claims"], 1)) * 10
    
    if stats.get("avg_ml_fraud_probability", 0) > 0:
        ml_deduction = stats["avg_ml_fraud_probability"] * 30
        base_score -= ml_deduction
    
    base_score = max(min(base_score, 100), 0)
    
    trust_level = determine_trust_level(base_score)
    
    return {
        "company_id": company_id,
        "trust_score": round(base_score, 1),
        "trust_level": trust_level.value,
        "fraud_rate": fraud_rate,
        "avg_ml_fraud_probability": stats.get("avg_ml_fraud_probability", 0),
        "total_claims": stats["total_claims"]
    }

@router.get("/high-risk/list")
async def get_high_risk_companies(
    limit: int = 10,
    current_user: dict = Depends(get_current_user)
):
    """Get list of high-risk companies"""
    companies = await get_companies_collection()
    
    cursor = companies.find()
    all_companies = await cursor.to_list(length=100)
    
    high_risk = []
    for company in all_companies:
        stats = await calculate_trust_score(company["hospital_id"])
        
        if stats["total_claims"] == 0:
            continue
            
        fraud_rate = (stats["fraud_cases"] / stats["total_claims"] * 100)
        
        # Calculate risk score using ML as well
        risk_score = 100
        risk_score -= (100 - fraud_rate * 2)
        
        if stats.get("avg_ml_fraud_probability", 0) > 0:
            risk_score += stats["avg_ml_fraud_probability"] * 30
        
        risk_score = max(min(risk_score, 100), 0)
        
        if risk_score > 60:  # High risk threshold
            high_risk.append({
                "id": company["hospital_id"],
                "name": company["hospital_name"],
                "risk": round(risk_score, 1),
                "claims": stats["total_claims"],
                "fraudRate": f"{fraud_rate:.1f}%",
                "mlFraudProbability": f"{stats.get('avg_ml_fraud_probability', 0)*100:.1f}%"
            })
    
    # Sort by risk score descending
    high_risk.sort(key=lambda x: x["risk"], reverse=True)
    
    return high_risk[:limit]

@router.patch("/{company_id}/trust-level")
async def update_company_trust_level(
    company_id: str,
    trust_level: TrustLevel,
    reason: str,
    current_user: dict = Depends(get_current_user)
):
    """Update company trust level (Insurance only)"""
    if current_user["role"] != "Insurance":
        raise HTTPException(status_code=403, detail="Only insurance can update trust levels")
    
    companies = await get_companies_collection()
    
    result = await companies.update_one(
        {"hospital_id": company_id},
        {
            "$set": {
                "trust_level_override": trust_level.value,
                "trust_level_reason": reason,
                "trust_level_updated_by": str(current_user["_id"]),
                "trust_level_updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Company not found")
    
    return {
        "message": f"Company trust level updated to {trust_level.value}",
        "reason": reason
    }

@router.get("/{company_id}/claim-history")
async def get_company_claim_history(
    company_id: str,
    period: str = "month",
    current_user: dict = Depends(get_current_user)
):
    """Get claim history for a company"""
    claims = await get_claims_collection()
    
    # Determine date range based on period
    end_date = datetime.utcnow()
    if period == "month":
        start_date = end_date - timedelta(days=30)
    elif period == "quarter":
        start_date = end_date - timedelta(days=90)
    elif period == "year":
        start_date = end_date - timedelta(days=365)
    else:
        start_date = end_date - timedelta(days=30)
    
    pipeline = [
        {
            "$match": {
                "hospital_id": company_id,
                "submitted_at": {"$gte": start_date}
            }
        },
        {
            "$group": {
                "_id": {
                    "year": {"$year": "$submitted_at"},
                    "month": {"$month": "$submitted_at"},
                    "day": {"$dayOfMonth": "$submitted_at"}
                },
                "claims": {"$sum": 1},
                "total_amount": {"$sum": "$claim_amount"},
                "fraud": {
                    "$sum": {"$cond": [{"$eq": ["$status", "Fraud"]}, 1, 0]}
                },
                "flagged": {
                    "$sum": {"$cond": [{"$eq": ["$status", "Flagged"]}, 1, 0]}
                },
                "avg_ml_prob": {"$avg": "$fraud_probability"}
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1, "_id.day": 1}}
    ]
    
    cursor = claims.aggregate(pipeline)
    history = await cursor.to_list(length=100)
    
    formatted_history = []
    for item in history:
        formatted_history.append({
            "date": f"{item['_id']['year']}-{item['_id']['month']:02d}-{item['_id']['day']:02d}",
            "claims": item["claims"],
            "amount": item["total_amount"],
            "fraud": item["fraud"],
            "flagged": item["flagged"],
            "avgMLProbability": f"{item.get('avg_ml_prob', 0)*100:.1f}%"
        })
    
    return formatted_history