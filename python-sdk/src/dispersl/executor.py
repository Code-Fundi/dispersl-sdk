from __future__ import annotations

import json
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from .client import AsyncDisperslClient
from .errors import ToolExecutionError
from .handover import NextAction, next_action_from_tool
from .mcp import MCPConfigLoader, MCPRegistry
from .models import NDJSONChunk
from .ndjson import parse_ndjson_stream


@dataclass
class ToolResult:
    tool_name: str
    status: str
    output: str
    error: str | None = None


ToolExecutorFn = Callable[[dict[str, Any]], Awaitable[ToolResult]]


class AgenticExecutor:
    def __init__(
        self,
        client: AsyncDisperslClient,
        tool_executor: ToolExecutorFn | None = None,
    ) -> None:
        self.client = client
        self.tool_executor = tool_executor
        self.mcp_loader = MCPConfigLoader()
        self.mcp_tools = MCPRegistry()

    async def run_agent_completion_loop(
        self,
        name_id: str,
        prompt: str,
        model: str | None = None,
        task_id: str | None = None,
        mcp_override: dict[str, Any] | None = None,
        max_loops: int = 50,
    ) -> dict[str, Any]:
        run_task_id = task_id or str(uuid.uuid4())
        mcp = self.mcp_loader.merge(self.mcp_loader.load_default(), mcp_override)
        tools = [
            {"name": t.name, "description": t.description, "inputSchema": t.parameters}
            for t in self.mcp_tools.list()
        ]
        events: list[NDJSONChunk] = []
        tool_results: list[ToolResult] = []
        current_prompt = prompt

        for _ in range(max_loops):
            stream_response = await self.client.agent_completion(
                {
                    "name_id": name_id,
                    "prompt": current_prompt,
                    "model": model,
                    "task_id": run_task_id,
                    "mcp": {"version": mcp.version, "servers": mcp.servers, "tools": tools},
                }
            )
            next_action = NextAction(type="none")
            turn_tool_results: list[ToolResult] = []

            async def _lines(response: Any) -> Any:
                async for raw in response.aiter_text():
                    yield raw

            async for chunk in parse_ndjson_stream(_lines(stream_response)):
                events.append(chunk)
                if not chunk.tools:
                    continue
                for tool in chunk.tools:
                    action = next_action_from_tool(tool.model_dump())
                    if action.type != "none":
                        next_action = action
                    if self.tool_executor is None:
                        continue
                    result = await self.tool_executor(tool.model_dump())
                    turn_tool_results.append(result)
                    tool_results.append(result)
                    if result.status != "success":
                        raise ToolExecutionError(
                            f"Tool failed: {result.tool_name} => {result.error}"
                        )

            if next_action.type == "end":
                break

            if turn_tool_results:
                lines = [
                    f"{idx + 1}. {r.tool_name} => {r.status.upper()} => {r.output}"
                    for idx, r in enumerate(turn_tool_results)
                ]
                current_prompt = "\n".join(
                    [
                        f"You are {name_id} continuing the same task.",
                        f"Previous assignment: {current_prompt}",
                        "Tool results:",
                        *lines,
                        (
                            "Continue as the same agent and call end_session when complete. "
                            "Do not hand over to another agent."
                        ),
                    ]
                )
            else:
                break

        return {
            "task_id": run_task_id,
            "events": [e.model_dump() for e in events],
            "tool_results": [r.__dict__ for r in tool_results],
        }

    async def run_plan_and_agent_loop(
        self,
        prompt: str,
        agent_choices: list[str],
        model: str | None = None,
        task_id: str | None = None,
        mcp_override: dict[str, Any] | None = None,
        max_loops: int = 50,
    ) -> dict[str, Any]:
        run_task_id = task_id or str(uuid.uuid4())
        mcp = self.mcp_loader.merge(self.mcp_loader.load_default(), mcp_override)
        tools = [
            {"name": t.name, "description": t.description, "inputSchema": t.parameters}
            for t in self.mcp_tools.list()
        ]
        events: list[NDJSONChunk] = []
        tool_results: list[ToolResult] = []
        step = "plan"
        current_agent: str | None = None
        current_prompt = prompt

        for _ in range(max_loops):
            if step == "plan":
                stream_response = await self.client.agent_plan(
                    {
                        "prompt": current_prompt,
                        "agent_choice": agent_choices,
                        "model": model,
                        "task_id": run_task_id,
                        "mcp": {"version": mcp.version, "servers": mcp.servers, "tools": tools},
                    }
                )
            else:
                stream_response = await self.client.agent_completion(
                    {
                        "name_id": current_agent,
                        "prompt": current_prompt,
                        "model": model,
                        "task_id": run_task_id,
                        "mcp": {"version": mcp.version, "servers": mcp.servers, "tools": tools},
                    }
                )

            next_action = NextAction(type="none")
            turn_tool_results: list[ToolResult] = []

            async def _lines(response: Any) -> Any:
                async for raw in response.aiter_text():
                    yield raw

            async for chunk in parse_ndjson_stream(_lines(stream_response)):
                events.append(chunk)
                if not chunk.tools:
                    continue
                for tool in chunk.tools:
                    action = next_action_from_tool(tool.model_dump())
                    if action.type != "none":
                        next_action = action
                    if self.tool_executor is None:
                        continue
                    result = await self.tool_executor(tool.model_dump())
                    turn_tool_results.append(result)
                    tool_results.append(result)
                    if result.status != "success":
                        raise ToolExecutionError(
                            f"Tool failed: {result.tool_name} => {result.error}"
                        )
                    if tool.function.name == "handover_task":
                        try:
                            payload = json.loads(result.output)
                            action2 = next_action_from_tool({"type": "handover_task", **payload})
                            if action2.type != "none":
                                next_action = action2
                        except Exception:
                            pass

            if next_action.type == "handover" and next_action.to_agent:
                step = "agent"
                current_agent = next_action.to_agent
                current_prompt = next_action.prompt or "Continue with the same task."
                continue

            if next_action.type == "end":
                break

            if step == "plan":
                break

            if turn_tool_results:
                lines = [
                    f"{idx + 1}. {r.tool_name} => {r.status.upper()} => {r.output}"
                    for idx, r in enumerate(turn_tool_results)
                ]
                current_prompt = "\n".join(
                    [
                        f"You are {current_agent or 'agent'} continuing the same task.",
                        f"Previous assignment: {current_prompt}",
                        "Tool results:",
                        *lines,
                        (
                            "Decide next action. Call handover_task if needed, "
                            "otherwise end_session when complete."
                        ),
                    ]
                )
            else:
                break

        return {
            "task_id": run_task_id,
            "events": [e.model_dump() for e in events],
            "tool_results": [r.__dict__ for r in tool_results],
        }
