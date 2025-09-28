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

@router.post("/")
async def create_entity(
    entity_data: Dict[str, Any],
    user_id: str = Depends(get_current_user)
):
    """Create a Method entity for the current user"""
    supabase = get_supabase_client()
    
    try:
        # Check if user already has a Method entity
        user_response = supabase.table("users").select("method_account_id").eq("id", user_id).execute()
        
        if user_response.data and user_response.data[0]["method_account_id"]:
            raise HTTPException(status_code=400, detail="User already has a Method entity")
        
        # Create entity via Method API
        method_service = MethodAPIService()
        entity = await method_service.create_entity(
            email=entity_data["email"],
            full_name=entity_data["full_name"],
            phone=entity_data.get("phone")
        )
        
        # Update user record with Method entity ID
        supabase.table("users").update({
            "method_account_id": entity["id"]
        }).eq("id", user_id).execute()
        
        return entity
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create entity: {str(e)}")

@router.get("/me")
async def get_my_entity(user_id: str = Depends(get_current_user)):
    """Get the current user's Method entity"""
    supabase = get_supabase_client()
    
    try:
        # Get user's Method entity ID
        user_response = supabase.table("users").select("method_account_id").eq("id", user_id).execute()
        
        if not user_response.data or not user_response.data[0]["method_account_id"]:
            raise HTTPException(status_code=404, detail="User does not have a Method entity")
        
        method_account_id = user_response.data[0]["method_account_id"]
        
        # Get entity from Method API
        method_service = MethodAPIService()
        entity = await method_service.get_entity(method_account_id)
        return entity
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch entity: {str(e)}")

@router.get("/")
async def list_entities(page: int = 1, page_limit: int = 100):
    """List all entities (admin endpoint)"""
    try:
        method_service = MethodAPIService()
        entities = await method_service.list_entities(page=page, page_limit=page_limit)
        return entities
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list entities: {str(e)}")

@router.put("/me")
async def update_my_entity(
    entity_data: Dict[str, Any],
    user_id: str = Depends(get_current_user)
):
    """Update the current user's Method entity"""
    supabase = get_supabase_client()
    
    try:
        # Get user's Method entity ID
        user_response = supabase.table("users").select("method_account_id").eq("id", user_id).execute()
        
        if not user_response.data or not user_response.data[0]["method_account_id"]:
            raise HTTPException(status_code=404, detail="User does not have a Method entity")
        
        method_account_id = user_response.data[0]["method_account_id"]
        
        # Update entity via Method API
        method_service = MethodAPIService()
        updated_entity = await method_service.update_entity(method_account_id, entity_data)
        return updated_entity
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update entity: {str(e)}")
