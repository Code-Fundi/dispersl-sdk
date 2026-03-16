"""Backward-compatible local example for the current API surface.

For more complete scenarios, see the root examples:
- examples/py/plan_handover_loop.py
- examples/py/single_agent_completion.py
"""

import asyncio

from dispersl import AgenticExecutor, AsyncDisperslClient


async def main() -> None:
    client = AsyncDisperslClient(
        base_url="https://api.dispersl.com/v1",
        api_key="YOUR_API_KEY",
    )
    executor = AgenticExecutor(client)
    out = await executor.run_plan_and_agent_loop(
        prompt="Plan and execute a production migration.",
        agent_choices="auto",
    )
    print(out["task_id"], len(out["events"]))
    await client.aclose()


if __name__ == "__main__":
    asyncio.run(main())
