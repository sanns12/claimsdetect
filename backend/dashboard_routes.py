from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import Claim, Company
from backend.auth import require_role,security

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
    dependencies=[Security(security)]
)

@router.get("/summary")
def dashboard_summary(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["insurance"]))
):
    total_claims = db.query(Claim).count()
    approved = db.query(Claim).filter(Claim.status == "Approved").count()
    flagged = db.query(Claim).filter(Claim.status == "Flagged").count()
    fraud = db.query(Claim).filter(Claim.status == "Fraud").count()

    return {
        "total_claims": total_claims,
        "approved": approved,
        "flagged": flagged,
        "fraud": fraud
    }


@router.get("/company-trust")
def company_trust_list(
    db: Session = Depends(get_db),
    current_user=Depends(require_role(["insurance"]))
):
    companies = db.query(Company).all()

    return [
        {
            "company_id": c.company_id,
            "name": c.name,
            "trust_score": c.trust_score,
            "flagged_count": c.flagged_count
        }
        for c in companies
    ]
