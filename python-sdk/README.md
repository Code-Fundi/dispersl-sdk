<p align="center">
 <img width="300px" src="https://github.com/Code-Fundi/.github/blob/main/media/dispersl/banner-light.png?raw=true" align="center" alt="Dispersl Multi-Agent SDK" />
</p>
</p>

<p align="center">
  <a href="https://discord.gg/6RJTWCuWZj">
    <img src="https://img.shields.io/badge/Discord-7289DA?logo=discord&logoColor=white" />
  </a>
  <a href="https://x.com/disperslHQ">
    <img src="https://img.shields.io/badge/X/Twitter-808080?logo=x&logoColor=white" />
  </a>
  <a href="https://www.tiktok.com/@codefundi">
    <img src="https://img.shields.io/badge/TikTok-000000?logo=tiktok&logoColor=white" />
  </a>
  <a href="https://dispersl.com">
    <img src="https://img.shields.io/badge/Website-dispersl.com-blue" />
  </a>
<br />
</p>

#

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
