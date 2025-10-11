"""
Tests for the agentic execution module.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from dispersl.agentic import AgenticExecutor
from dispersl.models import (
    AgenticSession,
    HandoverRequest,
    MCPClient,
    MCPTool,
    StandardNdjsonResponse,
    ToolCall,
    ToolResponse,
)
from dispersl.exceptions import DisperslError


class TestAgenticExecutor:
    """Test cases for the AgenticExecutor class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.mock_http_client = Mock()
        self.executor = AgenticExecutor(self.mock_http_client)

    def test_create_session(self):
        """Test session creation."""
        session_id = self.executor.create_session()
        assert session_id is not None
        assert session_id in self.executor.sessions
        
        session = self.executor.sessions[session_id]
        assert isinstance(session, AgenticSession)
        assert session.id == session_id
        assert session.context == {}
        assert session.conversation_history == []
        assert session.active_tools == []
        assert session.tool_responses == []

    def test_create_session_with_custom_id(self):
        """Test session creation with custom ID."""
        custom_id = "test-session-123"
        session_id = self.executor.create_session(custom_id)
        assert session_id == custom_id
        assert custom_id in self.executor.sessions

    def test_get_session(self):
        """Test getting an existing session."""
        session_id = self.executor.create_session()
        session = self.executor.get_session(session_id)
        assert session is not None
        assert session.id == session_id

    def test_get_nonexistent_session(self):
        """Test getting a non-existent session."""
        session = self.executor.get_session("nonexistent")
        assert session is None

    def test_end_session(self):
        """Test ending a session."""
        session_id = self.executor.create_session()
        assert session_id in self.executor.sessions
        
        result = self.executor.end_session(session_id)
        assert result is True
        assert session_id not in self.executor.sessions

    def test_end_nonexistent_session(self):
        """Test ending a non-existent session."""
        result = self.executor.end_session("nonexistent")
        assert result is False

    def test_add_mcp_client(self):
        """Test adding an MCP client."""
        client = MCPClient(
            name="test-client",
            command="test-command",
            args=["arg1", "arg2"],
            env={"TEST_ENV": "test_value"}
        )
        
        self.executor.add_mcp_client(client)
        assert "test-client" in self.executor.mcp_clients
        assert self.executor.mcp_clients["test-client"] == client

    def test_remove_mcp_client(self):
        """Test removing an MCP client."""
        client = MCPClient(name="test-client")
        self.executor.add_mcp_client(client)
        
        result = self.executor.remove_mcp_client("test-client")
        assert result is True
        assert "test-client" not in self.executor.mcp_clients

    def test_remove_nonexistent_mcp_client(self):
        """Test removing a non-existent MCP client."""
        result = self.executor.remove_mcp_client("nonexistent")
        assert result is False

    def test_execute_agentic_workflow_basic(self):
        """Test basic agentic workflow execution."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.text = json.dumps({
            "content": "Test response",
            "tools": [],
            "status": "completed",
            "message": "Success"
        })
        self.mock_http_client.post.return_value = mock_response

        # Execute workflow
        request_data = {"prompt": "Test prompt"}
        responses = list(self.executor.execute_agentic_workflow(
            "/agent/chat",
            request_data,
            max_iterations=1
        ))

        # Verify response
        assert len(responses) == 1
        assert responses[0].content == "Test response"
        assert responses[0].status == "completed"

        # Verify HTTP client was called
        self.mock_http_client.post.assert_called_once()
        call_args = self.mock_http_client.post.call_args
        assert call_args[0][0] == "/agent/chat"
        assert call_args[1]["headers"]["Accept"] == "application/x-ndjson"

    def test_execute_agentic_workflow_with_tool_calls(self):
        """Test agentic workflow with tool calls."""
        # Mock HTTP response with tool calls
        tool_call = ToolCall(
            function={"name": "test_tool", "arguments": '{"arg": "value"}'},
            arguments='{"arg": "value"}'
        )
        
        mock_response = Mock()
        mock_response.text = json.dumps({
            "content": "Tool call response",
            "tools": [tool_call.dict()],
            "status": "in_progress",
            "message": "Processing"
        })
        self.mock_http_client.post.return_value = mock_response

        # Execute workflow
        request_data = {"prompt": "Test prompt"}
        responses = list(self.executor.execute_agentic_workflow(
            "/agent/chat",
            request_data,
            max_iterations=1
        ))

        # Verify response
        assert len(responses) == 1
        assert responses[0].content == "Tool call response"

    def test_execute_agentic_workflow_with_handover(self):
        """Test agentic workflow with handover."""
        # Mock HTTP response with handover tool call
        handover_tool_call = ToolCall(
            function={
                "name": "handover_task",
                "arguments": '{"agent_name": "code", "prompt": "New task"}'
            },
            arguments='{"agent_name": "code", "prompt": "New task"}'
        )
        
        mock_response = Mock()
        mock_response.text = json.dumps({
            "content": "Handover response",
            "tools": [handover_tool_call.dict()],
            "status": "in_progress",
            "message": "Handing over"
        })
        self.mock_http_client.post.return_value = mock_response

        # Execute workflow
        request_data = {"prompt": "Test prompt"}
        responses = list(self.executor.execute_agentic_workflow(
            "/agent/chat",
            request_data,
            max_iterations=1
        ))

        # Verify response
        assert len(responses) == 1
        assert responses[0].content == "Handover response"

    def test_execute_agentic_workflow_max_iterations(self):
        """Test agentic workflow hitting max iterations."""
        # Mock HTTP response that always returns tool calls
        tool_call = ToolCall(
            function={"name": "test_tool", "arguments": '{"arg": "value"}'},
            arguments='{"arg": "value"}'
        )
        
        mock_response = Mock()
        mock_response.text = json.dumps({
            "content": "Tool call response",
            "tools": [tool_call.dict()],
            "status": "in_progress",
            "message": "Processing"
        })
        self.mock_http_client.post.return_value = mock_response

        # Execute workflow with max iterations
        request_data = {"prompt": "Test prompt"}
        responses = list(self.executor.execute_agentic_workflow(
            "/agent/chat",
            request_data,
            max_iterations=2
        ))

        # Verify HTTP client was called multiple times
        assert self.mock_http_client.post.call_count == 2

    def test_execute_agentic_workflow_error_handling(self):
        """Test agentic workflow error handling."""
        # Mock HTTP client to raise an exception
        self.mock_http_client.post.side_effect = Exception("Network error")

        # Execute workflow
        request_data = {"prompt": "Test prompt"}
        responses = list(self.executor.execute_agentic_workflow(
            "/agent/chat",
            request_data,
            max_iterations=1
        ))

        # Verify no responses due to error
        assert len(responses) == 0

    def test_parse_text_tool_calls(self):
        """Test parsing text-based tool calls."""
        text = """Some text before
