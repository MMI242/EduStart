import numpy as np
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class AdaptiveLearningModel:
    """
    Adaptive learning model for personalized difficulty adjustment
    """
    
    def __init__(self):
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load or initialize the ML model"""
        try:
            # In production, load a trained model
            # self.model = tf.keras.models.load_model(settings.ML_MODEL_PATH)
            logger.info("Adaptive learning model initialized")
        except Exception as e:
            logger.warning(f"Could not load model, using rule-based system: {str(e)}")
    
    def predict_optimal_difficulty(
        self,
        child_age: int,
        current_level: int,
        accuracy: float,
        avg_time_seconds: float,
        learning_velocity: float
    ) -> int:
        """
        Predict optimal difficulty level for a child
        
        Args:
            child_age: Age of the child (4-10)
            current_level: Current difficulty level (1-10)
            accuracy: Recent accuracy rate (0-1)
            avg_time_seconds: Average time per question
            learning_velocity: Rate of improvement
        
        Returns:
            Recommended difficulty level (1-10)
        """
        # Rule-based approach (can be replaced with ML model)
        
        # Normalize inputs
        age_factor = (child_age - 4) / 6  # Normalize to 0-1
        
        # Calculate performance score
        performance_score = (
            accuracy * 0.5 +
            (1 - min(avg_time_seconds / 60, 1)) * 0.3 +
            max(0, learning_velocity) * 0.2
        )
        
        # Adjust difficulty based on performance
        if performance_score > 0.8:
            # High performance - increase difficulty
            recommended_level = min(10, current_level + 1)
        elif performance_score > 0.6:
            # Good performance - maintain or slightly increase
            recommended_level = min(10, current_level + 0.5)
        elif performance_score > 0.4:
            # Moderate performance - maintain level
            recommended_level = current_level
        else:
            # Low performance - decrease difficulty
            recommended_level = max(1, current_level - 1)
        
        # Consider age appropriateness
        max_age_level = int(4 + (age_factor * 6))
        recommended_level = min(recommended_level, max_age_level)
        
        return int(round(recommended_level))
    
    def calculate_engagement_score(
        self,
        session_duration_minutes: int,
        completion_rate: float,
        return_rate: float
    ) -> float:
        """
        Calculate child's engagement score (0-1)
        
        Args:
            session_duration_minutes: Average session duration
            completion_rate: Module completion rate (0-1)
            return_rate: How often child returns (0-1)
        
        Returns:
            Engagement score between 0 and 1
        """
        # Normalize session duration (target: 15-30 minutes)
        duration_score = min(session_duration_minutes / 30, 1)
        
        # Calculate weighted engagement score
        engagement_score = (
            duration_score * 0.3 +
            completion_rate * 0.4 +
            return_rate * 0.3
        )
        
        return min(max(engagement_score, 0), 1)
    
    def predict_next_session_time(
        self,
        historical_sessions: List[datetime]
    ) -> Optional[datetime]:
        """
        Predict when child is likely to engage next
        
        Args:
            historical_sessions: List of previous session timestamps
        
        Returns:
            Predicted next session time
        """
        if len(historical_sessions) < 3:
            return None
        
        # Calculate time differences
        intervals = []
        for i in range(1, len(historical_sessions)):
            delta = (historical_sessions[i] - historical_sessions[i-1]).total_seconds() / 3600
            intervals.append(delta)
        
        # Predict next session (simple average)
        avg_interval_hours = np.mean(intervals)
        predicted_time = historical_sessions[-1] + timedelta(hours=avg_interval_hours)
        
        return predicted_time


class SkillLevelEstimator:
    """
    Estimates child's skill level in different subjects
    """
    
    @staticmethod
    def estimate_skill_level(
        progress_data: List[Dict[str, Any]],
        subject: str
    ) -> Dict[str, Any]:
        """
        Estimate skill level for a specific subject
        
        Returns:
            Dictionary with skill level, confidence, and details
        """
        subject_progress = [p for p in progress_data if p.get("subject") == subject]
        
        if not subject_progress:
            return {
                "level": 1,
                "confidence": 0.0,
                "ready_for_next": False
            }
        
        # Calculate metrics
        total = len(subject_progress)
        correct = sum(1 for p in subject_progress if p["is_correct"])
        accuracy = correct / total
        
        avg_difficulty = np.mean([p.get("difficulty", 1) for p in subject_progress])
        
        # Estimate level
        if accuracy > 0.85:
            estimated_level = min(10, int(avg_difficulty) + 1)
            ready_for_next = True
        elif accuracy > 0.70:
            estimated_level = int(avg_difficulty)
            ready_for_next = True
        else:
            estimated_level = max(1, int(avg_difficulty) - 1)
            ready_for_next = False
        
        # Confidence based on sample size
        confidence = min(total / 20, 1.0)
        
        return {
            "level": estimated_level,
            "confidence": confidence,
            "accuracy": accuracy,
            "ready_for_next": ready_for_next,
            "sample_size": total
        }


from datetime import timedelta

class LearningPathGenerator:
    """
    Generates personalized learning paths
    """
    
    @staticmethod
    def generate_learning_path(
        child_data: Dict[str, Any],
        skill_levels: Dict[str, int],
        available_modules: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate a sequence of recommended modules
        
        Returns:
            List of module IDs in recommended order
        """
        learning_path = []
        
        # Group modules by subject and difficulty
        modules_by_subject = {}
        for module in available_modules:
            subject = module["type"]
            if subject not in modules_by_subject:
                modules_by_subject[subject] = []
            modules_by_subject[subject].append(module)
        
        # For each subject, recommend modules at appropriate level
        for subject, current_level in skill_levels.items():
            if subject in modules_by_subject:
                # Get modules at or slightly above current level
                suitable_modules = [
                    m for m in modules_by_subject[subject]
                    if current_level <= m["difficulty_level"] <= current_level + 2
                ]
                
                # Sort by difficulty
                suitable_modules.sort(key=lambda x: x["difficulty_level"])
                
                # Add to learning path
                for module in suitable_modules[:3]:  # Top 3 per subject
                    learning_path.append(module["id"])
        
        return learning_path