from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class PaginationInfo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    limit: int
    has_next: bool = Field(alias="hasNext")
    has_prev: bool = Field(alias="hasPrev")
    next_token: str | None = Field(default=None, alias="nextToken")
    prev_token: str | None = Field(default=None, alias="prevToken")


class PaginatedResponse(BaseModel):
    status: str
    message: str
    data: list[dict[str, Any]]
    pagination: PaginationInfo


class ToolFunction(BaseModel):
    name: str
    arguments: str


class ToolCall(BaseModel):
    id: str | None = None
    type: str | None = None
    function: ToolFunction


class NDJSONChunk(BaseModel):
    status: Literal["processing", "complete", "error"]
    message: str
    content: str | None = None
    tools: list[ToolCall] | None = None
    metadata: dict[str, Any] | None = None
    error: dict[str, Any] | None = None


class AgentRequestBase(BaseModel):
    prompt: str
    model: str | None = None
    context: list[str] | None = None
    task_id: str | None = None
    knowledge: list[str] | None = None
    memory: bool | None = None
    os: str | None = None
    default_dir: str | None = None
    current_dir: str | None = None
    mcp: dict[str, Any] | None = None


class PlanRequest(AgentRequestBase):
    agent_choice: list[str] = Field(default_factory=list)
