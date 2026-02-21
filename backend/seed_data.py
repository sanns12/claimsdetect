from database import Database
import asyncio

async def seed_companies():
    """Add initial companies to database"""
    await Database.connect_db()
    companies = Database.db.companies
    
    # Sample companies
    sample_companies = [
        {
            "hospital_id": "HOSP-001",
            "hospital_name": "City General Hospital",
            "address": "123 Main St, New York, NY 10001",
            "created_at": datetime.utcnow()
        },
        {
            "hospital_id": "HOSP-002",
            "hospital_name": "MediCare Plus Clinic",
            "address": "456 Oak Ave, Los Angeles, CA 90001",
            "created_at": datetime.utcnow()
        },
        {
            "hospital_id": "HOSP-003",
            "hospital_name": "HealthFirst Medical Center",
            "address": "789 Pine St, Chicago, IL 60601",
            "created_at": datetime.utcnow()
        },
        {
            "hospital_id": "HOSP-004",
            "hospital_name": "QuickCare Emergency",
            "address": "321 Elm St, Houston, TX 77001",
            "created_at": datetime.utcnow()
        },
        {
            "hospital_id": "HOSP-005",
            "hospital_name": "Premier Health Group",
            "address": "555 Cedar Rd, Miami, FL 33101",
            "created_at": datetime.utcnow()
        }
    ]
    
    for company in sample_companies:
        # Check if exists
        existing = await companies.find_one({"hospital_id": company["hospital_id"]})
        if not existing:
            await companies.insert_one(company)
            print(f"✅ Added {company['hospital_name']}")
    
    print("✅ Seed data complete")
    await Database.close_db()

if __name__ == "__main__":
    from datetime import datetime
    asyncio.run(seed_companies())