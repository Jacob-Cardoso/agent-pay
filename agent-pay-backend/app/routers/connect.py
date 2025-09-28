from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, Any

from app.database import get_supabase_client
from app.utils.auth import verify_supabase_token
from app.services.method_api import MethodAPIService

router = APIRouter()
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token_data = verify_supabase_token(credentials.credentials)
    return token_data["user_id"]

@router.post("/element-token")
async def create_connect_token(user_id: str = Depends(get_current_user)):
    """
    Create a Method Connect element token for bank account connection
    
    This token is used by the frontend Method Connect component to securely
    connect the user's bank account.
    """
    supabase = get_supabase_client()
    
    try:
        # Get user's Method entity ID
        user_response = supabase.table("users").select("method_account_id").eq("id", user_id).execute()
        
        if not user_response.data or not user_response.data[0]["method_account_id"]:
            raise HTTPException(status_code=400, detail="User does not have a Method entity")
        
        method_entity_id = user_response.data[0]["method_account_id"]
        
        # Create element token for Method Connect
        method_service = MethodAPIService()
        element_response = await method_service.create_element_token(
            entity_id=method_entity_id,
            element_type="connect"
        )
        
        return {
            "element_token": element_response.get("token"),
            "expires_at": element_response.get("expires_at"),
            "entity_id": method_entity_id
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create connect token: {str(e)}")

@router.get("/element-results/{element_token}")
async def get_connect_results(element_token: str, user_id: str = Depends(get_current_user)):
    """
    Get the results from Method Connect after user completes bank connection
    
    This endpoint is called after the user successfully connects their bank account
    through Method Connect to retrieve the connected account information.
    """
    try:
        method_service = MethodAPIService()
        element_results = await method_service.get_element_results(element_token)
        
        # The results will contain the connected bank account information
        return element_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get connect results: {str(e)}")

@router.get("/bank-accounts")
async def get_user_bank_accounts(user_id: str = Depends(get_current_user)):
    """
    Get all connected bank accounts for the user
    
    Returns both checking and savings accounts that can be used as payment sources.
    """
    supabase = get_supabase_client()
    
    try:
        # Get user's Method entity ID
        user_response = supabase.table("users").select("method_account_id").eq("id", user_id).execute()
        
        if not user_response.data or not user_response.data[0]["method_account_id"]:
            raise HTTPException(status_code=400, detail="User does not have a Method entity")
        
        method_entity_id = user_response.data[0]["method_account_id"]
        
        # Get all accounts for the user
        method_service = MethodAPIService()
        all_accounts = await method_service.get_accounts(method_entity_id)
        
        # Filter for bank accounts (checking/savings) - exclude credit cards
        bank_accounts = []
        for account in all_accounts.get("data", []):
            if account.get("type") in ["checking", "savings", "ach"]:
                bank_accounts.append({
                    "id": account["id"],
                    "type": account["type"],
                    "bank_name": account.get("bank_name", "Unknown Bank"),
                    "last_four": account.get("last_four", "****"),
                    "status": account.get("status", "unknown"),
                    "balance": account.get("balance"),
                    "routing_number": account.get("routing_number")
                })
        
        return {
            "bank_accounts": bank_accounts,
            "total": len(bank_accounts)
        }
        
    except Exception as e:
        import traceback
        error_details = f"Error: {str(e)}, Traceback: {traceback.format_exc()}"
        print(f"Get bank accounts error: {error_details}")  # Log to console
        raise HTTPException(status_code=500, detail=f"Failed to get bank accounts: {str(e)}")

@router.post("/manual-account")
async def create_manual_bank_account(
    account_data: Dict[str, Any],
    user_id: str = Depends(get_current_user)
):
    """
    Manually create a bank account (alternative to Method Connect)
    
    This is for users who prefer to enter their bank details manually
    instead of using the automated Method Connect flow.
    """
    supabase = get_supabase_client()
    
    try:
        # Get user's Method entity ID
        user_response = supabase.table("users").select("method_account_id").eq("id", user_id).execute()
        
        if not user_response.data or not user_response.data[0]["method_account_id"]:
            raise HTTPException(status_code=400, detail="User does not have a Method entity")
        
        method_entity_id = user_response.data[0]["method_account_id"]
        
        # Prepare account data for Method API
        method_account_data = {
            "entity_id": method_entity_id,
            "type": account_data.get("type", "checking"),  # checking or savings
            "routing_number": account_data["routing_number"],
            "account_number": account_data["account_number"],
            "account_name": account_data.get("account_name", "Primary Account")
        }
        
        # Create account via Method API
        method_service = MethodAPIService()
        created_account = await method_service.create_account(method_account_data)
        
        return created_account
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create manual bank account: {str(e)}")

@router.post("/simulate-connection")
async def simulate_bank_connection(user_id: str = Depends(get_current_user)):
    """
    🎭 SIMULATION: Simulate connecting a bank account (dev environment only)
    
    This bypasses Method Connect and creates a simulated bank account
    that can be used for payments in the dev environment.
    
    If the user doesn't have a Method entity, one will be created automatically.
    """
    print(f"🔍 Starting simulation for user_id: {user_id}")
    supabase = get_supabase_client()
    
    try:
        # Get user's Method entity ID
        user_response = supabase.table("users").select("method_account_id, email, phone_number").eq("id", user_id).execute()
        
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_response.data[0]
        method_entity_id = user_data.get("method_account_id")
        
        # If user doesn't have a Method entity, create one
        if not method_entity_id:
            method_service = MethodAPIService()
            
            # Create a simulated Method entity
            entity_data = {
                "type": "individual",
                "individual": {
                    "first_name": "Simulation",
                    "last_name": "User",
                    "phone": user_data.get("phone_number", "+15551234567"),
                    "email": user_data.get("email"),
                    "dob": "1990-01-01"
                }
            }
            
            # For simulation, we'll create a mock entity ID
            import uuid
            method_entity_id = f"ent_simulation_{str(uuid.uuid4())[:8]}"
            
            # Update user with the simulated entity ID
            supabase.table("users").update({
                "method_account_id": method_entity_id
            }).eq("id", user_id).execute()
        
        # Simulate bank account connection
        method_service = MethodAPIService()
        simulated_account = await method_service.simulate_bank_account_connection(
            entity_id=method_entity_id,
            account_type="checking"
        )
        
        return {
            "success": True,
            "message": "🎭 Simulated bank account connected successfully!",
            "account": simulated_account,
            "entity_id": method_entity_id,
            "simulation": True
        }
        
    except Exception as e:
        import traceback
        error_details = f"Error: {str(e)}, Traceback: {traceback.format_exc()}"
        print(f"Simulation error: {error_details}")  # Log to console
        raise HTTPException(status_code=500, detail=f"Failed to simulate bank connection: {str(e)}")

@router.post("/simulate-multiple-accounts")
async def simulate_multiple_bank_accounts(user_id: str = Depends(get_current_user)):
    """
    🎭 SIMULATION: Create multiple simulated bank accounts for comprehensive testing
    
    Creates both checking and savings accounts for the user.
    """
    supabase = get_supabase_client()
    
    try:
        # Get user's Method entity ID
        user_response = supabase.table("users").select("method_account_id").eq("id", user_id).execute()
        
        if not user_response.data or not user_response.data[0]["method_account_id"]:
            raise HTTPException(status_code=400, detail="User does not have a Method entity")
        
        method_entity_id = user_response.data[0]["method_account_id"]
        
        # Simulate multiple bank accounts
        method_service = MethodAPIService()
        simulated_accounts = await method_service.simulate_multiple_bank_accounts(method_entity_id)
        
        return {
            "success": True,
            "message": "🎭 Multiple simulated bank accounts created successfully!",
            "accounts": simulated_accounts["accounts"],
            "total": simulated_accounts["total"],
            "simulation": True
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to simulate multiple bank accounts: {str(e)}")

@router.post("/simulate-credit-cards")
async def simulate_credit_cards(user_id: str = Depends(get_current_user)):
    """
    🎭 SIMULATION: Create multiple simulated credit cards for testing
    
    Creates simulated credit cards from various brands (Visa, Mastercard, Amex, Discover)
    with realistic balances, due dates, and payment information.
    """
    print(f"🔍 Starting credit card simulation for user_id: {user_id}")
    supabase = get_supabase_client()
    
    try:
        # Get user's Method entity ID
        user_response = supabase.table("users").select("method_account_id, email, phone_number").eq("id", user_id).execute()
        
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_response.data[0]
        method_entity_id = user_data.get("method_account_id")
        
        # If user doesn't have a Method entity, create one
        if not method_entity_id:
            method_service = MethodAPIService()
            
            # For simulation, we'll create a mock entity ID
            import uuid
            method_entity_id = f"ent_simulation_{str(uuid.uuid4())[:8]}"
            
            # Update user with the simulated entity ID
            supabase.table("users").update({
                "method_account_id": method_entity_id
            }).eq("id", user_id).execute()
        
        # Create simple simulated credit cards
        import uuid
        
        simulated_cards = {
            "cards": [
                {
                    "id": f"acc_cc_{str(uuid.uuid4())[:8]}",
                    "entity_id": method_entity_id,
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
                        "next_payment_due_date": "2024-03-15T00:00:00Z",
                        "next_payment_minimum_amount": 3000
                    },
                    "_simulation": True
                },
                {
                    "id": f"acc_cc_{str(uuid.uuid4())[:8]}",
                    "entity_id": method_entity_id,
                    "type": "liability",
                    "brand": "mastercard",
                    "last_four": "5555",
                    "name": "Capital One Venture",
                    "status": "active",
                    "balance": 250000,
                    "exp_month": 6,
                    "exp_year": 2026,
                    "liability": {
                        "mch": "5555",
                        "mask": "5555",
                        "name": "Capital One Venture",
                        "type": "credit_card",
                        "balance": 250000,
                        "next_payment_due_date": "2024-03-20T00:00:00Z",
                        "next_payment_minimum_amount": 5000
                    },
                    "_simulation": True
                }
            ],
            "total": 2,
            "_simulation": True
        }
        
        # Store in simulated accounts for retrieval by get_accounts
        from app.services.method_api import _simulated_accounts
        if method_entity_id not in _simulated_accounts:
            _simulated_accounts[method_entity_id] = []
        
        # Add the credit cards to simulated storage
        for card in simulated_cards["cards"]:
            _simulated_accounts[method_entity_id].append(card)
        
        return {
            "success": True,
            "message": "🎭 Simulated credit cards created successfully!",
            "cards": simulated_cards["cards"],
            "total": simulated_cards["total"],
            "entity_id": method_entity_id,
            "simulation": True
        }
        
    except Exception as e:
        import traceback
        error_details = f"Error: {str(e)}, Traceback: {traceback.format_exc()}"
        print(f"Credit card simulation error: {error_details}")  # Log to console
        raise HTTPException(status_code=500, detail=f"Failed to simulate credit cards: {str(e)}")

@router.post("/simulate-full-setup")
async def simulate_full_setup(user_id: str = Depends(get_current_user)):
    """
    🎭 SIMULATION: Complete simulation setup for AgentPay testing
    
    Creates:
    - Method entity (if needed)
    - Simulated bank accounts (checking and savings)
    - Simulated credit cards (Visa, Mastercard, Amex)
    - Sample payment history
    """
    print(f"🔍 Starting full simulation setup for user_id: {user_id}")
    supabase = get_supabase_client()
    
    try:
        # Get user's Method entity ID
        user_response = supabase.table("users").select("method_account_id, email, phone_number").eq("id", user_id).execute()
        
        if not user_response.data:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = user_response.data[0]
        method_entity_id = user_data.get("method_account_id")
        
        # If user doesn't have a Method entity, create one
        if not method_entity_id:
            import uuid
            method_entity_id = f"ent_simulation_{str(uuid.uuid4())[:8]}"
            
            # Update user with the simulated entity ID
            supabase.table("users").update({
                "method_account_id": method_entity_id
            }).eq("id", user_id).execute()
        
        method_service = MethodAPIService()
        
        # 1. Create bank accounts
        bank_accounts = await method_service.simulate_multiple_bank_accounts(method_entity_id)
        
        # 2. Create simple credit cards
        import uuid
        
        credit_cards = {
            "cards": [
                {
                    "id": f"acc_cc_{str(uuid.uuid4())[:8]}",
                    "entity_id": method_entity_id,
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
                        "next_payment_due_date": "2024-03-15T00:00:00Z",
                        "next_payment_minimum_amount": 3000
                    },
                    "_simulation": True
                },
                {
                    "id": f"acc_cc_{str(uuid.uuid4())[:8]}",
                    "entity_id": method_entity_id,
                    "type": "liability",
                    "brand": "mastercard",
                    "last_four": "5555",
                    "name": "Capital One Venture",
                    "status": "active",
                    "balance": 250000,
                    "exp_month": 6,
                    "exp_year": 2026,
                    "liability": {
                        "mch": "5555",
                        "mask": "5555",
                        "name": "Capital One Venture",
                        "type": "credit_card",
                        "balance": 250000,
                        "next_payment_due_date": "2024-03-20T00:00:00Z",
                        "next_payment_minimum_amount": 5000
                    },
                    "_simulation": True
                },
                {
                    "id": f"acc_cc_{str(uuid.uuid4())[:8]}",
                    "entity_id": method_entity_id,
                    "type": "liability",
                    "brand": "amex",
                    "last_four": "1005",
                    "name": "American Express Gold",
                    "status": "active",
                    "balance": 89000,
                    "exp_month": 3,
                    "exp_year": 2028,
                    "liability": {
                        "mch": "1005",
                        "mask": "1005",
                        "name": "American Express Gold",
                        "type": "credit_card",
                        "balance": 89000,
                        "next_payment_due_date": "2024-03-10T00:00:00Z",
                        "next_payment_minimum_amount": 1780
                    },
                    "_simulation": True
                }
            ],
            "total": 3,
            "_simulation": True
        }
        
        # Store credit cards in simulated accounts
        from app.services.method_api import _simulated_accounts
        for card in credit_cards["cards"]:
            _simulated_accounts[method_entity_id].append(card)
        
        return {
            "success": True,
            "message": "🎭 Full AgentPay simulation setup completed!",
            "setup": {
                "entity_id": method_entity_id,
                "bank_accounts": {
                    "accounts": bank_accounts["accounts"],
                    "total": bank_accounts["total"]
                },
                "credit_cards": {
                    "cards": credit_cards["cards"],
                    "total": credit_cards["total"]
                }
            },
            "simulation": True,
            "ready_for_testing": True
        }
        
    except Exception as e:
        import traceback
        error_details = f"Error: {str(e)}, Traceback: {traceback.format_exc()}"
        print(f"Full simulation setup error: {error_details}")  # Log to console
        raise HTTPException(status_code=500, detail=f"Failed to complete simulation setup: {str(e)}")
