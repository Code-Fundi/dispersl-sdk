"""
HTTP transport layer with enterprise-grade reliability.

This module handles all HTTP communication with retry logic,
connection pooling, and timeout management.
"""

import asyncio
import json
import logging
from typing import Any, Dict, Optional, Union
from urllib.parse import urljoin

import httpx

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
from .retry import retry_with_backoff


logger = logging.getLogger(__name__)


class HTTPClient:
    """
    Robust HTTP client with automatic retries and circuit breaking.
    
    This client provides enterprise-grade HTTP communication with:
    - Connection pooling
    - Automatic retries with exponential backoff
    - Circuit breaker pattern
    - Comprehensive error handling
    - Request/response logging
    
    Attributes:
        base_url: API base URL
        timeout: Request timeout in seconds
        max_retries: Maximum retry attempts
        backoff_factor: Exponential backoff multiplier
    """
    
    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        connect_timeout: float = 10.0,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Initialize the HTTP client.
        
        Args:
            base_url: Base URL for API requests
            timeout: Total request timeout in seconds
            connect_timeout: Connection timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff multiplier
            headers: Default headers for all requests
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.connect_timeout = connect_timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        
        # Create HTTP client with connection pooling
        self._client = httpx.Client(
            timeout=httpx.Timeout(
                connect=connect_timeout,
                read=timeout,
                write=timeout,
                pool=timeout,
            ),
            headers=headers or {},
            limits=httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100,
            ),
        )
        
        logger.info(f"HTTP client initialized for {self.base_url}")
    
    def __enter__(self) -> "HTTPClient":
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
    
    def close(self) -> None:
        """Close the HTTP client and cleanup resources."""
        self._client.close()
        logger.info("HTTP client closed")
    
    @retry_with_backoff(max_retries=3, backoff_factor=2.0)
    def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Make an HTTP request with automatic retries.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path (relative to base_url)
            params: Query parameters
            json_data: JSON request body
            headers: Additional headers
            **kwargs: Additional httpx request parameters
        
        Returns:
            HTTP response object
        
        Raises:
            DisperslError: For various API errors
        """
        url = urljoin(self.base_url + "/", path.lstrip("/"))
        
        # Prepare request data
        request_data: Dict[str, Any] = {
            "method": method,
            "url": url,
            "params": params,
            "headers": headers or {},
        }
        
        if json_data is not None:
            request_data["json"] = json_data
        
        request_data.update(kwargs)
        
        # Log request (excluding sensitive data)
        self._log_request(method, url, params, headers)
        
        try:
            response = self._client.request(**request_data)
            
            # Log response
            self._log_response(response)
            
            # Handle response
            self._handle_response(response)
            
            return response
            
        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {e}")
            raise TimeoutError(f"Request timeout: {e}")
        
        except httpx.ConnectError as e:
            logger.error(f"Connection error: {e}")
            raise NetworkError(f"Connection error: {e}", original_error=e)
        
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise NetworkError(f"Request error: {e}", original_error=e)
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise SerializationError(f"JSON decode error: {e}", original_error=e)
    
    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make a GET request."""
        return self.request("GET", path, params=params, headers=headers, **kwargs)
    
    def post(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make a POST request."""
        return self.request(
            "POST", path, params=params, json_data=json_data, headers=headers, **kwargs
        )
    
    def put(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make a PUT request."""
        return self.request(
            "PUT", path, params=params, json_data=json_data, headers=headers, **kwargs
        )
    
    def delete(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make a DELETE request."""
        return self.request("DELETE", path, params=params, headers=headers, **kwargs)
    
    def _log_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]],
        headers: Optional[Dict[str, str]],
    ) -> None:
        """Log outgoing request (excluding sensitive data)."""
        if logger.isEnabledFor(logging.DEBUG):
            safe_headers = self._sanitize_headers(headers or {})
            logger.debug(
                f"Request: {method} {url} | "
                f"Params: {params} | "
                f"Headers: {safe_headers}"
            )
    
    def _log_response(self, response: httpx.Response) -> None:
        """Log incoming response."""
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                f"Response: {response.status_code} | "
                f"Headers: {dict(response.headers)} | "
                f"Size: {len(response.content)} bytes"
            )
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Remove sensitive headers from logging."""
        sensitive_keys = {"authorization", "x-api-key", "cookie"}
        return {
            k: "***" if k.lower() in sensitive_keys else v
            for k, v in headers.items()
        }
    
    def _handle_response(self, response: httpx.Response) -> None:
        """
        Handle HTTP response and raise appropriate exceptions.
        
        Args:
            response: HTTP response object
        
        Raises:
            DisperslError: For various API errors
        """
        if response.is_success:
            return
        
        # Extract error information
        request_id = response.headers.get("x-request-id")
        retry_after = response.headers.get("retry-after")
        
        try:
            error_data = response.json()
        except (json.JSONDecodeError, ValueError):
            error_data = {"message": response.text or "Unknown error"}
        
        # Create appropriate exception based on status code
        if response.status_code == 401:
            raise AuthenticationError(
                message=error_data.get("message", "Authentication failed"),
                status_code=response.status_code,
                request_id=request_id,
                response_body=error_data,
            )
        
        elif response.status_code == 403:
            raise AuthenticationError(
                message=error_data.get("message", "Access forbidden"),
                status_code=response.status_code,
                request_id=request_id,
                response_body=error_data,
            )
        
        elif response.status_code == 404:
            raise NotFoundError(
                message=error_data.get("message", "Resource not found"),
                status_code=response.status_code,
                request_id=request_id,
                response_body=error_data,
            )
        
        elif response.status_code == 429:
            retry_after_seconds = None
            if retry_after:
                try:
                    retry_after_seconds = int(retry_after)
                except ValueError:
                    pass
            
            raise RateLimitError(
                message=error_data.get("message", "Rate limit exceeded"),
                status_code=response.status_code,
                request_id=request_id,
                response_body=error_data,
                retry_after=retry_after_seconds,
            )
        
        elif response.status_code in (400, 422):
            raise ValidationError(
                message=error_data.get("message", "Request validation failed"),
                status_code=response.status_code,
                request_id=request_id,
                response_body=error_data,
                validation_errors=error_data.get("errors", {}),
            )
        
        elif 500 <= response.status_code < 600:
            raise ServerError(
                message=error_data.get("message", "Server error occurred"),
                status_code=response.status_code,
                request_id=request_id,
                response_body=error_data,
            )
        
        else:
            raise DisperslError(
                message=error_data.get("message", f"HTTP {response.status_code}"),
                status_code=response.status_code,
                request_id=request_id,
                response_body=error_data,
            )


class AsyncHTTPClient:
    """
    Async version of the HTTP client.
    
    Provides the same functionality as HTTPClient but with async/await support.
    """
    
    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        connect_timeout: float = 10.0,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Initialize the async HTTP client.
        
        Args:
            base_url: Base URL for API requests
            timeout: Total request timeout in seconds
            connect_timeout: Connection timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff multiplier
            headers: Default headers for all requests
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.connect_timeout = connect_timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        
        # Create async HTTP client with connection pooling
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(
                connect=connect_timeout,
                read=timeout,
                write=timeout,
                pool=timeout,
            ),
            headers=headers or {},
            limits=httpx.Limits(
                max_keepalive_connections=20,
                max_connections=100,
            ),
        )
        
        logger.info(f"Async HTTP client initialized for {self.base_url}")
    
    async def __aenter__(self) -> "AsyncHTTPClient":
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()
    
    async def close(self) -> None:
        """Close the async HTTP client and cleanup resources."""
        await self._client.aclose()
        logger.info("Async HTTP client closed")
    
    @retry_with_backoff(max_retries=3, backoff_factor=2.0)
    async def request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """
        Make an async HTTP request with automatic retries.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path (relative to base_url)
            params: Query parameters
            json_data: JSON request body
            headers: Additional headers
            **kwargs: Additional httpx request parameters
        
        Returns:
            HTTP response object
        
        Raises:
            DisperslError: For various API errors
        """
        url = urljoin(self.base_url + "/", path.lstrip("/"))
        
        # Prepare request data
        request_data: Dict[str, Any] = {
            "method": method,
            "url": url,
            "params": params,
            "headers": headers or {},
        }
        
        if json_data is not None:
            request_data["json"] = json_data
        
        request_data.update(kwargs)
        
        # Log request (excluding sensitive data)
        self._log_request(method, url, params, headers)
        
        try:
            response = await self._client.request(**request_data)
            
            # Log response
            self._log_response(response)
            
            # Handle response
            self._handle_response(response)
            
            return response
            
        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {e}")
            raise TimeoutError(f"Request timeout: {e}")
        
        except httpx.ConnectError as e:
            logger.error(f"Connection error: {e}")
            raise NetworkError(f"Connection error: {e}", original_error=e)
        
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise NetworkError(f"Request error: {e}", original_error=e)
        
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise SerializationError(f"JSON decode error: {e}", original_error=e)
    
    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make an async GET request."""
        return await self.request("GET", path, params=params, headers=headers, **kwargs)
    
    async def post(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make an async POST request."""
        return await self.request(
            "POST", path, params=params, json_data=json_data, headers=headers, **kwargs
        )
    
    async def put(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make an async PUT request."""
        return await self.request(
            "PUT", path, params=params, json_data=json_data, headers=headers, **kwargs
        )
    
    async def delete(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> httpx.Response:
        """Make an async DELETE request."""
        return await self.request("DELETE", path, params=params, headers=headers, **kwargs)
    
    def _log_request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]],
        headers: Optional[Dict[str, str]],
    ) -> None:
        """Log outgoing request (excluding sensitive data)."""
        if logger.isEnabledFor(logging.DEBUG):
            safe_headers = self._sanitize_headers(headers or {})
            logger.debug(
                f"Request: {method} {url} | "
                f"Params: {params} | "
                f"Headers: {safe_headers}"
            )
    
    def _log_response(self, response: httpx.Response) -> None:
        """Log incoming response."""
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                f"Response: {response.status_code} | "
                f"Headers: {dict(response.headers)} | "
                f"Size: {len(response.content)} bytes"
            )
    
    def _sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Remove sensitive headers from logging."""
        sensitive_keys = {"authorization", "x-api-key", "cookie"}
        return {
            k: "***" if k.lower() in sensitive_keys else v
            for k, v in headers.items()
        }
    
    def _handle_response(self, response: httpx.Response) -> None:
        """
        Handle HTTP response and raise appropriate exceptions.
        
        Args:
            response: HTTP response object
        
        Raises:
            DisperslError: For various API errors
        """
        if response.is_success:
            return
        
        # Extract error information
        request_id = response.headers.get("x-request-id")
        retry_after = response.headers.get("retry-after")
        
        try:
            error_data = response.json()
        except (json.JSONDecodeError, ValueError):
            error_data = {"message": response.text or "Unknown error"}
        
        # Create appropriate exception based on status code
        if response.status_code == 401:
            raise AuthenticationError(
                message=error_data.get("message", "Authentication failed"),
                status_code=response.status_code,
                request_id=request_id,
                response_body=error_data,
            )
        
        elif response.status_code == 403:
            raise AuthenticationError(
                message=error_data.get("message", "Access forbidden"),
                status_code=response.status_code,
                request_id=request_id,
                response_body=error_data,
            )
        
        elif response.status_code == 404:
            raise NotFoundError(
                message=error_data.get("message", "Resource not found"),
                status_code=response.status_code,
                request_id=request_id,
                response_body=error_data,
            )
        
        elif response.status_code == 429:
            retry_after_seconds = None
            if retry_after:
                try:
                    retry_after_seconds = int(retry_after)
                except ValueError:
                    pass
            
            raise RateLimitError(
                message=error_data.get("message", "Rate limit exceeded"),
                status_code=response.status_code,
                request_id=request_id,
                response_body=error_data,
                retry_after=retry_after_seconds,
            )
        
        elif response.status_code in (400, 422):
            raise ValidationError(
                message=error_data.get("message", "Request validation failed"),
                status_code=response.status_code,
                request_id=request_id,
                response_body=error_data,
                validation_errors=error_data.get("errors", {}),
            )
        
        elif 500 <= response.status_code < 600:
            raise ServerError(
                message=error_data.get("message", "Server error occurred"),
                status_code=response.status_code,
                request_id=request_id,
                response_body=error_data,
            )
        
        else:
            raise DisperslError(
                message=error_data.get("message", f"HTTP {response.status_code}"),
                status_code=response.status_code,
                request_id=request_id,
                response_body=error_data,
            )
