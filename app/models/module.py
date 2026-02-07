"""
Module model definition
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class ModuleModel(BaseModel):
    """Learning module database model"""
    id: str
    title: str
    description: str
    type: str  # 'reading', 'counting', 'cognitive'
    education_level: str  # 'TK', 'SD1', 'SD2', 'SD3', 'SD4', 'SD5', 'SD6', 'SMP', 'SMA'
    difficulty_level: int
    estimated_duration_minutes: int
    thumbnail_url: Optional[str] = None
    total_questions: int
    points_reward: int
    prerequisites: Optional[List[str]] = None
    learning_objectives: List[str]
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    
    class Config:
        from_attributes = True


# SQL Schema
MODULE_TABLE_SCHEMA = """
CREATE TABLE modules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(200) NOT NULL,
    description TEXT,
    type VARCHAR(50) NOT NULL CHECK (type IN ('reading', 'counting', 'cognitive')),
    education_level VARCHAR(20) DEFAULT 'TK',
    difficulty_level INTEGER NOT NULL CHECK (difficulty_level >= 1 AND difficulty_level <= 10),
    estimated_duration_minutes INTEGER DEFAULT 15,
    thumbnail_url VARCHAR(500),
    total_questions INTEGER DEFAULT 0,
    points_reward INTEGER DEFAULT 100,
    prerequisites JSONB,
    learning_objectives JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE
);

-- Indexes
CREATE INDEX idx_modules_type ON modules(type);
CREATE INDEX idx_modules_education_level ON modules(education_level);
CREATE INDEX idx_modules_difficulty ON modules(difficulty_level);
CREATE INDEX idx_modules_active ON modules(is_active);

-- Row Level Security (public read)
ALTER TABLE modules ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Anyone can view active modules"
    ON modules FOR SELECT
    USING (is_active = TRUE);
"""


class QuestionModel(BaseModel):
    """Question database model"""
    id: str
    module_id: str
    question_text: str
    question_type: str
    options: Optional[List[str]] = None
    correct_answer: str
    media_url: Optional[str] = None
    audio_url: Optional[str] = None
    hints: Optional[List[str]] = None
    sequence_order: int
    points: int = 10
    created_at: datetime
    
    class Config:
        from_attributes = True


QUESTION_TABLE_SCHEMA = """
CREATE TABLE questions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    module_id UUID NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) NOT NULL CHECK (question_type IN ('drag_drop', 'multiple_choice', 'audio_guess', 'coloring')),
    options JSONB,
    correct_answer TEXT NOT NULL,
    media_url VARCHAR(500),
    audio_url VARCHAR(500),
    hints JSONB,
    sequence_order INTEGER NOT NULL,
    points INTEGER DEFAULT 10,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_questions_module_id ON questions(module_id);
CREATE INDEX idx_questions_sequence ON questions(module_id, sequence_order);
"""