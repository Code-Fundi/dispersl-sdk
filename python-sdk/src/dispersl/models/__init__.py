"""
Base data models for the Dispersl SDK.

This module contains the base model classes and common data structures
used throughout the SDK.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, validator


class BaseResponse(BaseModel):
    """
    Base response model for all API responses.
    
    Provides common fields that appear in most API responses.
    """
    
    status: str = Field(..., description="Response status")
    message: str = Field(..., description="Response message")
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"
        validate_assignment = True


class ErrorResponse(BaseResponse):
    """
    Error response model.
    
    Used for API error responses with additional error details.
    """
    
    error: Optional[Dict[str, Any]] = Field(None, description="Error details")
    code: Optional[int] = Field(None, description="Error code")
    
    @validator('status')
    def validate_status(cls, v: str) -> str:
        """Validate that status is 'error'."""
        if v != 'error':
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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {k: v for k, v in self.dict().items() if v is not None}


class PaginatedResponse(BaseResponse):
    """
    Paginated response model.
    
    Used for responses that contain paginated data.
    """
    
    data: List[Any] = Field(..., description="List of items")
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
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class StandardNdjsonResponse(BaseResponse):
    """
    Standard NDJSON streaming response model.
    
    Used for streaming responses from agent endpoints.
    """
    
    content: Optional[str] = Field(None, description="Text content")
    knowledge: Optional[List[str]] = Field(None, description="Knowledge source IDs")
    tools: Optional[List[Dict[str, Any]]] = Field(None, description="Tool call data")
    audio: Optional[str] = Field(None, description="Base64-encoded audio or URL")
    error: Optional[Dict[str, Any]] = Field(None, description="Error details")
    metadata: Optional[Metadata] = Field(None, description="Response metadata")
    
    @validator('status')
    def validate_status(cls, v: str) -> str:
        """Validate status values."""
        valid_statuses = {'processing', 'complete', 'error'}
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of {valid_statuses}')
        return v


class TimestampedModel(BaseModel):
    """
    Base model with timestamp fields.
    
    Provides created_at and updated_at fields for models
    that track creation and modification times.
    """
    
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class IdentifiableModel(BaseModel):
    """
    Base model with ID field.
    
    Provides an id field for models that have unique identifiers.
    """
    
    id: str = Field(..., description="Unique identifier")
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"


class NamedModel(BaseModel):
    """
    Base model with name field.
    
    Provides a name field for models that have human-readable names.
    """
    
    name: str = Field(..., description="Human-readable name")
    
    class Config:
        """Pydantic configuration."""
        extra = "allow"
