import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from app.schemas.module import ModuleResponse, ModuleDetail
from app.schemas.user import User
from datetime import datetime

# Setup Mocks
@pytest.fixture
def mock_module_service():
    with patch("app.api.v1.endpoints.modules.module_service") as mock:
        yield mock

@pytest.fixture
def mock_educator():
    return User(
        id="educator-123",
        email="educator@example.com",
        role="educator",
        created_at=datetime.utcnow(),
        full_name="Test Educator"
    )

@pytest.mark.asyncio
async def test_get_modules(async_client: AsyncClient, mock_module_service, override_get_current_user):
    # Prepare
    mock_modules = [
        ModuleResponse(
            id="mod-1",
            title="Module 1",
            description="Desc 1",
            type="reading",
            education_level="TK",
            difficulty_level=1,
            estimated_duration_minutes=10,
            total_questions=5,
            points_reward=100
        ),
        ModuleResponse(
            id="mod-2",
            title="Module 2",
            description="Desc 2",
            type="counting",
            education_level="TK",
            difficulty_level=2,
            estimated_duration_minutes=15,
            total_questions=5,
            points_reward=150
        )
    ]
    
    mock_module_service.get_modules = AsyncMock(return_value=mock_modules)
    
    # Act
    response = await async_client.get("/api/v1/modules")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["title"] == "Module 1"
    mock_module_service.get_modules.assert_called_once()

@pytest.mark.asyncio
async def test_get_module_detail(async_client: AsyncClient, mock_module_service, override_get_current_user):
    # Prepare
    mock_module = ModuleDetail(
        id="mod-1",
        title="Module 1",
        description="Desc 1",
        type="reading",
        education_level="TK",
        difficulty_level=1,
        estimated_duration_minutes=10,
        total_questions=5,
        points_reward=100,
        questions=[],
        learning_objectives=["Learn to read"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    mock_module_service.get_module_by_id = AsyncMock(return_value=mock_module)
    
    # Act
    response = await async_client.get("/api/v1/modules/mod-1")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "mod-1"
    mock_module_service.get_module_by_id.assert_called_once()

@pytest.mark.asyncio
async def test_create_module_unauthorized(async_client: AsyncClient, mock_module_service, override_get_current_user):
    # Parent should not be able to create module
    module_data = {
        "title": "New Module",
        "description": "Desc",
        "module_type": "reading",
        "difficulty_level": 1,
        "content": {},
        "questions": []
    }
    
    response = await async_client.post("/api/v1/modules", json=module_data)
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_create_module_authorized(async_client: AsyncClient, mock_module_service, mock_educator):
    # Override dependency with educator
    from app.dependencies import get_current_user
    from app.main import app
    app.dependency_overrides[get_current_user] = lambda: mock_educator
    
    # Prepare
    module_data = {
        "title": "New Module",
        "description": "Desc",
        "module_type": "reading",
        "difficulty_level": 1,
        "content": {},
        "questions": []
    }
    
    mock_response = ModuleResponse(
        id="new-mod",
        title=module_data["title"],
        description=module_data["description"],
        type=module_data["module_type"],
        education_level="TK",
        difficulty_level=module_data["difficulty_level"],
        estimated_duration_minutes=10,
        total_questions=0,
        points_reward=100
    )
    
    mock_module_service.create_module = AsyncMock(return_value=mock_response)
    
    # Act
    response = await async_client.post("/api/v1/modules", json=module_data)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["id"] == "new-mod"
    assert data["id"] == "new-mod"
    mock_module_service.create_module.assert_called_once()

@pytest.mark.asyncio
async def test_get_module_not_found(async_client: AsyncClient, mock_module_service, override_get_current_user):
    # Prepare
    mock_module_service.get_module_by_id = AsyncMock(return_value=None)
    
    # Act
    response = await async_client.get("/api/v1/modules/non-existent")
    
    # Assert
    # Assuming endpoint checks None and raises 404
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Module not found"
