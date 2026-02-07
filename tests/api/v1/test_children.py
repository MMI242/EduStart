import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from app.schemas.child import ChildResponse
from datetime import datetime

# Setup Mocks
@pytest.fixture
def mock_child_service():
    with patch("app.api.v1.endpoints.children.child_service") as mock:
        yield mock

@pytest.mark.asyncio
async def test_create_child(async_client: AsyncClient, mock_child_service, override_get_current_user):
    # Prepare
    child_data = {
        "name": "Kiddo",
        "age": 8,
        "avatar": "avatar1.png"
    }
    
    mock_response = ChildResponse(
        id="child-123",
        name=child_data["name"],
        age=child_data["age"],
        avatar=child_data["avatar"],
        parent_id="test-user-id",
        current_level=1,
        total_points=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    # Configure mock
    mock_child_service.create_child = AsyncMock(return_value=mock_response)
    
    # Act
    response = await async_client.post("/api/v1/children", json=child_data)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Kiddo"
    assert data["id"] == "child-123"
    mock_child_service.create_child.assert_called_once()

@pytest.mark.asyncio
async def test_get_children(async_client: AsyncClient, mock_child_service, override_get_current_user):
    # Prepare
    mock_children = [
        ChildResponse(
            id="child-1",
            name="Kid 1",
            age=8,
            avatar="a1.png",
            parent_id="test-user-id",
            current_level=1,
            total_points=10,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        ),
        ChildResponse(
            id="child-2",
            name="Kid 2",
            age=10,
            avatar="a2.png",
            parent_id="test-user-id",
            current_level=2,
            total_points=20,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    ]
    
    mock_child_service.get_children_by_parent = AsyncMock(return_value=mock_children)
    
    # Act
    response = await async_client.get("/api/v1/children")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Kid 1"
    mock_child_service.get_children_by_parent.assert_called_once()

@pytest.mark.asyncio
async def test_get_child_detail(async_client: AsyncClient, mock_child_service, override_get_current_user):
    # Prepare
    mock_child = ChildResponse(
        id="child-123",
        name="Kiddo",
        age=8,
        avatar="avatar1.png",
        parent_id="test-user-id",
        current_level=1,
        total_points=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    mock_child_service.get_child_by_id = AsyncMock(return_value=mock_child)
    
    # Act
    response = await async_client.get("/api/v1/children/child-123")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "child-123"
    mock_child_service.get_child_by_id.assert_called_once()

@pytest.mark.asyncio
async def test_update_child(async_client: AsyncClient, mock_child_service, override_get_current_user):
    # Prepare
    update_data = {"name": "Kiddo Updated"}
    
    mock_updated_child = ChildResponse(
        id="child-123",
        name="Kiddo Updated",
        age=8,
        avatar="avatar1.png",
        parent_id="test-user-id",
        current_level=1,
        total_points=0,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    mock_child_service.update_child = AsyncMock(return_value=mock_updated_child)
    
    # Act
    response = await async_client.put("/api/v1/children/child-123", json=update_data)
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Kiddo Updated"
    mock_child_service.update_child.assert_called_once()

@pytest.mark.asyncio
async def test_delete_child(async_client: AsyncClient, mock_child_service, override_get_current_user):
    # Prepare
    mock_child_service.delete_child = AsyncMock(return_value=True)
    
    # Act
    response = await async_client.delete("/api/v1/children/child-123")
    
    # Assert
    assert response.status_code == 204
    mock_child_service.delete_child.assert_called_once()

@pytest.mark.asyncio
async def test_get_child_not_found(async_client: AsyncClient, mock_child_service, override_get_current_user):
    # Prepare
    mock_child_service.get_child_by_id = AsyncMock(return_value=None)
    
    # Act
    response = await async_client.get("/api/v1/children/non-existent")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Child not found"

@pytest.mark.asyncio
async def test_delete_child_not_found(async_client: AsyncClient, mock_child_service, override_get_current_user):
    # Prepare
    mock_child_service.delete_child = AsyncMock(return_value=False)
    
    # Act
    response = await async_client.delete("/api/v1/children/non-existent")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Child not found"
