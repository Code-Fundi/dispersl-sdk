import asyncio
import json

from dispersl import AgenticExecutor, AsyncDisperslClient, MCPTool, ToolResult


async def tool_runner(tool: dict) -> ToolResult:
    name = tool["function"]["name"]
    if name == "get_release_calendar":
        output = json.dumps({"freeze_date": "2026-04-15", "release_date": "2026-04-22"})
        return ToolResult(tool_name=name, status="success", output=output)
    return ToolResult(tool_name=name, status="success", output=tool["function"]["arguments"])


async def main() -> None:
    client = AsyncDisperslClient(
        base_url="https://api.dispersl.com/v1",
        api_key="YOUR_API_KEY",
    )
    executor = AgenticExecutor(client, tool_runner)

    executor.mcp_tools.register(
        MCPTool(
            name="get_release_calendar",
            description="Return release calendar dates for planning and rollout.",
            parameters={"type": "object", "properties": {}, "required": []},
            execute=lambda _args: {"freeze_date": "2026-04-15", "release_date": "2026-04-22"},
        )
    )

    # Plan does not require MCP tools. Use auto to discover the right team.
    planned = await executor.run_plan_and_agent_loop(
        prompt="Create a release plan for onboarding automation in regulated environments.",
        agent_choices="auto",
    )
    print("Planned task:", planned["task_id"])

    # Completion run can use MCP-backed custom tools with a specific custom agent.
    completed = await executor.run_agent_completion_loop(
        name_id="release-manager",
        prompt="Finalize release checklist with custom tool data.",
    )
    print("Completion events:", len(completed["events"]))
    await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
