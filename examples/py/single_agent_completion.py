import asyncio

from dispersl import AgenticExecutor, AsyncDisperslClient, ToolResult


async def tool_runner(tool: dict) -> ToolResult:
    return ToolResult(
        tool_name=tool["function"]["name"],
        status="success",
        output=tool["function"]["arguments"],
    )


async def main() -> None:
    client = AsyncDisperslClient(
        base_url="https://api.dispersl.com/v1",
        api_key="YOUR_API_KEY",
    )
    executor = AgenticExecutor(client, tool_runner)
    out = await executor.run_agent_completion_loop(
        name_id="architect",
        prompt="Review backend resilience and produce concrete hardening actions.",
        max_loops=50,
    )
    print({"task_id": out["task_id"], "events": len(out["events"]), "tools": len(out["tool_results"])})
    await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
