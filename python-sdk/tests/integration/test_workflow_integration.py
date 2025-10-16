"""Integration tests for complete agentic workflows."""

import pytest
import os
from dispersl import Dispersl
from dispersl.agentic import AgenticExecutor
from dispersl.exceptions import DisperslError


@pytest.mark.integration
class TestAgenticWorkflowIntegration:
    """Test complete agentic workflow integration."""

    @pytest.fixture
    def client(self, api_url, api_key):
        """Create Dispersl client for integration tests."""
        return Dispersl(api_key=api_key, base_url=api_url)

    @pytest.fixture
    def executor(self, client):
        """Create agentic executor."""
        return AgenticExecutor(client._http_client)

    @pytest.mark.skipif(
        os.getenv("RUN_INTEGRATION_TESTS") != "true",
        reason="Integration tests disabled"
    )
    def test_simple_chat_workflow(self, executor):
        """Test a simple chat workflow."""
        session_id = executor.start_session()
        
        try:
            result = executor.execute_workflow(
                session_id=session_id,
                prompt="Hello, how are you?",
                agent_type="chat",
                default_dir="/tmp/test",
                current_dir="/tmp/test"
            )
            
            assert result is not None
            assert isinstance(result, dict)
            
        finally:
            executor.end_session(session_id)

    @pytest.mark.skipif(
        os.getenv("RUN_INTEGRATION_TESTS") != "true",
        reason="Integration tests disabled"
    )
    def test_code_generation_workflow(self, executor):
        """Test code generation workflow."""
        session_id = executor.start_session()
        
        try:
            result = executor.execute_workflow(
                session_id=session_id,
                prompt="Create a simple Python function to calculate factorial",
                agent_type="code",
                default_dir="/tmp/test",
                current_dir="/tmp/test"
            )
            
            assert result is not None
            # Should contain generated code
            assert "code" in str(result).lower() or "function" in str(result).lower()
            
        finally:
            executor.end_session(session_id)

    @pytest.mark.skipif(
        os.getenv("RUN_INTEGRATION_TESTS") != "true",
        reason="Integration tests disabled"
    )
    def test_multi_step_workflow(self, client):
        """Test multi-step workflow with task and step creation."""
        # Create a task
        task = client.tasks.create(
            name="Integration Test Task",
            description="Test multi-step workflow",
            agent_type="code"
        )
        
        assert task is not None
        assert "id" in task
        task_id = task["id"]
        
        try:
            # Create steps
            step1 = client.steps.create(
                task_id=task_id,
                name="Step 1: Prepare",
                action="prepare"
            )
            
            step2 = client.steps.create(
                task_id=task_id,
                name="Step 2: Execute",
                action="execute"
            )
            
            assert step1["task_id"] == task_id
            assert step2["task_id"] == task_id
            
            # Get task status
            task_status = client.tasks.get_status(task_id)
            assert "status" in task_status
            
        finally:
            # Cleanup
            try:
                client.tasks.cancel(task_id)
            except:
                pass

    @pytest.mark.skipif(
        os.getenv("RUN_INTEGRATION_TESTS") != "true",
        reason="Integration tests disabled"
    )
    def test_workflow_with_context(self, executor):
        """Test workflow with context sharing."""
        session_id = executor.start_session()
        
        try:
            # Add context to session
            session = executor.get_session(session_id)
            session.update_context({
                "language": "python",
                "framework": "pytest",
                "task": "create tests"
            })
            
            result = executor.execute_workflow(
                session_id=session_id,
                prompt="Create unit tests using the specified framework",
                agent_type="test",
                default_dir="/tmp/test",
                current_dir="/tmp/test"
            )
            
            assert result is not None
            
        finally:
            executor.end_session(session_id)

    @pytest.mark.skipif(
        os.getenv("RUN_INTEGRATION_TESTS") != "true",
        reason="Integration tests disabled"
    )
    def test_streaming_workflow(self, executor):
        """Test streaming workflow execution."""
        session_id = executor.start_session()
        
        try:
            chunks = []
            for chunk in executor.execute_workflow_stream(
                session_id=session_id,
                prompt="Generate a simple function",
                agent_type="code",
                default_dir="/tmp/test",
                current_dir="/tmp/test"
            ):
                chunks.append(chunk)
            
            assert len(chunks) > 0
            
        finally:
            executor.end_session(session_id)

    @pytest.mark.skipif(
        os.getenv("RUN_INTEGRATION_TESTS") != "true",
        reason="Integration tests disabled"
    )
    def test_workflow_with_tools(self, executor):
        """Test workflow with custom tools."""
        session_id = executor.start_session()
        
        # Register a custom tool
        def calculator(operation: str, a: float, b: float) -> float:
            if operation == "add":
                return a + b
            elif operation == "subtract":
                return a - b
            elif operation == "multiply":
                return a * b
            elif operation == "divide":
                return a / b if b != 0 else 0
            return 0
        
        executor.tool_registry.register("calculator", calculator)
        
        try:
            result = executor.execute_workflow(
                session_id=session_id,
                prompt="Calculate 10 plus 5 using the calculator tool",
                agent_type="chat",
                default_dir="/tmp/test",
                current_dir="/tmp/test"
            )
            
            assert result is not None
            
        finally:
            executor.end_session(session_id)

    @pytest.mark.skipif(
        os.getenv("RUN_INTEGRATION_TESTS") != "true",
        reason="Integration tests disabled"
    )
    def test_error_recovery_workflow(self, executor):
        """Test workflow error recovery."""
        session_id = executor.start_session()
        
        try:
            # Execute a workflow that might fail
            result = executor.execute_workflow(
                session_id=session_id,
                prompt="Execute invalid command",
                agent_type="code",
                default_dir="/tmp/test",
                current_dir="/tmp/test",
                max_iterations=2
            )
            
            # Should handle gracefully
            assert result is not None
            
        except DisperslError as e:
            # Error handling is expected
            assert e is not None
            
        finally:
            executor.end_session(session_id)


