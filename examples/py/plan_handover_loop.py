import asyncio

from dispersl import AgenticExecutor, AsyncDisperslClient, ToolResult


async def tool_runner(tool: dict) -> ToolResult:
    name = tool["function"]["name"]
    if name in {"end_session", "finish_task"}:
        return ToolResult(tool_name=name, status="success", output="{}")
    return ToolResult(
        tool_name=name,
        status="success",
        output=tool["function"]["arguments"],
    )


async def main() -> None:
    client = AsyncDisperslClient(
        base_url="https://api.dispersl.com/v1",
        api_key="YOUR_API_KEY",
    )
    executor = AgenticExecutor(client, tool_runner)
    out = await executor.run_plan_and_agent_loop(
        prompt="Design and implement an audit-ready API release workflow.",
        agent_choices="auto",
        max_loops=50,
    )
    print({"task_id": out["task_id"], "events": len(out["events"]), "tools": len(out["tool_results"])})
    await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
