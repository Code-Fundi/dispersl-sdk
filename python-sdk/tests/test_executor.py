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
        handover_args = '{"agent_name":"code","prompt":"go"}'
        handover_args_escaped = handover_args.replace('"', '\\"')
        processing_line = (
            '{"status":"processing","message":"Tool calls",'
            '"tools":[{"function":{"name":"handover_task",'
            f'"arguments":"{handover_args_escaped}"}}]}\n'
        )
        return _FakeResponse(
            [
                processing_line,
                '{"status":"complete","message":"done"}\n',
            ]
        )

    async def agent(self, _body):
        processing_line = (
            '{"status":"processing","message":"Tool calls",'
            '"tools":[{"function":{"name":"end_session",'
            '"arguments":"{}"}}]}\n'
        )
        return _FakeResponse(
            [
                processing_line,
                '{"status":"complete","message":"done"}\n',
            ]
        )


@pytest.mark.asyncio
async def test_executor_loop() -> None:
    async def tool_exec(tool):
        return ToolResult(
            tool_name=tool["function"]["name"],
            status="success",
            output=tool["function"]["arguments"],
        )

    executor = AgenticExecutor(_FakeClient(), tool_exec)
    out = await executor.run_plan_and_agent_loop(prompt="Build SDK", agent_choices=["code"])
    assert out["task_id"]
    assert len(out["events"]) > 0
    assert any(t["tool_name"] == "end_session" for t in out["tool_results"])
