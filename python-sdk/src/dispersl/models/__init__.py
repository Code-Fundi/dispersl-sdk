"""
Base data models for the Dispersl SDK.

This module contains the base model classes and common data structures
used throughout the SDK.
"""

from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator

if TYPE_CHECKING:
    from .api import ToolCall


class BaseResponse(BaseModel):
    """
    Base response model for all API responses.

    Provides common fields that appear in most API responses.
    """

    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")

    model_config = ConfigDict(extra="allow", validate_assignment=True)


class ErrorResponse(BaseResponse):
    """
    Error response model.

    Used for API error responses with additional error details.
    """

    error: Optional[dict[str, Any]] = Field(None, description="Error details")
    code: Optional[int] = Field(None, description="Error code")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate that status is 'error'."""
        if v != "error":
            raise ValueError('Status must be "error" for error responses')
        return v


class PaginationParams(BaseModel):
    """
    Pagination parameters for list endpoints.

    Provides common pagination fields used across the API.
    """

    limit: Optional[int] = Field(None, ge=1, le=1000, description="Number of items per page")
    offset: Optional[int] = Field(None, ge=0, description="Number of items to skip")
    cursor: Optional[str] = Field(None, description="Pagination cursor")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in self.model_dump().items() if v is not None}


class PaginatedResponse(BaseResponse):
    """
    Paginated response model.

    Used for responses that contain paginated data.
    """

    data: list[Any] = Field(..., description="List of items")
    has_more: Optional[bool] = Field(None, description="Whether there are more items")
    next_cursor: Optional[str] = Field(None, description="Cursor for next page")
    total: Optional[int] = Field(None, description="Total number of items")

    @property
    def count(self) -> int:
        """Get the number of items in the current page."""
        return len(self.data)


class Metadata(BaseModel):
    """
    Metadata model for API responses.

    Contains additional information about the response.
    """

    tokens: Optional[int] = Field(None, description="Number of tokens used")
    cost: Optional[float] = Field(None, description="Cost of the operation")
    language: Optional[str] = Field(None, description="Language of the response")
    files_processed: Optional[int] = Field(None, description="Number of files processed")
    request_id: Optional[str] = Field(None, description="Unique request identifier")
    timestamp: Optional[datetime] = Field(None, description="Response timestamp")

    model_config = ConfigDict(extra="allow")


class StandardNdjsonResponse(BaseResponse):
    """
    Standard NDJSON streaming response model.

    Used for streaming responses from agent endpoints.
    """

    content: Optional[str] = Field(None, description="Text content")
    knowledge: Optional[list[str]] = Field(None, description="Knowledge source IDs")
    tools: Optional[list["ToolCall"]] = Field(None, description="Tool call data")
    audio: Optional[str] = Field(None, description="Base64-encoded audio or URL")
    error: Optional[dict[str, Any]] = Field(None, description="Error details")
    metadata: Optional[Metadata] = Field(None, description="Response metadata")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """Validate status values."""
        valid_statuses = {"processing", "complete", "error"}
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        return v


class TimestampedModel(BaseModel):
    """
    Base model with timestamp fields.

    Provides created_at and updated_at fields for models
    that track creation and modification times.
    """

    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    model_config = ConfigDict(extra="allow")


class IdentifiableModel(BaseModel):
    """
    Base model with ID field.

    Provides an id field for models that have unique identifiers.
    """

    id: str = Field(..., description="Unique identifier")

    model_config = ConfigDict(extra="allow")


class NamedModel(BaseModel):
    """
    Base model with name field.

    Provides a name field for models that have human-readable names.
    """

    name: str = Field(..., description="Human-readable name")

    model_config = ConfigDict(extra="allow")


# Import ToolCall and rebuild StandardNdjsonResponse to resolve forward references
from .api import ToolCall  # noqa: E402, F401

StandardNdjsonResponse.model_rebuild()
