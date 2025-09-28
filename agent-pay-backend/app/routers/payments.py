from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List, Dict, Any, Optional

from app.database import get_supabase_client
from app.utils.auth import verify_supabase_token
from app.services.method_api import MethodAPIService
from app.models.payment import PaymentCreate, PaymentResponse, PaymentListResponse, PaymentSimulation

router = APIRouter()
security = HTTPBearer()

# In-memory storage for simulated payments (in production, this would be in a database)
_user_payments = {}

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token_data = verify_supabase_token(credentials.credentials)
    return token_data["user_id"]


@router.post("/", response_model=PaymentResponse)
async def create_payment(
    payment_data: PaymentCreate,
    user_id: str = Depends(get_current_user)
):
    """Create a new payment via Method API"""
    supabase = get_supabase_client()
    
    try:
        # Get user's Method entity ID
        user_response = supabase.table("users").select("method_account_id").eq("id", user_id).execute()
        
        if not user_response.data or not user_response.data[0]["method_account_id"]:
            raise HTTPException(status_code=400, detail="User does not have a Method entity")
        
        method_entity_id = user_response.data[0]["method_account_id"]
        
        # For now, create a simulated payment since we don't have real bank accounts set up
        # In production, this would use real Method API payment creation
        import uuid
        from datetime import datetime
        
        # Simulate a realistic Method payment response
        payment_id = f"pmt_{str(uuid.uuid4())[:8]}"
        simulated_payment = {
            "id": payment_id,
            "amount": payment_data.amount,
            "source": payment_data.source or f"acc_bank_{str(uuid.uuid4())[:8]}",
            "destination": payment_data.destination,
            "description": payment_data.description,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "metadata": {
                "user_id": user_id,
                "entity_id": method_entity_id
            }
        }
        
        # Store payment in our in-memory store
        if user_id not in _user_payments:
            _user_payments[user_id] = []
        _user_payments[user_id].append(simulated_payment)
        
        # TODO: Replace with real Method API call once bank accounts are connected
        # method_service = MethodAPIService()
        # payment_response = await method_service.create_payment(...)
        
        return PaymentResponse(**simulated_payment)
        
    except Exception as e:
        import traceback
        error_details = f"Error: {str(e)}, Traceback: {traceback.format_exc()}"
        print(f"Failed to create payment: {error_details}")
        raise HTTPException(status_code=500, detail=f"Failed to create payment: {str(e)}")

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: str, user_id: str = Depends(get_current_user)):
    """Get details of a specific payment from Method API"""
    try:
        method_service = MethodAPIService()
        payment = await method_service.get_payment(payment_id)
        
        return payment
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch payment: {str(e)}")

# SIMULATION ENDPOINTS (DEV ENVIRONMENT ONLY)
@router.post("/{payment_id}/simulate", response_model=PaymentResponse)
async def simulate_payment_update(
    payment_id: str,
    simulation_data: PaymentSimulation,
    user_id: str = Depends(get_current_user)
):
    """Simulate updating a payment's status (dev environment only)"""
    try:
        method_service = MethodAPIService()
        updated_payment = await method_service.simulate_payment_update(
            payment_id=payment_id,
            status=simulation_data.status,
            error_code=simulation_data.error_code
        )
        
        return updated_payment
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to simulate payment update: {str(e)}")

@router.delete("/{payment_id}")
async def delete_payment(payment_id: str, user_id: str = Depends(get_current_user)):
    """Delete a payment via Method API"""
    try:
        method_service = MethodAPIService()
        result = await method_service.delete_payment(payment_id)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete payment: {str(e)}")

@router.get("/")
async def get_payment_history(
    status: Optional[str] = Query(None, description="Payment status filter"),
    limit: int = Query(50, description="Number of payments to return"),
    offset: int = Query(0, description="Number of payments to skip"),
    user_id: str = Depends(get_current_user)
):
    """Get payment history for the current user"""
    try:
        # Get payments from our in-memory store
        user_payment_list = _user_payments.get(user_id, [])
        
        # Apply status filter if provided
        if status:
            user_payment_list = [p for p in user_payment_list if p.get("status") == status]
        
        # Sort by created_at desc (newest first)
        user_payment_list.sort(key=lambda x: x["created_at"], reverse=True)
        
        # Apply pagination
        start_idx = offset
        end_idx = offset + limit
        paginated_payments = user_payment_list[start_idx:end_idx]
        
        # Return simple payment objects that match frontend expectations
        return paginated_payments
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch payments: {str(e)}")
