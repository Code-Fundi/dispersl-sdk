"""
Dispersl Python SDK

Official Python SDK for the Dispersl API - an agentic workflow platform
for AI-driven software development.
"""

from .agentic import AgenticExecutor
from .client import AsyncClient, Client
from .exceptions import (
    AuthenticationError,
    DisperslError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    SerializationError,
    ServerError,
    TimeoutError,
    ValidationError,
)
from .models import StandardNdjsonResponse
from .models.api import (
    AgenticSession,
    HandoverRequest,
    MCPClient,
    MCPTool,
    ToolCall,
    ToolResponse,
)

__version__ = "0.1.0"
__all__ = [
    "AgenticExecutor",
    "AgenticSession",
    "AsyncClient",
    "AuthenticationError",
    "Client",
    "DisperslError",
    "HandoverRequest",
    "MCPClient",
    "MCPTool",
    "NetworkError",
    "NotFoundError",
    "RateLimitError",
    "SerializationError",
    "ServerError",
    "StandardNdjsonResponse",
    "TimeoutError",
    "ToolCall",
    "ToolResponse",
    "ValidationError",
]
