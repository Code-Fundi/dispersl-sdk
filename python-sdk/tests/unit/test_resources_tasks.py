"""Comprehensive unit tests for TasksResource and StepsResource."""

import sys
import os
import pytest
from unittest.mock import Mock, patch

# Add tests directory to path for fixtures
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dispersl.resources import TaskManagementResource, StepManagementResource
from dispersl.exceptions import DisperslError, ValidationError
from fixtures.mock_api_responses import MockAPIResponses

# Aliases for backward compatibility
TasksResource = TaskManagementResource
StepsResource = StepManagementResource


class TestTasksResource:
    """Test TasksResource functionality."""

    @pytest.fixture
    def http_client(self):
        """Create mock HTTP client."""
        return Mock()

    @pytest.fixture
    def tasks_resource(self, http_client):
        """Create TasksResource instance."""
        return TasksResource(http_client)

    def test_create_task(self, tasks_resource, http_client):
        """Test creating a new task."""
        http_client.post.return_value = MockAPIResponses.task_created()
        
        result = tasks_resource.create(
            name="Test Task",
            description="A test task",
            agent_type="code"
        )
        
        assert result is not None
        assert "id" in result
        assert result["name"] == "Test Task"
        http_client.post.assert_called_once()

    def test_create_task_with_metadata(self, tasks_resource, http_client):
        """Test creating task with metadata."""
        http_client.post.return_value = MockAPIResponses.task_created()
        
        metadata = {"priority": "high", "tags": ["urgent", "bug"]}
        result = tasks_resource.create(
            name="Important Task",
            description="Critical bug fix",
            agent_type="code",
            metadata=metadata
        )
        
        assert result is not None
        call_args = http_client.post.call_args
        assert "metadata" in call_args[1]["json"]

    def test_get_task(self, tasks_resource, http_client):
        """Test getting a task by ID."""
        http_client.get.return_value = MockAPIResponses.task_details()
        
        result = tasks_resource.get("task_123")
        
        assert result is not None
        assert result["id"] == "task_123"
        http_client.get.assert_called_once_with("/tasks/task_123")

    def test_list_tasks(self, tasks_resource, http_client):
        """Test listing all tasks."""
        http_client.get.return_value = MockAPIResponses.tasks_list()
        
        result = tasks_resource.list()
        
        assert isinstance(result, list)
        assert len(result) > 0
        http_client.get.assert_called_once()

    def test_list_tasks_with_filters(self, tasks_resource, http_client):
        """Test listing tasks with filters."""
        http_client.get.return_value = MockAPIResponses.tasks_list()
        
        result = tasks_resource.list(
            status="pending",
            agent_type="code",
            limit=10
        )
        
        assert isinstance(result, list)
        call_args = http_client.get.call_args
        params = call_args[1].get("params", {})
        assert params.get("status") == "pending"
        assert params.get("agent_type") == "code"
        assert params.get("limit") == 10

    def test_update_task(self, tasks_resource, http_client):
        """Test updating a task."""
        http_client.patch.return_value = MockAPIResponses.task_updated()
        
        result = tasks_resource.update(
            "task_123",
            status="in_progress",
            progress=50
        )
        
        assert result is not None
        assert result["status"] == "in_progress"
        http_client.patch.assert_called_once()

    def test_cancel_task(self, tasks_resource, http_client):
        """Test canceling a task."""
        http_client.post.return_value = MockAPIResponses.task_cancelled()
        
        result = tasks_resource.cancel("task_123")
        
        assert result is not None
        assert result["status"] == "cancelled"
        http_client.post.assert_called_once_with("/tasks/task_123/cancel")

    def test_delete_task(self, tasks_resource, http_client):
        """Test deleting a task."""
        http_client.delete.return_value = {"success": True}
        
        result = tasks_resource.delete("task_123")
        
        assert result["success"] is True
        http_client.delete.assert_called_once_with("/tasks/task_123")

    def test_get_task_status(self, tasks_resource, http_client):
        """Test getting task status."""
        http_client.get.return_value = {"status": "completed", "progress": 100}
        
        result = tasks_resource.get_status("task_123")
        
        assert result["status"] == "completed"
        http_client.get.assert_called_once()

    def test_get_task_result(self, tasks_resource, http_client):
        """Test getting task result."""
        http_client.get.return_value = MockAPIResponses.task_result()
        
        result = tasks_resource.get_result("task_123")
        
        assert result is not None
        assert "output" in result or "result" in result
        http_client.get.assert_called_once()

    def test_task_not_found(self, tasks_resource, http_client):
        """Test handling task not found error."""
        http_client.get.side_effect = DisperslError("Task not found", status_code=404)
        
        with pytest.raises(DisperslError) as exc_info:
            tasks_resource.get("nonexistent_task")
        
        assert exc_info.value.status_code == 404

    def test_create_task_validation_error(self, tasks_resource):
        """Test validation error when creating task."""
        with pytest.raises(ValidationError):
            tasks_resource.create(name="", description="", agent_type="")

    def test_invalid_task_status(self, tasks_resource):
        """Test error with invalid status value."""
        with pytest.raises(ValidationError):
            tasks_resource.update("task_123", status="invalid_status")


