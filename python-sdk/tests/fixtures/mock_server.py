"""Mock HTTP server for testing API interactions."""

from typing import Any, Callable
from unittest.mock import Mock

from .mock_api_responses import (
    MOCK_AUTH_KEYS_RESPONSE,
    MOCK_AUTH_NEW_KEY_RESPONSE,
    MOCK_CHAT_STREAM,
    MOCK_CODE_STREAM_WITH_TOOLS,
    MOCK_COMPLEX_WORKFLOW_STREAM,
    MOCK_HANDOVER_STREAM,
    MOCK_HISTORY_RESPONSE,
    MOCK_MODELS_RESPONSE,
    MOCK_STEPS_RESPONSE,
    MOCK_TASK_CREATE_RESPONSE,
    MOCK_TASK_GET_RESPONSE,
    MOCK_TASK_LIST_RESPONSE,
    MOCK_TEXT_TOOL_CALLS_STREAM,
    create_json_response,
    create_streaming_response,
)


class MockHTTPClient:
    """Mock HTTP client that simulates API responses."""
    
    def __init__(self):
        """Initialize mock client."""
        self.calls = []
        self.response_overrides = {}
    
    def request(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
        headers: dict | None = None,
        stream: bool = False,
    ):
        """Mock HTTP request."""
        # Record the call
        self.calls.append({
            "method": method,
            "endpoint": endpoint,
            "data": data,
            "headers": headers,
            "stream": stream,
        })
        
        # Check for response override
        override_key = f"{method}:{endpoint}"
        if override_key in self.response_overrides:
            return self.response_overrides[override_key]
        
        # Return appropriate mock response
        if stream:
            return self._get_streaming_response(endpoint, data)
        else:
            return self._get_json_response(endpoint, method, data)
    
    def _get_streaming_response(self, endpoint: str, data: dict | None):
        """Get streaming response based on endpoint."""
        if "/agent/chat" in endpoint:
            return create_streaming_response(MOCK_CHAT_STREAM)
        elif "/agent/code" in endpoint:
            return create_streaming_response(MOCK_CODE_STREAM_WITH_TOOLS)
        elif "/agent/plan" in endpoint:
            # Check if handover is needed
            agent_choice = (data or {}).get("agent_choice", [])
            if len(agent_choice) > 1:
                return create_streaming_response(MOCK_COMPLEX_WORKFLOW_STREAM)
            return create_streaming_response(MOCK_HANDOVER_STREAM)
        elif "/agent/test" in endpoint:
            return create_streaming_response(MOCK_CODE_STREAM_WITH_TOOLS)
        elif "/agent/git" in endpoint:
            return create_streaming_response(MOCK_CODE_STREAM_WITH_TOOLS)
        elif "/agent/document" in endpoint or "/docs/repo" in endpoint:
            return create_streaming_response(MOCK_TEXT_TOOL_CALLS_STREAM)
        else:
            return create_streaming_response(MOCK_CHAT_STREAM)
    
    def _get_json_response(self, endpoint: str, method: str, data: dict | None):
        """Get JSON response based on endpoint."""
        if "/models" in endpoint:
            return create_json_response(MOCK_MODELS_RESPONSE)
        elif "/tasks/new" in endpoint and method == "POST":
            return create_json_response(MOCK_TASK_CREATE_RESPONSE)
        elif "/tasks/" in endpoint and "/edit" in endpoint:
            return create_json_response(MOCK_TASK_GET_RESPONSE)
        elif "/tasks/" in endpoint and "/delete" in endpoint:
            return create_json_response({"status": "success"})
        elif "/tasks/" in endpoint and method == "GET":
            if endpoint.endswith("/tasks"):
                return create_json_response(MOCK_TASK_LIST_RESPONSE)
            else:
                return create_json_response(MOCK_TASK_GET_RESPONSE)
        elif "/steps/" in endpoint:
            return create_json_response(MOCK_STEPS_RESPONSE)
        elif "/history/" in endpoint:
            return create_json_response(MOCK_HISTORY_RESPONSE)
        elif "/auth/keys" in endpoint:
            if method == "POST":
                return create_json_response(MOCK_AUTH_NEW_KEY_RESPONSE)
            return create_json_response(MOCK_AUTH_KEYS_RESPONSE)
        elif "/health" in endpoint:
            return create_json_response({"status": "healthy"})
        else:
            return create_json_response({"status": "success"})
    
    def set_response_override(self, method: str, endpoint: str, response):
        """Set a response override for testing specific scenarios."""
        self.response_overrides[f"{method}:{endpoint}"] = response
    
    def clear_response_overrides(self):
        """Clear all response overrides."""
        self.response_overrides.clear()
    
    def get_call_count(self, endpoint: str | None = None) -> int:
        """Get number of calls made, optionally filtered by endpoint."""
        if endpoint is None:
            return len(self.calls)
        return sum(1 for call in self.calls if endpoint in call["endpoint"])
    
    def get_last_call(self) -> dict | None:
        """Get the last call made."""
        return self.calls[-1] if self.calls else None
    
    def reset(self):
        """Reset call history and overrides."""
        self.calls.clear()
        self.response_overrides.clear()


class MockStreamingResponse:
    """Mock streaming response with iterator."""
    
    def __init__(self, chunks: list[str]):
        """Initialize with chunks."""
        self.chunks = chunks
        self.status_code = 200
        self.headers = {"content-type": "application/x-ndjson"}
    
    def iter_lines(self):
        """Iterate over chunks."""
        for chunk in self.chunks:
            yield chunk.encode()
    
    def __iter__(self):
        """Make iterable."""
        return self.iter_lines()


class MockAgentExecutor:
    """Mock agentic executor for testing workflows."""
    
    def __init__(self, http_client: MockHTTPClient):
        """Initialize with mock HTTP client."""
        self.http_client = http_client
        self.sessions = {}
        self.mcp_clients = {}
        self.mcp_tools = {}
    
    def create_session(self, session_id: str | None = None) -> str:
        """Create a mock session."""
        if session_id is None:
            session_id = f"session_{len(self.sessions) + 1}"
        
        self.sessions[session_id] = {
            "id": session_id,
            "conversation_history": [],
            "tool_responses": [],
            "context": {},
        }
        return session_id
    
    def end_session(self, session_id: str) -> bool:
        """End a session."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
    
    def get_session(self, session_id: str) -> dict | None:
        """Get session data."""
        return self.sessions.get(session_id)


def create_mock_http_client() -> MockHTTPClient:
    """Factory function to create a mock HTTP client."""
    return MockHTTPClient()


def create_error_response(status_code: int, message: str):
    """Create a mock error response."""
    class MockErrorResponse:
        def __init__(self, status_code, message):
            self.status_code = status_code
            self.message = message
        
        def json(self):
            return {"error": {"code": status_code, "message": message}}
        
        def raise_for_status(self):
            raise Exception(f"HTTP {self.status_code}: {self.message}")
    
    return MockErrorResponse(status_code, message)


def create_rate_limit_response():
    """Create a 429 rate limit response."""
    response = create_error_response(429, "Rate limit exceeded")
    response.headers = {"retry-after": "60"}
    return response


def create_auth_error_response():
    """Create a 401 authentication error."""
    return create_error_response(401, "Invalid API key")


def create_server_error_response():
    """Create a 500 server error."""
    return create_error_response(500, "Internal server error")


def create_timeout_response():
    """Create a timeout scenario."""
    def timeout_raiser(*args, **kwargs):
        raise TimeoutError("Request timed out")
    
    mock_response = Mock()
    mock_response.side_effect = timeout_raiser
    return mock_response

