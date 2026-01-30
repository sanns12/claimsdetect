from backend.database import SessionLocal, engine
from backend.models import User
from backend.auth import get_password_hash

def seed_users():
    db = SessionLocal()

    users = [
        {
            "name": "Test User",
            "email": "user@test.com",
            "password": "user123",
            "role": "user"
        },
        {
            "name": "Test Hospital",
            "email": "hospital@test.com",
            "password": "hospital123",
            "role": "hospital"
        },
        {
            "name": "Test Insurance",
            "email": "insurance@test.com",
            "password": "insurance123",
            "role": "insurance"
        }
    ]

    for u in users:
        existing = db.query(User).filter(User.email == u["email"]).first()
        if not existing:
            user = User(
                name=u["name"],
                email=u["email"],
                hashed_password=get_password_hash(u["password"]),
                role=u["role"]
            )
            db.add(user)

    db.commit()
    db.close()
    print("✅ Dummy users seeded successfully")


if __name__ == "__main__":
    seed_users()
