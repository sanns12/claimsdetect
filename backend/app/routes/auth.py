# backend/routes/auth.py

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
    users = await get_users_collection()

    role_lower = request.role.lower()
    if role_lower not in ["user", "hospital", "insurance"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    user = users.find_one({"email": request.email})

    if not user:
        # Auto-create for demo
        hashed = get_password_hash(request.password)
        user_data = {
            "full_name": request.email.split("@")[0],
            "email": request.email,
            "password_hash": hashed,
            "role": role_lower,
            "created_at": datetime.utcnow().isoformat()
        }

        result = users.insert_one(user_data)
        user = users.find_one({"id": result.inserted_id})

    else:
        if not verify_password(request.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token({
        "sub": str(user["id"]),
        "role": user["role"],
        "email": user["email"]
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
async def get_me(user: dict = Depends(get_current_user)):
    return UserResponse(
        id=user["id"],
        full_name=user["full_name"],
        email=user["email"],
        role=user["role"].capitalize(),
        created_at=datetime.fromisoformat(user["created_at"])
    )
