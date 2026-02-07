import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from app.schemas.recommendation import RecommendationResponse, RecommendedModule
from app.schemas.module import ModuleResponse
from datetime import datetime, timedelta

# Setup Mocks
@pytest.fixture
def mock_ai_service():
    with patch("app.api.v1.endpoints.recommendations.ai_service") as mock:
        yield mock

@pytest.mark.asyncio
async def test_get_recommendations(async_client: AsyncClient, mock_ai_service, override_get_current_user):
    # Prepare
    mock_module = ModuleResponse(
        id="mod-1",
        title="Module 1",
        description="Desc 1",
        type="reading",
        education_level="TK",
        difficulty_level=1,
        estimated_duration_minutes=10,
        total_questions=5,
        points_reward=100
    )
    
    mock_rec_module = RecommendedModule(
        module=mock_module,
        confidence_score=0.9,
        reasons=[],
        expected_difficulty=1
    )
    
    mock_response = RecommendationResponse(
        child_id="child-1",
        recommended_modules=[mock_rec_module],
        next_best_module=mock_rec_module,
        personalization_level="high",
        generated_at=datetime.utcnow(),
        valid_until=datetime.utcnow() + timedelta(hours=24)
    )
    
    mock_ai_service.get_recommendations = AsyncMock(return_value=mock_response)
    
    # Act
    response = await async_client.get("/api/v1/recommendations/children/child-1")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data["recommended_modules"]) == 1
    mock_ai_service.get_recommendations.assert_called_once()

@pytest.mark.asyncio
async def test_get_next_module(async_client: AsyncClient, mock_ai_service, override_get_current_user):
    # Prepare
    mock_next = {
        "module": {
            "id": "mod-1",
            "title": "Module 1",
            "type": "reading",
            "difficulty_level": 1
        },
        "confidence": 0.95,
        "reasons": [],
        "estimated_difficulty": 1
    }
    
    mock_ai_service.get_next_module = AsyncMock(return_value=mock_next)
    
    # Act
    response = await async_client.get("/api/v1/recommendations/children/child-1/next-module")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["confidence"] == 0.95
    mock_ai_service.get_next_module.assert_called_once()

@pytest.mark.asyncio
async def test_adjust_difficulty(async_client: AsyncClient, mock_ai_service, override_get_current_user):
    # Prepare
    mock_result = {
        "new_level": 2,
        "previous_level": 1,
        "reason": "Good job",
        "performance_metrics": {}
    }
    
    mock_ai_service.adjust_difficulty_level = AsyncMock(return_value=mock_result)
    
    # Act
    response = await async_client.post(
        "/api/v1/recommendations/children/child-1/adjust-difficulty?module_id=mod-1",
        json={} # Empty body or query params depend on implementation, but endpoint is POST
    )
    # Actually endpoint definition:
    # @router.post("/children/{child_id}/adjust-difficulty")
    # async def adjust_difficulty(child_id: str, module_id: str, ...)
    # It expects query param module_id based on signature (or body if pydantic model, but here it is simple arg)
    # "module_id: str" in FastAPI usually defaults to query param if not Path and not Pydantic model.
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["new_level"] == 2
    mock_ai_service.adjust_difficulty_level.assert_called_once()

@pytest.mark.asyncio
async def test_get_recommendations_child_not_found(async_client: AsyncClient, mock_ai_service, override_get_current_user):
    # Prepare
    mock_ai_service.get_recommendations = AsyncMock(return_value=None)
    
    # Act
    response = await async_client.get("/api/v1/recommendations/children/non-existent")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Child not found or insufficient data for recommendations"
