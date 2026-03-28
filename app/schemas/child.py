from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ChildCreate(BaseModel):
    """Schema for creating a child"""
    name: str = Field(
        ..., 
        min_length=2, 
        max_length=100,
        pattern=r"^[A-Za-z\s]+$",
        description="Nama anak"
    )
    age: int = Field(
        ..., 
        ge=4, 
        le=10,
        description="Umur anak harus antara 4 hingga 10 tahun"
    )
    avatar: Optional[str] = Field(None, description="URL untuk foto profil/avatar anak")


class ChildUpdate(BaseModel):
    """Schema for updating a child"""
    name: Optional[str] = Field(
        None, 
        min_length=2, 
        max_length=100,
        pattern=r"^[A-Za-z\s]+$",
        description="Nama anak"
    )
    age: Optional[int] = Field(
        None, 
        ge=4, 
        le=10,
        description="Umur anak harus antara 4 hingga 10 tahun"
    )
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
