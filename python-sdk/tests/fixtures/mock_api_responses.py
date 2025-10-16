"""Mock API response data for testing."""

import json

# NDJSON streaming responses
MOCK_CHAT_STREAM = [
    '{"status": "processing", "message": "Content chunk", "content": "Hello, "}',
    '{"status": "processing", "message": "Content chunk", "content": "this is "}',
    '{"status": "processing", "message": "Content chunk", "content": "a test response."}',
    '{"status": "complete", "message": "Stream completed", "metadata": {"tokens": 150, "cost": 0.01}}',
]

MOCK_CODE_STREAM_WITH_TOOLS = [
    '{"status": "processing", "message": "Content chunk", "content": "Creating user model...\\n"}',
    '{"status": "processing", "message": "Tool calls", "tools": [{"function": {"name": "write_to_file", "arguments": "{\\"path\\": \\"models/user.py\\", \\"content\\": \\"class User:\\\\n    pass\\"}"}}]}',
    '{"status": "processing", "message": "Content chunk", "content": "File created successfully."}',
    '{"status": "complete", "message": "Stream completed", "metadata": {"tokens": 200}}',
]

MOCK_HANDOVER_STREAM = [
    '{"status": "processing", "message": "Content chunk", "content": "Planning implementation..."}',
    '{"status": "processing", "message": "Tool calls", "tools": [{"function": {"name": "handover_task", "arguments": "{\\"agent_name\\": \\"code\\", \\"prompt\\": \\"Implement user authentication\\"}"}}]}',
    '{"status": "processing", "message": "Content chunk", "content": "Implementing authentication..."}',
    '{"status": "processing", "message": "Tool calls", "tools": [{"function": {"name": "write_to_file", "arguments": "{\\"path\\": \\"auth.py\\", \\"content\\": \\"def authenticate(): pass\\"}"}}]}',
    '{"status": "complete", "message": "Stream completed"}',
]

MOCK_TEXT_TOOL_CALLS_STREAM = [
    '{"status": "processing", "content": "Using text-based tool calls..."}',
    '{"status": "processing", "content": "<｜tool▁call▁begin｜>function<｜tool▁sep｜>read_file\\njson\\n{\\"path\\": \\"README.md\\"}\\n<｜tool▁call▁end｜>"}',
    '{"status": "processing", "content": "File content: Test README"}',
    '{"status": "complete"}',
]

MOCK_ERROR_STREAM = [
    '{"status": "processing", "content": "Processing..."}',
    '{"status": "error", "message": "An error occurred", "error": {"code": 500, "message": "Internal server error"}}',
]

# Regular API responses
MOCK_MODELS_RESPONSE = {
    "models": [
        {
            "id": "gpt-4-turbo",
            "name": "GPT-4 Turbo",
            "description": "Advanced reasoning with 128k context",
            "context_length": 128000,
            "tier_requirements": {"free_model": False}
        },
        {
            "id": "gpt-3.5-turbo",
            "name": "GPT-3.5 Turbo",
            "description": "Fast and economical",
            "context_length": 16000,
            "tier_requirements": {"free_model": True}
        },
        {
            "id": "claude-3-opus",
            "name": "Claude 3 Opus",
            "description": "Most capable Claude model",
            "context_length": 200000,
            "tier_requirements": {"free_model": False}
        }
    ],
    "status": "success"
}

MOCK_TASK_CREATE_RESPONSE = {
    "data": [{
        "id": "task_123456",
        "name": "New Task",
        "status": "pending",
        "created_at": "2025-01-10T12:00:00Z",
        "updated_at": "2025-01-10T12:00:00Z"
    }],
    "status": "success"
}

MOCK_TASK_LIST_RESPONSE = {
    "data": [
        {
            "id": "task_123456",
            "name": "Task 1",
            "status": "completed",
            "created_at": "2025-01-10T12:00:00Z"
        },
        {
            "id": "task_789012",
            "name": "Task 2",
            "status": "in-progress",
            "created_at": "2025-01-10T13:00:00Z"
        }
    ],
    "status": "success"
}

MOCK_PAGINATED_TASK_LIST_RESPONSE = {
    "status": "success",
    "message": "Data retrieved.",
    "data": [
        {
            "id": "task_123456",
            "name": "Task 1",
            "status": "completed",
            "created_at": "2025-01-10T12:00:00Z",
            "updated_at": "2025-01-10T14:00:00Z"
        },
        {
            "id": "task_789012",
            "name": "Task 2",
            "status": "in-progress",
            "created_at": "2025-01-10T13:00:00Z",
            "updated_at": "2025-01-10T15:00:00Z"
        }
    ],
    "pagination": {
        "page": 1,
        "pageSize": 20,
        "total": 50,
        "totalPages": 3,
        "hasNext": True,
        "hasPrev": False
    }
}

MOCK_TASK_GET_RESPONSE = {
    "data": [{
        "id": "task_123456",
        "name": "Task 1",
        "status": "completed",
        "created_at": "2025-01-10T12:00:00Z",
        "updated_at": "2025-01-10T14:00:00Z"
    }],
    "status": "success"
}