<｜tool▁call▁begin｜>function<｜tool▁sep｜>test_tool
json
{"arg": "value"}
<｜tool▁call▁end｜>
Some text after"""

        tool_calls = self.executor.parse_text_tool_calls(text)
        
        assert len(tool_calls) == 1
        assert tool_calls[0].function["name"] == "test_tool"
        assert tool_calls[0].function["arguments"] == '{"arg": "value"}'

    def test_parse_text_tool_calls_multiple(self):
        """Test parsing multiple text-based tool calls."""
        text = """Text before
<｜tool▁call▁begin｜>function<｜tool▁sep｜>tool1
json
{"arg1": "value1"}
<｜tool▁call▁end｜>
Middle text
<｜tool▁call▁begin｜>function<｜tool▁sep｜>tool2
json
{"arg2": "value2"}
<｜tool▁call▁end｜>
Text after"""

        tool_calls = self.executor.parse_text_tool_calls(text)
        
        assert len(tool_calls) == 2
        assert tool_calls[0].function["name"] == "tool1"
        assert tool_calls[1].function["name"] == "tool2"

    def test_parse_text_tool_calls_invalid_format(self):
        """Test parsing invalid text-based tool calls."""
        text = "Invalid tool call format"
        
        tool_calls = self.executor.parse_text_tool_calls(text)
        assert len(tool_calls) == 0

    def test_get_built_in_tools(self):
        """Test getting built-in tools list."""
        tools = self.executor._get_built_in_tools()
        assert isinstance(tools, list)
        assert "list_files" in tools
        assert "read_file" in tools
        assert "write_to_file" in tools

    def test_execute_built_in_tool(self):
        """Test executing built-in tools."""
        session = AgenticSession(id="test", context={})
        
        # Test list_files tool
        result = self.executor._execute_built_in_tool("list_files", {}, session)
        assert "files" in json.loads(result)
        
        # Test read_file tool
        result = self.executor._execute_built_in_tool("read_file", {}, session)
        assert result == "File content here"

    def test_execute_tool_not_found(self):
        """Test executing a non-existent tool."""
        session = AgenticSession(id="test", context={})
        
        with pytest.raises(DisperslError, match="Tool nonexistent not found"):
            self.executor._execute_tool("nonexistent", {}, session)

    def test_get_endpoint_for_agent(self):
        """Test getting endpoint for different agents."""
        assert self.executor._get_endpoint_for_agent("code") == "/agent/code"
        assert self.executor._get_endpoint_for_agent("test") == "/agent/test"
        assert self.executor._get_endpoint_for_agent("git") == "/agent/git"
        assert self.executor._get_endpoint_for_agent("docs") == "/agent/document/repo"
        assert self.executor._get_endpoint_for_agent("chat") == "/agent/chat"
        assert self.executor._get_endpoint_for_agent("plan") == "/agent/plan"
        assert self.executor._get_endpoint_for_agent("unknown") == "/agent/chat"

    def test_process_tool_calls_end_session(self):
        """Test processing end_session tool call."""
        session = AgenticSession(id="test", context={})
        tool_call = ToolCall(
            function={"name": "end_session", "arguments": "{}"},
            arguments="{}"
        )
        
        tool_responses, handover = self.executor._process_tool_calls([tool_call], session)
        
        assert len(tool_responses) == 1
        assert tool_responses[0].tool == "end_session"
        assert tool_responses[0].status == "SUCCESS"
        assert handover is None

    def test_process_tool_calls_handover(self):
        """Test processing handover tool call."""
        session = AgenticSession(id="test", context={})
        tool_call = ToolCall(
            function={
                "name": "handover_task",
                "arguments": '{"agent_name": "code", "prompt": "New task"}'
            },
            arguments='{"agent_name": "code", "prompt": "New task"}'
        )
        
        tool_responses, handover = self.executor._process_tool_calls([tool_call], session)
        
        assert len(tool_responses) == 1
        assert tool_responses[0].tool == "handover_task"
        assert tool_responses[0].status == "SUCCESS"
        assert handover is not None
        assert handover.agent_name == "code"
        assert handover.prompt == "New task"

    def test_process_tool_calls_error(self):
        """Test processing tool calls with errors."""
        session = AgenticSession(id="test", context={})
        tool_call = ToolCall(
            function={"name": "invalid_tool", "arguments": "{}"},
            arguments="{}"
        )
        
        tool_responses, handover = self.executor._process_tool_calls([tool_call], session)
        
        assert len(tool_responses) == 1
        assert tool_responses[0].tool == "invalid_tool"
        assert tool_responses[0].status == "FAILURE"
        assert "Error executing tool" in tool_responses[0].message
        assert handover is None
