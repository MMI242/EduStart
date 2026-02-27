"""
Unit tests for AuthService — tests authentication business logic
with mocked Supabase dependency.
"""
import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from datetime import datetime

from app.services.auth_service import AuthService
from app.schemas.user import UserRegister, UserLogin


# ---------------------------------------------------------------------------
# Fixture: service with mocked Supabase client
# ---------------------------------------------------------------------------
@pytest.fixture
def mock_supabase():
    """Create a fully mocked Supabase client."""
    with patch("app.services.auth_service.get_supabase_client") as mock_fn:
        client = MagicMock()
        mock_fn.return_value = client
        yield client


@pytest.fixture
def auth_service(mock_supabase):
    """Return an AuthService with mocked Supabase."""
    return AuthService()


# ============================= register_user ===============================

class TestRegisterUser:
    """Tests for AuthService.register_user"""

    @pytest.mark.asyncio
    async def test_register_user_happy_path(self, auth_service, mock_supabase):
        """Happy path: successful user registration."""
        # Arrange
        user_data = UserRegister(
            email="newuser@example.com",
            password="password123",
            role="parent",
            full_name="New User",
        )

        # Mock Supabase auth response
        mock_user = MagicMock()
        mock_user.id = "user-uuid-123"
        mock_user.email = "newuser@example.com"

        mock_auth_response = MagicMock()
        mock_auth_response.user = mock_user

        mock_supabase.auth.sign_up.return_value = mock_auth_response
        mock_supabase.table.return_value.insert.return_value.execute.return_value = MagicMock()

        # Act
        result = await auth_service.register_user(user_data)

        # Assert
        assert result.email == "newuser@example.com"
        assert result.id == "user-uuid-123"
        assert result.role == "parent"
        mock_supabase.auth.sign_up.assert_called_once()
        mock_supabase.table("users").insert.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_auth_failure(self, auth_service, mock_supabase):
        """Error path: Supabase auth returns no user (e.g. duplicate email)."""
        user_data = UserRegister(
            email="existing@example.com",
            password="password123",
            role="parent",
            full_name="Existing User",
        )

        # Mock — sign_up returns response without user
        mock_auth_response = MagicMock()
        mock_auth_response.user = None
        mock_supabase.auth.sign_up.return_value = mock_auth_response

        # Act & Assert
        with pytest.raises(ValueError, match="Registration failed"):
            await auth_service.register_user(user_data)

    @pytest.mark.asyncio
    async def test_register_user_exception(self, auth_service, mock_supabase):
        """Error path: Supabase throws an exception."""
        user_data = UserRegister(
            email="error@example.com",
            password="password123",
            role="parent",
            full_name="Error User",
        )

        mock_supabase.auth.sign_up.side_effect = Exception("Network error")

        with pytest.raises(ValueError, match="Registration failed"):
            await auth_service.register_user(user_data)


# ============================= login_user ==================================

class TestLoginUser:
    """Tests for AuthService.login_user"""

    @pytest.mark.asyncio
    async def test_login_user_happy_path(self, auth_service, mock_supabase):
        """Happy path: successful login returns tokens."""
        credentials = UserLogin(email="user@example.com", password="password123")

        mock_session = MagicMock()
        mock_session.access_token = "access-token-abc"
        mock_session.refresh_token = "refresh-token-xyz"

        mock_auth_response = MagicMock()
        mock_auth_response.session = mock_session

        mock_supabase.auth.sign_in_with_password.return_value = mock_auth_response

        # Act
        result = await auth_service.login_user(credentials)

        # Assert
        assert result.access_token == "access-token-abc"
        assert result.refresh_token == "refresh-token-xyz"
        assert result.token_type == "bearer"
        mock_supabase.auth.sign_in_with_password.assert_called_once()

    @pytest.mark.asyncio
    async def test_login_user_invalid_credentials(self, auth_service, mock_supabase):
        """Error path: invalid credentials."""
        credentials = UserLogin(email="user@example.com", password="wrong")

        mock_auth_response = MagicMock()
        mock_auth_response.session = None
        mock_supabase.auth.sign_in_with_password.return_value = mock_auth_response

        with pytest.raises(ValueError, match="Invalid email or password"):
            await auth_service.login_user(credentials)

    @pytest.mark.asyncio
    async def test_login_user_supabase_error(self, auth_service, mock_supabase):
        """Error path: Supabase raises exception."""
        credentials = UserLogin(email="user@example.com", password="password123")

        mock_supabase.auth.sign_in_with_password.side_effect = Exception("Service down")

        with pytest.raises(ValueError, match="Invalid email or password"):
            await auth_service.login_user(credentials)


# ============================= logout_user =================================

class TestLogoutUser:
    """Tests for AuthService.logout_user"""

    @pytest.mark.asyncio
    async def test_logout_user_happy_path(self, auth_service, mock_supabase):
        """Happy path: successful logout."""
        mock_supabase.auth.sign_out.return_value = None

        result = await auth_service.logout_user("user-id-123")

        assert result is True
        mock_supabase.auth.sign_out.assert_called_once()

    @pytest.mark.asyncio
    async def test_logout_user_error(self, auth_service, mock_supabase):
        """Error path: Supabase sign_out raises exception."""
        mock_supabase.auth.sign_out.side_effect = Exception("Session error")

        with pytest.raises(Exception):
            await auth_service.logout_user("user-id-123")


# ========================= get_user_profile ================================

class TestGetUserProfile:
    """Tests for AuthService.get_user_profile"""

    @pytest.mark.asyncio
    async def test_get_profile_happy_path(self, auth_service, mock_supabase):
        """Happy path: returns user profile dict."""
        expected_profile = {
            "id": "user-id-123",
            "email": "user@example.com",
            "role": "parent",
            "privacy_policy_accepted_at": datetime.utcnow().isoformat(),
        }

        mock_response = MagicMock()
        mock_response.data = expected_profile
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response

        result = await auth_service.get_user_profile("user-id-123")
        assert result == expected_profile

    @pytest.mark.asyncio
    async def test_get_profile_error(self, auth_service, mock_supabase):
        """Error path: Supabase raises exception."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.side_effect = Exception(
            "DB error"
        )

        with pytest.raises(Exception):
            await auth_service.get_user_profile("user-id-123")
