"""
Authentication resource for API key management.

This module provides the AuthenticationResource class for interacting with
the Dispersl API's authentication endpoints.
"""

import logging
from typing import Optional

from ..models.api import APIKeysResponse, NewAPIKeyRequest, NewAPIKeyResponse
from .base import AsyncResource, Resource

logger = logging.getLogger(__name__)


class AuthenticationResource(Resource):
    """
    Resource for API key management.

    Provides methods for retrieving and generating API keys.
    """

    def get_keys(self) -> APIKeysResponse:
        """
        Get API keys.

        Retrieves API keys for the authenticated user.

        Returns:
            APIKeysResponse: List of API keys

        Raises:
            DisperslError: For various API errors
        """
        return self.get(
            "/keys",
            response_model=APIKeysResponse,
        )

    def generate_new_key(
        self,
        user_id: str,
        name: Optional[str] = None,
    ) -> NewAPIKeyResponse:
        """
        Generate new API key.

        Generates new API key pair for the specified user.

        Args:
            user_id: The user ID for which to generate the API key
            name: Optional name for the API key

        Returns:
            NewAPIKeyResponse: Generated API key information

        Raises:
            DisperslError: For various API errors
        """
        request_data = NewAPIKeyRequest(
            user_id=user_id,
            name=name,
        )

        return self.post(
            "/keys/new",
            json_data=request_data.dict(exclude_none=True),
            response_model=NewAPIKeyResponse,
        )


class AsyncAuthenticationResource(AsyncResource):
    """
    Async resource for API key management.

    Provides async methods for retrieving and generating API keys.
    """

    async def get_keys(self) -> APIKeysResponse:
        """
        Async get API keys.

        Retrieves API keys for the authenticated user.

        Returns:
            APIKeysResponse: List of API keys

        Raises:
            DisperslError: For various API errors
        """
        return await self.get(
            "/keys",
            response_model=APIKeysResponse,
        )

    async def generate_new_key(
        self,
        user_id: str,
        name: Optional[str] = None,
    ) -> NewAPIKeyResponse:
        """
        Async generate new API key.

        Generates new API key pair for the specified user.

        Args:
            user_id: The user ID for which to generate the API key
            name: Optional name for the API key

        Returns:
            NewAPIKeyResponse: Generated API key information

        Raises:
            DisperslError: For various API errors
        """
        request_data = NewAPIKeyRequest(
            user_id=user_id,
            name=name,
        )

        return await self.post(
            "/keys/new",
            json_data=request_data.dict(exclude_none=True),
            response_model=NewAPIKeyResponse,
        )
