"""
User model definition
Note: Actual table is managed by Supabase
This is for reference and type hints
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class UserModel(BaseModel):
    """User database model"""
    id: str
    email: str
    role: str  # 'parent' or 'educator'
    full_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    is_active: bool = True
    privacy_policy_accepted_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# SQL Schema for reference
USER_TABLE_SCHEMA = """
CREATE TABLE users (
    id UUID PRIMARY KEY REFERENCES auth.users(id),
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('parent', 'educator')),
    full_name VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    privacy_policy_accepted_at TIMESTAMP WITH TIME ZONE
);

-- Row Level Security
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
    ON users FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON users FOR UPDATE
    USING (auth.uid() = id);
"""