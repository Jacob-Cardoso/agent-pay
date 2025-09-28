from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any

from app.database import get_supabase_client
from app.utils.auth import verify_supabase_token
from app.services.method_api import MethodAPIService

router = APIRouter()
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token_data = verify_supabase_token(credentials.credentials)
    return token_data["user_id"]

@router.post("/payments/{payment_id}")
async def simulate_payment_update(
    payment_id: str,
    simulation_data: Dict[str, Any],
    user_id: str = Depends(get_current_user)
):
    """
    Simulate updating a payment's status (dev environment only)
    
    Body should contain:
    - status: The next status (processing, completed, failed, etc.)
    - error_code: Optional error code for failed payments
    """
    try:
        method_service = MethodAPIService()
        updated_payment = await method_service.simulate_payment_update(
            payment_id=payment_id,
            status=simulation_data["status"],
            error_code=simulation_data.get("error_code")
        )
        
        return updated_payment
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to simulate payment update: {str(e)}")

@router.post("/transactions")
async def simulate_create_transaction(
    transaction_data: Dict[str, Any],
    user_id: str = Depends(get_current_user)
):
    """
    Simulate creating a transaction (dev environment only)
    
    Body should contain transaction data as per Method API docs
    """
    try:
        method_service = MethodAPIService()
        transaction = await method_service.simulate_create_transaction(transaction_data)
        
        return transaction
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to simulate transaction creation: {str(e)}")

@router.post("/events")
async def simulate_event(
    event_data: Dict[str, Any],
    user_id: str = Depends(get_current_user)
):
    """
    Simulate an event (dev environment only)
    
    Body should contain event data as per Method API docs
    """
    try:
        method_service = MethodAPIService()
        
        # Add simulate_event method to MethodAPIService if not exists
        if hasattr(method_service, 'simulate_event'):
            event = await method_service.simulate_event(event_data)
            return event
        else:
            return {
                "message": "Event simulation not yet implemented",
                "data": event_data
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to simulate event: {str(e)}")

@router.get("/status")
async def get_simulation_status():
    """Get simulation environment status"""
    try:
        method_service = MethodAPIService()
        
        return {
            "environment": method_service.environment,
            "simulation_available": method_service.environment == "dev",
            "base_url": method_service.base_url,
            "endpoints": {
                "payments": "/api/simulations/payments/{payment_id}",
                "transactions": "/api/simulations/transactions",
                "events": "/api/simulations/events"
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get simulation status: {str(e)}")
