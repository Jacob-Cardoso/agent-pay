from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CardPreferences(BaseModel):
    """User preferences for a Method API card"""
    id: str
    user_id: str
    method_card_id: str
    autopay_enabled: bool = False
    reminder_days: int = 3
    max_autopay_amount: float = 1000.00
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CardPreferencesCreate(BaseModel):
    method_card_id: str
    autopay_enabled: bool = False
    reminder_days: int = 3
    max_autopay_amount: float = 1000.00

class CardPreferencesUpdate(BaseModel):
    autopay_enabled: Optional[bool] = None
    reminder_days: Optional[int] = None
    max_autopay_amount: Optional[float] = None

class MethodCreditCard(BaseModel):
    """Credit card data from Method API"""
    id: str
    holder_id: str
    status: str
    type: str  # liability, asset
    brand: str  # visa, mastercard, etc.
    last_four: str
    name: Optional[str] = None
    balance: Optional[float] = None
    exp_month: Optional[int] = None
    exp_year: Optional[int] = None
    liability: Optional[dict] = None
    issuer: Optional[dict] = None
    
class CreditCardWithPreferences(BaseModel):
    """Combined Method card data with user preferences"""
    method_card: MethodCreditCard
    preferences: Optional[CardPreferences] = None
    upcoming_bills_count: Optional[int] = None
    total_pending_amount: Optional[float] = None
