"""
Child model definition
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ChildModel(BaseModel):
    """Child database model"""
    id: str
    name: str
    age: int
    avatar: Optional[str] = None
    parent_id: str
    current_level: int = 1
    total_points: int = 0
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# SQL Schema
CHILD_TABLE_SCHEMA = """
CREATE TABLE children (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 4 AND age <= 10),
    avatar VARCHAR(500),
    parent_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    current_level INTEGER DEFAULT 1 CHECK (current_level >= 1 AND current_level <= 10),
    total_points INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_children_parent_id ON children(parent_id);

-- Row Level Security
ALTER TABLE children ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Parents can manage their children"
    ON children FOR ALL
    USING (parent_id = auth.uid());
"""