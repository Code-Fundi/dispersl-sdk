"""Unit tests for pagination functionality."""

import sys
import os
import pytest
from unittest.mock import Mock, patch

# Add tests directory to path for fixtures
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dispersl.resources import TaskManagementResource, AgentsResource, StepManagementResource, HistoryResource
from dispersl.models.base import PaginationParams
from fixtures.mock_api_responses import (
    MOCK_PAGINATED_TASK_LIST_RESPONSE,
    MOCK_PAGINATED_AGENTS_RESPONSE,
    MOCK_PAGINATED_STEPS_RESPONSE,
    MOCK_PAGINATED_HISTORY_RESPONSE
)


class TestPagination:
    """Test pagination functionality across all resources."""

    @pytest.fixture
    def http_client(self):
        """Create mock HTTP client."""
        return Mock()

    @pytest.fixture
    def tasks_resource(self, http_client):
        """Create TaskManagementResource instance."""
        return TaskManagementResource(http_client)

    @pytest.fixture
    def agents_resource(self, http_client):
        """Create AgentsResource instance."""
        return AgentsResource(http_client)

    @pytest.fixture
    def steps_resource(self, http_client):
        """Create StepManagementResource instance."""
        return StepManagementResource(http_client)

    @pytest.fixture
    def history_resource(self, http_client):
        """Create HistoryResource instance."""
        return HistoryResource(http_client)

    def test_tasks_pagination_with_params(self, tasks_resource, http_client):
        """Test tasks list with pagination parameters."""
        http_client.get.return_value = MOCK_PAGINATED_TASK_LIST_RESPONSE
        
        params = PaginationParams(page=1, pageSize=10)
        result = tasks_resource.list(params)
        
        assert result is not None
        assert result.status == "success"
        assert result.message == "Data retrieved."
        assert len(result.data) == 2
        assert result.pagination.page == 1
        assert result.pagination.pageSize == 20
        assert result.pagination.total == 50
        assert result.pagination.totalPages == 3
        assert result.pagination.hasNext is True
        assert result.pagination.hasPrev is False
        
        # Verify the request was made with correct parameters
        http_client.get.assert_called_once()
        call_args = http_client.get.call_args
        assert call_args[0][0] == "/tasks"
        assert call_args[1]["params"] == {"page": 1, "pageSize": 10}

    def test_tasks_pagination_without_params(self, tasks_resource, http_client):
        """Test tasks list without pagination parameters."""
        http_client.get.return_value = MOCK_PAGINATED_TASK_LIST_RESPONSE
        
        result = tasks_resource.list()
        
        assert result is not None
        assert result.status == "success"
        assert result.pagination is not None
        
        # Verify the request was made without parameters
        http_client.get.assert_called_once()
        call_args = http_client.get.call_args
        assert call_args[0][0] == "/tasks"
        assert call_args[1]["params"] is None

    def test_agents_pagination_with_params(self, agents_resource, http_client):
        """Test agents list with pagination parameters."""
        http_client.get.return_value = MOCK_PAGINATED_AGENTS_RESPONSE
        
        params = PaginationParams(page=1, pageSize=5)
        result = agents_resource.list(params)
        
        assert result is not None
        assert result.status == "success"
        assert result.message == "Data retrieved."
        assert len(result.data) == 2
        assert result.pagination.page == 1
        assert result.pagination.pageSize == 20
        assert result.pagination.total == 5
        assert result.pagination.totalPages == 1
        assert result.pagination.hasNext is False
        assert result.pagination.hasPrev is False
        
        # Verify the request was made with correct parameters
        http_client.get.assert_called_once()
        call_args = http_client.get.call_args
        assert call_args[0][0] == "/agents"
        assert call_args[1]["params"] == {"page": 1, "pageSize": 5}

    def test_agents_pagination_without_params(self, agents_resource, http_client):
        """Test agents list without pagination parameters."""
        http_client.get.return_value = MOCK_PAGINATED_AGENTS_RESPONSE
        
        result = agents_resource.list()
        
        assert result is not None
        assert result.status == "success"
        assert result.pagination is not None
        
        # Verify the request was made without parameters
        http_client.get.assert_called_once()
        call_args = http_client.get.call_args
        assert call_args[0][0] == "/agents"
        assert call_args[1]["params"] is None

    def test_steps_pagination_with_params(self, steps_resource, http_client):
        """Test steps by task ID with pagination parameters."""
        http_client.get.return_value = MOCK_PAGINATED_STEPS_RESPONSE
        
        params = PaginationParams(page=2, pageSize=15)
        result = steps_resource.get_by_task_id("task_123456", params)
        
        assert result is not None
        assert result.status == "success"
        assert result.message == "Data retrieved."
        assert len(result.data) == 2
        assert result.pagination.page == 1
        assert result.pagination.pageSize == 20
        assert result.pagination.total == 25
        assert result.pagination.totalPages == 2
        assert result.pagination.hasNext is True
        assert result.pagination.hasPrev is False
        
        # Verify the request was made with correct parameters
        http_client.get.assert_called_once()
        call_args = http_client.get.call_args
        assert call_args[0][0] == "/steps/task/task_123456"
        assert call_args[1]["params"] == {"page": 2, "pageSize": 15}

    def test_steps_pagination_without_params(self, steps_resource, http_client):
        """Test steps by task ID without pagination parameters."""
        http_client.get.return_value = MOCK_PAGINATED_STEPS_RESPONSE
        
        result = steps_resource.get_by_task_id("task_123456")
        
        assert result is not None
        assert result.status == "success"
        assert result.pagination is not None
        
        # Verify the request was made without parameters
        http_client.get.assert_called_once()
        call_args = http_client.get.call_args
        assert call_args[0][0] == "/steps/task/task_123456"
        assert call_args[1]["params"] is None

    def test_history_pagination_with_params(self, history_resource, http_client):
        """Test task history with pagination parameters."""
        http_client.get.return_value = MOCK_PAGINATED_HISTORY_RESPONSE
        
        result = history_resource.get_task_history(
            "task_123456",
            page=1,
            pageSize=10
        )
        
        assert result is not None
        assert result.status == "success"
        assert result.message == "Data retrieved."
        assert len(result.data) == 2
        assert result.pagination.page == 1
        assert result.pagination.pageSize == 20
        assert result.pagination.total == 15
        assert result.pagination.totalPages == 1
        assert result.pagination.hasNext is False
        assert result.pagination.hasPrev is False
        
        # Verify the request was made with correct parameters
        http_client.get.assert_called_once()
        call_args = http_client.get.call_args
        assert call_args[0][0] == "/history/task/task_123456"
        assert call_args[1]["json_data"] == {"page": 1, "pageSize": 10}

    def test_step_history_pagination_with_params(self, history_resource, http_client):
        """Test step history with pagination parameters."""
        http_client.get.return_value = MOCK_PAGINATED_HISTORY_RESPONSE
        
        result = history_resource.get_step_history(
            "step_123456",
            page=1,
            pageSize=5
        )
        
        assert result is not None
        assert result.status == "success"
        assert result.pagination is not None
        
        # Verify the request was made with correct parameters
        http_client.get.assert_called_once()
        call_args = http_client.get.call_args
        assert call_args[0][0] == "/history/step/step_123456"
        assert call_args[1]["json_data"] == {"page": 1, "pageSize": 5}


    def test_pagination_parameter_validation(self, tasks_resource, http_client):
        """Test pagination parameter validation."""
        http_client.get.return_value = MOCK_PAGINATED_TASK_LIST_RESPONSE
        
        # Test with invalid page number (should not throw error)
        params = PaginationParams(page=0, pageSize=10)
        result = tasks_resource.list(params)
        assert result is not None
        
        # Test with invalid page size (should not throw error)
        params = PaginationParams(page=1, pageSize=150)
        result = tasks_resource.list(params)
        assert result is not None

    def test_pagination_response_structure(self, tasks_resource, http_client):
        """Test pagination response structure."""
        http_client.get.return_value = MOCK_PAGINATED_TASK_LIST_RESPONSE
        
        result = tasks_resource.list(PaginationParams(page=1, pageSize=10))
        
        # Test pagination object structure
        assert hasattr(result.pagination, 'page')
        assert hasattr(result.pagination, 'pageSize')
        assert hasattr(result.pagination, 'total')
        assert hasattr(result.pagination, 'totalPages')
        assert hasattr(result.pagination, 'hasNext')
        assert hasattr(result.pagination, 'hasPrev')
        
        # Test data types
        assert isinstance(result.pagination.page, int)
        assert isinstance(result.pagination.pageSize, int)
        assert isinstance(result.pagination.total, int)
        assert isinstance(result.pagination.totalPages, int)
        assert isinstance(result.pagination.hasNext, bool)
        assert isinstance(result.pagination.hasPrev, bool)
        
        # Test data array structure
        assert isinstance(result.data, list)
        assert len(result.data) > 0
        
        # Check structure of first item
        first_item = result.data[0]
        assert hasattr(first_item, 'id')
        assert hasattr(first_item, 'name')
        assert hasattr(first_item, 'status')
        assert hasattr(first_item, 'created_at')
        assert hasattr(first_item, 'updated_at')