@pytest.mark.integration
class TestAPIEndpointsIntegration:
    """Test API endpoints integration."""

    @pytest.fixture
    def client(self, api_url, api_key):
        """Create Dispersl client for integration tests."""
        return Dispersl(api_key=api_key, base_url=api_url)

    @pytest.mark.skipif(
        os.getenv("RUN_INTEGRATION_TESTS") != "true",
        reason="Integration tests disabled"
    )
    def test_models_endpoint(self, client):
        """Test models endpoint."""
        models = client.models.list()
        
        assert isinstance(models, list)
        if len(models) > 0:
            assert "id" in models[0] or "name" in models[0]

    @pytest.mark.skipif(
        os.getenv("RUN_INTEGRATION_TESTS") != "true",
        reason="Integration tests disabled"
    )
    def test_health_endpoint(self, client):
        """Test health check endpoint."""
        result = client.health_check()
        
        assert result is not None
        assert "status" in result

    @pytest.mark.skipif(
        os.getenv("RUN_INTEGRATION_TESTS") != "true",
        reason="Integration tests disabled"
    )
    def test_auth_verification(self, client):
        """Test authentication verification."""
        result = client.verify_connection()
        
        assert result is True

    @pytest.mark.skipif(
        os.getenv("RUN_INTEGRATION_TESTS") != "true",
        reason="Integration tests disabled"
    )
    def test_task_crud_operations(self, client):
        """Test complete CRUD operations on tasks."""
        # Create
        task = client.tasks.create(
            name="CRUD Test Task",
            description="Testing CRUD operations",
            agent_type="code"
        )
        
        assert "id" in task
        task_id = task["id"]
        
        try:
            # Read
            retrieved_task = client.tasks.get(task_id)
            assert retrieved_task["id"] == task_id
            
            # Update
            updated_task = client.tasks.update(
                task_id,
                status="in_progress"
            )
            assert updated_task["status"] == "in_progress"
            
            # List
            tasks = client.tasks.list()
            assert isinstance(tasks, list)
            assert any(t["id"] == task_id for t in tasks)
            
        finally:
            # Delete
            try:
                client.tasks.delete(task_id)
            except:
                pass


@pytest.mark.integration
class TestMCPIntegration:
    """Test MCP (Model Context Protocol) integration."""

    @pytest.fixture
    def executor(self, api_url, api_key):
        """Create executor with MCP support."""
        client = Dispersl(api_key=api_key, base_url=api_url)
        return AgenticExecutor(client._http_client)

    @pytest.mark.skipif(
        os.getenv("RUN_INTEGRATION_TESTS") != "true",
        reason="Integration tests disabled"
    )
    def test_mcp_client_management(self, executor):
        """Test MCP client management."""
        from unittest.mock import Mock
        
        mcp_client = Mock()
        
        # Add MCP client
        executor.add_mcp_client("test_server", mcp_client)
        assert executor.has_mcp_client("test_server")
        
        # Remove MCP client
        executor.remove_mcp_client("test_server")
        assert not executor.has_mcp_client("test_server")

    @pytest.mark.skipif(
        os.getenv("RUN_INTEGRATION_TESTS") != "true",
        reason="Integration tests disabled"
    )
    def test_workflow_with_mcp(self, executor):
        """Test workflow execution with MCP tools."""
        from unittest.mock import Mock
        
        # Setup mock MCP client
        mcp_client = Mock()
        mcp_client.execute_tool = Mock(return_value={"result": "MCP tool executed"})
        
        executor.add_mcp_client("test_server", mcp_client)
        
        session_id = executor.start_session()
        
        try:
            # Execute workflow that uses MCP
            mcp_config = {
                "server": "test_server",
                "tools": ["test_tool"]
            }
            
            result = executor.execute_workflow(
                session_id=session_id,
                prompt="Use MCP tool",
                agent_type="chat",
                default_dir="/tmp/test",
                current_dir="/tmp/test",
                mcp_config=mcp_config
            )
            
            assert result is not None
            
        finally:
            executor.end_session(session_id)
            executor.remove_mcp_client("test_server")

