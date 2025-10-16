"""Comprehensive unit tests for agentic execution functionality."""

import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock

# Add tests directory to path for fixtures
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dispersl.agentic import AgenticExecutor
from dispersl.models.api import AgenticSession
from dispersl.exceptions import DisperslError, ValidationError
from fixtures.mock_api_responses import MockAPIResponses


class TestAgenticSession:
    """Test agentic session management."""

    def test_create_session(self):
        """Test creating a new session."""
        session = AgenticSession(id="session_123")
        
        assert session.session_id == "session_123"
        assert session.context == {}
        assert session.history == []

    def test_session_with_initial_context(self):
        """Test creating session with initial context."""
        context = {"user_id": "user_123", "project": "test_project"}
        session = AgenticSession(id="session_123", context=context)
        
        assert session.context == context

    def test_add_message_to_history(self):
        """Test adding messages to session history."""
        session = AgenticSession(id="session_123")
        
        session.add_message("user", "Hello")
        session.add_message("assistant", "Hi there!")
        
        assert len(session.history) == 2
        assert session.history[0]["role"] == "user"
        assert session.history[1]["role"] == "assistant"

    def test_update_context(self):
        """Test updating session context."""
        session = AgenticSession(id="session_123")
        
        session.update_context({"key": "value"})
        assert session.context["key"] == "value"
        
        session.update_context({"key": "updated"})
        assert session.context["key"] == "updated"

    def test_clear_history(self):
        """Test clearing session history."""
        session = AgenticSession(id="session_123")
        
        session.add_message("user", "Message 1")
        session.add_message("assistant", "Response 1")
        
        session.clear_history()
        assert len(session.history) == 0

    def test_get_session_state(self):
        """Test getting full session state."""
        session = AgenticSession(id="session_123")
        session.add_message("user", "Test")
        session.update_context({"data": "value"})
        
        state = session.get_state()
        
        assert state["session_id"] == "session_123"
        assert len(state["history"]) == 1
        assert state["context"]["data"] == "value"


