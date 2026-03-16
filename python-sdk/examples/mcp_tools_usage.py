"""MCP example aligned to /agent/plan and /agent/completion endpoints.

For complete MCP workflows, see: examples/py/mcp_custom_agent_flow.py
"""

import asyncio

from dispersl import AgenticExecutor, AsyncDisperslClient, MCPTool


async def main() -> None:
    client = AsyncDisperslClient(
        base_url="https://api.dispersl.com/v1",
        api_key="YOUR_API_KEY",
    )
    executor = AgenticExecutor(client)

    executor.mcp_tools.register(
        MCPTool(
            name="get_env",
            description="Return environment profile",
            parameters={"type": "object", "properties": {}, "required": []},
            execute=lambda _args: {"env": "prod", "region": "us-east-1"},
        )
    )

    # Plan step (agent choices can be "auto" or explicit name_ids list).
    await executor.run_plan_and_agent_loop(
        prompt="Plan rollout strategy for zero-downtime migration.",
        agent_choices="auto",
    )

    # Completion step with a specific custom agent.
    out = await executor.run_agent_completion_loop(
        name_id="release-manager",
        prompt="Finalize migration checklist using available MCP tools.",
    )
    print(out["task_id"], len(out["events"]))
    await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
