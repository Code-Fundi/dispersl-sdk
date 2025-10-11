"""
History resource for task and step history tracking.

This module provides the HistoryResource class for interacting with
the Dispersl API's history endpoints.
"""

import logging
from typing import Optional

from ..models.api import HistoryRequest, HistoryResponse
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
        limit: Optional[int] = None,
    ) -> HistoryResponse:
        """
        Get task history by ID.

        Retrieves the history for a specific task by its ID.

        Args:
            task_id: Task ID to retrieve history for
            limit: Number of items to return

        Returns:
            HistoryResponse: Task history

        Raises:
            DisperslError: For various API errors
        """
        request_data = HistoryRequest(limit=limit)

        return self.get(
            f"/history/task{task_id}",
            json_data=request_data.dict(exclude_none=True),
            response_model=HistoryResponse,
        )

    def get_step_history(
        self,
        step_id: str,
        limit: Optional[int] = None,
    ) -> HistoryResponse:
        """
        Get step history by ID.

        Retrieves the history for a specific step by its ID.

        Args:
            step_id: Step ID to retrieve history for
            limit: Number of items to return

        Returns:
            HistoryResponse: Step history

        Raises:
            DisperslError: For various API errors
        """
        request_data = HistoryRequest(limit=limit)

        return self.get(
            f"/history/step/{step_id}",
            json_data=request_data.dict(exclude_none=True),
            response_model=HistoryResponse,
        )


class AsyncHistoryResource(AsyncResource):
    """
    Async resource for task and step history tracking.

    Provides async methods for retrieving task and step history.
    """

    async def get_task_history(
        self,
        task_id: str,
        limit: Optional[int] = None,
    ) -> HistoryResponse:
        """
        Async get task history by ID.

        Retrieves the history for a specific task by its ID.

        Args:
            task_id: Task ID to retrieve history for
            limit: Number of items to return

        Returns:
            HistoryResponse: Task history

        Raises:
            DisperslError: For various API errors
        """
        request_data = HistoryRequest(limit=limit)

        return await self.get(
            f"/history/task{task_id}",
            json_data=request_data.dict(exclude_none=True),
            response_model=HistoryResponse,
        )

    async def get_step_history(
        self,
        step_id: str,
        limit: Optional[int] = None,
    ) -> HistoryResponse:
        """
        Async get step history by ID.

        Retrieves the history for a specific step by its ID.

        Args:
            step_id: Step ID to retrieve history for
            limit: Number of items to return

        Returns:
            HistoryResponse: Step history

        Raises:
            DisperslError: For various API errors
        """
        request_data = HistoryRequest(limit=limit)

        return await self.get(
            f"/history/step/{step_id}",
            json_data=request_data.dict(exclude_none=True),
            response_model=HistoryResponse,
        )
