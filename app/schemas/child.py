from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ChildCreate(BaseModel):
    """Schema for creating a child"""
    name: str = Field(..., min_length=1, max_length=100)
    age: int = Field(..., ge=4, le=10)
    avatar: Optional[str] = None


class ChildUpdate(BaseModel):
    """Schema for updating a child"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    age: Optional[int] = Field(None, ge=4, le=10)
    avatar: Optional[str] = None


class ChildResponse(BaseModel):
    """Schema for child response"""
    id: str
    name: str
    age: int
    avatar: Optional[str] = None
    parent_id: str
    current_level: int = 1
    total_points: int = 0
    created_at: datetime
    updated_at: datetime