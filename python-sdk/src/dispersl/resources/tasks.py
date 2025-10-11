"""
Task management resource for task lifecycle management.

This module provides the TaskManagementResource class for interacting with
the Dispersl API's task management endpoints.
"""

import logging
from typing import Optional

from ..models.api import TaskEditRequest, TaskResponse
from .base import AsyncResource, Resource

logger = logging.getLogger(__name__)


class TaskManagementResource(Resource):
    """
    Resource for task lifecycle management.

    Provides methods for creating, editing, retrieving, and deleting tasks.
    """

    def create(self) -> TaskResponse:
        """
        Create a new task.

        Creates a new task for the authenticated user.

        Returns:
            TaskResponse: Created task information

        Raises:
            DisperslError: For various API errors
        """
        return self.post(
            "/tasks/new",
            response_model=TaskResponse,
        )

    def edit(
        self,
        task_id: str,
        name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> TaskResponse:
        """
        Edit a task by ID.

        Edits a specific task by its ID.

        Args:
            task_id: Task ID to edit
            name: New task name
            status: New task status

        Returns:
            TaskResponse: Updated task information

        Raises:
            DisperslError: For various API errors
        """
        request_data = TaskEditRequest(
            name=name,
            status=status,
        )

        return self.post(
            f"/tasks/{task_id}/edit",
            json_data=request_data.dict(exclude_none=True),
            response_model=TaskResponse,
        )

    def list(self) -> TaskResponse:
        """
        Get all tasks.

        Retrieves all tasks for the authenticated user.

        Returns:
            TaskResponse: List of tasks

        Raises:
            DisperslError: For various API errors
        """
        return self.get(
            "/tasks",
            response_model=TaskResponse,
        )

    def get(self, task_id: str) -> TaskResponse:
        """
        Get a task by ID.

        Retrieves a specific task by its ID.

        Args:
            task_id: Task ID to retrieve

        Returns:
            TaskResponse: Task information

        Raises:
            DisperslError: For various API errors
        """
        return self.get(
            f"/tasks/{task_id}",
            response_model=TaskResponse,
        )

    def delete(self, task_id: str) -> TaskResponse:
        """
        Cancel a task by ID.

        Deletes a specific task by its ID.

        Args:
            task_id: Task ID to delete

        Returns:
            TaskResponse: Deletion confirmation

        Raises:
            DisperslError: For various API errors
        """
        return self.delete(
            f"/tasks/{task_id}/delete",
            response_model=TaskResponse,
        )


class AsyncTaskManagementResource(AsyncResource):
    """
    Async resource for task lifecycle management.

    Provides async methods for creating, editing, retrieving, and deleting tasks.
    """

    async def create(self) -> TaskResponse:
        """
        Async create a new task.

        Creates a new task for the authenticated user.

        Returns:
            TaskResponse: Created task information

        Raises:
            DisperslError: For various API errors
        """
        return await self.post(
            "/tasks/new",
            response_model=TaskResponse,
        )

    async def edit(
        self,
        task_id: str,
        name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> TaskResponse:
        """
        Async edit a task by ID.

        Edits a specific task by its ID.

        Args:
            task_id: Task ID to edit
            name: New task name
            status: New task status

        Returns:
            TaskResponse: Updated task information

        Raises:
            DisperslError: For various API errors
        """
        request_data = TaskEditRequest(
            name=name,
            status=status,
        )

        return await self.post(
            f"/tasks/{task_id}/edit",
            json_data=request_data.dict(exclude_none=True),
            response_model=TaskResponse,
        )

    async def list(self) -> TaskResponse:
        """
        Async get all tasks.

        Retrieves all tasks for the authenticated user.

        Returns:
            TaskResponse: List of tasks

        Raises:
            DisperslError: For various API errors
        """
        return await self.get(
            "/tasks",
            response_model=TaskResponse,
        )

    async def get(self, task_id: str) -> TaskResponse:
        """
        Async get a task by ID.

        Retrieves a specific task by its ID.

        Args:
            task_id: Task ID to retrieve

        Returns:
            TaskResponse: Task information

        Raises:
            DisperslError: For various API errors
        """
        return await self.get(
            f"/tasks/{task_id}",
            response_model=TaskResponse,
        )

    async def delete(self, task_id: str) -> TaskResponse:
        """
        Async cancel a task by ID.

        Deletes a specific task by its ID.

        Args:
            task_id: Task ID to delete

        Returns:
            TaskResponse: Deletion confirmation

        Raises:
            DisperslError: For various API errors
        """
        return await self.delete(
            f"/tasks/{task_id}/delete",
            response_model=TaskResponse,
        )
