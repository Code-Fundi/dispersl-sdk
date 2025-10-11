"""
Authentication handlers for the Dispersl SDK.

This module provides various authentication methods including
API key, Bearer token, and OAuth 2.0 support.
"""

import os
from typing import Optional, Union


class AuthHandler:
    """
    Base class for authentication handlers.

    All authentication methods should inherit from this class
    and implement the get_headers method.
    """

    def get_headers(self) -> dict[str, str]:
        """
        Get authentication headers for requests.

        Returns:
            Dictionary of headers to include in requests
        """
        raise NotImplementedError("Subclasses must implement get_headers")


class APIKeyAuth(AuthHandler):
    """
    API Key authentication handler.

    Supports both header-based and query parameter-based API keys.
    """

    def __init__(
        self,
        api_key: str,
        header_name: str = "Authorization",
        header_format: str = "Bearer {api_key}",
    ) -> None:
        """
        Initialize API key authentication.

        Args:
            api_key: The API key to use for authentication
            header_name: Name of the header to use
            header_format: Format string for the header value
        """
        self.api_key = api_key
        self.header_name = header_name
        self.header_format = header_format

    def get_headers(self) -> dict[str, str]:
        """Get authentication headers with API key."""
        return {self.header_name: self.header_format.format(api_key=self.api_key)}


class BearerTokenAuth(AuthHandler):
    """
    Bearer token authentication handler.

    Used for OAuth 2.0 and other token-based authentication.
    """

    def __init__(self, token: str) -> None:
        """
        Initialize Bearer token authentication.

        Args:
            token: The Bearer token to use for authentication
        """
        self.token = token

    def get_headers(self) -> dict[str, str]:
        """Get authentication headers with Bearer token."""
        return {"Authorization": f"Bearer {self.token}"}


class OAuth2Auth(AuthHandler):
    """
    OAuth 2.0 authentication handler.

    Supports client credentials flow and automatic token refresh.
    """

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        token_url: str,
        scope: Optional[str] = None,
        token: Optional[str] = None,
        refresh_token: Optional[str] = None,
    ) -> None:
        """
        Initialize OAuth 2.0 authentication.

        Args:
            client_id: OAuth 2.0 client ID
            client_secret: OAuth 2.0 client secret
            token_url: URL for token endpoint
            scope: OAuth 2.0 scope
            token: Existing access token
            refresh_token: Refresh token for token renewal
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.scope = scope
        self.token = token
        self.refresh_token = refresh_token

    def get_headers(self) -> dict[str, str]:
        """Get authentication headers with OAuth 2.0 token."""
        if not self.token:
            raise ValueError("No access token available. Call get_token() first.")

        return {"Authorization": f"Bearer {self.token}"}

    def get_token(self) -> str:
        """
        Get access token using client credentials flow.

        Returns:
            Access token string

        Raises:
            ValueError: If token retrieval fails
        """
        # This would typically make an HTTP request to the token endpoint
        # For now, we'll raise an error indicating this needs to be implemented
        raise NotImplementedError(
            "OAuth 2.0 token retrieval not implemented. "
            "Please provide a token directly or implement token refresh logic."
        )


class BasicAuth(AuthHandler):
    """
    Basic authentication handler.

    Uses username and password for HTTP Basic authentication.
    """

    def __init__(self, username: str, password: str) -> None:
        """
        Initialize Basic authentication.

        Args:
            username: Username for authentication
            password: Password for authentication
        """
        self.username = username
        self.password = password

    def get_headers(self) -> dict[str, str]:
        """Get authentication headers with Basic auth."""
        import base64

        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        return {"Authorization": f"Basic {encoded_credentials}"}


def get_auth_from_env() -> Optional[AuthHandler]:
    """
    Create authentication handler from environment variables.

    Checks for the following environment variables:
    - DISPERSL_API_KEY: API key for authentication
    - DISPERSL_TOKEN: Bearer token for authentication
    - DISPERSL_CLIENT_ID: OAuth 2.0 client ID
    - DISPERSL_CLIENT_SECRET: OAuth 2.0 client secret

    Returns:
        AuthHandler instance or None if no credentials found
    """
    # Check for API key
    api_key = os.getenv("DISPERSL_API_KEY")
    if api_key:
        return APIKeyAuth(api_key)

    # Check for Bearer token
    token = os.getenv("DISPERSL_TOKEN")
    if token:
        return BearerTokenAuth(token)

    # Check for OAuth 2.0 credentials
    client_id = os.getenv("DISPERSL_CLIENT_ID")
    client_secret = os.getenv("DISPERSL_CLIENT_SECRET")
    if client_id and client_secret:
        token_url = os.getenv("DISPERSL_TOKEN_URL", "https://api.dispersl.com/oauth/token")
        return OAuth2Auth(client_id, client_secret, token_url)

    return None


def create_auth_handler(
    auth: Optional[Union[str, AuthHandler]] = None,
) -> Optional[AuthHandler]:
    """
    Create authentication handler from various input types.

    Args:
        auth: Authentication method. Can be:
            - None: Try to get from environment variables
            - str: Treat as API key
            - AuthHandler: Use directly

    Returns:
        AuthHandler instance or None
    """
    if auth is None:
        return get_auth_from_env()

    if isinstance(auth, str):
        return APIKeyAuth(auth)

    if isinstance(auth, AuthHandler):
        return auth

    raise ValueError(
        f"Invalid auth type: {type(auth)}. Expected None, str, or AuthHandler instance."
    )
