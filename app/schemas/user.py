from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: str = Field(..., pattern="^(parent|educator)$")
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response"""
    id: str
    email: str
    role: str
    created_at: datetime
    full_name: Optional[str] = None
    privacy_policy_accepted_at: Optional[datetime] = None


class User(BaseModel):
    """Internal user model"""
    id: str
    email: str
    role: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    full_name: Optional[str] = None
    privacy_policy_accepted_at: Optional[datetime] = None


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
