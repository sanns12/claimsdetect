# backend/app/routes/auth.py

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from datetime import datetime

from database import get_users_collection
from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash,
    get_current_user
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


# -------------------------------
# Schemas
# -------------------------------

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    role: str


class UserResponse(BaseModel):
    id: int
    full_name: str
    email: str
    role: str
    created_at: datetime


class LoginResponse(BaseModel):
    token: str
    user: UserResponse


# -------------------------------
# Login
# -------------------------------

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    db = await get_users_collection()

    role_lower = request.role.lower()
    if role_lower not in ["user", "hospital", "insurance"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    # Find user by email
    async with db.execute(
        "SELECT * FROM users WHERE email = ?", (request.email,)
    ) as cursor:
        user = await cursor.fetchone()

    if not user:
        # Auto-create for demo
        hashed = get_password_hash(request.password)
        await db.execute(
            """INSERT INTO users (full_name, email, password_hash, role, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (
                request.email.split("@")[0],
                request.email,
                hashed,
                role_lower,
                datetime.utcnow().isoformat()
            )
        )
        await db.commit()

        # Fetch the newly created user
        async with db.execute(
            "SELECT * FROM users WHERE email = ?", (request.email,)
        ) as cursor:
            user = await cursor.fetchone()

    else:
        if not verify_password(request.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": str(user["id"]),
        "role": user["role"],
        "email": user["email"],
        "full_name": user["full_name"]
    })

    return LoginResponse(
        token=token,
        user=UserResponse(
            id=user["id"],
            full_name=user["full_name"],
            email=user["email"],
            role=user["role"].capitalize(),
            created_at=datetime.fromisoformat(user["created_at"])
        )
    )


# -------------------------------
# Current User
# -------------------------------

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    db = await get_users_collection()

    async with db.execute(
        "SELECT * FROM users WHERE id = ?", (current_user["id"],)
    ) as cursor:
        user = await cursor.fetchone()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=user["id"],
        full_name=user["full_name"],
        email=user["email"],
        role=user["role"].capitalize(),
        created_at=datetime.fromisoformat(user["created_at"])
    )