MOCK_STEPS_RESPONSE = {
    "data": [
        {
            "id": "step_111",
            "task_id": "task_123456",
            "name": "Step 1",
            "status": "completed",
            "created_at": "2025-01-10T12:00:00Z"
        },
        {
            "id": "step_222",
            "task_id": "task_123456",
            "name": "Step 2",
            "status": "pending",
            "created_at": "2025-01-10T12:05:00Z"
        }
    ],
    "status": "success"
}

MOCK_PAGINATED_STEPS_RESPONSE = {
    "status": "success",
    "message": "Data retrieved.",
    "data": [
        {
            "id": "step_111",
            "task_id": "task_123456",
            "name": "Step 1",
            "status": "completed",
            "created_at": "2025-01-10T12:00:00Z",
            "updated_at": "2025-01-10T12:30:00Z"
        },
        {
            "id": "step_222",
            "task_id": "task_123456",
            "name": "Step 2",
            "status": "pending",
            "created_at": "2025-01-10T12:05:00Z",
            "updated_at": "2025-01-10T12:05:00Z"
        }
    ],
    "pagination": {
        "page": 1,
        "pageSize": 20,
        "total": 25,
        "totalPages": 2,
        "hasNext": True,
        "hasPrev": False
    }
}

MOCK_HISTORY_RESPONSE = {
    "data": [
        {
            "id": "hist_001",
            "task_id": "task_123456",
            "event": "task_created",
            "details": "Task created",
            "timestamp": "2025-01-10T12:00:00Z"
        },
        {
            "id": "hist_002",
            "task_id": "task_123456",
            "event": "status_changed",
            "details": "Status changed to in-progress",
            "timestamp": "2025-01-10T12:05:00Z"
        }
    ],
    "status": "success"
}

MOCK_PAGINATED_HISTORY_RESPONSE = {
    "status": "success",
    "message": "Data retrieved.",
    "data": [
        {
            "id": "hist_001",
            "event": "task_created",
            "timestamp": "2025-01-10T12:00:00Z",
            "details": {"task_id": "task_123456"}
        },
        {
            "id": "hist_002",
            "event": "status_changed",
            "timestamp": "2025-01-10T12:05:00Z",
            "details": {"task_id": "task_123456", "status": "in-progress"}
        }
    ],
    "pagination": {
        "page": 1,
        "pageSize": 20,
        "total": 15,
        "totalPages": 1,
        "hasNext": False,
        "hasPrev": False
    }
}

MOCK_PAGINATED_AGENTS_RESPONSE = {
    "status": "success",
    "message": "Data retrieved.",
    "data": [
        {
            "id": "agent_1",
            "name": "Code Agent",
            "description": "Generates and builds code",
            "status": "active",
            "created_at": "2025-01-10T12:00:00Z",
            "updated_at": "2025-01-10T12:00:00Z"
        },
        {
            "id": "agent_2",
            "name": "Test Agent",
            "description": "Generates and runs tests",
            "status": "active",
            "created_at": "2025-01-10T12:00:00Z",
            "updated_at": "2025-01-10T12:00:00Z"
        }
    ],
    "pagination": {
        "page": 1,
        "pageSize": 20,
        "total": 5,
        "totalPages": 1,
        "hasNext": False,
        "hasPrev": False
    }
}

MOCK_AUTH_KEYS_RESPONSE = {
    "keys": [
        {
            "id": "key_001",
            "key": "sk_test_***",
            "name": "Test Key",
            "created_at": "2025-01-01T00:00:00Z"
        }
    ],
    "status": "success"
}

MOCK_AUTH_NEW_KEY_RESPONSE = {
    "key": {
        "id": "key_002",
        "key": "sk_test_new_key_12345",
        "name": "New Test Key",
        "created_at": "2025-01-10T12:00:00Z"
    },
    "status": "success"
}

# MCP configuration
MOCK_MCP_CONFIG = {
    "mcpServers": {
        "filesystem": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp/test"],
            "env": {}
        },
        "github": {
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-github"],
            "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": "test_token"}
        }
    }
}

# Tool call parsing test data
MOCK_CONCATENATED_JSON = '{"a": 1}{"b": 2}{"c": 3}'
MOCK_CONCATENATED_JSON_RESULT = {"a": 1}

MOCK_TEXT_TOOL_CALL = """
<｜tool▁call▁begin｜>function<｜tool▁sep｜>write_to_file
json
{"path": "test.py", "content": "print('hello')"}
<｜tool▁call▁end｜>
"""

MOCK_MULTIPLE_TEXT_TOOL_CALLS = """
Some text before
<｜tool▁call▁begin｜>function<｜tool▁sep｜>read_file
json
{"path": "input.txt"}
<｜tool▁call▁end｜>
Some text in between
<｜tool▁call▁begin｜>function<｜tool▁sep｜>write_to_file
json
{"path": "output.txt", "content": "result"}
<｜tool▁call▁end｜>
Some text after
"""

