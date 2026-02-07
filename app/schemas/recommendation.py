from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from app.schemas.module import ModuleResponse


class RecommendationReason(BaseModel):
    """Schema for recommendation reasoning"""
    factor: str
    weight: float
    description: str


class RecommendedModule(BaseModel):
    """Schema for a recommended module"""
    module: ModuleResponse
    confidence_score: float  # 0-1
    reasons: List[RecommendationReason]
    expected_difficulty: int


class RecommendationResponse(BaseModel):
    """Schema for recommendations response"""
    child_id: str
    recommended_modules: List[RecommendedModule]
    next_best_module: RecommendedModule
    personalization_level: str  # low, medium, high
    generated_at: datetime
    valid_until: datetime