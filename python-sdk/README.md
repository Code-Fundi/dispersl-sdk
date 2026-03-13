# Dispersl Python SDK

Production Python SDK for the Dispersl API.

## Install

```bash
pip install dispersl-sdk
```

## Quick Start

```python
import asyncio

from dispersl import AgenticExecutor, AsyncDisperslClient


async def main() -> None:
    client = AsyncDisperslClient(
        base_url="https://api.dispersl.com/v1",
        api_key=""
    )
    executor = AgenticExecutor(client)
    out = await executor.run_plan_and_agent_loop(
        prompt="Plan and implement SDK improvements",
        agent_choices=["code", "test", "git"]
    )
    print(out["task_id"], len(out["events"]))
    await client.aclose()


asyncio.run(main())
```

## Development

```bash
python -m pip install -e ".[dev]"
ruff check src tests
ruff format --check src tests
mypy src
pytest -q
python -m build
```
