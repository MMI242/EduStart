from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Question(BaseModel):
    """Schema for a question in a module"""
    id: str
    question_text: str
    question_type: str  # drag_drop, multiple_choice, audio_guess, coloring, matching
    options: Optional[List[str]] = None
    correct_answer: str
    media_url: Optional[str] = None
    audio_url: Optional[str] = None
    hints: Optional[List[str]] = None
    matching_pairs: Optional[List[Dict[str, str]]] = None  # List of {left: "A", right: "Apple"}


class ModuleResponse(BaseModel):
    """Schema for module list response"""
    id: str
    title: str
    description: str
    type: str  # reading, counting, cognitive
    education_level: str
    difficulty_level: int = Field(..., ge=1, le=10)
    estimated_duration_minutes: int
    thumbnail_url: Optional[str] = None
    total_questions: int
    points_reward: int


class ModuleCreate(BaseModel):
    """Schema for creating a module"""
    title: str
    description: str
    module_type: str
    education_level: str = "TK"
    difficulty_level: int = Field(..., ge=1, le=10)
    estimated_duration_minutes: int = 10
    thumbnail_url: Optional[str] = None
    is_premium: bool = False
    content: Dict[str, Any]  # Should contain 'questions' list


class ModuleUpdate(BaseModel):
    """Schema for updating a module"""
    title: Optional[str] = None
    description: Optional[str] = None
    module_type: Optional[str] = None
    education_level: Optional[str] = None
    difficulty_level: Optional[int] = Field(None, ge=1, le=10)
    estimated_duration_minutes: Optional[int] = None
    thumbnail_url: Optional[str] = None
    is_premium: Optional[bool] = None
    content: Optional[Dict[str, Any]] = None


class ModuleDetail(ModuleResponse):
    """Schema for detailed module with questions"""
    questions: List[Question]
    prerequisites: Optional[List[str]] = None
    learning_objectives: List[str]
    created_at: datetime
    updated_at: datetime


class ModuleDownload(BaseModel):
    """Schema for module download data"""
    module_id: str
    download_url: Optional[str] = None
    offline_data: Dict[str, Any]
    size_mb: float
    version: str