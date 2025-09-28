from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any

from app.models.card import (
    CardPreferences, 
    CardPreferencesCreate, 
    CardPreferencesUpdate,
    MethodCreditCard,
    CreditCardWithPreferences
)
from app.database import get_supabase_client
from app.utils.auth import verify_supabase_token
from app.services.method_api import MethodAPIService

router = APIRouter()
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token_data = verify_supabase_token(credentials.credentials)
    return token_data["user_id"]

@router.get("/test")
async def test_auth(user_id: str = Depends(get_current_user)):
    """Test authentication"""
    return {"user_id": user_id, "message": "Auth working"}

@router.get("/")
async def get_user_credit_cards(user_id: str = Depends(get_current_user)):
    """Get all credit cards - simplified mock version"""
    # Return static mock data
    return [
        {
            "id": "acc_12345678",
            "method_card": {
                "id": "acc_12345678",
                "type": "liability",
                "brand": "visa",
                "last_four": "4242",
                "name": "Chase Sapphire Preferred",
                "status": "active",
                "balance": 150000,
                "exp_month": 12,
                "exp_year": 2027,
                "liability": {
                    "mch": "4242",
                    "mask": "4242",
                    "name": "Chase Sapphire Preferred",
                    "type": "credit_card",
                    "balance": 150000,
                    "credit_limit": 500000,
                    "available_credit": 350000,
                    "next_payment_due_date": "2025-10-15",
                    "next_payment_minimum_amount": 3000,
                    "apr": 24.99,
                    "statement_balance": 150000
                }
            },
            "preferences": {
                "autopay_enabled": False,
                "autopay_amount": "minimum",
                "reminder_days": 3,
                "notifications_enabled": True
            }
        },
        {
            "id": "acc_87654321",
            "method_card": {
                "id": "acc_87654321",
                "type": "liability",
                "brand": "mastercard",
                "last_four": "5555",
                "name": "Capital One Venture",
                "status": "active",
                "balance": 89000,
                "exp_month": 6,
                "exp_year": 2026,
                "liability": {
                    "mch": "5555",
                    "mask": "5555",
                    "name": "Capital One Venture",
                    "type": "credit_card",
                    "balance": 89000,
                    "credit_limit": 300000,
                    "available_credit": 211000,
                    "next_payment_due_date": "2025-10-22",
                    "next_payment_minimum_amount": 1780,
                    "apr": 19.99,
                    "statement_balance": 89000
                }
            },
            "preferences": {
                "autopay_enabled": False,
                "autopay_amount": "minimum",
                "reminder_days": 3,
                "notifications_enabled": True
            }
        },
        {
            "id": "acc_11223344",
            "method_card": {
                "id": "acc_11223344",
                "type": "liability",
                "brand": "amex",
                "last_four": "1005",
                "name": "American Express Gold",
                "status": "active",
                "balance": 25000,
                "exp_month": 3,
                "exp_year": 2028,
                "liability": {
                    "mch": "1005",
                    "mask": "1005",
                    "name": "American Express Gold",
                    "type": "credit_card",
                    "balance": 25000,
                    "credit_limit": 200000,
                    "available_credit": 175000,
                    "next_payment_due_date": "2025-10-10",
                    "next_payment_minimum_amount": 500,
                    "apr": 29.99,
                    "statement_balance": 25000
                }
            },
            "preferences": {
                "autopay_enabled": False,
                "autopay_amount": "minimum",
                "reminder_days": 3,
                "notifications_enabled": True
            }
        }
    ]

@router.post("/{card_id}/preferences", response_model=CardPreferences)
async def create_card_preferences(
    card_id: str,
    preferences: CardPreferencesCreate,
    user_id: str = Depends(get_current_user)
):
    """Create or update preferences for a specific card"""
    supabase = get_supabase_client()
    
    try:
        # Check if preferences already exist
        existing_response = supabase.table("card_preferences").select("id").eq("user_id", user_id).eq("method_card_id", card_id).execute()
        
        prefs_data = preferences.model_dump()
        prefs_data["user_id"] = user_id
        prefs_data["method_card_id"] = card_id
        
        if existing_response.data:
            # Update existing preferences
            response = supabase.table("card_preferences").update(prefs_data).eq("id", existing_response.data[0]["id"]).execute()
        else:
            # Create new preferences
            response = supabase.table("card_preferences").insert(prefs_data).execute()
        
        if not response.data:
            raise HTTPException(status_code=400, detail="Failed to save card preferences")
        
        return CardPreferences(**response.data[0])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save card preferences: {str(e)}")

@router.put("/{card_id}/preferences", response_model=CardPreferences)
async def update_card_preferences(
    card_id: str,
    preferences_update: CardPreferencesUpdate,
    user_id: str = Depends(get_current_user)
):
    """Update preferences for a specific card"""
    supabase = get_supabase_client()
    
    try:
        update_data = preferences_update.model_dump(exclude_unset=True)
        
        if not update_data:
            raise HTTPException(status_code=400, detail="No data to update")
        
        response = supabase.table("card_preferences").update(update_data).eq("user_id", user_id).eq("method_card_id", card_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Card preferences not found")
        
        return CardPreferences(**response.data[0])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update card preferences: {str(e)}")

@router.get("/{card_id}/preferences", response_model=CardPreferences)
async def get_card_preferences(card_id: str, user_id: str = Depends(get_current_user)):
    """Get preferences for a specific card"""
    supabase = get_supabase_client()
    
    try:
        response = supabase.table("card_preferences").select("*").eq("user_id", user_id).eq("method_card_id", card_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Card preferences not found")
        
        return CardPreferences(**response.data[0])
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch card preferences: {str(e)}")
