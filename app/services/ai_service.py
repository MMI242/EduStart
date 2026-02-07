from typing import List, Optional, Dict, Any
import logging
from datetime import datetime, timedelta
import numpy as np

from app.core.supabase_client import get_supabase_client
from app.schemas.recommendation import (
    RecommendationResponse,
    RecommendedModule,
    RecommendationReason
)
from app.schemas.module import ModuleResponse
from app.core.config import settings
from app.ml.adaptive_model import AdaptiveLearningModel
from app.ml.recommendation_engine import RecommendationEngine

logger = logging.getLogger(__name__)


class AIService:
    """Service for AI-powered adaptive learning and recommendations"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
        self.adaptive_model = AdaptiveLearningModel()
        self.recommendation_engine = RecommendationEngine()
    
    async def get_recommendations(self, child_id: str) -> Optional[RecommendationResponse]:
        """
        Get personalized module recommendations for a child
        """
        try:
            # Get child data
            child = self.supabase.table("children")\
                .select("*")\
                .eq("id", child_id)\
                .single()\
                .execute()
            
            if not child.data:
                return None
            
            # Get child's progress history
            progress = self.supabase.table("progress")\
                .select("*")\
                .eq("child_id", child_id)\
                .order("created_at", desc=True)\
                .limit(100)\
                .execute()
            
            # Check if we have enough data for personalization
            if len(progress.data) < settings.ML_MIN_DATA_POINTS:
                # Return beginner modules
                return await self._get_beginner_recommendations(child_id, child.data)
            
            # Analyze progress data
            analysis = self._analyze_progress_data(progress.data)
            
            # Get all available modules
            modules = self.supabase.table("modules")\
                .select("*")\
                .execute()
            
            # Generate recommendations using ML model
            recommendations = await self.recommendation_engine.generate_recommendations(
                child_data=child.data,
                progress_analysis=analysis,
                available_modules=modules.data
            )
            
            # Convert to response format
            recommended_modules = []
            for rec in recommendations:
                module_data = next((m for m in modules.data if m["id"] == rec["module_id"]), None)
                if module_data:
                    recommended_modules.append(
                        RecommendedModule(
                            module=ModuleResponse(**module_data),
                            confidence_score=rec["confidence"],
                            reasons=rec["reasons"],
                            expected_difficulty=rec["expected_difficulty"]
                        )
                    )
            
            # Determine personalization level
            personalization_level = "high" if len(progress.data) > 50 else \
                                   "medium" if len(progress.data) > 20 else "low"
            
            logger.info(f"Generated {len(recommended_modules)} recommendations for child {child_id}")
            
            return RecommendationResponse(
                child_id=child_id,
                recommended_modules=recommended_modules,
                next_best_module=recommended_modules[0] if recommended_modules else None,
                personalization_level=personalization_level,
                generated_at=datetime.utcnow(),
                valid_until=datetime.utcnow() + timedelta(hours=24)
            )
            
        except Exception as e:
            logger.error(f"Get recommendations failed: {str(e)}")
            return None
    
    async def get_next_module(self, child_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the next best module for immediate learning
        """
        try:
            recommendations = await self.get_recommendations(child_id)
            
            if not recommendations or not recommendations.next_best_module:
                return None
            
            next_module = recommendations.next_best_module
            
            return {
                "module": next_module.module.dict(),
                "confidence": next_module.confidence_score,
                "reasons": [r.dict() for r in next_module.reasons],
                "estimated_difficulty": next_module.expected_difficulty
            }
            
        except Exception as e:
            logger.error(f"Get next module failed: {str(e)}")
            return None
    
    async def adjust_difficulty_level(
        self,
        child_id: str,
        module_id: str
    ) -> Dict[str, Any]:
        """
        Adjust difficulty level based on recent performance
        """
        try:
            # Get recent progress for this module
            recent_progress = self.supabase.table("progress")\
                .select("*")\
                .eq("child_id", child_id)\
                .eq("module_id", module_id)\
                .order("created_at", desc=True)\
                .limit(10)\
                .execute()
            
            if not recent_progress.data:
                raise ValueError("No progress data found for this module")
            
            # Calculate performance metrics
            data = recent_progress.data
            accuracy = sum(1 for p in data if p["is_correct"]) / len(data)
            avg_time = sum(p["time_taken_seconds"] for p in data) / len(data)
            
            # Get current module difficulty
            module = self.supabase.table("modules")\
                .select("difficulty_level")\
                .eq("id", module_id)\
                .single()\
                .execute()
            
            current_level = module.data["difficulty_level"]
            
            # Determine new difficulty level
            new_level, reason = self._calculate_new_difficulty(
                current_level=current_level,
                accuracy=accuracy,
                avg_time=avg_time,
                attempt_count=len(data)
            )
            
            logger.info(f"Adjusted difficulty for child {child_id}, module {module_id}: {current_level} -> {new_level}")
            
            return {
                "new_level": new_level,
                "previous_level": current_level,
                "reason": reason,
                "performance_metrics": {
                    "accuracy": round(accuracy * 100, 2),
                    "avg_time_seconds": round(avg_time, 2)
                }
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Adjust difficulty failed: {str(e)}")
            raise
    
    async def _get_beginner_recommendations(
        self,
        child_id: str,
        child_data: Dict[str, Any]
    ) -> RecommendationResponse:
        """
        Get beginner-level recommendations for new users
        """
        age = child_data["age"]
        
        # Get age-appropriate beginner modules
        modules = self.supabase.table("modules")\
            .select("*")\
            .lte("difficulty_level", 3)\
            .limit(5)\
            .execute()
        
        recommended_modules = []
        for i, module_data in enumerate(modules.data):
            reasons = [
                RecommendationReason(
                    factor="age_appropriate",
                    weight=1.0,
                    description=f"Suitable for age {age}"
                ),
                RecommendationReason(
                    factor="beginner_level",
                    weight=0.9,
                    description="Great for starting your learning journey"
                )
            ]
            
            recommended_modules.append(
                RecommendedModule(
                    module=ModuleResponse(**module_data),
                    confidence_score=0.8 - (i * 0.1),
                    reasons=reasons,
                    expected_difficulty=module_data["difficulty_level"]
                )
            )
        
        return RecommendationResponse(
            child_id=child_id,
            recommended_modules=recommended_modules,
            next_best_module=recommended_modules[0] if recommended_modules else None,
            personalization_level="low",
            generated_at=datetime.utcnow(),
            valid_until=datetime.utcnow() + timedelta(hours=24)
        )
    
    def _analyze_progress_data(self, progress_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze progress data to extract learning patterns
        """
        if not progress_data:
            return {}
        
        # Calculate overall metrics
        total_questions = len(progress_data)
        correct_answers = sum(1 for p in progress_data if p["is_correct"])
        accuracy = correct_answers / total_questions if total_questions > 0 else 0
        
        # Calculate average time
        avg_time = sum(p["time_taken_seconds"] for p in progress_data) / total_questions
        
        # Group by module type
        module_performance = {}
        for progress in progress_data:
            module_id = progress["module_id"]
            
            # Get module info
            module = self.supabase.table("modules")\
                .select("type, difficulty_level")\
                .eq("id", module_id)\
                .single()\
                .execute()
            
            if module.data:
                module_type = module.data["type"]
                if module_type not in module_performance:
                    module_performance[module_type] = {
                        "attempts": 0,
                        "correct": 0,
                        "total_time": 0,
                        "difficulty_levels": []
                    }
                
                module_performance[module_type]["attempts"] += 1
                if progress["is_correct"]:
                    module_performance[module_type]["correct"] += 1
                module_performance[module_type]["total_time"] += progress["time_taken_seconds"]
                module_performance[module_type]["difficulty_levels"].append(module.data["difficulty_level"])
        
        # Calculate accuracy by module type
        for module_type, perf in module_performance.items():
            perf["accuracy"] = perf["correct"] / perf["attempts"] if perf["attempts"] > 0 else 0
            perf["avg_time"] = perf["total_time"] / perf["attempts"] if perf["attempts"] > 0 else 0
            perf["avg_difficulty"] = np.mean(perf["difficulty_levels"]) if perf["difficulty_levels"] else 0
        
        # Identify learning velocity (improvement rate)
        recent_accuracy = self._calculate_recent_accuracy(progress_data[-10:])
        older_accuracy = self._calculate_recent_accuracy(progress_data[:10])
        learning_velocity = recent_accuracy - older_accuracy
        
        return {
            "overall_accuracy": accuracy,
            "avg_time_seconds": avg_time,
            "total_attempts": total_questions,
            "module_performance": module_performance,
            "learning_velocity": learning_velocity,
            "consistency_score": self._calculate_consistency(progress_data)
        }
    
    def _calculate_recent_accuracy(self, progress_data: List[Dict[str, Any]]) -> float:
        """Calculate accuracy for a subset of progress data"""
        if not progress_data:
            return 0.0
        correct = sum(1 for p in progress_data if p["is_correct"])
        return correct / len(progress_data)
    
    def _calculate_consistency(self, progress_data: List[Dict[str, Any]]) -> float:
        """Calculate learning consistency score (0-1)"""
        if len(progress_data) < 7:
            return 0.5
        
        # Group by date
        dates = {}
        for p in progress_data:
            date = p["created_at"][:10]  # Extract date part
            dates[date] = dates.get(date, 0) + 1
        
        # Calculate standard deviation of daily activity
        daily_counts = list(dates.values())
        if len(daily_counts) < 2:
            return 0.5
        
        std_dev = np.std(daily_counts)
        mean_count = np.mean(daily_counts)
        
        # Lower std_dev relative to mean = higher consistency
        consistency = max(0, 1 - (std_dev / (mean_count + 1)))
        
        return consistency
    
    def _calculate_new_difficulty(
        self,
        current_level: int,
        accuracy: float,
        avg_time: float,
        attempt_count: int
    ) -> tuple:
        """
        Calculate new difficulty level based on performance
        """
        # Decision logic
        if accuracy >= 0.85 and avg_time < 15:
            # Excellent performance - increase difficulty
            new_level = min(10, current_level + 1)
            reason = "Excellent performance! Time for a bigger challenge."
        elif accuracy >= 0.70 and accuracy < 0.85:
            # Good performance - maintain level
            new_level = current_level
            reason = "Great job! Keep practicing at this level."
        elif accuracy >= 0.50 and accuracy < 0.70:
            # Moderate performance - maintain or decrease slightly
            if attempt_count >= 15:
                new_level = max(1, current_level - 1)
                reason = "Let's practice some fundamentals to build confidence."
            else:
                new_level = current_level
                reason = "Keep trying! You're making progress."
        else:
            # Poor performance - decrease difficulty
            new_level = max(1, current_level - 1)
            reason = "Let's work on building a strong foundation first."
        
        # Consider time factor
        if avg_time > 30:
            new_level = max(1, new_level - 1)
            reason += " Taking your time is good, let's ensure understanding."
        
        return new_level, reason


class PerformanceAnalyzer:
    """Utility class for analyzing learning performance"""
    
    @staticmethod
    def identify_struggling_areas(progress_data: List[Dict[str, Any]]) -> List[str]:
        """Identify areas where child is struggling"""
        struggling_areas = []
        
        # Group by module type and analyze
        module_groups = {}
        for p in progress_data:
            module_type = p.get("module_type", "unknown")
            if module_type not in module_groups:
                module_groups[module_type] = []
            module_groups[module_type].append(p)
        
        for module_type, data in module_groups.items():
            accuracy = sum(1 for p in data if p["is_correct"]) / len(data)
            if accuracy < 0.6:
                struggling_areas.append(module_type)
        
        return struggling_areas
    
    @staticmethod
    def identify_strengths(progress_data: List[Dict[str, Any]]) -> List[str]:
        """Identify child's strengths"""
        strengths = []
        
        module_groups = {}
        for p in progress_data:
            module_type = p.get("module_type", "unknown")
            if module_type not in module_groups:
                module_groups[module_type] = []
            module_groups[module_type].append(p)
        
        for module_type, data in module_groups.items():
            accuracy = sum(1 for p in data if p["is_correct"]) / len(data)
            if accuracy >= 0.85:
                strengths.append(module_type)
        
        return strengths