class TestAsyncPagination:
    """Test async pagination functionality."""

    @pytest.fixture
    def http_client(self):
        """Create mock HTTP client."""
        return Mock()

    @pytest.fixture
    def async_tasks_resource(self, http_client):
        """Create AsyncTaskManagementResource instance."""
        from dispersl.resources import AsyncTaskManagementResource
        return AsyncTaskManagementResource(http_client)

    @pytest.fixture
    def async_agents_resource(self, http_client):
        """Create AsyncAgentsResource instance."""
        from dispersl.resources import AsyncAgentsResource
        return AsyncAgentsResource(http_client)

    @pytest.fixture
    def async_steps_resource(self, http_client):
        """Create AsyncStepManagementResource instance."""
        from dispersl.resources import AsyncStepManagementResource
        return AsyncStepManagementResource(http_client)

    @pytest.fixture
    def async_history_resource(self, http_client):
        """Create AsyncHistoryResource instance."""
        from dispersl.resources import AsyncHistoryResource
        return AsyncHistoryResource(http_client)

    @pytest.mark.asyncio
    async def test_async_tasks_pagination(self, async_tasks_resource, http_client):
        """Test async tasks list with pagination."""
        http_client.get.return_value = MOCK_PAGINATED_TASK_LIST_RESPONSE
        
        params = PaginationParams(page=1, pageSize=10)
        result = await async_tasks_resource.list(params)
        
        assert result is not None
        assert result.status == "success"
        assert result.pagination is not None
        
        # Verify the request was made
        http_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_agents_pagination(self, async_agents_resource, http_client):
        """Test async agents list with pagination."""
        http_client.get.return_value = MOCK_PAGINATED_AGENTS_RESPONSE
        
        params = PaginationParams(page=1, pageSize=5)
        result = await async_agents_resource.list(params)
        
        assert result is not None
        assert result.status == "success"
        assert result.pagination is not None
        
        # Verify the request was made
        http_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_steps_pagination(self, async_steps_resource, http_client):
        """Test async steps by task ID with pagination."""
        http_client.get.return_value = MOCK_PAGINATED_STEPS_RESPONSE
        
        params = PaginationParams(page=2, pageSize=15)
        result = await async_steps_resource.get_by_task_id("task_123456", params)
        
        assert result is not None
        assert result.status == "success"
        assert result.pagination is not None
        
        # Verify the request was made
        http_client.get.assert_called_once()

    @pytest.mark.asyncio
    async def test_async_history_pagination(self, async_history_resource, http_client):
        """Test async history with pagination."""
        http_client.get.return_value = MOCK_PAGINATED_HISTORY_RESPONSE
        
        result = await async_history_resource.get_task_history(
            "task_123456",
            page=1,
            pageSize=10
        )
        
        assert result is not None
        assert result.status == "success"
        assert result.pagination is not None
        
        # Verify the request was made
        http_client.get.assert_called_once()
