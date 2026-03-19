# backend/seed_data.py

from datetime import datetime
from database import get_companies_collection, init_db


async def seed_companies():
    """
    Seed companies table aligned with SQLite schema.
    """

    init_db()  # ensure tables exist

    companies_collection = await get_companies_collection()

    sample_companies = [
        {
            "name": "City General Hospital",
            "type": "hospital",
            "trust_status": "green",
            "fraud_percentage": 0.5,
            "total_claims": 450,
            "flagged_claims": 8,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "name": "MediCare Plus Clinic",
            "type": "hospital",
            "trust_status": "green",
            "fraud_percentage": 0.9,
            "total_claims": 320,
            "flagged_claims": 12,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "name": "HealthFirst Medical",
            "type": "hospital",
            "trust_status": "yellow",
            "fraud_percentage": 1.8,
            "total_claims": 280,
            "flagged_claims": 18,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "name": "QuickCare Emergency",
            "type": "hospital",
            "trust_status": "yellow",
            "fraud_percentage": 2.1,
            "total_claims": 195,
            "flagged_claims": 15,
            "created_at": datetime.utcnow().isoformat()
        },
        {
            "name": "Premier Health Group",
            "type": "hospital",
            "trust_status": "green",
            "fraud_percentage": 0.8,
            "total_claims": 520,
            "flagged_claims": 14,
            "created_at": datetime.utcnow().isoformat()
        }
    ]

    for company in sample_companies:
        existing = companies_collection.find_one({"name": company["name"]})
        if not existing:
            companies_collection.insert_one(company)
            print(f"✅ Added {company['name']}")

    print("✅ Company seed complete")


if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_companies())