from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
import logging

from app.schemas.recommendation import RecommendationResponse
from app.services.ai_service import AIService
from app.dependencies import get_current_user
from app.schemas.user import User

router = APIRouter()
logger = logging.getLogger(__name__)
ai_service = AIService()


@router.get("/children/{child_id}", response_model=RecommendationResponse)
async def get_recommendations(
    child_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get AI-powered module recommendations for a child
    """
    try:
        recommendations = await ai_service.get_recommendations(child_id)
        if not recommendations:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Child not found or insufficient data for recommendations"
            )
        return recommendations
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get recommendations error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendations"
        )


@router.get("/children/{child_id}/next-module")
async def get_next_module(
    child_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get the next recommended module for immediate learning
    """
    try:
        next_module = await ai_service.get_next_module(child_id)
        if not next_module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No suitable module found"
            )
        return next_module
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get next module error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get next module"
        )


@router.post("/children/{child_id}/adjust-difficulty")
async def adjust_difficulty(
    child_id: str,
    module_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Trigger AI to adjust difficulty level for a specific module
    """
    try:
        result = await ai_service.adjust_difficulty_level(child_id, module_id)
        return {
            "message": "Difficulty adjusted successfully",
            "new_level": result["new_level"],
            "reason": result["reason"]
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Adjust difficulty error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to adjust difficulty"
        )