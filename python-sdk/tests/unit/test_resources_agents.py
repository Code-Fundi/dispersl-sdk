"""Comprehensive unit tests for AgentsResource."""

import sys
import os
import pytest
from unittest.mock import Mock, patch, MagicMock

# Add tests directory to path for fixtures
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from dispersl.resources import AgentsResource
from dispersl.exceptions import DisperslError, ValidationError
from fixtures.mock_api_responses import MockAPIResponses


class TestAgentsResource:
    """Test AgentsResource functionality."""

    @pytest.fixture
    def http_client(self):
        """Create mock HTTP client."""
        return Mock()

    @pytest.fixture
    def agents_resource(self, http_client):
        """Create AgentsResource instance."""
        return AgentsResource(http_client)

    def test_chat_agent_basic(self, agents_resource, http_client):
        """Test basic chat agent execution."""
        http_client.post.return_value = MockAPIResponses.chat_agent_response()
        
        result = agents_resource.chat(
            prompt="Hello, agent!",
            default_dir="/project",
            current_dir="/project/src"
        )
        
        assert result is not None
        assert "response" in result or "content" in result
        http_client.post.assert_called_once()

    def test_chat_agent_with_context(self, agents_resource, http_client):
        """Test chat agent with context files."""
        http_client.post.return_value = MockAPIResponses.chat_agent_response()
        
        result = agents_resource.chat(
            prompt="Analyze this code",
            default_dir="/project",
            current_dir="/project/src",
            context=["file1.py", "file2.py"]
        )
        
        assert result is not None
        call_args = http_client.post.call_args
        assert "context" in call_args[1]["json"]
        assert len(call_args[1]["json"]["context"]) == 2

    def test_chat_agent_with_knowledge(self, agents_resource, http_client):
        """Test chat agent with knowledge base."""
        http_client.post.return_value = MockAPIResponses.chat_agent_response()
        
        result = agents_resource.chat(
            prompt="Use this knowledge",
            default_dir="/project",
            current_dir="/project",
            knowledge=["doc1.md", "doc2.md"]
        )
        
        assert result is not None
        call_args = http_client.post.call_args
        assert "knowledge" in call_args[1]["json"]

    def test_chat_agent_with_model(self, agents_resource, http_client):
        """Test chat agent with specific model."""
        http_client.post.return_value = MockAPIResponses.chat_agent_response()
        
        result = agents_resource.chat(
            prompt="Hello",
            default_dir="/project",
            current_dir="/project",
            model="claude-3-opus-20240229"
        )
        
        assert result is not None
        call_args = http_client.post.call_args
        assert call_args[1]["json"]["model"] == "claude-3-opus-20240229"

    def test_chat_agent_streaming(self, agents_resource, http_client):
        """Test chat agent with streaming."""
        http_client.post_stream.return_value = MockAPIResponses.chat_agent_stream()
        
        stream = agents_resource.chat(
            prompt="Hello",
            default_dir="/project",
            current_dir="/project",
            stream=True
        )
        
        chunks = list(stream)
        assert len(chunks) > 0
        http_client.post_stream.assert_called_once()

    def test_plan_agent_basic(self, agents_resource, http_client):
        """Test plan agent execution."""
        http_client.post.return_value = MockAPIResponses.plan_agent_response()
        
        result = agents_resource.plan(
            prompt="Create a task plan",
            default_dir="/project",
            current_dir="/project",
            agent_choice=["code", "test"]
        )
        
        assert result is not None
        assert "plan" in result or "tasks" in result

    def test_plan_agent_with_multiple_agents(self, agents_resource, http_client):
        """Test plan agent with multiple agent choices."""
        http_client.post.return_value = MockAPIResponses.plan_agent_response()
        
        result = agents_resource.plan(
            prompt="Complex task",
            default_dir="/project",
            current_dir="/project",
            agent_choice=["code", "test", "docs", "git"]
        )
        
        assert result is not None
        call_args = http_client.post.call_args
        assert len(call_args[1]["json"]["agent_choice"]) == 4

    def test_plan_agent_with_memory(self, agents_resource, http_client):
        """Test plan agent with memory enabled."""
        http_client.post.return_value = MockAPIResponses.plan_agent_response()
        
        result = agents_resource.plan(
            prompt="Remember this task",
            default_dir="/project",
            current_dir="/project",
            agent_choice=["code"],
            memory=True
        )
        
        assert result is not None
        call_args = http_client.post.call_args
        assert call_args[1]["json"]["memory"] is True

    def test_code_agent_basic(self, agents_resource, http_client):
        """Test code agent execution."""
        http_client.post.return_value = MockAPIResponses.code_agent_response()
        
        result = agents_resource.code(
            prompt="Create a Python function",
            default_dir="/project",
            current_dir="/project/src"
        )
        
        assert result is not None
        assert "code" in result or "files" in result

    def test_code_agent_streaming(self, agents_resource, http_client):
        """Test code agent with streaming."""
        http_client.post_stream.return_value = MockAPIResponses.code_agent_stream()
        
        stream = agents_resource.code(
            prompt="Generate code",
            default_dir="/project",
            current_dir="/project",
            stream=True
        )
        
        chunks = list(stream)
        assert len(chunks) > 0

    def test_test_agent_basic(self, agents_resource, http_client):
        """Test testing agent execution."""
        http_client.post.return_value = MockAPIResponses.test_agent_response()
        
        result = agents_resource.test(
            prompt="Create unit tests",
            default_dir="/project",
            current_dir="/project/tests"
        )
        
        assert result is not None
        assert "tests" in result or "files" in result

    def test_git_agent_basic(self, agents_resource, http_client):
        """Test git agent execution."""
        http_client.post.return_value = MockAPIResponses.git_agent_response()
        
        result = agents_resource.git(
            prompt="Create a commit",
            default_dir="/project",
            current_dir="/project"
        )
        
        assert result is not None

    def test_docs_agent_basic(self, agents_resource, http_client):
        """Test docs agent execution."""
        http_client.post.return_value = MockAPIResponses.docs_agent_response()
        
        result = agents_resource.docs(
            url="https://github.com/user/repo",
            branch="main"
        )
        
        assert result is not None
        assert "documentation" in result or "status" in result

    def test_docs_agent_with_team_access(self, agents_resource, http_client):
        """Test docs agent with team access."""
        http_client.post.return_value = MockAPIResponses.docs_agent_response()
        
        result = agents_resource.docs(
            url="https://github.com/org/private-repo",
            branch="develop",
            team_access=True
        )
        
        assert result is not None
        call_args = http_client.post.call_args
        assert call_args[1]["json"]["team_access"] is True

    def test_agent_with_task_id(self, agents_resource, http_client):
        """Test agent execution with task ID tracking."""
        http_client.post.return_value = MockAPIResponses.chat_agent_response()
        
        result = agents_resource.chat(
            prompt="Track this task",
            default_dir="/project",
            current_dir="/project",
            task_id="task_123"
        )
        
        assert result is not None
        call_args = http_client.post.call_args
        assert call_args[1]["json"]["task_id"] == "task_123"

    def test_agent_with_mcp_config(self, agents_resource, http_client):
        """Test agent with MCP configuration."""
        http_client.post.return_value = MockAPIResponses.chat_agent_response()
        
        mcp_config = {
            "server": "test-server",
            "tools": ["tool1", "tool2"]
        }
        
        result = agents_resource.chat(
            prompt="Use MCP tools",
            default_dir="/project",
            current_dir="/project",
            mcp=mcp_config
        )
        
        assert result is not None
        call_args = http_client.post.call_args
        assert "mcp" in call_args[1]["json"]

    def test_missing_required_parameters(self, agents_resource):
        """Test error handling for missing required parameters."""
        with pytest.raises(ValidationError):
            agents_resource.chat(prompt="", default_dir="", current_dir="")

    def test_invalid_agent_choice(self, agents_resource):
        """Test error handling for invalid agent choice."""
        with pytest.raises(ValidationError):
            agents_resource.plan(
                prompt="Test",
                default_dir="/project",
                current_dir="/project",
                agent_choice=["invalid_agent"]
            )

    def test_invalid_directory_paths(self, agents_resource):
        """Test error handling for invalid directory paths."""
        with pytest.raises(ValidationError):
            agents_resource.chat(
                prompt="Test",
                default_dir="relative/path",  # Should be absolute
                current_dir="/project"
            )

    def test_api_error_handling(self, agents_resource, http_client):
        """Test handling of API errors."""
        http_client.post.side_effect = DisperslError("API Error", status_code=500)
        
        with pytest.raises(DisperslError):
            agents_resource.chat(
                prompt="Test",
                default_dir="/project",
                current_dir="/project"
            )

    def test_network_error_handling(self, agents_resource, http_client):
        """Test handling of network errors."""
        http_client.post.side_effect = ConnectionError("Network failed")
        
        with pytest.raises(DisperslError):
            agents_resource.chat(
                prompt="Test",
                default_dir="/project",
                current_dir="/project"
            )

    def test_timeout_handling(self, agents_resource, http_client):
        """Test handling of timeout errors."""
        http_client.post.side_effect = TimeoutError("Request timeout")
        
        with pytest.raises(DisperslError):
            agents_resource.chat(
                prompt="Test",
                default_dir="/project",
                current_dir="/project"
            )

    def test_streaming_error_handling(self, agents_resource, http_client):
        """Test error handling in streaming mode."""
        def error_generator():
            yield '{"type": "error", "message": "Stream error"}\n'
        
        http_client.post_stream.return_value = error_generator()
        
        stream = agents_resource.chat(
            prompt="Test",
            default_dir="/project",
            current_dir="/project",
            stream=True
        )
        
        # Should handle error in stream
        chunks = list(stream)
        assert any("error" in str(chunk) for chunk in chunks)

    def test_response_validation(self, agents_resource, http_client):
        """Test validation of API responses."""
        http_client.post.return_value = {"invalid": "response"}
        
        with pytest.raises(ValidationError):
            agents_resource.chat(
                prompt="Test",
                default_dir="/project",
                current_dir="/project"
            )

    def test_concurrent_agent_calls(self, agents_resource, http_client):
        """Test making concurrent agent calls."""
        import threading
        
        http_client.post.return_value = MockAPIResponses.chat_agent_response()
        
        results = []
        errors = []
        
        def make_call():
            try:
                result = agents_resource.chat(
                    prompt="Concurrent test",
                    default_dir="/project",
                    current_dir="/project"
                )
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        threads = [threading.Thread(target=make_call) for _ in range(5)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        assert len(errors) == 0
        assert len(results) == 5

