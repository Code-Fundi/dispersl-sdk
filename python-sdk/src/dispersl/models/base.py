"""
Base data models for the Dispersl SDK.

This module contains the base model classes and common data structures
used throughout the SDK.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class BaseResponse(BaseModel):
    """Base response model for all API responses."""

    status: str
    message: str


class ErrorDetail(BaseModel):
    """Error detail model."""

    code: Optional[int] = None
    message: str


class ErrorResponse(BaseResponse):
    """Error response model with additional error details."""

    status: str = "error"
    error: Optional[ErrorDetail] = None


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""

    limit: Optional[int] = Field(None, ge=1, le=1000)
    offset: Optional[int] = Field(None, ge=0)
    cursor: Optional[str] = None


class PaginatedResponse(BaseResponse):
    """Paginated response model."""

    data: List[Any]
    has_more: Optional[bool] = None
    next_cursor: Optional[str] = None
    total: Optional[int] = None


class Metadata(BaseModel):
    """Metadata model for API responses."""

    tokens: Optional[int] = None
    cost: Optional[float] = None
    language: Optional[str] = None
    files_processed: Optional[int] = None
    request_id: Optional[str] = None
    timestamp: Optional[datetime] = None


class StandardNdjsonResponse(BaseResponse):
    """Standard NDJSON streaming response model."""

    content: Optional[str] = None
    knowledge: Optional[List[str]] = None
    tools: Optional[List[Any]] = None
    audio: Optional[str] = None
    error: Optional[ErrorDetail] = None
    metadata: Optional[Metadata] = None


class TimestampedModel(BaseModel):
    """Base model with timestamp fields."""

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class IdentifiableModel(BaseModel):
    """Base model with ID field."""

    id: str


class NamedModel(BaseModel):
    """Base model with name field."""

    name: str

