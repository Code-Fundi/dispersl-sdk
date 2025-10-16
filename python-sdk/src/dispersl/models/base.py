"""
Base data models for the Dispersl SDK.

This module contains the base model classes and common data structures
used throughout the SDK.
"""

from datetime import datetime
from typing import Any, Optional

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

    page: Optional[int] = Field(None, ge=1, description="Page number (1-based)")
    pageSize: Optional[int] = Field(None, ge=1, le=100, description="Items per page")


class Pagination(BaseModel):
    """Pagination metadata model."""

    page: int = Field(..., description="Current page number")
    pageSize: int = Field(..., description="Number of items per page")
    total: int = Field(..., description="Total number of items")
    totalPages: int = Field(..., description="Total number of pages")
    hasNext: bool = Field(..., description="Whether there is a next page")
    hasPrev: bool = Field(..., description="Whether there is a previous page")


class PaginatedResponse(BaseResponse):
    """Paginated response model."""

    data: list[Any]
    pagination: Pagination


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
    knowledge: Optional[list[str]] = None
    tools: Optional[list[Any]] = None
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
