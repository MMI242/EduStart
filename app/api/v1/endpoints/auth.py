from fastapi import APIRouter, HTTPException, status, Depends
import logging

from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.services.auth_service import AuthService
from app.dependencies import get_current_user
from app.schemas.user import User

router = APIRouter()
logger = logging.getLogger(__name__)
auth_service = AuthService()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserRegister):
    """
    Register a new user (parent or educator)
    """
    try:
        user = await auth_service.register_user(user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to register user"
        )


@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    """
    Login user and return JWT tokens
    """
    try:
        tokens = await auth_service.login_user(credentials)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to login"
        )


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user
    """
    try:
        await auth_service.logout_user(current_user.id)
        return {"message": "Successfully logged out"}
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to logout"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current user information including privacy policy status
    """
    try:
        # Get full user profile from database including privacy policy status
        user_profile = await auth_service.get_user_profile(current_user.id)
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            role=current_user.role,
            created_at=current_user.created_at,
            full_name=current_user.full_name,
            privacy_policy_accepted_at=user_profile.get("privacy_policy_accepted_at")
        )
    except Exception as e:
        logger.error(f"Get user profile error: {str(e)}")
        # Fallback to basic info if profile fetch fails
        return UserResponse(
            id=current_user.id,
            email=current_user.email,
            role=current_user.role,
            created_at=current_user.created_at,
            full_name=current_user.full_name
        )


@router.post("/accept-privacy-policy")
async def accept_privacy_policy(current_user: User = Depends(get_current_user)):
    """
    Record user acceptance of privacy policy
    """
    try:
        await auth_service.accept_privacy_policy(current_user.id)
        return {"message": "Privacy policy accepted", "success": True}
    except Exception as e:
        logger.error(f"Accept privacy policy error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to accept privacy policy"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str):
    """
    Refresh access token using refresh token
    """
    try:
        tokens = await auth_service.refresh_access_token(refresh_token)
        return tokens
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh token"
        )