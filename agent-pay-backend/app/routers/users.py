from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, Any
import uuid

from app.models.user import User, UserUpdate, UserProfile, UserSettings, UserSettingsUpdate
from app.database import get_supabase_client
from app.utils.auth import verify_supabase_token

router = APIRouter()

async def get_current_user(token_data: Dict[str, Any] = Depends(verify_supabase_token)) -> str:
    return token_data["user_id"]

@router.get("/me", response_model=UserProfile)
async def get_user_profile(user_id: str = Depends(get_current_user)):
    """Get current user profile with settings"""
    supabase = get_supabase_client()
    
    try:
        # Get user data
        user_response = supabase.table("users").select("*").eq("id", user_id).execute()
        
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_response.data[0]
        
        # Get user settings
        settings_response = supabase.table("user_settings").select("*").eq("user_id", user_id).execute()
        
        settings_data = settings_response.data[0] if settings_response.data else None
        
        return UserProfile(
            **user_data,
            settings=UserSettings(**settings_data) if settings_data else None
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user profile: {str(e)}")

@router.put("/me", response_model=User)
async def update_user_profile(
    user_update: UserUpdate,
    user_id: str = Depends(get_current_user)
):
    """Update current user profile"""
    supabase = get_supabase_client()
    
    try:
        # Update user data
        update_data = user_update.model_dump(exclude_unset=True)
        
        if update_data:
            response = supabase.table("users").update(update_data).eq("id", user_id).execute()
            
            if not response.data:
                raise HTTPException(status_code=404, detail="User not found")
            
            return User(**response.data[0])
        
        # If no updates, return current user
        user_response = supabase.table("users").select("*").eq("id", user_id).execute()
        return User(**user_response.data[0])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user profile: {str(e)}")

@router.get("/settings", response_model=UserSettings)
async def get_user_settings(user_id: str = Depends(get_current_user)):
    """Get user settings"""
    supabase = get_supabase_client()
    
    try:
        response = supabase.table("user_settings").select("*").eq("user_id", user_id).execute()
        
        if not response.data:
            # Create default settings if they don't exist
            default_settings = {
                "user_id": user_id,
                "autopay_enabled": True,
                "default_reminder_days": 3,
                "email_notifications": True,
                "sms_notifications": False,
                "max_autopay_amount": 1000.00
            }
            
            create_response = supabase.table("user_settings").insert(default_settings).execute()
            return UserSettings(**create_response.data[0])
        
        return UserSettings(**response.data[0])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user settings: {str(e)}")

@router.put("/settings", response_model=UserSettings)
async def update_user_settings(
    settings_update: UserSettingsUpdate,
    user_id: str = Depends(get_current_user)
):
    """Update user settings"""
    supabase = get_supabase_client()
    
    try:
        update_data = settings_update.model_dump(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No settings to update")
        
        response = supabase.table("user_settings").update(update_data).eq("user_id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="User settings not found")
        
        return UserSettings(**response.data[0])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user settings: {str(e)}")

@router.post("/method-account")
async def create_method_account(user_id: str = Depends(get_current_user)):
    """Create Method API account for user"""
    # TODO: Implement Method API account creation
    # This will integrate with Method's API to create a new account
    
    # For now, return a placeholder
    return {
        "message": "Method account creation not yet implemented",
        "user_id": user_id,
        "method_account_id": f"method_{uuid.uuid4().hex[:8]}"
    }

