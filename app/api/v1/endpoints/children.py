from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
import logging

from app.schemas.child import ChildCreate, ChildUpdate, ChildResponse
from app.services.child_service import ChildService
from app.dependencies import get_current_parent, get_pagination_params
from app.schemas.user import User

router = APIRouter()
logger = logging.getLogger(__name__)
child_service = ChildService()


@router.post("", response_model=ChildResponse, status_code=status.HTTP_201_CREATED)
async def create_child(
    child_data: ChildCreate,
    current_user: User = Depends(get_current_parent)
):
    """
    Create a new child profile
    """
    try:
        child = await child_service.create_child(child_data, current_user.id)
        return child
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Create child error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create child profile"
        )


@router.get("", response_model=List[ChildResponse])
async def get_children(
    current_user: User = Depends(get_current_parent),
    pagination: dict = Depends(get_pagination_params)
):
    """
    Get all children for current user
    """
    try:
        children = await child_service.get_children_by_parent(
            current_user.id,
            skip=pagination["skip"],
            limit=pagination["limit"]
        )
        return children
    except Exception as e:
        logger.error(f"Get children error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve children"
        )


@router.get("/{child_id}", response_model=ChildResponse)
async def get_child(
    child_id: str,
    current_user: User = Depends(get_current_parent)
):
    """
    Get specific child by ID
    """
    try:
        child = await child_service.get_child_by_id(child_id, current_user.id)
        if not child:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Child not found"
            )
        return child
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get child error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve child"
        )


@router.put("/{child_id}", response_model=ChildResponse)
async def update_child(
    child_id: str,
    child_data: ChildUpdate,
    current_user: User = Depends(get_current_parent)
):
    """
    Update child profile
    """
    try:
        child = await child_service.update_child(child_id, child_data, current_user.id)
        if not child:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Child not found"
            )
        return child
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Update child error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update child"
        )


@router.delete("/{child_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_child(
    child_id: str,
    current_user: User = Depends(get_current_parent)
):
    """
    Delete child profile
    """
    try:
        success = await child_service.delete_child(child_id, current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Child not found"
            )
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete child error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete child"
        )
