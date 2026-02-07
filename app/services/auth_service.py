from typing import Optional
import logging
from datetime import datetime, timedelta

from app.core.supabase_client import get_supabase_client
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.core.config import settings

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self):
        self.supabase = get_supabase_client()
    
    async def register_user(self, user_data: UserRegister) -> UserResponse:
        """
        Register a new user
        """
        try:
            # Register with Supabase Auth
            auth_response = self.supabase.auth.sign_up({
                "email": user_data.email,
                "password": user_data.password,
                "options": {
                    "data": {
                        "role": user_data.role,
                        "full_name": user_data.full_name
                    }
                }
            })
            
            if not auth_response.user:
                raise ValueError("Failed to create user")
            
            user = auth_response.user
            
            # Create user profile in database
            profile_data = {
                "id": user.id,
                "email": user.email,
                "role": user_data.role,
                "full_name": user_data.full_name,
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.supabase.table("users").insert(profile_data).execute()
            
            logger.info(f"User registered successfully: {user.email}")
            
            return UserResponse(
                id=user.id,
                email=user.email,
                role=user_data.role,
                created_at=datetime.utcnow(),
                full_name=user_data.full_name
            )
            
        except Exception as e:
            logger.error(f"Registration failed: {str(e)}")
            raise ValueError(f"Registration failed: {str(e)}")
    
    async def login_user(self, credentials: UserLogin) -> TokenResponse:
        """
        Login user and return tokens
        """
        try:
            auth_response = self.supabase.auth.sign_in_with_password({
                "email": credentials.email,
                "password": credentials.password
            })
            
            if not auth_response.session:
                raise ValueError("Invalid credentials")
            
            session = auth_response.session
            
            logger.info(f"User logged in: {credentials.email}")
            
            return TokenResponse(
                access_token=session.access_token,
                refresh_token=session.refresh_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            raise ValueError("Invalid email or password")
    
    async def logout_user(self, user_id: str) -> bool:
        """
        Logout user
        """
        try:
            self.supabase.auth.sign_out()
            logger.info(f"User logged out: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            raise
    
    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """
        Refresh access token
        """
        try:
            auth_response = self.supabase.auth.refresh_session(refresh_token)
            
            if not auth_response.session:
                raise ValueError("Invalid refresh token")
            
            session = auth_response.session
            
            return TokenResponse(
                access_token=session.access_token,
                refresh_token=session.refresh_token,
                token_type="bearer",
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise ValueError("Invalid or expired refresh token")
    
    async def accept_privacy_policy(self, user_id: str) -> bool:
        """
        Record user acceptance of privacy policy
        """
        try:
            self.supabase.table("users").update({
                "privacy_policy_accepted_at": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            
            logger.info(f"User accepted privacy policy: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to record privacy policy acceptance: {str(e)}")
            raise
    
    async def get_user_profile(self, user_id: str) -> dict:
        """
        Get user profile including privacy policy status
        """
        try:
            response = self.supabase.table("users").select("*").eq("id", user_id).single().execute()
            return response.data
        except Exception as e:
            logger.error(f"Failed to get user profile: {str(e)}")
            raise