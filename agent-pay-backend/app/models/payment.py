from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class PaymentCreate(BaseModel):
    """Model for creating a payment via Method API"""
    amount: int = Field(..., description="Payment amount in cents (e.g. $1.00 = 100)")
    source: str = Field(..., description="ID of source account (bank account)")
    destination: str = Field(..., description="ID of destination account (credit card/loan)")
    description: str = Field(..., max_length=100, description="Payment description (max 100 chars)")
    dry_run: Optional[bool] = Field(False, description="If true, simulates payment without processing")

class PaymentResponse(BaseModel):
    """Method API Payment response model"""
    id: str
    source: str
    destination: str
    amount: int
    description: str
    status: str
    estimated_completion_date: Optional[str] = None
    source_trace_id: Optional[str] = None
    source_settlement_date: Optional[str] = None
    source_status: Optional[str] = None
    destination_trace_id: Optional[str] = None
    destination_settlement_date: Optional[str] = None
    destination_payment_method: Optional[str] = None
    destination_status: Optional[str] = None
    reversal_id: Optional[str] = None
    error: Optional[dict] = None
    metadata: Optional[dict] = None
    created_at: str
    updated_at: str

class PaymentListResponse(BaseModel):
    """Method API Payment list response"""
    data: list[PaymentResponse]

class PaymentSimulation(BaseModel):
    """Model for simulating payment status changes"""
    status: str = Field(..., description="New payment status (processing, completed, failed, etc.)")
    error_code: Optional[str] = Field(None, description="Error code for failed payments")

# Legacy models for backward compatibility
class Payment(BaseModel):
    id: str
    user_id: str
    bill_id: str
    credit_card_id: str
    amount: float
    status: str
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

class PaymentCreateLegacy(BaseModel):
    bill_id: str
    credit_card_id: str
    amount: float