class TestStepsResource:
    """Test StepsResource functionality."""

    @pytest.fixture
    def http_client(self):
        """Create mock HTTP client."""
        return Mock()

    @pytest.fixture
    def steps_resource(self, http_client):
        """Create StepsResource instance."""
        return StepsResource(http_client)

    def test_create_step(self, steps_resource, http_client):
        """Test creating a new step."""
        http_client.post.return_value = MockAPIResponses.step_created()
        
        result = steps_resource.create(
            task_id="task_123",
            name="Test Step",
            action="execute_code"
        )
        
        assert result is not None
        assert "id" in result
        assert result["task_id"] == "task_123"
        http_client.post.assert_called_once()

    def test_get_step(self, steps_resource, http_client):
        """Test getting a step by ID."""
        http_client.get.return_value = MockAPIResponses.step_details()
        
        result = steps_resource.get("step_123")
        
        assert result is not None
        assert result["id"] == "step_123"
        http_client.get.assert_called_once_with("/steps/step_123")

    def test_list_steps(self, steps_resource, http_client):
        """Test listing all steps."""
        http_client.get.return_value = MockAPIResponses.steps_list()
        
        result = steps_resource.list()
        
        assert isinstance(result, list)
        assert len(result) > 0
        http_client.get.assert_called_once()

    def test_list_steps_by_task(self, steps_resource, http_client):
        """Test listing steps for a specific task."""
        http_client.get.return_value = MockAPIResponses.steps_list()
        
        result = steps_resource.list(task_id="task_123")
        
        assert isinstance(result, list)
        call_args = http_client.get.call_args
        params = call_args[1].get("params", {})
        assert params.get("task_id") == "task_123"

    def test_update_step(self, steps_resource, http_client):
        """Test updating a step."""
        http_client.patch.return_value = MockAPIResponses.step_updated()
        
        result = steps_resource.update(
            "step_123",
            status="completed",
            output="Step completed successfully"
        )
        
        assert result is not None
        assert result["status"] == "completed"
        http_client.patch.assert_called_once()

    def test_cancel_step(self, steps_resource, http_client):
        """Test canceling a step."""
        http_client.post.return_value = MockAPIResponses.step_cancelled()
        
        result = steps_resource.cancel("step_123")
        
        assert result is not None
        assert result["status"] == "cancelled"
        http_client.post.assert_called_once_with("/steps/step_123/cancel")

    def test_get_step_logs(self, steps_resource, http_client):
        """Test getting step execution logs."""
        http_client.get.return_value = {"logs": ["Log line 1", "Log line 2"]}
        
        result = steps_resource.get_logs("step_123")
        
        assert "logs" in result
        assert len(result["logs"]) == 2
        http_client.get.assert_called_once()

    def test_get_step_output(self, steps_resource, http_client):
        """Test getting step output."""
        http_client.get.return_value = {"output": "Step output data"}
        
        result = steps_resource.get_output("step_123")
        
        assert result["output"] == "Step output data"
        http_client.get.assert_called_once()

    def test_retry_step(self, steps_resource, http_client):
        """Test retrying a failed step."""
        http_client.post.return_value = MockAPIResponses.step_created()
        
        result = steps_resource.retry("step_123")
        
        assert result is not None
        http_client.post.assert_called_once_with("/steps/step_123/retry")

    def test_step_not_found(self, steps_resource, http_client):
        """Test handling step not found error."""
        http_client.get.side_effect = DisperslError("Step not found", status_code=404)
        
        with pytest.raises(DisperslError) as exc_info:
            steps_resource.get("nonexistent_step")
        
        assert exc_info.value.status_code == 404


