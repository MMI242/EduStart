from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
import logging

from app.schemas.module import ModuleResponse, ModuleDetail, ModuleCreate, ModuleUpdate
from app.services.module_service import ModuleService
from app.dependencies import get_current_user, get_pagination_params
from app.schemas.user import User

router = APIRouter()
logger = logging.getLogger(__name__)
module_service = ModuleService()


@router.get("", response_model=List[ModuleResponse])
async def get_modules(
    module_type: Optional[str] = Query(None, description="Filter by type: reading, counting, cognitive"),
    difficulty_level: Optional[int] = Query(None, ge=1, le=10, description="Filter by difficulty level"),
    current_user: User = Depends(get_current_user),
    pagination: dict = Depends(get_pagination_params)
):
    """
    Get all available learning modules with optional filters
    """
    try:
        modules = await module_service.get_modules(
            module_type=module_type,
            difficulty_level=difficulty_level,
            skip=pagination["skip"],
            limit=pagination["limit"]
        )
        return modules
    except Exception as e:
        logger.error(f"Get modules error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve modules"
        )


@router.get("/{module_id}", response_model=ModuleDetail)
async def get_module_detail(
    module_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get detailed information about a specific module including questions
    """
    try:
        module = await module_service.get_module_by_id(module_id)
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        return module
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get module detail error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve module detail"
        )


@router.get("/{module_id}/download")
async def get_module_download(
    module_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get download URL or data for offline mode
    """
    try:
        download_data = await module_service.prepare_module_download(module_id)
        if not download_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        return download_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get module download error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to prepare module download"
        )


@router.get("/types/list")
async def get_module_types(current_user: User = Depends(get_current_user)):
    """
    Get list of all available module types
    """
    try:
        types = await module_service.get_module_types()
        return {"types": types}
    except Exception as e:
        logger.error(f"Get module types error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve module types"
        )


@router.post("", response_model=ModuleResponse, status_code=status.HTTP_201_CREATED)
async def create_module(
    module_data: ModuleCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new module (Educator only)
    """
    if current_user.role != "educator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only educators can create modules"
        )
        
    try:
        module = await module_service.create_module(module_data.dict())
        if not module:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create module"
            )
        return module
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create module error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create module"
        )


@router.put("/{module_id}", response_model=ModuleResponse)
async def update_module(
    module_id: str,
    module_data: ModuleUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update an existing module (Educator only)
    """
    if current_user.role != "educator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only educators can update modules"
        )
        
    try:
        module = await module_service.update_module(module_id, module_data.dict(exclude_unset=True))
        if not module:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
        return module
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update module error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update module"
        )


@router.delete("/{module_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_module(
    module_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a module (Educator only)
    """
    if current_user.role != "educator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only educators can delete modules"
        )
        
    try:
        success = await module_service.delete_module(module_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Module not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete module error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete module"
        )