"""
Request and response models for the Dispersl API.

This module contains all the data models used for API requests and responses,
generated from the OpenAPI specification.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator

from .base import BaseResponse, ErrorResponse, Metadata, StandardNdjsonResponse


# Request Models

class ChatRequest(BaseModel):
    """Request model for chat interactions."""
    
    prompt: str = Field(..., description="Chat prompt")
    model: Optional[str] = Field(None, description="AI model to use")
    context: Optional[str] = Field(None, description="Additional context")
    memory: Optional[bool] = Field(None, description="Enable memory")
    voice: Optional[bool] = Field(None, description="Enable voice response")
    task_id: Optional[str] = Field(None, description="Task ID for context")
    knowledge: Optional[str] = Field(None, description="Knowledge sources")
    os: Optional[str] = Field(None, description="Operating system")
    default_dir: Optional[str] = Field(None, description="Default directory")
    current_dir: Optional[str] = Field(None, description="Current directory")
    mcp: Optional[Dict[str, Any]] = Field(None, description="MCP configuration")


class DisperseRequest(BaseModel):
    """Request model for multi-agent task dispersion."""
    
    prompt: str = Field(..., description="Task prompt")
    model: Optional[str] = Field(None, description="AI model to use")
    agent_name: Optional[str] = Field(None, description="Agent name")
    context: Optional[str] = Field(None, description="Additional context")
    task_id: Optional[str] = Field(None, description="Task ID")
    knowledge: Optional[str] = Field(None, description="Knowledge sources")
    os: Optional[str] = Field(None, description="Operating system")
    default_dir: Optional[str] = Field(None, description="Default directory")
    current_dir: Optional[str] = Field(None, description="Current directory")
    memory: Optional[bool] = Field(None, description="Enable memory")


class BuildRequest(BaseModel):
    """Request model for code/test generation."""
    
    prompt: str = Field(..., description="Build prompt")
    model: Optional[str] = Field(None, description="AI model to use")
    context: Optional[str] = Field(None, description="Additional context")
    task_id: Optional[str] = Field(None, description="Task ID")
    knowledge: Optional[str] = Field(None, description="Knowledge sources")
    os: Optional[str] = Field(None, description="Operating system")
    default_dir: Optional[str] = Field(None, description="Default directory")
    current_dir: Optional[str] = Field(None, description="Current directory")
    mcp: Optional[Dict[str, Any]] = Field(None, description="MCP configuration")


class RepoDocsRequest(BaseModel):
    """Request model for repository documentation generation."""
    
    url: str = Field(..., description="Repository URL")
    branch: str = Field(..., description="Git branch")
    model: Optional[str] = Field(None, description="AI model to use")
    team_access: Optional[bool] = Field(None, description="Team access")
    task_id: Optional[str] = Field(None, description="Task ID")


class NewAPIKeyRequest(BaseModel):
    """Request model for generating new API keys."""
    
    user_id: str = Field(..., description="User ID")
    name: Optional[str] = Field(None, description="API key name")


class TaskEditRequest(BaseModel):
    """Request model for editing tasks."""
    
    name: Optional[str] = Field(None, description="Task name")
    status: Optional[str] = Field(None, description="Task status")


class HistoryRequest(BaseModel):
    """Request model for history queries."""
    
    limit: Optional[int] = Field(None, ge=1, le=1000, description="Number of items to return")


# Response Models

class ModelInfo(BaseModel):
    """Information about an AI model."""
    
    id: str = Field(..., description="Model ID")
    name: str = Field(..., description="Model name")
    description: str = Field(..., description="Model description")
    context_length: int = Field(..., description="Context length")
    tier_requirements: Dict[str, Any] = Field(..., description="Tier requirements")


class ModelsResponse(BaseResponse):
    """Response model for listing available models."""
    
    models: List[ModelInfo] = Field(..., description="List of available models")


class APIKeyInfo(BaseModel):
    """Information about an API key."""
    
    name: str = Field(..., description="API key name")
    public_key: str = Field(..., description="Public key")
    created_at: str = Field(..., description="Creation timestamp")


class APIKeysResponse(BaseResponse):
    """Response model for listing API keys."""
    
    api_keys: List[APIKeyInfo] = Field(..., description="List of API keys")


class NewAPIKeyResponse(BaseResponse):
    """Response model for new API key generation."""
    
    public_key: str = Field(..., description="Generated public key")


class TaskInfo(BaseModel):
    """Information about a task."""
    
    id: str = Field(..., description="Task ID")
    name: str = Field(..., description="Task name")
    status: str = Field(..., description="Task status")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


class TaskResponse(BaseResponse):
    """Response model for task operations."""
    
    data: List[TaskInfo] = Field(..., description="Task data")


class StepInfo(BaseModel):
    """Information about a step."""
    
    id: str = Field(..., description="Step ID")
    task_id: str = Field(..., description="Parent task ID")
    name: str = Field(..., description="Step name")
    status: str = Field(..., description="Step status")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Last update timestamp")


class StepResponse(BaseResponse):
    """Response model for step operations."""
    
    data: List[StepInfo] = Field(..., description="Step data")


class HistoryEntry(BaseModel):
    """History entry model."""
    
    id: str = Field(..., description="Entry ID")
    event: str = Field(..., description="Event type")
    timestamp: str = Field(..., description="Event timestamp")
    details: Dict[str, Any] = Field(..., description="Event details")


class HistoryResponse(BaseResponse):
    """Response model for history queries."""
    
    data: List[HistoryEntry] = Field(..., description="History data")


class StatsResponse(BaseResponse):
    """Response model for statistics."""
    
    data: Dict[str, Any] = Field(..., description="Statistics data")


# Tool Models

class ToolParameter(BaseModel):
    """Tool parameter definition."""
    
    type: str = Field(..., description="Parameter type")
    description: Optional[str] = Field(None, description="Parameter description")
    required: Optional[List[str]] = Field(None, description="Required parameters")


class ToolDefinition(BaseModel):
    """Tool definition model."""
    
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: ToolParameter = Field(..., description="Tool parameters")
    endpoints: List[str] = Field(..., description="Available endpoints")


class ToolCall(BaseModel):
    """Tool call model."""
    
    function: Dict[str, Any] = Field(..., description="Function call data")
    arguments: str = Field(..., description="Function arguments")


class HandoverRequest(BaseModel):
    """Request model for agent handover."""
    
    agent_name: str = Field(..., description="Target agent name")
    prompt: str = Field(..., description="Handover prompt")
    additional_args: Optional[Dict[str, Any]] = Field(None, description="Additional arguments")


class ToolResponse(BaseModel):
    """Tool execution response model."""
    
    status: str = Field(..., description="Tool execution status")
    message: str = Field(..., description="Response message")
    tool: str = Field(..., description="Tool name")
    output: str = Field(..., description="Tool output")


class AgenticSession(BaseModel):
    """Agentic session model."""
    
    id: str = Field(..., description="Session ID")
    context: Dict[str, Any] = Field(default_factory=dict, description="Session context")
    conversation_history: List[Dict[str, Any]] = Field(default_factory=list, description="Conversation history")
    active_tools: List[str] = Field(default_factory=list, description="Active tools")
    tool_responses: List[ToolResponse] = Field(default_factory=list, description="Tool responses")


class MCPTool(BaseModel):
    """MCP tool definition."""
    
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict[str, Any] = Field(..., description="Tool parameters")
    execute: Optional[callable] = Field(None, description="Tool execution function")


class MCPClient(BaseModel):
    """MCP client configuration."""
    
    name: str = Field(..., description="Client name")
    command: Optional[str] = Field(None, description="Command to execute")
    args: Optional[List[str]] = Field(None, description="Command arguments")
    env: Optional[Dict[str, str]] = Field(None, description="Environment variables")
    url: Optional[str] = Field(None, description="HTTP URL for remote clients")
    headers: Optional[Dict[str, str]] = Field(None, description="HTTP headers")


# NDJSON Response Examples

class NdjsonTextExample(BaseModel):
    """Example of text content in NDJSON response."""
    
    status: str = Field("processing", description="Status")
    message: str = Field("Content chunk", description="Message")
    content: str = Field("Generated text...", description="Content")


class NdjsonReasoningExample(BaseModel):
    """Example of reasoning in NDJSON response."""
    
    status: str = Field("processing", description="Status")
    message: str = Field("Reasoning chunk", description="Message")
    content: str = Field("AI reasoning...", description="Content")


class NdjsonToolExample(BaseModel):
    """Example of tool calls in NDJSON response."""
    
    status: str = Field("processing", description="Status")
    message: str = Field("Tool calls", description="Message")
    tools: List[ToolCall] = Field(..., description="Tool calls")


class NdjsonKnowledgeExample(BaseModel):
    """Example of knowledge sources in NDJSON response."""
    
    status: str = Field("processing", description="Status")
    message: str = Field("Knowledge sources", description="Message")
    knowledge: List[str] = Field(..., description="Knowledge source IDs")


class NdjsonAudioExample(BaseModel):
    """Example of audio in NDJSON response."""
    
    status: str = Field("processing", description="Status")
    message: str = Field("Audio chunk", description="Message")
    audio: str = Field("base64_encoded_audio", description="Audio data")


class NdjsonCompleteExample(BaseModel):
    """Example of completion in NDJSON response."""
    
    status: str = Field("complete", description="Status")
    message: str = Field("Stream completed", description="Message")
    metadata: Metadata = Field(..., description="Response metadata")


class NdjsonErrorExample(BaseModel):
    """Example of error in NDJSON response."""
    
    status: str = Field("error", description="Status")
    message: str = Field("Error occurred", description="Message")
    error: Dict[str, Any] = Field(..., description="Error details")