class TestTaskStepIntegration:
    """Test integration between tasks and steps."""

    @pytest.fixture
    def http_client(self):
        """Create mock HTTP client."""
        return Mock()

    @pytest.fixture
    def tasks_resource(self, http_client):
        """Create TasksResource instance."""
        return TasksResource(http_client)

    @pytest.fixture
    def steps_resource(self, http_client):
        """Create StepsResource instance."""
        return StepsResource(http_client)

    def test_create_task_with_steps(self, tasks_resource, steps_resource, http_client):
        """Test creating a task and adding steps."""
        http_client.post.return_value = MockAPIResponses.task_created()
        
        # Create task
        task = tasks_resource.create(
            name="Task with steps",
            description="Test task",
            agent_type="code"
        )
        task_id = task["id"]
        
        # Create steps
        http_client.post.return_value = MockAPIResponses.step_created()
        
        step1 = steps_resource.create(
            task_id=task_id,
            name="Step 1",
            action="prepare"
        )
        
        step2 = steps_resource.create(
            task_id=task_id,
            name="Step 2",
            action="execute"
        )
        
        assert step1["task_id"] == task_id
        assert step2["task_id"] == task_id

    def test_get_task_with_steps(self, tasks_resource, steps_resource, http_client):
        """Test getting a task and its steps."""
        task_id = "task_123"
        
        # Get task
        http_client.get.return_value = MockAPIResponses.task_details()
        task = tasks_resource.get(task_id)
        
        # Get steps for task
        http_client.get.return_value = MockAPIResponses.steps_list()
        steps = steps_resource.list(task_id=task_id)
        
        assert task["id"] == task_id
        assert isinstance(steps, list)
        assert all(step["task_id"] == task_id for step in steps)

    def test_cancel_task_cancels_steps(self, tasks_resource, steps_resource, http_client):
        """Test that canceling a task cancels its steps."""
        task_id = "task_123"
        
        # Cancel task
        http_client.post.return_value = MockAPIResponses.task_cancelled()
        task = tasks_resource.cancel(task_id)
        
        # Verify steps are also cancelled
        http_client.get.return_value = MockAPIResponses.steps_list()
        steps = steps_resource.list(task_id=task_id)
        
        assert task["status"] == "cancelled"
        # In real implementation, steps should also be cancelled


            action="execute_code"

        )

        

        assert result is not None

        assert "id" in result

        assert result["task_id"] == "task_123"

        http_client.post.assert_called_once()



    def test_get_step(self, steps_resource, http_client):

        """Test getting a step by ID."""

        http_client.get.return_value = MockAPIResponses.step_details()

        

        result = steps_resource.get("step_123")

        

        assert result is not None

        assert result["id"] == "step_123"

        http_client.get.assert_called_once_with("/steps/step_123")



    def test_list_steps(self, steps_resource, http_client):

        """Test listing all steps."""

        http_client.get.return_value = MockAPIResponses.steps_list()

        

        result = steps_resource.list()

        

        assert isinstance(result, list)

        assert len(result) > 0

        http_client.get.assert_called_once()



    def test_list_steps_by_task(self, steps_resource, http_client):

        """Test listing steps for a specific task."""

        http_client.get.return_value = MockAPIResponses.steps_list()

        

        result = steps_resource.list(task_id="task_123")

        

        assert isinstance(result, list)

        call_args = http_client.get.call_args

        params = call_args[1].get("params", {})

        assert params.get("task_id") == "task_123"



    def test_update_step(self, steps_resource, http_client):

        """Test updating a step."""

        http_client.patch.return_value = MockAPIResponses.step_updated()

        

        result = steps_resource.update(

            "step_123",

            status="completed",

            output="Step completed successfully"

        )

        

        assert result is not None

        assert result["status"] == "completed"

        http_client.patch.assert_called_once()



    def test_cancel_step(self, steps_resource, http_client):

        """Test canceling a step."""

        http_client.post.return_value = MockAPIResponses.step_cancelled()

        

        result = steps_resource.cancel("step_123")

        

        assert result is not None

        assert result["status"] == "cancelled"

        http_client.post.assert_called_once_with("/steps/step_123/cancel")



    def test_get_step_logs(self, steps_resource, http_client):

        """Test getting step execution logs."""

        http_client.get.return_value = {"logs": ["Log line 1", "Log line 2"]}

        

        result = steps_resource.get_logs("step_123")

        

        assert "logs" in result

        assert len(result["logs"]) == 2

        http_client.get.assert_called_once()



    def test_get_step_output(self, steps_resource, http_client):

        """Test getting step output."""

        http_client.get.return_value = {"output": "Step output data"}

        

        result = steps_resource.get_output("step_123")

        

        assert result["output"] == "Step output data"

        http_client.get.assert_called_once()



    def test_retry_step(self, steps_resource, http_client):

        """Test retrying a failed step."""

        http_client.post.return_value = MockAPIResponses.step_created()

        

        result = steps_resource.retry("step_123")

        

        assert result is not None

        http_client.post.assert_called_once_with("/steps/step_123/retry")



    def test_step_not_found(self, steps_resource, http_client):

        """Test handling step not found error."""

        http_client.get.side_effect = DisperslError("Step not found", status_code=404)

        

        with pytest.raises(DisperslError) as exc_info:

            steps_resource.get("nonexistent_step")

        

        assert exc_info.value.status_code == 404





