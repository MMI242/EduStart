from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
import logging

from app.core.supabase_client import get_supabase_client
from app.core.security import verify_token
from app.schemas.user import User

logger = logging.getLogger(__name__)
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """
    Dependency to get current authenticated user from JWT token
    """
    token = credentials.credentials
    
    try:
        # Verify token with Supabase
        supabase = get_supabase_client()
        user_response = supabase.auth.get_user(token)
        
        if not user_response or not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user_data = user_response.user
        
        # Get user role from metadata or database
        role = user_data.user_metadata.get("role", "parent")
        
        return User(
            id=user_data.id,
            email=user_data.email,
            role=role,
            created_at=user_data.created_at,
            full_name=user_data.user_metadata.get("full_name", "")
        )
        
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_parent(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure current user is a parent
    """
    if current_user.role not in ["parent", "educator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only parents and educators can access this resource"
        )
    return current_user


async def get_current_educator(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure current user is an educator
    """
    if current_user.role != "educator":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only educators can access this resource"
        )
    return current_user


def get_pagination_params(
    skip: int = 0,
    limit: int = 100
) -> dict:
    """
    Dependency for pagination parameters
    """
    if skip < 0:
        skip = 0
    if limit > 100:
        limit = 100
    if limit < 1:
        limit = 10
        
    return {"skip": skip, "limit": limit}