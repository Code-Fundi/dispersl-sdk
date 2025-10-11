"""
Dispersl Python SDK

Official Python SDK for the Dispersl API - an agentic workflow platform 
for AI-driven software development.
"""

from .agentic import AgenticExecutor
from .client import Client, AsyncClient
from .exceptions import (
    DisperslError,
    AuthenticationError,
    NotFoundError,
    ValidationError,
    RateLimitError,
    ServerError,
    TimeoutError,
    NetworkError,
    SerializationError,
)
from .models import (
    AgenticSession,
    HandoverRequest,
    MCPClient,
    MCPTool,
    StandardNdjsonResponse,
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