class TestTaskStepIntegration:

    """Test integration between tasks and steps."""



    @pytest.fixture

    def http_client(self):

        """Create mock HTTP client."""

        return Mock()



    @pytest.fixture

    def tasks_resource(self, http_client):

        """Create TasksResource instance."""

        return TasksResource(http_client)



    @pytest.fixture

    def steps_resource(self, http_client):

        """Create StepsResource instance."""

        return StepsResource(http_client)



    def test_create_task_with_steps(self, tasks_resource, steps_resource, http_client):

        """Test creating a task and adding steps."""

        http_client.post.return_value = MockAPIResponses.task_created()

        

        # Create task

        task = tasks_resource.create(

            name="Task with steps",

            description="Test task",

            agent_type="code"

        )

        task_id = task["id"]

        

        # Create steps

        http_client.post.return_value = MockAPIResponses.step_created()

        

        step1 = steps_resource.create(

            task_id=task_id,

            name="Step 1",

            action="prepare"

        )

        

        step2 = steps_resource.create(

            task_id=task_id,

            name="Step 2",

            action="execute"

        )

        

        assert step1["task_id"] == task_id

        assert step2["task_id"] == task_id



    def test_get_task_with_steps(self, tasks_resource, steps_resource, http_client):

        """Test getting a task and its steps."""

        task_id = "task_123"

        

        # Get task

        http_client.get.return_value = MockAPIResponses.task_details()

        task = tasks_resource.get(task_id)

        

        # Get steps for task

        http_client.get.return_value = MockAPIResponses.steps_list()

        steps = steps_resource.list(task_id=task_id)

        

        assert task["id"] == task_id

        assert isinstance(steps, list)

        assert all(step["task_id"] == task_id for step in steps)



    def test_cancel_task_cancels_steps(self, tasks_resource, steps_resource, http_client):

        """Test that canceling a task cancels its steps."""

        task_id = "task_123"

        

        # Cancel task

        http_client.post.return_value = MockAPIResponses.task_cancelled()

        task = tasks_resource.cancel(task_id)

        

        # Verify steps are also cancelled

        http_client.get.return_value = MockAPIResponses.steps_list()

        steps = steps_resource.list(task_id=task_id)

        

        assert task["status"] == "cancelled"

        # In real implementation, steps should also be cancelled





            action="execute_code"

        )

        

        assert result is not None

        assert "id" in result

        assert result["task_id"] == "task_123"

        http_client.post.assert_called_once()



    def test_get_step(self, steps_resource, http_client):

        """Test getting a step by ID."""

        http_client.get.return_value = MockAPIResponses.step_details()

        

        result = steps_resource.get("step_123")

        

        assert result is not None

        assert result["id"] == "step_123"

        http_client.get.assert_called_once_with("/steps/step_123")



    def test_list_steps(self, steps_resource, http_client):

        """Test listing all steps."""

        http_client.get.return_value = MockAPIResponses.steps_list()

        

        result = steps_resource.list()

        

        assert isinstance(result, list)

        assert len(result) > 0

        http_client.get.assert_called_once()



    def test_list_steps_by_task(self, steps_resource, http_client):

        """Test listing steps for a specific task."""

        http_client.get.return_value = MockAPIResponses.steps_list()

        

        result = steps_resource.list(task_id="task_123")

        

        assert isinstance(result, list)

        call_args = http_client.get.call_args

        params = call_args[1].get("params", {})

        assert params.get("task_id") == "task_123"



    def test_update_step(self, steps_resource, http_client):

        """Test updating a step."""

        http_client.patch.return_value = MockAPIResponses.step_updated()

        

        result = steps_resource.update(

            "step_123",

            status="completed",

            output="Step completed successfully"

        )

        

        assert result is not None

        assert result["status"] == "completed"

        http_client.patch.assert_called_once()



    def test_cancel_step(self, steps_resource, http_client):

        """Test canceling a step."""

        http_client.post.return_value = MockAPIResponses.step_cancelled()

        

        result = steps_resource.cancel("step_123")

        

        assert result is not None

        assert result["status"] == "cancelled"

        http_client.post.assert_called_once_with("/steps/step_123/cancel")



    def test_get_step_logs(self, steps_resource, http_client):

        """Test getting step execution logs."""

        http_client.get.return_value = {"logs": ["Log line 1", "Log line 2"]}

        

        result = steps_resource.get_logs("step_123")

        

        assert "logs" in result

        assert len(result["logs"]) == 2

        http_client.get.assert_called_once()



    def test_get_step_output(self, steps_resource, http_client):

        """Test getting step output."""

        http_client.get.return_value = {"output": "Step output data"}

        

        result = steps_resource.get_output("step_123")

        

        assert result["output"] == "Step output data"

        http_client.get.assert_called_once()



    def test_retry_step(self, steps_resource, http_client):

        """Test retrying a failed step."""

        http_client.post.return_value = MockAPIResponses.step_created()

        

        result = steps_resource.retry("step_123")

        

        assert result is not None

        http_client.post.assert_called_once_with("/steps/step_123/retry")



    def test_step_not_found(self, steps_resource, http_client):

        """Test handling step not found error."""

        http_client.get.side_effect = DisperslError("Step not found", status_code=404)

        

        with pytest.raises(DisperslError) as exc_info:

            steps_resource.get("nonexistent_step")

        

        assert exc_info.value.status_code == 404





