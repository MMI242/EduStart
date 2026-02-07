"""
Analytics model definition for ML data collection
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AnalyticsModel(BaseModel):
    """Analytics database model"""
    id: str
    child_id: str
    module_id: str
    question_id: str
    question_type: str
    difficulty_level: int
    is_correct: bool
    duration_ms: int
    hesitation_ms: int  # Time until first interaction
    timestamp: datetime
    
    class Config:
        from_attributes = True


# SQL Schema
ANALYTICS_TABLE_SCHEMA = """
CREATE TABLE analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    child_id UUID NOT NULL REFERENCES children(id) ON DELETE CASCADE,
    module_id UUID NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    question_id UUID REFERENCES questions(id) ON DELETE SET NULL,
    question_type VARCHAR(50) NOT NULL,
    difficulty_level INTEGER NOT NULL,
    is_correct BOOLEAN NOT NULL,
    duration_ms INTEGER NOT NULL,
    hesitation_ms INTEGER DEFAULT 0,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for ML queries
CREATE INDEX idx_analytics_child_id ON analytics_events(child_id);
CREATE INDEX idx_analytics_module_id ON analytics_events(module_id);
CREATE INDEX idx_analytics_metrics ON analytics_events(is_correct, duration_ms, hesitation_ms);
CREATE INDEX idx_analytics_timestamp ON analytics_events(timestamp DESC);

-- RLS
ALTER TABLE analytics_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "System can insert analytics"
    ON analytics_events FOR INSERT
    WITH CHECK (
        child_id IN (
            SELECT id FROM children WHERE parent_id = auth.uid()
        )
    );

CREATE POLICY "Parents can view own child analytics"
    ON analytics_events FOR SELECT
    USING (
        child_id IN (
            SELECT id FROM children WHERE parent_id = auth.uid()
        )
    );
"""
