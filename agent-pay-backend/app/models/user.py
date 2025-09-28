from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[str] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    method_account_id: Optional[str] = None

class User(UserBase):
    id: str
    method_account_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserSettings(BaseModel):
    id: str
    user_id: str
    autopay_enabled: bool = True
    default_reminder_days: int = 3
    email_notifications: bool = True
    sms_notifications: bool = False
    max_autopay_amount: float = 1000.00
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserSettingsUpdate(BaseModel):
    autopay_enabled: Optional[bool] = None
    default_reminder_days: Optional[int] = None
    email_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    max_autopay_amount: Optional[float] = None

class UserProfile(User):
    """Extended user profile with settings"""
    settings: Optional[UserSettings] = None
