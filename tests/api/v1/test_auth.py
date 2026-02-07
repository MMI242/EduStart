import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from app.schemas.user import UserResponse, TokenResponse
from datetime import datetime

# Setup Mocks
@pytest.fixture
def mock_auth_service():
    with patch("app.api.v1.endpoints.auth.auth_service") as mock:
        yield mock

@pytest.mark.asyncio
async def test_register_user(async_client: AsyncClient, mock_auth_service):
    # Prepare
    user_data = {
        "email": "newuser@example.com",
        "password": "password123",
        "role": "parent",
        "full_name": "New User"
    }
    
    mock_response = UserResponse(
        id="new-user-id",
        email=user_data["email"],
        role=user_data["role"],
        created_at=datetime.utcnow(),
        full_name=user_data["full_name"]
    )
    
    # Configure mock
    mock_auth_service.register_user = AsyncMock(return_value=mock_response)
    
    # Act
    response = await async_client.post("/api/v1/auth/register", json=user_data)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["id"] == "new-user-id"
    mock_auth_service.register_user.assert_called_once()

@pytest.mark.asyncio
async def test_login_user(async_client: AsyncClient, mock_auth_service):
    # Prepare
    credentials = {
        "email": "user@example.com",
        "password": "password123"
    }
    
    mock_token_response = TokenResponse(
        access_token="mock_access_token",
        refresh_token="mock_refresh_token",
        token_type="bearer",
        expires_in=3600
    )
    
    # Configure mock
    mock_auth_service.login_user = AsyncMock(return_value=mock_token_response)
    
    # Act
    response = await async_client.post("/api/v1/auth/login", json=credentials)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "mock_access_token"
    mock_auth_service.login_user.assert_called_once()

@pytest.mark.asyncio
async def test_get_me(async_client: AsyncClient, mock_auth_service, override_get_current_user):
    # Prepare
    mock_profile = {
        "privacy_policy_accepted_at": datetime.utcnow().isoformat()
    }
    mock_auth_service.get_user_profile = AsyncMock(return_value=mock_profile)
    
    # Act
    response = await async_client.get("/api/v1/auth/me")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "privacy_policy_accepted_at" in data

@pytest.mark.asyncio
async def test_logout(async_client: AsyncClient, mock_auth_service, override_get_current_user):
    # Prepare
    mock_auth_service.logout_user = AsyncMock(return_value=True)
    
    # Act
    response = await async_client.post("/api/v1/auth/logout")
    
    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"
    mock_auth_service.logout_user.assert_called_once()

@pytest.mark.asyncio
async def test_register_duplicate_user(async_client: AsyncClient, mock_auth_service):
    # Prepare
    user_data = {
        "email": "existing@example.com",
        "password": "password123",
        "role": "parent",
        "full_name": "Existing User"
    }
    
    # Configure mock to raise ValueError
    mock_auth_service.register_user = AsyncMock(side_effect=ValueError("User already exists"))
    
    # Act
    response = await async_client.post("/api/v1/auth/register", json=user_data)
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "User already exists"

@pytest.mark.asyncio
async def test_login_invalid_credentials(async_client: AsyncClient, mock_auth_service):
    # Prepare
    credentials = {
        "email": "user@example.com",
        "password": "wrongpassword"
    }
    
    # Configure mock to raise ValueError
    mock_auth_service.login_user = AsyncMock(side_effect=ValueError("Invalid email or password"))
    
    # Act
    response = await async_client.post("/api/v1/auth/login", json=credentials)
    
    # Assert
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid email or password"
