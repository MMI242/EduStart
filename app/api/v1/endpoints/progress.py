from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from datetime import datetime
import logging

from app.schemas.progress import (
    ProgressEventCreate,
    ProgressBatchCreate,
    ProgressResponse,
    ProgressSummary,
    ProgressReport
)
from app.services.progress_service import ProgressService
from app.dependencies import get_current_user, get_current_parent
from app.schemas.user import User

router = APIRouter()
logger = logging.getLogger(__name__)
progress_service = ProgressService()


@router.post("/children/{child_id}/events", response_model=ProgressResponse, status_code=status.HTTP_201_CREATED)
async def record_progress(
    child_id: str,
    progress_data: ProgressEventCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Record a single learning progress event
    """
    try:
        progress = await progress_service.record_progress_event(child_id, progress_data)
        return progress
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Record progress error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to record progress"
        )


@router.post("/children/{child_id}/sync", status_code=status.HTTP_201_CREATED)
async def sync_offline_progress(
    child_id: str,
    batch_data: ProgressBatchCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Sync batch progress data from offline mode
    """
    try:
        result = await progress_service.sync_batch_progress(child_id, batch_data)
        return {
            "message": "Progress synced successfully",
            "synced_count": result["synced_count"],
            "failed_count": result["failed_count"]
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Sync progress error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to sync progress"
        )


@router.get("/children/{child_id}/summary", response_model=ProgressSummary)
async def get_progress_summary(
    child_id: str,
    days: int = Query(30, ge=1, le=365, description="Number of days to include in summary"),
    current_user: User = Depends(get_current_parent)
):
    """
    Get progress summary for a child
    """
    try:
        summary = await progress_service.get_progress_summary(child_id, days)
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Child not found or no progress data available"
            )
        return summary
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get progress summary error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve progress summary"
        )


@router.get("/children/{child_id}/report", response_model=ProgressReport)
async def get_progress_report(
    child_id: str,
    start_date: Optional[datetime] = Query(None, description="Start date for report"),
    end_date: Optional[datetime] = Query(None, description="End date for report"),
    current_user: User = Depends(get_current_parent)
):
    """
    Get detailed progress report with strengths and weaknesses
    """
    try:
        report = await progress_service.get_detailed_report(
            child_id,
            start_date,
            end_date
        )
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Child not found or no progress data available"
            )
        return report
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get progress report error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate progress report"
        )


@router.get("/children/{child_id}/history", response_model=List[ProgressResponse])
async def get_progress_history(
    child_id: str,
    module_id: Optional[str] = Query(None, description="Filter by module ID"),
    limit: int = Query(100, ge=1, le=500, description="Number of records to return"),
    current_user: User = Depends(get_current_parent)
):
    """
    Get progress history for a child
    """
    try:
        history = await progress_service.get_progress_history(
            child_id,
            module_id=module_id,
            limit=limit
        )
        return history
    except Exception as e:
        logger.error(f"Get progress history error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve progress history"
        )