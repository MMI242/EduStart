import numpy as np
from typing import Dict, List, Any
from datetime import datetime, timedelta
import logging

from app.schemas.recommendation import RecommendationReason

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    Recommendation engine for personalized module suggestions
    """
    
    def __init__(self):
        self.weights = {
            "accuracy_match": 0.3,
            "difficulty_progression": 0.25,
            "variety": 0.15,
            "engagement_history": 0.15,
            "time_since_last": 0.15
        }
    
    async def generate_recommendations(
        self,
        child_data: Dict[str, Any],
        progress_analysis: Dict[str, Any],
        available_modules: List[Dict[str, Any]],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate personalized module recommendations
        
        Returns:
            List of recommendations with confidence scores and reasons
        """
        recommendations = []
        
        # Calculate scores for each module
        for module in available_modules:
            score, reasons = self._calculate_module_score(
                module=module,
                child_data=child_data,
                progress_analysis=progress_analysis
            )
            
            if score > 0.3:  # Threshold for recommendation
                recommendations.append({
                    "module_id": module["id"],
                    "confidence": score,
                    "reasons": reasons,
                    "expected_difficulty": self._predict_difficulty(
                        module, progress_analysis
                    )
                })
        
        # Sort by confidence score
        recommendations.sort(key=lambda x: x["confidence"], reverse=True)
        
        # Apply diversity filter
        recommendations = self._apply_diversity_filter(recommendations, limit)
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        
        return recommendations[:limit]
    
    def _calculate_module_score(
        self,
        module: Dict[str, Any],
        child_data: Dict[str, Any],
        progress_analysis: Dict[str, Any]
    ) -> tuple:
        """
        Calculate recommendation score for a module
        
        Returns:
            Tuple of (score, reasons)
        """
        reasons = []
        scores = {}
        
        # 1. Accuracy match - recommend modules at appropriate difficulty
        module_performance = progress_analysis.get("module_performance", {})
        module_type = module["type"]
        
        if module_type in module_performance:
            type_accuracy = module_performance[module_type]["accuracy"]
            avg_difficulty = module_performance[module_type]["avg_difficulty"]
            
            # Score based on how well difficulty matches performance
            difficulty_diff = abs(module["difficulty_level"] - avg_difficulty)
            
            if type_accuracy > 0.8 and module["difficulty_level"] >= avg_difficulty:
                scores["accuracy_match"] = 0.9
                reasons.append(RecommendationReason(
                    factor="high_performance",
                    weight=0.9,
                    description=f"You're doing great with {module_type}! Ready for more challenges."
                ))
            elif 0.6 <= type_accuracy <= 0.8 and difficulty_diff <= 1:
                scores["accuracy_match"] = 0.7
                reasons.append(RecommendationReason(
                    factor="good_fit",
                    weight=0.7,
                    description=f"Perfect difficulty level for your {module_type} skills."
                ))
            else:
                scores["accuracy_match"] = 0.5
        else:
            # New module type - moderate score
            scores["accuracy_match"] = 0.6
            reasons.append(RecommendationReason(
                factor="new_subject",
                weight=0.6,
                description=f"Explore something new with {module_type}!"
            ))
        
        # 2. Difficulty progression
        current_level = child_data.get("current_level", 1)
        level_diff = module["difficulty_level"] - current_level
        
        if -1 <= level_diff <= 1:
            scores["difficulty_progression"] = 0.9
        elif -2 <= level_diff <= 2:
            scores["difficulty_progression"] = 0.7
        else:
            scores["difficulty_progression"] = 0.4
        
        # 3. Variety score - encourage trying different types
        recent_types = self._get_recent_module_types(progress_analysis)
        if module_type not in recent_types[:3]:
            scores["variety"] = 0.8
            reasons.append(RecommendationReason(
                factor="variety",
                weight=0.8,
                description="Try something different to keep learning fun!"
            ))
        else:
            scores["variety"] = 0.5
        
        # 4. Engagement history
        learning_velocity = progress_analysis.get("learning_velocity", 0)
        if learning_velocity > 0.1:
            scores["engagement_history"] = 0.9
            reasons.append(RecommendationReason(
                factor="positive_trend",
                weight=0.9,
                description="You're improving fast! Keep up the momentum."
            ))
        else:
            scores["engagement_history"] = 0.6
        
        # 5. Time-based factor
        scores["time_since_last"] = 0.7  # Default
        
        # Calculate weighted final score
        final_score = sum(
            scores.get(factor, 0.5) * weight
            for factor, weight in self.weights.items()
        )
        
        return final_score, reasons
    
    def _predict_difficulty(
        self,
        module: Dict[str, Any],
        progress_analysis: Dict[str, Any]
    ) -> int:
        """
        Predict perceived difficulty for the child
        """
        base_difficulty = module["difficulty_level"]
        
        # Adjust based on child's performance in this type
        module_performance = progress_analysis.get("module_performance", {})
        module_type = module["type"]
        
        if module_type in module_performance:
            type_accuracy = module_performance[module_type]["accuracy"]
            
            # If child is good at this type, effective difficulty is lower
            if type_accuracy > 0.8:
                return max(1, base_difficulty - 1)
            elif type_accuracy < 0.5:
                return min(10, base_difficulty + 1)
        
        return base_difficulty
    
    def _get_recent_module_types(
        self,
        progress_analysis: Dict[str, Any],
        limit: int = 5
    ) -> List[str]:
        """Get recently attempted module types"""
        module_performance = progress_analysis.get("module_performance", {})
        
        # Sort by recent activity (simplified)
        types = list(module_performance.keys())
        return types[:limit]
    
    def _apply_diversity_filter(
        self,
        recommendations: List[Dict[str, Any]],
        limit: int
    ) -> List[Dict[str, Any]]:
        """
        Ensure diversity in recommended modules
        """
        if len(recommendations) <= limit:
            return recommendations
        
        filtered = []
        used_types = set()
        
        # First pass: one of each type
        for rec in recommendations:
            module_id = rec["module_id"]
            # In real implementation, fetch module type
            # For now, just add based on score
            if len(filtered) < limit:
                filtered.append(rec)
        
        return filtered


