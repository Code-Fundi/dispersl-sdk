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


class _FakeCompletionTextThenEndClient:
    def __init__(self) -> None:
        self.calls = 0
        self.last_prompt = None

    async def agent_completion(self, body):
        self.calls += 1
        self.last_prompt = body.get("prompt")
        if self.calls == 1:
            payload1 = {
                "status": "processing",
                "message": "m",
                "content": "Step 1: do X.",
            }
            payload2 = {
                "status": "complete",
                "message": "done",
                "content": "Step 2: do Y.",
            }
            return _FakeResponse(
                [
                    json.dumps(payload1, separators=(",", ":")) + "\n",
                    json.dumps(payload2, separators=(",", ":")) + "\n",
                ]
            )

        payload = {
            "status": "processing",
            "message": "Tool calls",
            "tools": [{"function": {"name": "end_session", "arguments": "{}"}}],
        }
        processing_line = json.dumps(payload, separators=(",", ":")) + "\n"
        return _FakeResponse([processing_line, '{"status":"complete","message":"turn2"}\n'])


class _FakePlanTextThenHandoverClient:
    def __init__(self) -> None:
        self.plan_calls = 0
        self.last_plan_prompt = None

    async def agent_plan(self, body):
        self.plan_calls += 1
        self.last_plan_prompt = body.get("prompt")
        if self.plan_calls == 1:
            payload1 = {
                "status": "processing",
                "message": "m",
                "content": "Draft plan: A then B.",
            }
            payload2 = {
                "status": "complete",
                "message": "done",
                "content": "Need specialist agent.",
            }
            return _FakeResponse(
                [
                    json.dumps(payload1, separators=(",", ":")) + "\n",
                    json.dumps(payload2, separators=(",", ":")) + "\n",
                ]
            )

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
        return _FakeResponse([processing_line, '{"status":"complete","message":"done"}\n'])

    async def agent_completion(self, _body):
        payload = {
            "status": "processing",
            "message": "Tool calls",
            "tools": [{"function": {"name": "end_session", "arguments": "{}"}}],
        }
        processing_line = json.dumps(payload, separators=(",", ":")) + "\n"
        return _FakeResponse([processing_line, '{"status":"complete","message":"done"}\n'])


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


@pytest.mark.asyncio
async def test_completion_loop_text_only_turn_is_fed_back() -> None:
    async def tool_exec(tool):
        return ToolResult(
            tool_name=tool["function"]["name"],
            status="success",
            output=tool["function"]["arguments"],
        )

    client = _FakeCompletionTextThenEndClient()
    executor = AgenticExecutor(client, tool_exec)
    out = await executor.run_agent_completion_loop(
        name_id="architect",
        prompt="Audit architecture",
    )

    assert out["task_id"]
    assert client.calls == 2
    assert client.last_prompt is not None
    assert "Step 1: do X." in client.last_prompt
    assert "Step 2: do Y." in client.last_prompt
    assert any(t["tool_name"] == "end_session" for t in out["tool_results"])


@pytest.mark.asyncio
async def test_plan_loop_text_only_turn_is_fed_back_and_plan_reinvoked() -> None:
    async def tool_exec(tool):
        return ToolResult(
            tool_name=tool["function"]["name"],
            status="success",
            output=tool["function"]["arguments"],
        )

    client = _FakePlanTextThenHandoverClient()
    executor = AgenticExecutor(client, tool_exec)
    out = await executor.run_plan_and_agent_loop(
        prompt="Build SDK",
        agent_choices=["code"],
    )

    assert out["task_id"]
    assert client.plan_calls == 2
    assert client.last_plan_prompt is not None
    assert "Draft plan: A then B." in client.last_plan_prompt
    assert "Need specialist agent." in client.last_plan_prompt
    assert any(t["tool_name"] == "end_session" for t in out["tool_results"])

@pytest.mark.asyncio
async def test_plan_accepts_auto_agent_choice() -> None:
    class _CapturePlanClient:
        def __init__(self) -> None:
            self.last_body = None

        async def agent_plan(self, body):
            self.last_body = body
            return _FakeResponse(['{"status":"complete","message":"done"}\n'])

    client = _CapturePlanClient()
    executor = AgenticExecutor(client)
    out = await executor.run_plan_and_agent_loop(prompt="Build SDK", agent_choices="auto")
    assert out["task_id"]
    assert client.last_body is not None
    assert client.last_body["agent_choice"] == ["auto"]
