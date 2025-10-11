"""
Models resource for LLM model management.

This module provides the ModelsResource class for interacting with
the Dispersl API's model management endpoints.
"""

import logging
from typing import Any, Dict, Optional

from .base import AsyncResource, Resource
from ..models.api import ModelsResponse

logger = logging.getLogger(__name__)


class ModelsResource(Resource):
    """
    Resource for LLM model management.
    
    Provides methods for listing available AI models and their specifications.
    """
    
    def list(self) -> ModelsResponse:
        """
        List available AI models.
        
        Retrieves all available AI models with their specifications.
        
        Returns:
            ModelsResponse: List of available models
        
        Raises:
            DisperslError: For various API errors
        """
        return self.get(
            "/models",
            response_model=ModelsResponse,
        )


class AsyncModelsResource(AsyncResource):
    """
    Async resource for LLM model management.
    
    Provides async methods for listing available AI models and their specifications.
    """
    
    async def list(self) -> ModelsResponse:
        """
        Async list available AI models.
        
        Retrieves all available AI models with their specifications.
        
        Returns:
            ModelsResponse: List of available models
        
        Raises:
            DisperslError: For various API errors
        """
        return await self.get(
            "/models",
            response_model=ModelsResponse,
        )
