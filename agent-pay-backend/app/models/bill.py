from pydantic import BaseModel
from typing import Optional
from datetime import datetime, date
from decimal import Decimal

class BillBase(BaseModel):
    amount: Decimal
    due_date: date
    biller_name: Optional[str] = None
    biller_email: Optional[str] = None

class BillCreate(BillBase):
    user_id: str
    credit_card_id: Optional[str] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None

class BillUpdate(BaseModel):
    credit_card_id: Optional[str] = None
    status: Optional[str] = None
    method_payment_id: Optional[str] = None
    processed_at: Optional[datetime] = None

class Bill(BillBase):
    id: str
    user_id: str
    credit_card_id: Optional[str] = None
    status: str = "pending"  # pending, paid, overdue, failed
    method_payment_id: Optional[str] = None
    email_subject: Optional[str] = None
    email_body: Optional[str] = None
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class BillResponse(Bill):
    """Response model with additional data"""
    credit_card: Optional[dict] = None
    days_until_due: Optional[int] = None
    is_overdue: bool = False

class BillProcessRequest(BaseModel):
    """Request to process a bill email"""
    email_subject: str
    email_body: str
    sender_email: str
    received_at: datetime

