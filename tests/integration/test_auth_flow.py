"""
Integration test — Authentication flow (register → login → access protected → logout).

This test exercises the full API endpoint chain to verify that
the auth flow works end-to-end.  Supabase is mocked at the service
layer so no real database is needed.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.schemas.user import UserResponse, TokenResponse


@pytest.fixture
def mock_auth_service():
    """Mock the auth_service module-level instance used by the auth endpoints."""
    with patch("app.api.v1.endpoints.auth.auth_service") as mock:
        yield mock


@pytest.mark.asyncio
class TestAuthenticationFlow:
    """
    Integration test: full authentication flow through the API layer.
    
    Alur yang diuji:
    1. Register akun baru
    2. Login dengan akun tersebut
    3. Akses endpoint terproteksi (/auth/me)
    4. Logout
    5. Verifikasi bahwa akses setelah logout ditolak
    """

    async def test_full_auth_flow(self, async_client: AsyncClient, mock_auth_service):
        """End-to-end authentication flow."""

        # ─── Step 1: Register ─────────────────────────────────────────
        register_payload = {
            "email": "integration@example.com",
            "password": "securepass123",
            "role": "parent",
            "full_name": "Integration Test User",
        }

        mock_user_response = UserResponse(
            id="integ-user-001",
            email="integration@example.com",
            role="parent",
            created_at=datetime.utcnow(),
            full_name="Integration Test User",
        )
        mock_auth_service.register_user = AsyncMock(return_value=mock_user_response)

        register_resp = await async_client.post(
            "/api/v1/auth/register", json=register_payload
        )

        assert register_resp.status_code == 201, f"Register failed: {register_resp.text}"
        register_data = register_resp.json()
        assert register_data["email"] == "integration@example.com"
        assert register_data["id"] == "integ-user-001"
        assert register_data["role"] == "parent"

        # ─── Step 2: Login ────────────────────────────────────────────
        login_payload = {
            "email": "integration@example.com",
            "password": "securepass123",
        }

        mock_token_response = TokenResponse(
            access_token="integ-access-token-xyz",
            refresh_token="integ-refresh-token-abc",
            token_type="bearer",
            expires_in=1800,
        )
        mock_auth_service.login_user = AsyncMock(return_value=mock_token_response)

        login_resp = await async_client.post(
            "/api/v1/auth/login", json=login_payload
        )

        assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
        login_data = login_resp.json()
        assert login_data["access_token"] == "integ-access-token-xyz"
        assert login_data["token_type"] == "bearer"

        access_token = login_data["access_token"]

        # ─── Step 3: Access protected endpoint /auth/me ───────────────
        # We need to override the dependency that validates the JWT
        from app.main import app
        from app.dependencies import get_current_user
        from app.schemas.user import User

        mock_current_user = User(
            id="integ-user-001",
            email="integration@example.com",
            role="parent",
            created_at=datetime.utcnow(),
            full_name="Integration Test User",
        )
        app.dependency_overrides[get_current_user] = lambda: mock_current_user

        mock_auth_service.get_user_profile = AsyncMock(
            return_value={
                "id": "integ-user-001",
                "email": "integration@example.com",
                "role": "parent",
                "privacy_policy_accepted_at": datetime.utcnow().isoformat(),
            }
        )

        me_resp = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert me_resp.status_code == 200, f"Get /me failed: {me_resp.text}"
        me_data = me_resp.json()
        assert me_data["email"] == "integration@example.com"
        assert me_data["id"] == "integ-user-001"

        # ─── Step 4: Logout ───────────────────────────────────────────
        mock_auth_service.logout_user = AsyncMock(return_value=True)

        logout_resp = await async_client.post(
            "/api/v1/auth/logout",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert logout_resp.status_code == 200, f"Logout failed: {logout_resp.text}"
        assert logout_resp.json()["message"] == "Successfully logged out"
        mock_auth_service.logout_user.assert_called_once()

        # ─── Step 5: Access after logout should fail ──────────────────
        # Remove the dependency override to simulate unauthenticated access
        app.dependency_overrides = {}

        me_after_logout = await async_client.get("/api/v1/auth/me")

        # Without valid auth, should return 401 or 403
        assert me_after_logout.status_code in (401, 403), (
            f"Expected 401/403 after logout, got {me_after_logout.status_code}"
        )

    async def test_login_with_wrong_password(
        self, async_client: AsyncClient, mock_auth_service
    ):
        """Integration test: login with invalid credentials should fail."""
        login_payload = {
            "email": "integration@example.com",
            "password": "wrongpassword",
        }

        mock_auth_service.login_user = AsyncMock(
            side_effect=ValueError("Invalid email or password")
        )

        login_resp = await async_client.post(
            "/api/v1/auth/login", json=login_payload
        )

        assert login_resp.status_code == 401
        assert login_resp.json()["detail"] == "Invalid email or password"

    async def test_register_duplicate_email(
        self, async_client: AsyncClient, mock_auth_service
    ):
        """Integration test: registering with an existing email should fail."""
        register_payload = {
            "email": "existing@example.com",
            "password": "password123",
            "role": "parent",
            "full_name": "Duplicate User",
        }

        mock_auth_service.register_user = AsyncMock(
            side_effect=ValueError("User already exists")
        )

        register_resp = await async_client.post(
            "/api/v1/auth/register", json=register_payload
        )

        assert register_resp.status_code == 400
        assert register_resp.json()["detail"] == "User already exists"
