"""
Base resource class for API endpoints.

This module provides the base Resource class that all API resource
classes inherit from, providing common functionality for making
HTTP requests and handling responses.
"""

import logging
from typing import Any, Dict, Optional, Union

from ..exceptions import DisperslError
from ..http import AsyncHTTPClient, HTTPClient
from ..serializers import deserialize_response_data, serialize_request_data

logger = logging.getLogger(__name__)


class Resource:
    """
    Base resource class for API endpoints.
    
    Provides common functionality for making HTTP requests and
    handling responses across all API resources.
    """
    
    def __init__(self, http_client: HTTPClient) -> None:
        """
        Initialize the resource.
        
        Args:
            http_client: HTTP client instance for making requests
        """
        self.http = http_client
        logger.debug(f"Initialized {self.__class__.__name__}")
    
    def _make_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[type] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Make an HTTP request and handle the response.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            params: Query parameters
            json_data: JSON request body
            headers: Additional headers
            response_model: Optional Pydantic model for response validation
            **kwargs: Additional request parameters
        
        Returns:
            Response data, optionally validated with response_model
        
        Raises:
            DisperslError: For various API errors
        """
        try:
            # Serialize request data
            if json_data is not None:
                json_data = serialize_request_data(json_data)
            
            # Make the request
            response = self.http.request(
                method=method,
                path=path,
                params=params,
                json_data=json_data,
                headers=headers,
                **kwargs,
            )
            
            # Deserialize response
            response_data = deserialize_response_data(
                response.content,
                model_class=response_model,
            )
            
            return response_data
        
        except Exception as e:
            if isinstance(e, DisperslError):
                raise
            logger.error(f"Request failed: {e}")
            raise DisperslError(f"Request failed: {e}", original_error=e)
    
    def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[type] = None,
        **kwargs: Any,
    ) -> Any:
        """Make a GET request."""
        return self._make_request(
            "GET", path, params=params, headers=headers, response_model=response_model, **kwargs
        )
    
    def post(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[type] = None,
        **kwargs: Any,
    ) -> Any:
        """Make a POST request."""
        return self._make_request(
            "POST",
            path,
            params=params,
            json_data=json_data,
            headers=headers,
            response_model=response_model,
            **kwargs,
        )
    
    def put(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[type] = None,
        **kwargs: Any,
    ) -> Any:
        """Make a PUT request."""
        return self._make_request(
            "PUT",
            path,
            params=params,
            json_data=json_data,
            headers=headers,
            response_model=response_model,
            **kwargs,
        )
    
    def delete(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[type] = None,
        **kwargs: Any,
    ) -> Any:
        """Make a DELETE request."""
        return self._make_request(
            "DELETE", path, params=params, headers=headers, response_model=response_model, **kwargs
        )


class AsyncResource:
    """
    Base async resource class for API endpoints.
    
    Provides common functionality for making async HTTP requests and
    handling responses across all API resources.
    """
    
    def __init__(self, http_client: AsyncHTTPClient) -> None:
        """
        Initialize the async resource.
        
        Args:
            http_client: Async HTTP client instance for making requests
        """
        self.http = http_client
        logger.debug(f"Initialized {self.__class__.__name__}")
    
    async def _make_request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[type] = None,
        **kwargs: Any,
    ) -> Any:
        """
        Make an async HTTP request and handle the response.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            path: Request path
            params: Query parameters
            json_data: JSON request body
            headers: Additional headers
            response_model: Optional Pydantic model for response validation
            **kwargs: Additional request parameters
        
        Returns:
            Response data, optionally validated with response_model
        
        Raises:
            DisperslError: For various API errors
        """
        try:
            # Serialize request data
            if json_data is not None:
                json_data = serialize_request_data(json_data)
            
            # Make the request
            response = await self.http.request(
                method=method,
                path=path,
                params=params,
                json_data=json_data,
                headers=headers,
                **kwargs,
            )
            
            # Deserialize response
            response_data = deserialize_response_data(
                response.content,
                model_class=response_model,
            )
            
            return response_data
        
        except Exception as e:
            if isinstance(e, DisperslError):
                raise
            logger.error(f"Async request failed: {e}")
            raise DisperslError(f"Async request failed: {e}", original_error=e)
    
    async def get(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[type] = None,
        **kwargs: Any,
    ) -> Any:
        """Make an async GET request."""
        return await self._make_request(
            "GET", path, params=params, headers=headers, response_model=response_model, **kwargs
        )
    
    async def post(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[type] = None,
        **kwargs: Any,
    ) -> Any:
        """Make an async POST request."""
        return await self._make_request(
            "POST",
            path,
            params=params,
            json_data=json_data,
            headers=headers,
            response_model=response_model,
            **kwargs,
        )
    
    async def put(
        self,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[type] = None,
        **kwargs: Any,
    ) -> Any:
        """Make an async PUT request."""
        return await self._make_request(
            "PUT",
            path,
            params=params,
            json_data=json_data,
            headers=headers,
            response_model=response_model,
            **kwargs,
        )
    
    async def delete(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        response_model: Optional[type] = None,
        **kwargs: Any,
    ) -> Any:
        """Make an async DELETE request."""
        return await self._make_request(
            "DELETE", path, params=params, headers=headers, response_model=response_model, **kwargs
        )
