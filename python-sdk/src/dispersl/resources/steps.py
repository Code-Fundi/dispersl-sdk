"""
Step management resource for task step operations.

This module provides the StepManagementResource class for interacting with
the Dispersl API's step management endpoints.
"""

import logging
from typing import Optional

from ..models.api import StepResponse, PaginatedStepResponse
from ..models.base import PaginationParams
from .base import AsyncResource, Resource

logger = logging.getLogger(__name__)


class StepManagementResource(Resource):
    """
    Resource for task step operations.

    Provides methods for retrieving and deleting task steps.
    """

    def get_by_task_id(self, task_id: str, params: Optional[PaginationParams] = None) -> PaginatedStepResponse:
        """
        Get steps by Task ID.

        Retrieves steps for a specific task by its ID.

        Args:
            task_id: Task ID to retrieve steps for
            params: Pagination parameters

        Returns:
            PaginatedStepResponse: Step information with pagination info

        Raises:
            DisperslError: For various API errors
        """
        return self.get(
            f"/steps/task/{task_id}",
            params=params.dict(exclude_none=True) if params else None,
            response_model=PaginatedStepResponse,
        )

    def get(self, step_id: str) -> StepResponse:
        """
        Get a step by ID.

        Retrieves a specific step by its ID.

        Args:
            step_id: Step ID to retrieve

        Returns:
            StepResponse: Step information

        Raises:
            DisperslError: For various API errors
        """
        return self.get(
            f"/steps/{step_id}",
            response_model=StepResponse,
        )

    def delete(self, step_id: str) -> StepResponse:
        """
        Cancel a step by ID.

        Deletes a specific step by its ID.

        Args:
            step_id: Step ID to delete

        Returns:
            StepResponse: Deletion confirmation

        Raises:
            DisperslError: For various API errors
        """
        return self.delete(
            f"/steps/{step_id}/delete",
            response_model=StepResponse,
        )


class AsyncStepManagementResource(AsyncResource):
    """
    Async resource for task step operations.

    Provides async methods for retrieving and deleting task steps.
    """

    async def get_by_task_id(self, task_id: str, params: Optional[PaginationParams] = None) -> PaginatedStepResponse:
        """
        Async get steps by Task ID.

        Retrieves steps for a specific task by its ID.

        Args:
            task_id: Task ID to retrieve steps for
            params: Pagination parameters

        Returns:
            PaginatedStepResponse: Step information with pagination info

        Raises:
            DisperslError: For various API errors
        """
        return await self.get(
            f"/steps/task/{task_id}",
            params=params.dict(exclude_none=True) if params else None,
            response_model=PaginatedStepResponse,
        )

    async def get(self, step_id: str) -> StepResponse:
        """
        Async get a step by ID.

        Retrieves a specific step by its ID.

        Args:
            step_id: Step ID to retrieve

        Returns:
            StepResponse: Step information

        Raises:
            DisperslError: For various API errors
        """
        return await self.get(
            f"/steps/{step_id}",
            response_model=StepResponse,
        )

    async def delete(self, step_id: str) -> StepResponse:
        """
        Async cancel a step by ID.

        Deletes a specific step by its ID.

        Args:
            step_id: Step ID to delete

        Returns:
            StepResponse: Deletion confirmation

        Raises:
            DisperslError: For various API errors
        """
        return await self.delete(
            f"/steps/{step_id}/delete",
            response_model=StepResponse,
        )
