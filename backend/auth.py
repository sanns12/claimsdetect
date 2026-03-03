from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import jwt
import bcrypt
import os
from typing import Optional

from database import get_users_collection

router = APIRouter()  # Remove the prefix from here
security = HTTPBearer()

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except:
        return False

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return user data"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Return user data from token
        return {
            "id": int(user_id),
            "email": payload.get("email"),
            "role": payload.get("role"),
            "full_name": payload.get("full_name", "User")
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    # Get users collection (mock database)
    users = get_users_collection()
    
    # Convert role to lowercase
    role_lower = request.role.lower()
    if role_lower not in ['user', 'hospital', 'insurance']:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    # Find user by email
    user = None
    for email, user_data in users.items():
        if email == request.email:
            user = user_data
            break
    
    if not user:
        # Create demo user if not exists
        user_id = len(users) + 1
        user = {
            "id": user_id,
            "full_name": request.email.split('@')[0],
            "email": request.email,
            "password_hash": get_password_hash("demo123"),  # Default password
            "role": role_lower,
            "created_at": datetime.utcnow().isoformat()
        }
        users[request.email] = user
        print(f"✅ New user created: {request.email} with role: {role_lower}")
    else:
        # For demo, accept any password
        pass
    
    # Create token
    token = create_access_token({
        "sub": str(user["id"]),
        "role": user["role"],
        "email": user["email"],
        "full_name": user["full_name"]
    })
    
    # For response
    display_role = user["role"].capitalize()
    
    return LoginResponse(
        token=token,
        user=UserResponse(
            id=user["id"],
            full_name=user["full_name"],
            email=user["email"],
            role=display_role,
            created_at=datetime.fromisoformat(user["created_at"])
        )
    )

@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(verify_token)):
    """Get current user information from JWT token"""
    return UserResponse(
        id=user["id"],
        full_name=user.get("full_name", "User"),
        email=user["email"],
        role=user["role"].capitalize(),
        created_at=datetime.utcnow()
    )

# Add this at the bottom of auth.py
get_current_user = verify_token