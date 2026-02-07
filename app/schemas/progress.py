from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class ProgressEventCreate(BaseModel):
    """Schema for creating a progress event"""
    module_id: str
    question_id: Optional[str] = None
    is_correct: bool
    time_taken_seconds: int = Field(..., ge=0)
    attempt_count: int = Field(default=1, ge=1)


class ProgressBatchCreate(BaseModel):
    """Schema for batch progress sync"""
    events: List[ProgressEventCreate]
    offline_session_id: str
    synced_at: datetime = Field(default_factory=datetime.utcnow)


class ProgressResponse(BaseModel):
    """Schema for progress response"""
    id: str
    child_id: str
    module_id: str
    question_id: Optional[str] = None
    is_correct: bool
    time_taken_seconds: int
    attempt_count: int
    points_earned: int
    created_at: datetime


class ProgressSummary(BaseModel):
    """Schema for progress summary"""
    child_id: str
    total_time_minutes: int
    total_modules_completed: int
    total_questions_answered: int
    average_accuracy: float
    current_streak_days: int
    total_points: int
    favorite_module_type: Optional[str] = None
    most_active_time: Optional[str] = None


class SubjectProgress(BaseModel):
    """Schema for subject-specific progress"""
    subject: str
    accuracy: float
    total_questions: int
    time_spent_minutes: int
    level: int
    progress_percentage: float


class StrengthWeakness(BaseModel):
    """Schema for strength/weakness analysis"""
    category: str
    skill_name: str
    performance_score: float  # 0-100
    recommendation: str


class ProgressReport(BaseModel):
    """Schema for detailed progress report"""
    child_id: str
    period_start: datetime
    period_end: datetime
    overall_summary: ProgressSummary
    subject_progress: List[SubjectProgress]
    strengths: List[StrengthWeakness]
    areas_for_improvement: List[StrengthWeakness]
    recent_achievements: List[str]
    weekly_activity: Dict[str, int]  # day -> minutes
    generated_at: datetime