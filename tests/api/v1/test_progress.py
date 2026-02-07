import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch
from app.schemas.progress import ProgressResponse, ProgressSummary, ProgressReport, StrengthWeakness
from datetime import datetime

# Setup Mocks
@pytest.fixture
def mock_progress_service():
    with patch("app.api.v1.endpoints.progress.progress_service") as mock:
        yield mock

@pytest.mark.asyncio
async def test_record_progress(async_client: AsyncClient, mock_progress_service, override_get_current_user):
    # Prepare
    progress_data = {
        "module_id": "mod-1",
        "question_id": "q-1",
        "is_correct": True,
        "time_taken_seconds": 15,
        "attempt_count": 1
    }
    
    mock_response = ProgressResponse(
        id="prog-1",
        child_id="child-1",
        module_id=progress_data["module_id"],
        question_id=progress_data["question_id"],
        is_correct=progress_data["is_correct"],
        time_taken_seconds=progress_data["time_taken_seconds"],
        attempt_count=progress_data["attempt_count"],
        points_earned=15,
        created_at=datetime.utcnow()
    )
    
    mock_progress_service.record_progress_event = AsyncMock(return_value=mock_response)
    
    # Act
    response = await async_client.post("/api/v1/progress/children/child-1/events", json=progress_data)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["points_earned"] == 15
    mock_progress_service.record_progress_event.assert_called_once()

@pytest.mark.asyncio
async def test_sync_progress(async_client: AsyncClient, mock_progress_service, override_get_current_user):
    # Prepare
    batch_data = {
        "events": [
            {
                "module_id": "mod-1",
                "question_id": "q-1",
                "is_correct": True,
                "time_taken_seconds": 10,
                "attempt_count": 1
            }
        ],
        "offline_session_id": "sess-123"
    }
    
    mock_result = {"synced_count": 1, "failed_count": 0}
    mock_progress_service.sync_batch_progress = AsyncMock(return_value=mock_result)
    
    # Act
    response = await async_client.post("/api/v1/progress/children/child-1/sync", json=batch_data)
    
    # Assert
    assert response.status_code == 201
    data = response.json()
    assert data["synced_count"] == 1

@pytest.mark.asyncio
async def test_get_progress_summary(async_client: AsyncClient, mock_progress_service, override_get_current_user):
    # Prepare
    mock_summary = ProgressSummary(
        child_id="child-1",
        total_time_minutes=10,
        total_modules_completed=1,
        total_questions_answered=5,
        average_accuracy=80.0,
        current_streak_days=2,
        total_points=50,
        favorite_module_type="reading"
    )
    
    mock_progress_service.get_progress_summary = AsyncMock(return_value=mock_summary)
    
    # Act
    response = await async_client.get("/api/v1/progress/children/child-1/summary")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["total_points"] == 50
    mock_progress_service.get_progress_summary.assert_called_once()

@pytest.mark.asyncio
async def test_get_progress_report(async_client: AsyncClient, mock_progress_service, override_get_current_user):
    # Prepare
    mock_summary = ProgressSummary(
        child_id="child-1",
        total_time_minutes=10,
        total_modules_completed=1,
        total_questions_answered=5,
        average_accuracy=80.0,
        current_streak_days=2,
        total_points=50,
        favorite_module_type="reading"
    )
    
    mock_strength = StrengthWeakness(
        category="Reading",
        skill_name="Comprehension",
        performance_score=90.0,
        recommendation="Keep it up"
    )

    mock_report = ProgressReport(
        child_id="child-1",
        period_start=datetime.utcnow(),
        period_end=datetime.utcnow(),
        overall_summary=mock_summary,
        subject_progress=[],
        strengths=[mock_strength],
        areas_for_improvement=[],
        recent_achievements=["First Module"],
        weekly_activity={},
        generated_at=datetime.utcnow()
    )
    
    mock_progress_service.get_detailed_report = AsyncMock(return_value=mock_report)
    
    # Act
    # Need to override dependency for get_current_parent if it's strictly checking parent role
    # Assuming standard get_current_user works for now or parent dependency is tolerant
    response = await async_client.get("/api/v1/progress/children/child-1/report")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data["strengths"]) == 1
    assert data["strengths"][0]["category"] == "Reading"

@pytest.mark.asyncio
async def test_get_progress_history(async_client: AsyncClient, mock_progress_service, override_get_current_user):
    # Prepare
    mock_history = [
        ProgressResponse(
            id="prog-1",
            child_id="child-1",
            module_id="mod-1",
            question_id="q-1",
            is_correct=True,
            time_taken_seconds=15,
            attempt_count=1,
            points_earned=15,
            created_at=datetime.utcnow()
        )
    ]
    
    mock_progress_service.get_progress_history = AsyncMock(return_value=mock_history)
    
    # Act
    response = await async_client.get("/api/v1/progress/children/child-1/history")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == "prog-1"

@pytest.mark.asyncio
async def test_record_progress_invalid_data(async_client: AsyncClient, mock_progress_service, override_get_current_user):
    # Prepare - Invalid time_taken (negative)
    progress_data = {
        "module_id": "mod-1",
        "question_id": "q-1",
        "is_correct": True,
        "time_taken_seconds": -5,
        "attempt_count": 1
    }
    
    # Act
    # Pydantic validation should catch this before it hits the service
    response = await async_client.post("/api/v1/progress/children/child-1/events", json=progress_data)
    
    # Assert
    assert response.status_code == 400

