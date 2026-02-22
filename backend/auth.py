from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta
import jwt
import bcrypt
import os

from database import get_users_collection

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()

SECRET_KEY = "insurance_claims_ai_super_secure_jwt_secret_key_2026"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

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
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token and return user data"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    users = await get_users_collection()
    user = users.find_one({"id": int(user_id)})
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        # Return consistent user object with _id
        return {
            "_id": int(user_id),
            "email": payload.get("email"),
            "role": payload.get("role")
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
# Alias for compatibility
get_current_user = verify_token

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    users = await get_users_collection()
    
    # Convert role to lowercase to match database constraint
    role_lower = request.role.lower()
    if role_lower not in ['user', 'hospital', 'insurance']:
        raise HTTPException(status_code=400, detail="Invalid role")
    
    # Find user by email
    user = users.find_one({"email": request.email})
    
    if not user:
        # Auto-create user for demo
        hashed = get_password_hash(request.password)
        user_data = {
            "full_name": request.email.split('@')[0],
            "email": request.email,
            "password_hash": hashed,
            "role": role_lower,  # Use lowercase role
            "created_at": datetime.utcnow().isoformat()
        }
        result = users.insert_one(user_data)
        user = users.find_one({"_id": result.inserted_id})
        print(f"✅ New user created: {request.email} with role: {role_lower}")
    else:
        # Verify password
        if not verify_password(request.password, user["password_hash"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create token (store original role in token for frontend)
    token = create_access_token({
        "sub": str(user["id"]),
        "role": user["role"],  # This will be lowercase
        "email": user["email"]
    })
    
    # For response, capitalize first letter for frontend display
    display_role = user["role"].capitalize()
    
    return LoginResponse(
        token=token,
        user=UserResponse(
            id=user["id"],
            full_name=user["full_name"],
            email=user["email"],
            role=display_role,  # Send capitalized version to frontend
            created_at=datetime.fromisoformat(user["created_at"])
        )
    )

@router.get("/me", response_model=UserResponse)
async def get_me(user: dict = Depends(verify_token)):
    """Get current user information from JWT token"""
    display_role = user["role"].capitalize()
    return UserResponse(
        id=user["id"],
        full_name=user["full_name"],
        email=user["email"],
        role=display_role,
        created_at=datetime.fromisoformat(user["created_at"])
    )