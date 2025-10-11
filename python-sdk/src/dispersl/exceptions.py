"""
Custom exceptions for the Dispersl SDK.

This module defines the exception hierarchy used throughout the SDK
for consistent error handling and user experience.
"""

from datetime import UTC, datetime
from typing import Any, Optional


class DisperslError(Exception):
    """
    Base exception class for all Dispersl SDK errors.

    All custom exceptions inherit from this class to provide
    consistent error handling across the SDK.
    """

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        request_id: Optional[str] = None,
        response_body: Optional[dict[str, Any]] = None,
        timestamp: Optional[datetime] = None,
    ) -> None:
        """
        Initialize the base exception.

        Args:
            message: Human-readable error message
            status_code: HTTP status code (if applicable)
            request_id: Unique request identifier
            response_body: Raw response body from API
            timestamp: When the error occurred
        """
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.request_id = request_id
        self.response_body = response_body
        self.timestamp = timestamp or datetime.now(UTC)

    def __str__(self) -> str:
        """Return string representation of the error."""
        parts = [self.message]
        if self.status_code:
            parts.append(f"Status: {self.status_code}")
        if self.request_id:
            parts.append(f"Request ID: {self.request_id}")
        return " | ".join(parts)


class AuthenticationError(DisperslError):
    """
    Raised when authentication fails (401, 403).

    This includes invalid API keys, expired tokens,
    and insufficient permissions.
    """

    def __init__(
        self,
        message: str = "Authentication failed",
        status_code: Optional[int] = None,
        request_id: Optional[str] = None,
        response_body: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, status_code, request_id, response_body)


class NotFoundError(DisperslError):
    """
    Raised when a requested resource is not found (404).

    This includes invalid task IDs, step IDs, or other
    resource identifiers.
    """

    def __init__(
        self,
        message: str = "Resource not found",
        status_code: Optional[int] = None,
        request_id: Optional[str] = None,
        response_body: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, status_code, request_id, response_body)


class ValidationError(DisperslError):
    """
    Raised when request validation fails (400, 422).

    This includes malformed requests, missing required fields,
    and invalid parameter values.
    """

    def __init__(
        self,
        message: str = "Request validation failed",
        status_code: Optional[int] = None,
        request_id: Optional[str] = None,
        response_body: Optional[dict[str, Any]] = None,
        validation_errors: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, status_code, request_id, response_body)
        self.validation_errors = validation_errors or {}


class RateLimitError(DisperslError):
    """
    Raised when rate limits are exceeded (429).

    Includes retry-after information for proper backoff.
    """

    def __init__(
        self,
        message: str = "Rate limit exceeded",
        status_code: Optional[int] = None,
        request_id: Optional[str] = None,
        response_body: Optional[dict[str, Any]] = None,
        retry_after: Optional[int] = None,
    ) -> None:
        super().__init__(message, status_code, request_id, response_body)
        self.retry_after = retry_after


class ServerError(DisperslError):
    """
    Raised when server errors occur (500-599).

    This includes internal server errors, service unavailable,
    and gateway timeouts.
    """

    def __init__(
        self,
        message: str = "Server error occurred",
        status_code: Optional[int] = None,
        request_id: Optional[str] = None,
        response_body: Optional[dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, status_code, request_id, response_body)


class TimeoutError(DisperslError):
    """
    Raised when requests timeout.

    This includes connection timeouts, read timeouts,
    and total request timeouts.
    """

    def __init__(
        self,
        message: str = "Request timeout",
        timeout_type: Optional[str] = None,
    ) -> None:
        super().__init__(message)
        self.timeout_type = timeout_type


class NetworkError(DisperslError):
    """
    Raised when network-related errors occur.

    This includes connection failures, DNS resolution errors,
    and other network issues.
    """

    def __init__(
        self,
        message: str = "Network error occurred",
        original_error: Optional[Exception] = None,
    ) -> None:
        super().__init__(message)
        self.original_error = original_error


class SerializationError(DisperslError):
    """
    Raised when serialization/deserialization fails.

    This includes JSON parsing errors, invalid data formats,
    and encoding/decoding issues.
    """

    def __init__(
        self,
        message: str = "Serialization error",
        original_error: Optional[Exception] = None,
    ) -> None:
        super().__init__(message)
        self.original_error = original_error