class CollaborativeFilter:
    """
    Collaborative filtering for recommendations based on similar children
    """
    
    @staticmethod
    def find_similar_children(
        child_profile: Dict[str, Any],
        all_children_data: List[Dict[str, Any]],
        top_k: int = 10
    ) -> List[str]:
        """
        Find children with similar learning patterns
        
        Returns:
            List of similar child IDs
        """
        # Calculate similarity scores
        similarities = []
        
        for other_child in all_children_data:
            if other_child["id"] == child_profile["id"]:
                continue
            
            similarity = CollaborativeFilter._calculate_similarity(
                child_profile,
                other_child
            )
            
            similarities.append((other_child["id"], similarity))
        
        # Sort by similarity and return top k
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return [child_id for child_id, _ in similarities[:top_k]]
    
    @staticmethod
    def _calculate_similarity(
        child1: Dict[str, Any],
        child2: Dict[str, Any]
    ) -> float:
        """
        Calculate similarity between two children
        Uses age, performance, and preferences
        """
        similarity = 0.0
        
        # Age similarity
        age_diff = abs(child1.get("age", 0) - child2.get("age", 0))
        age_similarity = max(0, 1 - (age_diff / 6))
        similarity += age_similarity * 0.3
        
        # Level similarity
        level_diff = abs(child1.get("current_level", 0) - child2.get("current_level", 0))
        level_similarity = max(0, 1 - (level_diff / 10))
        similarity += level_similarity * 0.4
        
        # Performance similarity (if available)
        # This would require comparing their progress patterns
        similarity += 0.3  # Placeholder
        
        return similarity