"""
Agents resource for AI operations.

This module provides the AgentsResource class for interacting with
the Dispersl API's agent endpoints, including chat, planning,
code generation, testing, and documentation.
"""

import logging
from collections.abc import Generator
from typing import Any, Optional

from ..models import StandardNdjsonResponse
from ..models.api import (
    BuildRequest,
    ChatRequest,
    DisperseRequest,
    RepoDocsRequest,
    PaginatedAgentResponse,
)
from ..models.base import PaginationParams
from .base import AsyncResource, Resource

logger = logging.getLogger(__name__)


class AgentsResource(Resource):
    """
    Resource for AI agent operations.

    Provides methods for interacting with various AI agents including
    chat, planning, code generation, testing, and documentation.
    """

    def list(self, params: Optional[PaginationParams] = None) -> PaginatedAgentResponse:
        """
        Get all agents.

        Retrieves all available agents.

        Args:
            params: Pagination parameters

        Returns:
            PaginatedAgentResponse: List of agents with pagination info

        Raises:
            DisperslError: For various API errors
        """
        return self.get(
            "/agents",
            params=params.dict(exclude_none=True) if params else None,
            response_model=PaginatedAgentResponse,
        )

    def chat(
        self,
        prompt: str,
        model: Optional[str] = None,
        context: Optional[str] = None,
        memory: Optional[bool] = None,
        voice: Optional[bool] = None,
        task_id: Optional[str] = None,
        knowledge: Optional[str] = None,
        os: Optional[str] = None,
        default_dir: Optional[str] = None,
        current_dir: Optional[str] = None,
        mcp: Optional[dict[str, Any]] = None,
    ) -> Generator[StandardNdjsonResponse, None, None]:
        """
        Chat with AI to understand internal codebase insights, task progress and documentation.

        Args:
            prompt: Chat prompt
            model: AI model to use
            context: Additional context
            memory: Enable memory
            voice: Enable voice response
            task_id: Task ID for context
            knowledge: Knowledge sources
            os: Operating system
            default_dir: Default directory
            current_dir: Current directory
            mcp: MCP configuration

        Yields:
            StandardNdjsonResponse: Streaming response chunks

        Raises:
            DisperslError: For various API errors
        """
        request_data = ChatRequest(
            prompt=prompt,
            model=model,
            context=context,
            memory=memory,
            voice=voice,
            task_id=task_id,
            knowledge=knowledge,
            os=os,
            default_dir=default_dir,
            current_dir=current_dir,
            mcp=mcp,
        )

        # Make streaming request
        response = self.http.post(
            "/agent/chat",
            json_data=request_data.dict(exclude_none=True),
            headers={"Accept": "application/x-ndjson"},
        )

        # Parse NDJSON stream
        for line in response.text.splitlines():
            if line.strip():
                try:
                    chunk_data = self._parse_ndjson_line(line)
                    yield StandardNdjsonResponse(**chunk_data)
                except Exception as e:
                    logger.warning(f"Failed to parse NDJSON line: {line}, error: {e}")
                    continue

    def plan(
        self,
        prompt: str,
        model: Optional[str] = None,
        agent_name: Optional[str] = None,
        context: Optional[str] = None,
        task_id: Optional[str] = None,
        knowledge: Optional[str] = None,
        os: Optional[str] = None,
        default_dir: Optional[str] = None,
        current_dir: Optional[str] = None,
        memory: Optional[bool] = None,
    ) -> Generator[StandardNdjsonResponse, None, None]:
        """
        Multi-agent task dispersion.

        Distributes a complex task across multiple specialized AI agents
        following SDLC principles.

        Args:
            prompt: Task prompt
            model: AI model to use
            agent_name: Agent name
            context: Additional context
            task_id: Task ID
            knowledge: Knowledge sources
            os: Operating system
            default_dir: Default directory
            current_dir: Current directory
            memory: Enable memory

        Yields:
            StandardNdjsonResponse: Streaming response chunks

        Raises:
            DisperslError: For various API errors
        """
        request_data = DisperseRequest(
            prompt=prompt,
            model=model,
            agent_name=agent_name,
            context=context,
            task_id=task_id,
            knowledge=knowledge,
            os=os,
            default_dir=default_dir,
            current_dir=current_dir,
            memory=memory,
        )

        # Make streaming request
        response = self.http.post(
            "/agent/plan",
            json_data=request_data.dict(exclude_none=True),
            headers={"Accept": "application/x-ndjson"},
        )

        # Parse NDJSON stream
        for line in response.text.splitlines():
            if line.strip():
                try:
                    chunk_data = self._parse_ndjson_line(line)
                    yield StandardNdjsonResponse(**chunk_data)
                except Exception as e:
                    logger.warning(f"Failed to parse NDJSON line: {line}, error: {e}")
                    continue

    def code(
        self,
        prompt: str,
        model: Optional[str] = None,
        context: Optional[str] = None,
        task_id: Optional[str] = None,
        knowledge: Optional[str] = None,
        os: Optional[str] = None,
        default_dir: Optional[str] = None,
        current_dir: Optional[str] = None,
        mcp: Optional[dict[str, Any]] = None,
    ) -> Generator[StandardNdjsonResponse, None, None]:
        """
        Code generation with agentic flow and tool execution.

        Generates and builds code based on the provided prompt.

        Args:
            prompt: Build prompt
            model: AI model to use
            context: Additional context
            task_id: Task ID
            knowledge: Knowledge sources
            os: Operating system
            default_dir: Default directory
            current_dir: Current directory
            mcp: MCP configuration

        Yields:
            StandardNdjsonResponse: Streaming response chunks

        Raises:
            DisperslError: For various API errors
        """
        request_data = BuildRequest(
            prompt=prompt,
            model=model,
            context=context,
            task_id=task_id,
            knowledge=knowledge,
            os=os,
            default_dir=default_dir,
            current_dir=current_dir,
            mcp=mcp,
        )

        # Make streaming request
        response = self.http.post(
            "/agent/code",
            json_data=request_data.dict(exclude_none=True),
            headers={"Accept": "application/x-ndjson"},
        )

        # Parse NDJSON stream
        for line in response.text.splitlines():
            if line.strip():
                try:
                    chunk_data = self._parse_ndjson_line(line)
                    yield StandardNdjsonResponse(**chunk_data)
                except Exception as e:
                    logger.warning(f"Failed to parse NDJSON line: {line}, error: {e}")
                    continue

    def test(
        self,
        prompt: str,
        model: Optional[str] = None,
        context: Optional[str] = None,
        task_id: Optional[str] = None,
        knowledge: Optional[str] = None,
        os: Optional[str] = None,
        default_dir: Optional[str] = None,
        current_dir: Optional[str] = None,
        mcp: Optional[dict[str, Any]] = None,
    ) -> Generator[StandardNdjsonResponse, None, None]:
        """
        Test generation with agentic flow and tool execution.

        Generates and builds tests based on the provided prompt.

        Args:
            prompt: Build prompt
            model: AI model to use
            context: Additional context
            task_id: Task ID
            knowledge: Knowledge sources
            os: Operating system
            default_dir: Default directory
            current_dir: Current directory
            mcp: MCP configuration

        Yields:
            StandardNdjsonResponse: Streaming response chunks

        Raises:
            DisperslError: For various API errors
        """
        request_data = BuildRequest(
            prompt=prompt,
            model=model,
            context=context,
            task_id=task_id,
            knowledge=knowledge,
            os=os,
            default_dir=default_dir,
            current_dir=current_dir,
            mcp=mcp,
        )

        # Make streaming request
        response = self.http.post(
            "/agent/test",
            json_data=request_data.dict(exclude_none=True),
            headers={"Accept": "application/x-ndjson"},
        )

        # Parse NDJSON stream
        for line in response.text.splitlines():
            if line.strip():
                try:
                    chunk_data = self._parse_ndjson_line(line)
                    yield StandardNdjsonResponse(**chunk_data)
                except Exception as e:
                    logger.warning(f"Failed to parse NDJSON line: {line}, error: {e}")
                    continue

    def git(
        self,
        prompt: str,
        model: Optional[str] = None,
        context: Optional[str] = None,
        task_id: Optional[str] = None,
        knowledge: Optional[str] = None,
        os: Optional[str] = None,
        default_dir: Optional[str] = None,
        current_dir: Optional[str] = None,
        mcp: Optional[dict[str, Any]] = None,
    ) -> Generator[StandardNdjsonResponse, None, None]:
        """
        Git versioning with agentic flow and tool execution.

        Handles Git versioning operations.

        Args:
            prompt: Build prompt
            model: AI model to use
            context: Additional context
            task_id: Task ID
            knowledge: Knowledge sources
            os: Operating system
            default_dir: Default directory
            current_dir: Current directory
            mcp: MCP configuration

        Yields:
            StandardNdjsonResponse: Streaming response chunks

        Raises:
            DisperslError: For various API errors
        """
        request_data = BuildRequest(
            prompt=prompt,
            model=model,
            context=context,
            task_id=task_id,
            knowledge=knowledge,
            os=os,
            default_dir=default_dir,
            current_dir=current_dir,
            mcp=mcp,
        )

        # Make streaming request
        response = self.http.post(
            "/agent/git",
            json_data=request_data.dict(exclude_none=True),
            headers={"Accept": "application/x-ndjson"},
        )

        # Parse NDJSON stream
        for line in response.text.splitlines():
            if line.strip():
                try:
                    chunk_data = self._parse_ndjson_line(line)
                    yield StandardNdjsonResponse(**chunk_data)
                except Exception as e:
                    logger.warning(f"Failed to parse NDJSON line: {line}, error: {e}")
                    continue

    def document_repo(
        self,
        url: str,
        branch: str,
        model: Optional[str] = None,
        team_access: Optional[bool] = None,
        task_id: Optional[str] = None,
    ) -> Generator[StandardNdjsonResponse, None, None]:
        """
        Generate end to end documentation for a repository.

        Generates documentation for a repository with agentic flow
        and tool execution.

        Args:
            url: Repository URL
            branch: Git branch
            model: AI model to use
            team_access: Team access
            task_id: Task ID

        Yields:
            StandardNdjsonResponse: Streaming response chunks

        Raises:
            DisperslError: For various API errors
        """
        request_data = RepoDocsRequest(
            url=url,
            branch=branch,
            model=model,
            team_access=team_access,
            task_id=task_id,
        )

        # Make streaming request
        response = self.http.post(
            "/agent/document/repo",
            json_data=request_data.dict(exclude_none=True),
            headers={"Accept": "application/x-ndjson"},
        )

        # Parse NDJSON stream
        for line in response.text.splitlines():
            if line.strip():
                try:
                    chunk_data = self._parse_ndjson_line(line)
                    yield StandardNdjsonResponse(**chunk_data)
                except Exception as e:
                    logger.warning(f"Failed to parse NDJSON line: {line}, error: {e}")
                    continue

    def _parse_ndjson_line(self, line: str) -> dict[str, Any]:
        """
        Parse a single NDJSON line.

        Args:
            line: NDJSON line to parse

        Returns:
            Parsed data as dictionary

        Raises:
            ValueError: If line is not valid JSON
        """
        import json

        return json.loads(line)


