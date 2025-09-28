from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from datetime import date, datetime

from app.database import get_supabase_client
from app.utils.auth import verify_supabase_token
from app.services.method_api import MethodAPIService

router = APIRouter()

async def get_current_user(token_data: Dict[str, Any] = Depends(verify_supabase_token)) -> str:
    return token_data["user_id"]

@router.get("/")
async def get_user_bills(user_id: str = Depends(get_current_user)):
    """Get all bills from Method API for the current user"""
    supabase = get_supabase_client()
    
    try:
        # Get user's Method account ID
        user_response = supabase.table("users").select("method_account_id").eq("id", user_id).execute()
        
        if not user_response.data or not user_response.data[0]["method_account_id"]:
            raise HTTPException(status_code=400, detail="User does not have a Method account")
        
        method_account_id = user_response.data[0]["method_account_id"]
        
        # TODO: Get bills from Method API
        # Method doesn't have a direct "bills" endpoint, but you would get:
        # 1. Credit card statements
        # 2. Payment due dates
        # 3. Outstanding balances
        
        # For now, return placeholder data
        return {
            "message": "Bills endpoint not yet implemented - will query Method API for credit card statements and due dates",
            "method_account_id": method_account_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch bills: {str(e)}")

@router.post("/process")
async def process_bill_email(user_id: str = Depends(get_current_user)):
    """Process an incoming bill email and extract bill information"""
    # TODO: This would integrate with AgentMail webhook
    # to receive incoming bill emails and process them with AI
    
    return {
        "message": "Bill email processing not yet implemented",
        "description": "This endpoint will receive bill emails from AgentMail and use AI to extract bill information"
    }

@router.post("/pay")
async def pay_bill(
    card_id: str,
    amount: float,
    description: str = "AgentPay bill payment",
    user_id: str = Depends(get_current_user)
):
    """Process payment for a bill using Method API"""
    supabase = get_supabase_client()
    
    try:
        # Get user's Method account ID
        user_response = supabase.table("users").select("method_account_id").eq("id", user_id).execute()
        
        if not user_response.data or not user_response.data[0]["method_account_id"]:
            raise HTTPException(status_code=400, detail="User does not have a Method account")
        
        method_account_id = user_response.data[0]["method_account_id"]
        
        # TODO: Implement actual payment via Method API
        # This would:
        # 1. Get the user's bank account for funding
        # 2. Create a payment to the specified credit card
        # 3. Return payment details
        
        return {
            "message": "Payment processing not yet implemented",
            "card_id": card_id,
            "amount": amount,
            "description": description,
            "method_account_id": method_account_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process payment: {str(e)}")