# Complex agentic workflow response
MOCK_COMPLEX_WORKFLOW_STREAM = [
    '{"status": "processing", "content": "Analyzing requirements..."}',
    '{"status": "processing", "content": "\\nStep 1: Planning"}',
    '{"status": "processing", "tools": [{"function": {"name": "handover_task", "arguments": "{\\"agent_name\\": \\"code\\", \\"prompt\\": \\"Create models\\"}"}}]}',
    '{"status": "processing", "content": "\\nStep 2: Implementation"}',
    '{"status": "processing", "tools": [{"function": {"name": "write_to_file", "arguments": "{\\"path\\": \\"models.py\\", \\"content\\": \\"class Model: pass\\"}"}}]}',
    '{"status": "processing", "tools": [{"function": {"name": "handover_task", "arguments": "{\\"agent_name\\": \\"test\\", \\"prompt\\": \\"Test models\\"}"}}]}',
    '{"status": "processing", "content": "\\nStep 3: Testing"}',
    '{"status": "processing", "tools": [{"function": {"name": "write_to_file", "arguments": "{\\"path\\": \\"test_models.py\\", \\"content\\": \\"def test_model(): pass\\"}"}}]}',
    '{"status": "processing", "tools": [{"function": {"name": "handover_task", "arguments": "{\\"agent_name\\": \\"git\\", \\"prompt\\": \\"Commit changes\\"}"}}]}',
    '{"status": "processing", "content": "\\nStep 4: Version control"}',
    '{"status": "processing", "tools": [{"function": {"name": "execute_git_command", "arguments": "{\\"command\\": \\"commit\\", \\"args\\": [\\"-m\\", \\"Add models\\"]}"}}]}',
    '{"status": "complete", "metadata": {"tokens": 500, "cost": 0.05}}',
]


def get_ndjson_lines(data: list) -> bytes:
    """Convert list of JSON strings to NDJSON bytes."""
    return b"\n".join(line.encode() for line in data) + b"\n"


def create_streaming_response(data: list):
    """Create a mock streaming response."""
    class MockResponse:
        def __init__(self, data):
            self.data = data
            self.status_code = 200
            self.headers = {"content-type": "application/x-ndjson"}
        
        def iter_lines(self):
            for line in self.data:
                yield line.encode()
        
        def __iter__(self):
            return self.iter_lines()
    
    return MockResponse(data)


def create_json_response(data: dict, status_code: int = 200):
    """Create a mock JSON response."""
    class MockResponse:
        def __init__(self, data, status_code):
            self.data = data
            self.status_code = status_code
            self.headers = {"content-type": "application/json"}
        
        def json(self):
            return self.data
        
        def raise_for_status(self):
            if self.status_code >= 400:
                raise Exception(f"HTTP {self.status_code}")
    
    return MockResponse(data, status_code)


class MockAPIResponses:
    """Centralized mock API responses for testing."""
    
    # NDJSON Streaming Responses
    CHAT_STREAM = MOCK_CHAT_STREAM
    CODE_STREAM_WITH_TOOLS = MOCK_CODE_STREAM_WITH_TOOLS
    HANDOVER_STREAM = MOCK_HANDOVER_STREAM
    TEXT_TOOL_CALLS_STREAM = MOCK_TEXT_TOOL_CALLS_STREAM
    ERROR_STREAM = MOCK_ERROR_STREAM
    COMPLEX_WORKFLOW_STREAM = MOCK_COMPLEX_WORKFLOW_STREAM
    
    # Regular API Responses
    MODELS_RESPONSE = MOCK_MODELS_RESPONSE
    TASK_CREATE_RESPONSE = MOCK_TASK_CREATE_RESPONSE
    TASK_LIST_RESPONSE = MOCK_TASK_LIST_RESPONSE
    TASK_GET_RESPONSE = MOCK_TASK_GET_RESPONSE
    STEPS_RESPONSE = MOCK_STEPS_RESPONSE
    HISTORY_RESPONSE = MOCK_HISTORY_RESPONSE
    AUTH_KEYS_RESPONSE = MOCK_AUTH_KEYS_RESPONSE
    AUTH_NEW_KEY_RESPONSE = MOCK_AUTH_NEW_KEY_RESPONSE
    
    # MCP Configuration
    MCP_CONFIG = MOCK_MCP_CONFIG
    
    # Tool Call Test Data
    CONCATENATED_JSON = MOCK_CONCATENATED_JSON
    TEXT_TOOL_CALL = MOCK_TEXT_TOOL_CALL
    MULTIPLE_TEXT_TOOL_CALLS = MOCK_MULTIPLE_TEXT_TOOL_CALLS
    
    @staticmethod
    def get_ndjson_lines(data: list) -> bytes:
        """Convert list of JSON strings to NDJSON bytes."""
        return get_ndjson_lines(data)
    
    @staticmethod
    def create_streaming_response(data: list):
        """Create a mock streaming response."""
        return create_streaming_response(data)
    
    @staticmethod
    def create_json_response(data: dict, status_code: int = 200):
        """Create a mock JSON response."""
        return create_json_response(data, status_code)
