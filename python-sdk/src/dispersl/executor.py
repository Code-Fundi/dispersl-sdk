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

    @staticmethod
    def _normalize_agent_choices(agent_choices: str | list[str]) -> list[str]:
        if agent_choices == "auto":
            return ["auto"]
        if isinstance(agent_choices, str):
            return [agent_choices]
        return agent_choices

    @staticmethod
    def _clean_text(value: Any) -> str | None:
        if not isinstance(value, str):
            return None
        t = value.strip()
        return t if t else None

    @staticmethod
    def _merge_turn_text(parts: list[str]) -> str | None:
        merged = "\n".join([p.strip() for p in parts if isinstance(p, str) and p.strip()])
        return merged if merged else None

    @staticmethod
    def _build_plan_text_continuation_prompt(previous_prompt: str, turn_text: str) -> str:
        return "\n".join(
            [
                "You previously responded with streamed text (no tool calls).",
                f"Previous assignment: {previous_prompt}",
                "Your latest output:",
                turn_text,
                "Continue planning and proceed with the workflow.",
                "If you need to hand over, call handover_task. If done, call end_session.",
            ]
        )

    @staticmethod
    def _build_completion_text_continuation_prompt(
        agent_id: str, previous_prompt: str, turn_text: str
    ) -> str:
        return "\n".join(
            [
                f"You are {agent_id} continuing the same task.",
                f"Previous assignment: {previous_prompt}",
                "Your latest output:",
                turn_text,
                "Continue with the next steps.",
                "If you need tools, call them. If done, call end_session.",
            ]
        )

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
            saw_tools = False
            turn_text_parts: list[str] = []

            async def _lines(response: Any) -> Any:
                async for raw in response.aiter_text():
                    yield raw

            async for chunk in parse_ndjson_stream(_lines(stream_response)):
                events.append(chunk)
                text = self._clean_text(chunk.content) or self._clean_text(chunk.message)
                if text:
                    turn_text_parts.append(text)
                if not chunk.tools:
                    continue
                saw_tools = True
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
                continue

            if not saw_tools:
                merged_text = self._merge_turn_text(turn_text_parts)
                if merged_text:
                    current_prompt = self._build_completion_text_continuation_prompt(
                        name_id, current_prompt, merged_text
                    )
                continue

            if self.tool_executor is None:
                break

        return {
            "task_id": run_task_id,
            "events": [e.model_dump() for e in events],
            "tool_results": [r.__dict__ for r in tool_results],
        }

    async def run_plan_and_agent_loop(
        self,
        prompt: str,
        agent_choices: str | list[str],
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
                        "agent_choice": self._normalize_agent_choices(agent_choices),
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
            saw_tools = False
            turn_text_parts: list[str] = []

            async def _lines(response: Any) -> Any:
                async for raw in response.aiter_text():
                    yield raw

            async for chunk in parse_ndjson_stream(_lines(stream_response)):
                events.append(chunk)
                text = self._clean_text(chunk.content) or self._clean_text(chunk.message)
                if text:
                    turn_text_parts.append(text)
                if not chunk.tools:
                    continue
                saw_tools = True
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
                if not saw_tools:
                    # /agent/plan responded with text-only content and no tools; per spec,
                    # call /agent/plan again with the same parameters to continue.
                    merged_text = self._merge_turn_text(turn_text_parts)
                    if merged_text:
                        current_prompt = self._build_plan_text_continuation_prompt(
                            current_prompt, merged_text
                        )
                    continue
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
                continue

            if not saw_tools:
                merged_text = self._merge_turn_text(turn_text_parts)
                if merged_text:
                    current_prompt = self._build_completion_text_continuation_prompt(
                        current_agent or "agent", current_prompt, merged_text
                    )
                continue

            if self.tool_executor is None:
                break

        return {
            "task_id": run_task_id,
            "events": [e.model_dump() for e in events],
            "tool_results": [r.__dict__ for r in tool_results],
        }
