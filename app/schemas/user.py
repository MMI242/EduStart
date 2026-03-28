from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


class UserRegister(BaseModel):
    """Schema for user registration"""
    email: EmailStr = Field(..., description="Email valid pengguna")
    password: str = Field(
        ...,
        min_length=8,
        max_length=64,
        description="Password minimal 8 karakter, harus mengandung huruf besar, huruf kecil, dan angka"
    )
    role: str = Field(
        ...,
        pattern="^(parent|educator)$",
        description="Peran pengguna: parent atau educator"
    )
    full_name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=100,
        pattern=r"^[A-Za-z\s]+$",
        description="Nama lengkap pengguna"
    )

    @field_validator('password')
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if not any(char.isupper() for char in v):
            raise ValueError('Password harus mengandung setidaknya satu huruf besar')
        if not any(char.islower() for char in v):
            raise ValueError('Password harus mengandung setidaknya satu huruf kecil')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password harus mengandung setidaknya satu angka')
        return v


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
