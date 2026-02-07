"""
Progress model definition
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ProgressModel(BaseModel):
    """Progress database model"""
    id: str
    child_id: str
    module_id: str
    question_id: Optional[str] = None
    is_correct: bool
    time_taken_seconds: int
    attempt_count: int = 1
    points_earned: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# SQL Schema
PROGRESS_TABLE_SCHEMA = """
CREATE TABLE progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    child_id UUID NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    module_id UUID NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    question_id UUID REFERENCES questions(id) ON DELETE SET NULL,
    is_correct BOOLEAN NOT NULL,
    time_taken_seconds INTEGER NOT NULL,
    attempt_count INTEGER DEFAULT 1,
    points_earned INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_progress_child_id ON progress(child_id);
CREATE INDEX idx_progress_module_id ON progress(module_id);
CREATE INDEX idx_progress_created_at ON progress(created_at DESC);
CREATE INDEX idx_progress_child_module ON progress(child_id, module_id);

-- Row Level Security
ALTER TABLE progress ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Parents can view their children's progress"
    ON progress FOR SELECT
    USING (
        child_id IN (
            SELECT id FROM children WHERE parent_id = auth.uid()
        )
    );

CREATE POLICY "System can insert progress"
    ON progress FOR INSERT
    WITH CHECK (
        child_id IN (
            SELECT id FROM children WHERE parent_id = auth.uid()
        )
    );
"""