class TestAgenticExecutor:
    """Test agentic executor functionality."""

    @pytest.fixture
    def http_client(self):
        """Create mock HTTP client."""
        return Mock()

    @pytest.fixture
    def executor(self, http_client):
        """Create AgenticExecutor instance."""
        return AgenticExecutor(http_client, auto_load_mcp_config=False)

    def test_create_executor(self, executor):
        """Test creating an executor."""
        assert executor is not None
        assert isinstance(executor.sessions, dict)
        assert isinstance(executor.mcp_clients, dict)

    def test_create_session(self, executor):
        """Test creating a new session."""
        session_id = executor.create_session()
        
        assert session_id is not None
        assert session_id in executor.sessions

    def test_create_session_with_id(self, executor):
        """Test creating session with custom ID."""
        session_id = executor.create_session(id="custom_123")
        
        assert session_id == "custom_123"
        assert "custom_123" in executor.sessions

    def test_get_session(self, executor):
        """Test getting an active session."""
        session_id = executor.create_session()
        session = executor.get_session(session_id)
        
        assert session is not None
        assert session.session_id == session_id

    def test_end_session(self, executor):
        """Test ending a session."""
        session_id = executor.create_session()
        
        result = executor.end_session(session_id)
        
        assert result is True
        assert session_id not in executor.sessions

    def test_execute_workflow_basic(self, executor, http_client):
        """Test executing a basic agentic workflow."""
        http_client.post_stream.return_value = MockAPIResponses.agentic_workflow_stream()
        
        session_id = executor.create_session()
        
        result = executor.execute_workflow(
            id=session_id,
            prompt="Execute a task",
            agent_type="code",
            default_dir="/project",
            current_dir="/project"
        )
        
        assert result is not None

    def test_execute_workflow_with_tools(self, executor, http_client):
        """Test executing workflow with tool calls."""
        http_client.post_stream.return_value = MockAPIResponses.agentic_workflow_with_tools()
        
        # Register a test tool
        def search_tool(query: str) -> str:
            return f"Search results for: {query}"
        
        executor.tool_registry.register("search", search_tool)
        
        session_id = executor.create_session()
        
        result = executor.execute_workflow(
            id=session_id,
            prompt="Search for information",
            agent_type="chat",
            default_dir="/project",
            current_dir="/project"
        )
        
        assert result is not None

    def test_execute_workflow_with_handover(self, executor, http_client):
        """Test executing workflow with agent handover."""
        http_client.post_stream.return_value = MockAPIResponses.agentic_workflow_with_handover()
        
        session_id = executor.create_session()
        
        result = executor.execute_workflow(
            id=session_id,
            prompt="Complex task requiring handover",
            agent_type="plan",
            default_dir="/project",
            current_dir="/project"
        )
        
        assert result is not None
        # Verify handover occurred
        session = executor.get_session(session_id)
        assert len(session.history) > 0

    def test_execute_workflow_streaming(self, executor, http_client):
        """Test executing workflow with streaming."""
        http_client.post_stream.return_value = MockAPIResponses.agentic_workflow_stream()
        
        session_id = executor.create_session()
        
        chunks = []
        for chunk in executor.execute_workflow_stream(
            id=session_id,
            prompt="Stream this task",
            agent_type="code",
            default_dir="/project",
            current_dir="/project"
        ):
            chunks.append(chunk)
        
        assert len(chunks) > 0

    def test_execute_workflow_with_context(self, executor, http_client):
        """Test executing workflow with context."""
        http_client.post_stream.return_value = MockAPIResponses.agentic_workflow_stream()
        
        session_id = executor.create_session()
        session = executor.get_session(session_id)
        session.update_context({"project": "test", "language": "python"})
        
        result = executor.execute_workflow(
            id=session_id,
            prompt="Use context",
            agent_type="code",
            default_dir="/project",
            current_dir="/project"
        )
        
        assert result is not None

    def test_execute_workflow_error_handling(self, executor, http_client):
        """Test workflow error handling."""
        http_client.post_stream.side_effect = DisperslError("Workflow error")
        
        session_id = executor.create_session()
        
        with pytest.raises(DisperslError):
            executor.execute_workflow(
                id=session_id,
                prompt="This will fail",
                agent_type="code",
                default_dir="/project",
                current_dir="/project"
            )

    def test_execute_workflow_with_max_iterations(self, executor, http_client):
        """Test workflow with maximum iterations."""
        http_client.post_stream.return_value = MockAPIResponses.agentic_workflow_stream()
        
        session_id = executor.create_session()
        
        result = executor.execute_workflow(
            id=session_id,
            prompt="Limited iterations",
            agent_type="code",
            default_dir="/project",
            current_dir="/project",
            max_iterations=5
        )
        
        assert result is not None

    def test_parse_tool_calls(self, executor):
        """Test parsing tool calls from response."""
        response_text = """
        <tool_call>
        <name>search</name>
        <arguments>{"query": "test"}</arguments>
        </tool_call>
        """
        
        tool_calls = executor.parse_tool_calls(response_text)
        
        assert len(tool_calls) > 0
        assert tool_calls[0]["name"] == "search"

    def test_execute_tool_call(self, executor):
        """Test executing a tool call."""
        def test_tool(arg1: str) -> str:
            return f"Result: {arg1}"
        
        executor.tool_registry.register("test_tool", test_tool)
        
        tool_call = {
            "name": "test_tool",
            "arguments": {"arg1": "value"}
        }
        
        result = executor.execute_tool_call(tool_call)
        
        assert result == "Result: value"

    def test_handle_agent_handover(self, executor, http_client):
        """Test handling agent handover."""
        http_client.post_stream.return_value = MockAPIResponses.agentic_workflow_stream()
        
        session_id = executor.create_session()
        
        handover_data = {
            "from_agent": "plan",
            "to_agent": "code",
            "context": {"task": "implement feature"},
            "reason": "requires code execution"
        }
        
        result = executor.handle_handover(session_id, handover_data)
        
        assert result is not None

    def test_concurrent_sessions(self, executor):
        """Test managing multiple concurrent sessions."""
        session_ids = [executor.create_session() for _ in range(5)]
        
        assert len(session_ids) == 5
        assert all(sid in executor.sessions for sid in session_ids)
        
        # End all sessions
        for session_id in session_ids:
            executor.end_session(session_id)
        
        assert not any(sid in executor.sessions for sid in session_ids)

    def test_session_isolation(self, executor):
        """Test that sessions are isolated from each other."""
        session1 = executor.create_session()
        session2 = executor.create_session()
        
        # Update session1 context
        s1 = executor.get_session(session1)
        s1.update_context({"data": "session1"})
        
        # Session2 should not have this context
        s2 = executor.get_session(session2)
        assert "data" not in s2.context

    def test_add_mcp_client(self, executor):
        """Test adding MCP client."""
        mcp_client = Mock()
        
        executor.add_mcp_client("test_server", mcp_client)
        
        assert executor.has_mcp_client("test_server")

    def test_remove_mcp_client(self, executor):
        """Test removing MCP client."""
        mcp_client = Mock()
        
        executor.add_mcp_client("test_server", mcp_client)
        assert executor.has_mcp_client("test_server")
        
        executor.remove_mcp_client("test_server")
        assert not executor.has_mcp_client("test_server")

    def test_execute_mcp_tool(self, executor):
        """Test executing MCP tool."""
        mcp_client = Mock()
        mcp_client.execute_tool = Mock(return_value="MCP result")
        
        executor.add_mcp_client("test_server", mcp_client)
        
        result = executor.execute_mcp_tool("test_server", "test_tool", {"arg": "value"})
        
        assert result == "MCP result"
        mcp_client.execute_tool.assert_called_once()



    def test_execute_workflow_with_tools(self, executor, http_client):

        """Test executing workflow with tool calls."""

        http_client.post_stream.return_value = MockAPIResponses.agentic_workflow_with_tools()

        

        # Register a test tool

        def search_tool(query: str) -> str:

            return f"Search results for: {query}"

        

        executor.tool_registry.register("search", search_tool)

        

        session_id = executor.start_session()

        

        result = executor.execute_workflow(

            session_id=session_id,

            prompt="Search for information",

            agent_type="chat",

            default_dir="/project",

            current_dir="/project"

        )

        

        assert result is not None



    def test_execute_workflow_with_handover(self, executor, http_client):

        """Test executing workflow with agent handover."""

        http_client.post_stream.return_value = MockAPIResponses.agentic_workflow_with_handover()

        

        session_id = executor.start_session()

        

        result = executor.execute_workflow(

            session_id=session_id,

            prompt="Complex task requiring handover",

            agent_type="plan",

            default_dir="/project",

            current_dir="/project"

        )

        

        assert result is not None

        # Verify handover occurred

        session = executor.get_session(session_id)

        assert len(session.history) > 0



    def test_execute_workflow_streaming(self, executor, http_client):

        """Test executing workflow with streaming."""

        http_client.post_stream.return_value = MockAPIResponses.agentic_workflow_stream()

        

        session_id = executor.start_session()

        

        chunks = []

        for chunk in executor.execute_workflow_stream(

            session_id=session_id,

            prompt="Stream this task",

            agent_type="code",

            default_dir="/project",

            current_dir="/project"

        ):

            chunks.append(chunk)

        

        assert len(chunks) > 0



    def test_execute_workflow_with_context(self, executor, http_client):

        """Test executing workflow with context."""

        http_client.post_stream.return_value = MockAPIResponses.agentic_workflow_stream()

        

        session_id = executor.start_session()

        session = executor.get_session(session_id)

        session.update_context({"project": "test", "language": "python"})

        

        result = executor.execute_workflow(

            session_id=session_id,

            prompt="Use context",

            agent_type="code",

            default_dir="/project",

            current_dir="/project"

        )

        

        assert result is not None



    def test_execute_workflow_error_handling(self, executor, http_client):

        """Test workflow error handling."""

        http_client.post_stream.side_effect = DisperslError("Workflow error")

        

        session_id = executor.start_session()

        

        with pytest.raises(DisperslError):

            executor.execute_workflow(

                session_id=session_id,

                prompt="This will fail",

                agent_type="code",

                default_dir="/project",

                current_dir="/project"

            )



    def test_execute_workflow_with_max_iterations(self, executor, http_client):

        """Test workflow with maximum iterations."""

        http_client.post_stream.return_value = MockAPIResponses.agentic_workflow_stream()

        

        session_id = executor.start_session()

        

        result = executor.execute_workflow(

            session_id=session_id,

            prompt="Limited iterations",

            agent_type="code",

            default_dir="/project",

            current_dir="/project",

            max_iterations=5

        )

        

        assert result is not None



    def test_parse_tool_calls(self, executor):

        """Test parsing tool calls from response."""

        response_text = """

        <tool_call>

        <name>search</name>

        <arguments>{"query": "test"}</arguments>

        </tool_call>

        """

        

        tool_calls = executor.parse_tool_calls(response_text)

        

        assert len(tool_calls) > 0

        assert tool_calls[0]["name"] == "search"



    def test_execute_tool_call(self, executor):

        """Test executing a tool call."""

        def test_tool(arg1: str) -> str:

            return f"Result: {arg1}"

        

        executor.tool_registry.register("test_tool", test_tool)

        

        tool_call = {

            "name": "test_tool",

            "arguments": {"arg1": "value"}

        }

        

        result = executor.execute_tool_call(tool_call)

        

        assert result == "Result: value"



    def test_handle_agent_handover(self, executor, http_client):

        """Test handling agent handover."""

        http_client.post_stream.return_value = MockAPIResponses.agentic_workflow_stream()

        

        session_id = executor.start_session()

        

        handover_data = {

            "from_agent": "plan",

            "to_agent": "code",

            "context": {"task": "implement feature"},

            "reason": "requires code execution"

        }

        

        result = executor.handle_handover(session_id, handover_data)

        

        assert result is not None



    def test_concurrent_sessions(self, executor):

        """Test managing multiple concurrent sessions."""

        session_ids = [executor.start_session() for _ in range(5)]

        

        assert len(session_ids) == 5

        assert all(executor.has_session(sid) for sid in session_ids)

        

        # End all sessions

        for session_id in session_ids:

            executor.end_session(session_id)

        

        assert not any(executor.has_session(sid) for sid in session_ids)



    def test_session_isolation(self, executor):

        """Test that sessions are isolated from each other."""

        session1 = executor.start_session()

        session2 = executor.start_session()

        

        # Update session1 context

        s1 = executor.get_session(session1)

        s1.update_context({"data": "session1"})

        

        # Session2 should not have this context

        s2 = executor.get_session(session2)

        assert "data" not in s2.context



    def test_add_mcp_client(self, executor):

        """Test adding MCP client."""

        mcp_client = Mock()

        

        executor.add_mcp_client("test_server", mcp_client)

        

        assert executor.has_mcp_client("test_server")



    def test_remove_mcp_client(self, executor):

        """Test removing MCP client."""

        mcp_client = Mock()

        

        executor.add_mcp_client("test_server", mcp_client)

        assert executor.has_mcp_client("test_server")

        

        executor.remove_mcp_client("test_server")

        assert not executor.has_mcp_client("test_server")



    def test_execute_mcp_tool(self, executor):

        """Test executing MCP tool."""

        mcp_client = Mock()

        mcp_client.execute_tool = Mock(return_value="MCP result")

        

        executor.add_mcp_client("test_server", mcp_client)

        

        result = executor.execute_mcp_tool("test_server", "test_tool", {"arg": "value"})

        

        assert result == "MCP result"

        mcp_client.execute_tool.assert_called_once()




