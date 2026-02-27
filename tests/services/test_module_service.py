"""
Unit tests for ModuleService — tests learning-module business logic
with mocked Supabase dependency.
"""
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

from app.services.module_service import ModuleService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture
def mock_supabase():
    """Create a fully mocked Supabase client."""
    with patch("app.services.module_service.get_supabase_client") as mock_fn:
        client = MagicMock()
        mock_fn.return_value = client
        yield client


@pytest.fixture
def module_service(mock_supabase):
    """Return a ModuleService with mocked Supabase."""
    return ModuleService()


NOW_ISO = datetime.utcnow().isoformat()


def _mock_module_row(module_id="mod-001", title="Belajar Huruf", difficulty=2):
    """Helper to create a realistic module DB row."""
    return {
        "id": module_id,
        "title": title,
        "description": "Belajar mengenal huruf A-Z",
        "module_type": "reading",
        "education_level": "TK",
        "difficulty_level": difficulty,
        "estimated_duration_minutes": 15,
        "thumbnail_url": "https://example.com/thumb.png",
        "content": {
            "questions": [
                {
                    "id": "q1",
                    "question_text": "Huruf apa ini?",
                    "question_type": "multiple_choice",
                    "options": ["A", "B", "C"],
                    "correct_answer": "A",
                },
            ],
            "learning_objectives": ["Mengenal huruf A-Z"],
        },
        "is_premium": False,
        "created_at": NOW_ISO,
    }


# ============================= get_modules =================================

class TestGetModules:
    """Tests for ModuleService.get_modules"""

    @pytest.mark.asyncio
    async def test_get_modules_happy_path(self, module_service, mock_supabase):
        """Happy path: returns list of modules."""
        mock_response = MagicMock()
        mock_response.data = [
            _mock_module_row("mod-001", "Belajar Huruf", 2),
            _mock_module_row("mod-002", "Belajar Angka", 3),
        ]

        # Chain: table().select().range().execute()
        mock_query = MagicMock()
        mock_query.range.return_value.execute.return_value = mock_response
        mock_supabase.table.return_value.select.return_value = mock_query

        result = await module_service.get_modules()

        assert len(result) == 2
        assert result[0].title == "Belajar Huruf"
        assert result[1].title == "Belajar Angka"
        assert result[0].points_reward == 20  # difficulty 2 * 10
        assert result[1].points_reward == 30  # difficulty 3 * 10

    @pytest.mark.asyncio
    async def test_get_modules_with_type_filter(self, module_service, mock_supabase):
        """Happy path: filter by module_type."""
        mock_response = MagicMock()
        mock_response.data = [_mock_module_row()]

        mock_query = MagicMock()
        mock_query.eq.return_value = mock_query  # chaining .eq()
        mock_query.range.return_value.execute.return_value = mock_response
        mock_supabase.table.return_value.select.return_value = mock_query

        result = await module_service.get_modules(module_type="reading")

        assert len(result) == 1
        mock_query.eq.assert_called_once_with("module_type", "reading")

    @pytest.mark.asyncio
    async def test_get_modules_db_error(self, module_service, mock_supabase):
        """Error path: database raises exception."""
        mock_query = MagicMock()
        mock_query.range.return_value.execute.side_effect = Exception("DB error")
        mock_supabase.table.return_value.select.return_value = mock_query

        with pytest.raises(Exception):
            await module_service.get_modules()


# =========================== get_module_by_id ==============================

class TestGetModuleById:
    """Tests for ModuleService.get_module_by_id"""

    @pytest.mark.asyncio
    async def test_get_module_by_id_happy_path(self, module_service, mock_supabase):
        """Happy path: returns detailed module with questions."""
        mock_response = MagicMock()
        mock_response.data = _mock_module_row()

        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response

        result = await module_service.get_module_by_id("mod-001")

        assert result is not None
        assert result.title == "Belajar Huruf"
        assert len(result.questions) == 1
        assert result.questions[0].id == "q1"
        assert result.learning_objectives == ["Mengenal huruf A-Z"]

    @pytest.mark.asyncio
    async def test_get_module_by_id_not_found(self, module_service, mock_supabase):
        """Edge case: module doesn't exist — returns None."""
        mock_response = MagicMock()
        mock_response.data = None

        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.return_value = mock_response

        result = await module_service.get_module_by_id("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_module_by_id_db_error(self, module_service, mock_supabase):
        """Error path: database exception — returns None (service catches it)."""
        mock_supabase.table.return_value.select.return_value.eq.return_value.single.return_value.execute.side_effect = Exception(
            "DB error"
        )

        result = await module_service.get_module_by_id("mod-001")
        assert result is None


# ============================ create_module ================================

class TestCreateModule:
    """Tests for ModuleService.create_module"""

    @pytest.mark.asyncio
    async def test_create_module_happy_path(self, module_service, mock_supabase):
        """Happy path: creates a module and returns response."""
        module_data = {
            "title": "Belajar Warna",
            "description": "Mengenal warna dasar",
            "module_type": "cognitive",
            "education_level": "TK",
            "difficulty_level": 1,
            "estimated_duration_minutes": 10,
            "content": {
                "questions": [
                    {
                        "id": "q1",
                        "question_text": "Warna apa ini?",
                        "question_type": "multiple_choice",
                        "options": ["Merah", "Biru"],
                        "correct_answer": "Merah",
                    }
                ]
            },
        }

        created_row = _mock_module_row("mod-new", "Belajar Warna", 1)
        created_row["module_type"] = "cognitive"

        mock_response = MagicMock()
        mock_response.data = [created_row]
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response

        result = await module_service.create_module(module_data)

        assert result is not None
        assert result.title == "Belajar Warna"
        assert result.points_reward == 10  # difficulty 1 * 10

    @pytest.mark.asyncio
    async def test_create_module_insert_failure(self, module_service, mock_supabase):
        """Error path: insert returns empty data."""
        module_data = {
            "title": "Fail",
            "description": "Test",
            "module_type": "reading",
            "difficulty_level": 1,
            "estimated_duration_minutes": 10,
            "content": {"questions": []},
        }

        mock_response = MagicMock()
        mock_response.data = []  # empty — no row created
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response

        result = await module_service.create_module(module_data)
        assert result is None

    @pytest.mark.asyncio
    async def test_create_module_exception(self, module_service, mock_supabase):
        """Error path: database exception during creation."""
        module_data = {
            "title": "Error",
            "description": "Test",
            "module_type": "reading",
            "difficulty_level": 1,
            "estimated_duration_minutes": 10,
            "content": {"questions": []},
        }

        mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception("DB error")

        with pytest.raises(Exception):
            await module_service.create_module(module_data)


# ============================ delete_module ================================

class TestDeleteModule:
    """Tests for ModuleService.delete_module"""

    @pytest.mark.asyncio
    async def test_delete_module_happy_path(self, module_service, mock_supabase):
        """Happy path: successfully deletes a module."""
        mock_response = MagicMock()
        mock_response.data = [_mock_module_row()]
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_response

        result = await module_service.delete_module("mod-001")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_module_not_found(self, module_service, mock_supabase):
        """Edge case: module doesn't exist — returns False."""
        mock_response = MagicMock()
        mock_response.data = []
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_response

        result = await module_service.delete_module("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_delete_module_exception(self, module_service, mock_supabase):
        """Error path: database exception."""
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.side_effect = Exception("DB error")

        with pytest.raises(Exception):
            await module_service.delete_module("mod-001")
