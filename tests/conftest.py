import pytest
from httpx import AsyncClient, ASGITransport
from typing import AsyncGenerator, Generator
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import get_current_user, get_supabase_client
from app.schemas.user import User
from datetime import datetime

# Mock User Data
MOCK_USER_ID = "test-user-id"
MOCK_USER_EMAIL = "test@example.com"

@pytest.fixture
def mock_user() -> User:
    return User(
        id=MOCK_USER_ID,
        email=MOCK_USER_EMAIL,
        role="parent",
        created_at=datetime.now(),
        full_name="Test User"
    )

@pytest.fixture
def mock_supabase():
    with patch("app.dependencies.get_supabase_client") as mock:
        client = MagicMock()
        mock.return_value = client
        yield client

@pytest.fixture
def override_get_current_user(mock_user):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    yield
    app.dependency_overrides = {}

@pytest.fixture
def client() -> Generator:
    with TestClient(app) as c:
        yield c

import pytest_asyncio

@pytest_asyncio.fixture
async def async_client() -> AsyncGenerator:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
