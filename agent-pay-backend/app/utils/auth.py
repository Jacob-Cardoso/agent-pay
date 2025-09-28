import os
from jose import jwt
from jose.exceptions import JWTError
from typing import Dict, Any
from fastapi import HTTPException

def verify_supabase_token(token: str) -> Dict[str, Any]:
    """
    Verify JWT token and extract user information
    
    Args:
        token: JWT token from our auth system
        
    Returns:
        Dict containing user information
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # Get JWT secret from environment
        jwt_secret = os.getenv("JWT_SECRET", "your-super-secret-key")
        
        # Decode and verify the token
        payload = jwt.decode(
            token,
            jwt_secret,
            algorithms=["HS256"]
        )
        
        # Extract user information
        user_id = payload.get("user_id")
        email = payload.get("sub")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token: missing user ID")
        
        return {
            "user_id": user_id,
            "email": email,
            "token_payload": payload
        }
        
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")

def get_user_from_token(token: str) -> str:
    """
    Extract user ID from Supabase token
    
    Args:
        token: JWT token from Supabase
        
    Returns:
        User ID string
    """
    user_data = verify_supabase_token(token)
    return user_data["user_id"]
