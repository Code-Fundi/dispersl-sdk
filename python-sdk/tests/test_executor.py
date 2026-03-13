import json

import pytest

from dispersl.executor import AgenticExecutor, ToolResult


class _FakeResponse:
    def __init__(self, lines):
        self._lines = lines

    async def aiter_text(self):
        for line in self._lines:
            yield line


class _FakeClient:
    async def agent_plan(self, _body):
        handover_args = json.dumps({"agent_name": "code", "prompt": "go"})
        payload = {
            "status": "processing",
            "message": "Tool calls",
            "tools": [
                {
                    "function": {
                        "name": "handover_task",
                        "arguments": handover_args,
                    }
                }
            ],
        }
        processing_line = json.dumps(payload, separators=(",", ":")) + "\n"
        return _FakeResponse(
            [
                processing_line,
                '{"status":"complete","message":"done"}\n',
            ]
        )

    async def agent_completion(self, _body):
        payload = {
            "status": "processing",
            "message": "Tool calls",
            "tools": [{"function": {"name": "end_session", "arguments": "{}"}}],
        }
        processing_line = json.dumps(payload, separators=(",", ":")) + "\n"
        return _FakeResponse(
            [
                processing_line,
                '{"status":"complete","message":"done"}\n',
            ]
        )


class _FakeCompletionLoopClient:
    def __init__(self) -> None:
        self.calls = 0

    async def agent_completion(self, _body):
        self.calls += 1
        if self.calls == 1:
            payload = {
                "status": "processing",
                "message": "Tool calls",
                "tools": [{"function": {"name": "read_file", "arguments": '{"path":"README.md"}'}}],
            }
            processing_line = json.dumps(payload, separators=(",", ":")) + "\n"
            return _FakeResponse([processing_line, '{"status":"complete","message":"turn1"}\n'])

        payload = {
            "status": "processing",
            "message": "Tool calls",
            "tools": [{"function": {"name": "end_session", "arguments": "{}"}}],
        }
        processing_line = json.dumps(payload, separators=(",", ":")) + "\n"
        return _FakeResponse([processing_line, '{"status":"complete","message":"turn2"}\n'])


@pytest.mark.asyncio
async def test_executor_loop() -> None:
    async def tool_exec(tool):
        return ToolResult(
            tool_name=tool["function"]["name"],
            status="success",
            output=tool["function"]["arguments"],
        )

    executor = AgenticExecutor(_FakeClient(), tool_exec)
    out = await executor.run_plan_and_agent_loop(
        prompt="Build SDK",
        agent_choices=["code"],
    )
    assert out["task_id"]
    assert len(out["events"]) > 0
    assert any(t["tool_name"] == "end_session" for t in out["tool_results"])


@pytest.mark.asyncio
async def test_direct_agent_completion_loop() -> None:
    async def tool_exec(tool):
        return ToolResult(
            tool_name=tool["function"]["name"],
            status="success",
            output=tool["function"]["arguments"],
        )

    client = _FakeCompletionLoopClient()
    executor = AgenticExecutor(client, tool_exec)
    out = await executor.run_agent_completion_loop(
        name_id="architect",
        prompt="Audit architecture",
    )

    assert out["task_id"]
    assert client.calls == 2
    assert any(t["tool_name"] == "end_session" for t in out["tool_results"])