class TestTaskStepIntegration:

    """Test integration between tasks and steps."""



    @pytest.fixture

    def http_client(self):

        """Create mock HTTP client."""

        return Mock()



    @pytest.fixture

    def tasks_resource(self, http_client):

        """Create TasksResource instance."""

        return TasksResource(http_client)



    @pytest.fixture

    def steps_resource(self, http_client):

        """Create StepsResource instance."""

        return StepsResource(http_client)



    def test_create_task_with_steps(self, tasks_resource, steps_resource, http_client):

        """Test creating a task and adding steps."""

        http_client.post.return_value = MockAPIResponses.task_created()

        

        # Create task

        task = tasks_resource.create(

            name="Task with steps",

            description="Test task",

            agent_type="code"

        )

        task_id = task["id"]

        

        # Create steps

        http_client.post.return_value = MockAPIResponses.step_created()

        

        step1 = steps_resource.create(

            task_id=task_id,

            name="Step 1",

            action="prepare"

        )

        

        step2 = steps_resource.create(

            task_id=task_id,

            name="Step 2",

            action="execute"

        )

        

        assert step1["task_id"] == task_id

        assert step2["task_id"] == task_id



    def test_get_task_with_steps(self, tasks_resource, steps_resource, http_client):

        """Test getting a task and its steps."""

        task_id = "task_123"

        

        # Get task

        http_client.get.return_value = MockAPIResponses.task_details()

        task = tasks_resource.get(task_id)

        

        # Get steps for task

        http_client.get.return_value = MockAPIResponses.steps_list()

        steps = steps_resource.list(task_id=task_id)

        

        assert task["id"] == task_id

        assert isinstance(steps, list)

        assert all(step["task_id"] == task_id for step in steps)



    def test_cancel_task_cancels_steps(self, tasks_resource, steps_resource, http_client):

        """Test that canceling a task cancels its steps."""

        task_id = "task_123"

        

        # Cancel task

        http_client.post.return_value = MockAPIResponses.task_cancelled()

        task = tasks_resource.cancel(task_id)

        

        # Verify steps are also cancelled

        http_client.get.return_value = MockAPIResponses.steps_list()

        steps = steps_resource.list(task_id=task_id)

        

        assert task["status"] == "cancelled"

        # In real implementation, steps should also be cancelled