class AsyncAgentsResource(AsyncResource):
    """
    Async resource for AI agent operations.

    Provides async methods for interacting with various AI agents including
    chat, planning, code generation, testing, and documentation.
    """

    async def list(self, params: Optional[PaginationParams] = None) -> PaginatedAgentResponse:
        """
        Async get all agents.

        Retrieves all available agents.

        Args:
            params: Pagination parameters

        Returns:
            PaginatedAgentResponse: List of agents with pagination info

        Raises:
            DisperslError: For various API errors
        """
        return await self.get(
            "/agents",
            params=params.dict(exclude_none=True) if params else None,
            response_model=PaginatedAgentResponse,
        )

    async def chat(
        self,
        prompt: str,
        model: Optional[str] = None,
        context: Optional[str] = None,
        memory: Optional[bool] = None,
        voice: Optional[bool] = None,
        task_id: Optional[str] = None,
        knowledge: Optional[str] = None,
        os: Optional[str] = None,
        default_dir: Optional[str] = None,
        current_dir: Optional[str] = None,
        mcp: Optional[dict[str, Any]] = None,
    ) -> Generator[StandardNdjsonResponse, None, None]:
        """
        Async chat with AI to understand internal codebase insights, task progress and documentation.

        Args:
            prompt: Chat prompt
            model: AI model to use
            context: Additional context
            memory: Enable memory
            voice: Enable voice response
            task_id: Task ID for context
            knowledge: Knowledge sources
            os: Operating system
            default_dir: Default directory
            current_dir: Current directory
            mcp: MCP configuration

        Yields:
            StandardNdjsonResponse: Streaming response chunks

        Raises:
            DisperslError: For various API errors
        """
        request_data = ChatRequest(
            prompt=prompt,
            model=model,
            context=context,
            memory=memory,
            voice=voice,
            task_id=task_id,
            knowledge=knowledge,
            os=os,
            default_dir=default_dir,
            current_dir=current_dir,
            mcp=mcp,
        )

        # Make streaming request
        response = await self.http.post(
            "/agent/chat",
            json_data=request_data.dict(exclude_none=True),
            headers={"Accept": "application/x-ndjson"},
        )

        # Parse NDJSON stream
        for line in response.text.splitlines():
            if line.strip():
                try:
                    chunk_data = self._parse_ndjson_line(line)
                    yield StandardNdjsonResponse(**chunk_data)
                except Exception as e:
                    logger.warning(f"Failed to parse NDJSON line: {line}, error: {e}")
                    continue

    async def plan(
        self,
        prompt: str,
        model: Optional[str] = None,
        agent_name: Optional[str] = None,
        context: Optional[str] = None,
        task_id: Optional[str] = None,
        knowledge: Optional[str] = None,
        os: Optional[str] = None,
        default_dir: Optional[str] = None,
        current_dir: Optional[str] = None,
        memory: Optional[bool] = None,
    ) -> Generator[StandardNdjsonResponse, None, None]:
        """
        Async multi-agent task dispersion.

        Distributes a complex task across multiple specialized AI agents
        following SDLC principles.

        Args:
            prompt: Task prompt
            model: AI model to use
            agent_name: Agent name
            context: Additional context
            task_id: Task ID
            knowledge: Knowledge sources
            os: Operating system
            default_dir: Default directory
            current_dir: Current directory
            memory: Enable memory

        Yields:
            StandardNdjsonResponse: Streaming response chunks

        Raises:
            DisperslError: For various API errors
        """
        request_data = DisperseRequest(
            prompt=prompt,
            model=model,
            agent_name=agent_name,
            context=context,
            task_id=task_id,
            knowledge=knowledge,
            os=os,
            default_dir=default_dir,
            current_dir=current_dir,
            memory=memory,
        )

        # Make streaming request
        response = await self.http.post(
            "/agent/plan",
            json_data=request_data.dict(exclude_none=True),
            headers={"Accept": "application/x-ndjson"},
        )

        # Parse NDJSON stream
        for line in response.text.splitlines():
            if line.strip():
                try:
                    chunk_data = self._parse_ndjson_line(line)
                    yield StandardNdjsonResponse(**chunk_data)
                except Exception as e:
                    logger.warning(f"Failed to parse NDJSON line: {line}, error: {e}")
                    continue

    async def code(
        self,
        prompt: str,
        model: Optional[str] = None,
        context: Optional[str] = None,
        task_id: Optional[str] = None,
        knowledge: Optional[str] = None,
        os: Optional[str] = None,
        default_dir: Optional[str] = None,
        current_dir: Optional[str] = None,
        mcp: Optional[dict[str, Any]] = None,
    ) -> Generator[StandardNdjsonResponse, None, None]:
        """
        Async code generation with agentic flow and tool execution.

        Generates and builds code based on the provided prompt.

        Args:
            prompt: Build prompt
            model: AI model to use
            context: Additional context
            task_id: Task ID
            knowledge: Knowledge sources
            os: Operating system
            default_dir: Default directory
            current_dir: Current directory
            mcp: MCP configuration

        Yields:
            StandardNdjsonResponse: Streaming response chunks

        Raises:
            DisperslError: For various API errors
        """
        request_data = BuildRequest(
            prompt=prompt,
            model=model,
            context=context,
            task_id=task_id,
            knowledge=knowledge,
            os=os,
            default_dir=default_dir,
            current_dir=current_dir,
            mcp=mcp,
        )

        # Make streaming request
        response = await self.http.post(
            "/agent/code",
            json_data=request_data.dict(exclude_none=True),
            headers={"Accept": "application/x-ndjson"},
        )

        # Parse NDJSON stream
        for line in response.text.splitlines():
            if line.strip():
                try:
                    chunk_data = self._parse_ndjson_line(line)
                    yield StandardNdjsonResponse(**chunk_data)
                except Exception as e:
                    logger.warning(f"Failed to parse NDJSON line: {line}, error: {e}")
                    continue

    async def test(
        self,
        prompt: str,
        model: Optional[str] = None,
        context: Optional[str] = None,
        task_id: Optional[str] = None,
        knowledge: Optional[str] = None,
        os: Optional[str] = None,
        default_dir: Optional[str] = None,
        current_dir: Optional[str] = None,
        mcp: Optional[dict[str, Any]] = None,
    ) -> Generator[StandardNdjsonResponse, None, None]:
        """
        Async test generation with agentic flow and tool execution.

        Generates and builds tests based on the provided prompt.

        Args:
            prompt: Build prompt
            model: AI model to use
            context: Additional context
            task_id: Task ID
            knowledge: Knowledge sources
            os: Operating system
            default_dir: Default directory
            current_dir: Current directory
            mcp: MCP configuration

        Yields:
            StandardNdjsonResponse: Streaming response chunks

        Raises:
            DisperslError: For various API errors
        """
        request_data = BuildRequest(
            prompt=prompt,
            model=model,
            context=context,
            task_id=task_id,
            knowledge=knowledge,
            os=os,
            default_dir=default_dir,
            current_dir=current_dir,
            mcp=mcp,
        )

        # Make streaming request
        response = await self.http.post(
            "/agent/test",
            json_data=request_data.dict(exclude_none=True),
            headers={"Accept": "application/x-ndjson"},
        )

        # Parse NDJSON stream
        for line in response.text.splitlines():
            if line.strip():
                try:
                    chunk_data = self._parse_ndjson_line(line)
                    yield StandardNdjsonResponse(**chunk_data)
                except Exception as e:
                    logger.warning(f"Failed to parse NDJSON line: {line}, error: {e}")
                    continue

    async def git(
        self,
        prompt: str,
        model: Optional[str] = None,
        context: Optional[str] = None,
        task_id: Optional[str] = None,
        knowledge: Optional[str] = None,
        os: Optional[str] = None,
        default_dir: Optional[str] = None,
        current_dir: Optional[str] = None,
        mcp: Optional[dict[str, Any]] = None,
    ) -> Generator[StandardNdjsonResponse, None, None]:
        """
        Async Git versioning with agentic flow and tool execution.

        Handles Git versioning operations.

        Args:
            prompt: Build prompt
            model: AI model to use
            context: Additional context
            task_id: Task ID
            knowledge: Knowledge sources
            os: Operating system
            default_dir: Default directory
            current_dir: Current directory
            mcp: MCP configuration

        Yields:
            StandardNdjsonResponse: Streaming response chunks

        Raises:
            DisperslError: For various API errors
        """
        request_data = BuildRequest(
            prompt=prompt,
            model=model,
            context=context,
            task_id=task_id,
            knowledge=knowledge,
            os=os,
            default_dir=default_dir,
            current_dir=current_dir,
            mcp=mcp,
        )

        # Make streaming request
        response = await self.http.post(
            "/agent/git",
            json_data=request_data.dict(exclude_none=True),
            headers={"Accept": "application/x-ndjson"},
        )

        # Parse NDJSON stream
        for line in response.text.splitlines():
            if line.strip():
                try:
                    chunk_data = self._parse_ndjson_line(line)
                    yield StandardNdjsonResponse(**chunk_data)
                except Exception as e:
                    logger.warning(f"Failed to parse NDJSON line: {line}, error: {e}")
                    continue

    async def document_repo(
        self,
        url: str,
        branch: str,
        model: Optional[str] = None,
        team_access: Optional[bool] = None,
        task_id: Optional[str] = None,
    ) -> Generator[StandardNdjsonResponse, None, None]:
        """
        Async generate end to end documentation for a repository.

        Generates documentation for a repository with agentic flow
        and tool execution.

        Args:
            url: Repository URL
            branch: Git branch
            model: AI model to use
            team_access: Team access
            task_id: Task ID

        Yields:
            StandardNdjsonResponse: Streaming response chunks

        Raises:
            DisperslError: For various API errors
        """
        request_data = RepoDocsRequest(
            url=url,
            branch=branch,
            model=model,
            team_access=team_access,
            task_id=task_id,
        )

        # Make streaming request
        response = await self.http.post(
            "/agent/document/repo",
            json_data=request_data.dict(exclude_none=True),
            headers={"Accept": "application/x-ndjson"},
        )

        # Parse NDJSON stream
        for line in response.text.splitlines():
            if line.strip():
                try:
                    chunk_data = self._parse_ndjson_line(line)
                    yield StandardNdjsonResponse(**chunk_data)
                except Exception as e:
                    logger.warning(f"Failed to parse NDJSON line: {line}, error: {e}")
                    continue

    def _parse_ndjson_line(self, line: str) -> dict[str, Any]:
        """
        Parse a single NDJSON line.

        Args:
            line: NDJSON line to parse

        Returns:
            Parsed data as dictionary

        Raises:
            ValueError: If line is not valid JSON
        """
        import json

        return json.loads(line)
