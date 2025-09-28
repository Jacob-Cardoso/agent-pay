from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from typing import Optional

from ..database import get_supabase_anon_client
from ..models.user import User, UserCreate

router = APIRouter(prefix="/auth", tags=["authentication"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = os.getenv("JWT_SECRET", "your-secret-key-change-this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    phone_number: str = Field(..., min_length=10, description="Phone number is required")
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token from Authorization header."""
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/register", response_model=Token)
async def register_user(user_data: UserRegister):
    """Register a new user."""
    try:
        supabase = get_supabase_anon_client()
        
        # Check if user already exists
        existing_user = supabase.table("users").select("*").eq("email", user_data.email).execute()
        if existing_user.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user in Supabase auth (this will trigger our database trigger)
        try:
            auth_response = supabase.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "full_name": user_data.full_name,
                        "phone_number": user_data.phone_number
                    },
                    "email_confirm": False  # Disable email confirmation
                }
            })
            
            if auth_response.user is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create user account"
                )
        except Exception as e:
            # If user already exists in Supabase auth, check if they exist in our table
            if "already" in str(e).lower() or "exists" in str(e).lower():
                # Check if user exists in our users table
                existing_user = supabase.table("users").select("*").eq("email", user_data.email).execute()
                if existing_user.data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already registered"
                    )
                else:
                    # User exists in auth but not in our table - this shouldn't happen, but handle it
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Account exists but profile incomplete. Please contact support."
                    )
            else:
                # Some other error
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Registration failed: {str(e)}"
                )
        
        # Update user profile in our users table
        user_update = supabase.table("users").update({
            "full_name": user_data.full_name,
            "phone_number": user_data.phone_number,
        }).eq("id", auth_response.user.id).execute()
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_data.email, "user_id": str(auth_response.user.id)},
            expires_delta=access_token_expires
        )
        
        # Get user data for response
        user_profile = supabase.table("users").select("*").eq("id", auth_response.user.id).execute()
        user_data_response = user_profile.data[0] if user_profile.data else {}
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(auth_response.user.id),
                "email": user_data.email,
                "full_name": user_data.full_name,
                "phone_number": user_data.phone_number,
                **user_data_response
            }
        }
        
    except Exception as e:
        if "Email already registered" in str(e):
            raise e
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

@router.post("/login", response_model=Token)
async def login_user(user_credentials: UserLogin):
    """Authenticate user and return token."""
    try:
        supabase = get_supabase_anon_client()
        
        # Authenticate with Supabase
        auth_response = supabase.auth.sign_in_with_password({
            "email": user_credentials.email,
            "password": user_credentials.password
        })
        
        if auth_response.user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Get user profile
        user_profile = supabase.table("users").select("*").eq("id", auth_response.user.id).execute()
        user_data = user_profile.data[0] if user_profile.data else {}
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_credentials.email, "user_id": str(auth_response.user.id)},
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(auth_response.user.id),
                "email": user_credentials.email,
                **user_data
            }
        }
        
    except Exception as e:
        if "Invalid login credentials" in str(e) or "Invalid email or password" in str(e):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )

@router.get("/me", response_model=User)
async def get_current_user(token_data: dict = Depends(verify_token)):
    """Get current user profile."""
    try:
        supabase = get_supabase_anon_client()
        
        user_id = token_data.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get user from database
        user_profile = supabase.table("users").select("*").eq("id", user_id).execute()
        if not user_profile.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return user_profile.data[0]
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user profile: {str(e)}"
        )

@router.post("/logout")
async def logout_user(token_data: dict = Depends(verify_token)):
    """Logout user (client should delete token)."""
    return {"message": "Successfully logged out"}
