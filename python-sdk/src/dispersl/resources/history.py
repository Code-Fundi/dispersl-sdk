"""
History resource for task and step history tracking.

This module provides the HistoryResource class for interacting with
the Dispersl API's history endpoints.
"""

import logging
from typing import Optional

from ..models.api import HistoryRequest, HistoryResponse, PaginatedHistoryResponse
from .base import AsyncResource, Resource

logger = logging.getLogger(__name__)


class HistoryResource(Resource):
    """
    Resource for task and step history tracking.

    Provides methods for retrieving task and step history.
    """

    def get_task_history(
        self,
        task_id: str,
        page: Optional[int] = None,
        pageSize: Optional[int] = None,
    ) -> PaginatedHistoryResponse:
        """
        Get task history by ID.

        Retrieves the history for a specific task by its ID.

        Args:
            task_id: Task ID to retrieve history for
            page: Page number (1-based)
            pageSize: Items per page

        Returns:
            PaginatedHistoryResponse: Task history with pagination info

        Raises:
            DisperslError: For various API errors
        """
        request_data = HistoryRequest(page=page, pageSize=pageSize)

        return self.get(
            f"/history/task/{task_id}",
            json_data=request_data.dict(exclude_none=True),
            response_model=PaginatedHistoryResponse,
        )

    def get_step_history(
        self,
        step_id: str,
        page: Optional[int] = None,
        pageSize: Optional[int] = None,
    ) -> PaginatedHistoryResponse:
        """
        Get step history by ID.

        Retrieves the history for a specific step by its ID.

        Args:
            step_id: Step ID to retrieve history for
            page: Page number (1-based)
            pageSize: Items per page

        Returns:
            PaginatedHistoryResponse: Step history with pagination info

        Raises:
            DisperslError: For various API errors
        """
        request_data = HistoryRequest(page=page, pageSize=pageSize)

        return self.get(
            f"/history/step/{step_id}",
            json_data=request_data.dict(exclude_none=True),
            response_model=PaginatedHistoryResponse,
        )


class AsyncHistoryResource(AsyncResource):
    """
    Async resource for task and step history tracking.

    Provides async methods for retrieving task and step history.
    """

    async def get_task_history(
        self,
        task_id: str,
        page: Optional[int] = None,
        pageSize: Optional[int] = None,
    ) -> PaginatedHistoryResponse:
        """
        Async get task history by ID.

        Retrieves the history for a specific task by its ID.

        Args:
            task_id: Task ID to retrieve history for
            page: Page number (1-based)
            pageSize: Items per page

        Returns:
            PaginatedHistoryResponse: Task history with pagination info

        Raises:
            DisperslError: For various API errors
        """
        request_data = HistoryRequest(page=page, pageSize=pageSize)

        return await self.get(
            f"/history/task/{task_id}",
            json_data=request_data.dict(exclude_none=True),
            response_model=PaginatedHistoryResponse,
        )

    async def get_step_history(
        self,
        step_id: str,
        page: Optional[int] = None,
        pageSize: Optional[int] = None,
    ) -> PaginatedHistoryResponse:
        """
        Async get step history by ID.

        Retrieves the history for a specific step by its ID.

        Args:
            step_id: Step ID to retrieve history for
            page: Page number (1-based)
            pageSize: Items per page

        Returns:
            PaginatedHistoryResponse: Step history with pagination info

        Raises:
            DisperslError: For various API errors
        """
        request_data = HistoryRequest(page=page, pageSize=pageSize)

        return await self.get(
            f"/history/step/{step_id}",
            json_data=request_data.dict(exclude_none=True),
            response_model=PaginatedHistoryResponse,
        )
