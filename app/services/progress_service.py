from typing import List, Optional, Dict
from datetime import datetime, timedelta
import logging

from app.core.supabase_client import get_supabase_client
from app.schemas.progress import (
    ProgressEventCreate,
    ProgressBatchCreate,
    ProgressResponse,
    ProgressSummary,
    ProgressReport,
    SubjectProgress,
    StrengthWeakness
)

logger = logging.getLogger(__name__)


class ProgressService:
    """Service for progress tracking operations"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def record_progress_event(
        self,
        child_id: str,
        progress_data: ProgressEventCreate
    ) -> ProgressResponse:
        """
        Record a single progress event
        """
        try:
            # Calculate points
            points = self._calculate_points(progress_data)
            
            now = datetime.utcnow().isoformat()
            record = {
                "child_id": child_id,
                "module_id": progress_data.module_id,
                "question_id": progress_data.question_id,
                "is_correct": progress_data.is_correct,
                "time_taken_seconds": progress_data.time_taken_seconds,
                "attempt_count": progress_data.attempt_count,
                "points_earned": points,
                "created_at": now
            }
            
            response = self.supabase.table("progress").insert(record).execute()
            
            if not response.data:
                raise ValueError("Failed to record progress")
            
            # Update child's total points
            await self._update_child_points(child_id, points)
            
            logger.info(f"Progress recorded for child {child_id}")
            
            return ProgressResponse(**response.data[0])
            
        except Exception as e:
            logger.error(f"Record progress failed: {str(e)}")
            raise
    
    async def sync_batch_progress(
        self,
        child_id: str,
        batch_data: ProgressBatchCreate
    ) -> Dict[str, int]:
        """
        Sync batch progress from offline mode
        """
        synced_count = 0
        failed_count = 0
        
        for event in batch_data.events:
            try:
                await self.record_progress_event(child_id, event)
                synced_count += 1
            except Exception as e:
                logger.error(f"Failed to sync event: {str(e)}")
                failed_count += 1
        
        logger.info(f"Synced {synced_count} events, {failed_count} failed")
        
        return {
            "synced_count": synced_count,
            "failed_count": failed_count
        }
    
    async def get_progress_summary(
        self,
        child_id: str,
        days: int = 30
    ) -> Optional[ProgressSummary]:
        """
        Get progress summary for a child
        """
        try:
            start_date = (datetime.utcnow() - timedelta(days=days)).isoformat()
            
            # Get progress data
            response = self.supabase.table("progress")\
                .select("*")\
                .eq("child_id", child_id)\
                .gte("created_at", start_date)\
                .execute()
            
            if not response.data:
                return None
            
            data = response.data
            
            # Calculate metrics
            total_time = sum(p["time_taken_seconds"] for p in data) // 60
            total_questions = len(data)
            correct_answers = sum(1 for p in data if p["is_correct"])
            accuracy = (correct_answers / total_questions * 100) if total_questions > 0 else 0
            
            # Get child's total points
            child = self.supabase.table("children")\
                .select("total_points")\
                .eq("id", child_id)\
                .single()\
                .execute()
            
            # Calculate streak
            streak = await self._calculate_streak(child_id)
            
            # Find favorite module type
            module_counts = {}
            for p in data:
                module_response = self.supabase.table("modules")\
                    .select("type")\
                    .eq("id", p["module_id"])\
                    .single()\
                    .execute()
                if module_response.data:
                    module_type = module_response.data["type"]
                    module_counts[module_type] = module_counts.get(module_type, 0) + 1
            
            favorite = max(module_counts, key=module_counts.get) if module_counts else None
            
            # Count completed modules
            completed_modules = len(set(p["module_id"] for p in data))
            
            return ProgressSummary(
                child_id=child_id,
                total_time_minutes=total_time,
                total_modules_completed=completed_modules,
                total_questions_answered=total_questions,
                average_accuracy=round(accuracy, 2),
                current_streak_days=streak,
                total_points=child.data["total_points"] if child.data else 0,
                favorite_module_type=favorite
            )
            
        except Exception as e:
            logger.error(f"Get progress summary failed: {str(e)}")
            return None
    
    async def get_detailed_report(
        self,
        child_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Optional[ProgressReport]:
        """
        Generate detailed progress report
        """
        try:
            if not start_date:
                start_date = datetime.utcnow() - timedelta(days=30)
            if not end_date:
                end_date = datetime.utcnow()
            
            # Get overall summary
            days = (end_date - start_date).days
            summary = await self.get_progress_summary(child_id, days)
            
            if not summary:
                return None
            
            # Get subject-specific progress
            subject_progress = await self._analyze_subject_progress(
                child_id, start_date, end_date
            )
            
            # Analyze strengths and weaknesses
            strengths, weaknesses = await self._analyze_strengths_weaknesses(
                child_id, start_date, end_date
            )
            
            # Get weekly activity
            weekly_activity = await self._get_weekly_activity(
                child_id, start_date, end_date
            )
            
            return ProgressReport(
                child_id=child_id,
                period_start=start_date,
                period_end=end_date,
                overall_summary=summary,
                subject_progress=subject_progress,
                strengths=strengths,
                areas_for_improvement=weaknesses,
                recent_achievements=await self._get_recent_achievements(child_id),
                weekly_activity=weekly_activity,
                generated_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Generate report failed: {str(e)}")
            return None
    
    async def get_progress_history(
        self,
        child_id: str,
        module_id: Optional[str] = None,
        limit: int = 100
    ) -> List[ProgressResponse]:
        """
        Get progress history for a child
        """
        try:
            query = self.supabase.table("progress")\
                .select("*")\
                .eq("child_id", child_id)
            
            if module_id:
                query = query.eq("module_id", module_id)
            
            response = query.order("created_at", desc=True).limit(limit).execute()
            
            return [ProgressResponse(**p) for p in response.data]
            
        except Exception as e:
            logger.error(f"Get progress history failed: {str(e)}")
            return []
    
    def _calculate_points(self, progress_data: ProgressEventCreate) -> int:
        """Calculate points earned for an event"""
        if not progress_data.is_correct:
            return 0
        
        base_points = 10
        
        # Time bonus (faster = more points)
        if progress_data.time_taken_seconds < 10:
            base_points += 5
        elif progress_data.time_taken_seconds < 20:
            base_points += 3
        
        # Attempt penalty
        if progress_data.attempt_count > 1:
            base_points = max(5, base_points - (progress_data.attempt_count - 1) * 2)
        
        return base_points
    
    async def _update_child_points(self, child_id: str, points: int):
        """Update child's total points"""
        try:
            child = self.supabase.table("children")\
                .select("total_points")\
                .eq("id", child_id)\
                .single()\
                .execute()
            
            if child.data:
                new_total = child.data["total_points"] + points
                self.supabase.table("children")\
                    .update({"total_points": new_total})\
                    .eq("id", child_id)\
                    .execute()
        except Exception as e:
            logger.error(f"Update child points failed: {str(e)}")
    
    async def _calculate_streak(self, child_id: str) -> int:
        """Calculate current learning streak in days"""
        # Simplified implementation
        return 0
    
    async def _analyze_subject_progress(
        self,
        child_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[SubjectProgress]:
        """Analyze progress by subject"""
        # Simplified implementation
        return []
    
    async def _analyze_strengths_weaknesses(
        self,
        child_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> tuple:
        """Analyze strengths and weaknesses"""
        # Simplified implementation
        return [], []
    
    async def _get_weekly_activity(
        self,
        child_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, int]:
        """Get activity by day of week"""
        # Simplified implementation
        return {}
    
    async def _get_recent_achievements(self, child_id: str) -> List[str]:
        """Get recent achievements"""
        # Simplified implementation
        return []