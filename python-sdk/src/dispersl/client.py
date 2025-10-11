"""
Main client class for the Dispersl SDK.

This module provides the main Client and AsyncClient classes that serve
as the primary interface for interacting with the Dispersl API.
"""

import logging
from typing import Any, Optional, Union

from .auth import AuthHandler, create_auth_handler
from .exceptions import DisperslError
from .http import AsyncHTTPClient, HTTPClient
from .resources import (
    AgentsResource,
    AuthenticationResource,
    HistoryResource,
    ModelsResource,
    StepManagementResource,
    TaskManagementResource,
)

logger = logging.getLogger(__name__)


class Client:
    """
    Main client for the Dispersl API.

    This client provides a high-level interface for interacting with
    the Dispersl API, including all available endpoints and resources.

    Example:
        ```python
        from dispersl import Client

        client = Client(api_key="your_api_key")
        response = client.agents.chat(prompt="Hello, world!")
        ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.dispersl.com/v1",
        timeout: float = 30.0,
        connect_timeout: float = 10.0,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        headers: Optional[dict[str, str]] = None,
        auth: Optional[Union[str, AuthHandler]] = None,
    ) -> None:
        """
        Initialize the Dispersl client.

        Args:
            api_key: API key for authentication (alternative to auth)
            base_url: Base URL for API requests
            timeout: Total request timeout in seconds
            connect_timeout: Connection timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff multiplier
            headers: Additional headers for all requests
            auth: Authentication handler (alternative to api_key)

        Raises:
            DisperslError: If authentication is not provided
        """
        # Set up authentication
        if auth is not None:
            self.auth = create_auth_handler(auth)
        elif api_key is not None:
            self.auth = create_auth_handler(api_key)
        else:
            self.auth = create_auth_handler()

        if self.auth is None:
            raise DisperslError(
                "Authentication required. Provide api_key or auth parameter, "
                "or set DISPERSL_API_KEY environment variable."
            )

        # Prepare headers
        auth_headers = self.auth.get_headers()
        all_headers = {**(headers or {}), **auth_headers}

        # Initialize HTTP client
        self.http = HTTPClient(
            base_url=base_url,
            timeout=timeout,
            connect_timeout=connect_timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            headers=all_headers,
        )

        # Initialize resources
        self.agents = AgentsResource(self.http)
        self.models = ModelsResource(self.http)
        self.auth_resource = AuthenticationResource(self.http)
        self.tasks = TaskManagementResource(self.http)
        self.steps = StepManagementResource(self.http)
        self.history = HistoryResource(self.http)

        logger.info(f"Dispersl client initialized for {base_url}")

    def __enter__(self) -> "Client":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()

    def close(self) -> None:
        """Close the client and cleanup resources."""
        self.http.close()
        logger.info("Dispersl client closed")

    def get_version(self) -> str:
        """
        Get the SDK version.

        Returns:
            SDK version string
        """
        from . import __version__

        return __version__

    def get_base_url(self) -> str:
        """
        Get the base URL for API requests.

        Returns:
            Base URL string
        """
        return self.http.base_url


class AsyncClient:
    """
    Async client for the Dispersl API.

    This client provides an async interface for interacting with
    the Dispersl API, supporting async/await patterns.

    Example:
        ```python
        import asyncio
        from dispersl import AsyncClient

        async def main():
            async with AsyncClient(api_key="your_api_key") as client:
                response = await client.agents.chat(prompt="Hello, world!")

        asyncio.run(main())
        ```
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.dispersl.com/v1",
        timeout: float = 30.0,
        connect_timeout: float = 10.0,
        max_retries: int = 3,
        backoff_factor: float = 2.0,
        headers: Optional[dict[str, str]] = None,
        auth: Optional[Union[str, AuthHandler]] = None,
    ) -> None:
        """
        Initialize the async Dispersl client.

        Args:
            api_key: API key for authentication (alternative to auth)
            base_url: Base URL for API requests
            timeout: Total request timeout in seconds
            connect_timeout: Connection timeout in seconds
            max_retries: Maximum number of retry attempts
            backoff_factor: Exponential backoff multiplier
            headers: Additional headers for all requests
            auth: Authentication handler (alternative to api_key)

        Raises:
            DisperslError: If authentication is not provided
        """
        # Set up authentication
        if auth is not None:
            self.auth = create_auth_handler(auth)
        elif api_key is not None:
            self.auth = create_auth_handler(api_key)
        else:
            self.auth = create_auth_handler()

        if self.auth is None:
            raise DisperslError(
                "Authentication required. Provide api_key or auth parameter, "
                "or set DISPERSL_API_KEY environment variable."
            )

        # Prepare headers
        auth_headers = self.auth.get_headers()
        all_headers = {**(headers or {}), **auth_headers}

        # Initialize async HTTP client
        self.http = AsyncHTTPClient(
            base_url=base_url,
            timeout=timeout,
            connect_timeout=connect_timeout,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            headers=all_headers,
        )

        # Initialize async resources
        from .resources import (
            AsyncAgentsResource,
            AsyncAuthenticationResource,
            AsyncHistoryResource,
            AsyncModelsResource,
            AsyncStepManagementResource,
            AsyncTaskManagementResource,
        )

        self.agents = AsyncAgentsResource(self.http)
        self.models = AsyncModelsResource(self.http)
        self.auth_resource = AsyncAuthenticationResource(self.http)
        self.tasks = AsyncTaskManagementResource(self.http)
        self.steps = AsyncStepManagementResource(self.http)
        self.history = AsyncHistoryResource(self.http)

        logger.info(f"Async Dispersl client initialized for {base_url}")

    async def __aenter__(self) -> "AsyncClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the async client and cleanup resources."""
        await self.http.close()
        logger.info("Async Dispersl client closed")

    def get_version(self) -> str:
        """
        Get the SDK version.

        Returns:
            SDK version string
        """
        from . import __version__

        return __version__

    def get_base_url(self) -> str:
        """
        Get the base URL for API requests.

        Returns:
            Base URL string
        """
        return self.http.base_url
