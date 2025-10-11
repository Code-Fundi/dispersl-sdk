"""
Resource classes for API endpoints.

This module provides all the resource classes for interacting with
different parts of the Dispersl API.
"""

from .agents import AgentsResource, AsyncAgentsResource
from .auth import AsyncAuthenticationResource, AuthenticationResource
from .base import AsyncResource, Resource
from .history import AsyncHistoryResource, HistoryResource
from .models import AsyncModelsResource, ModelsResource
from .steps import AsyncStepManagementResource, StepManagementResource
from .tasks import AsyncTaskManagementResource, TaskManagementResource

__all__ = [
    "Resource",
    "AsyncResource",
    "AgentsResource",
    "AsyncAgentsResource",
    "ModelsResource",
    "AsyncModelsResource",
    "AuthenticationResource",
    "AsyncAuthenticationResource",
    "TaskManagementResource",
    "AsyncTaskManagementResource",
    "StepManagementResource",
    "AsyncStepManagementResource",
    "HistoryResource",
    "AsyncHistoryResource",
]
