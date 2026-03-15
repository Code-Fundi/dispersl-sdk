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

<h2 align="center">Dispersl Python SDK</h2>
<p align="center">Flexible workflow automation with plug-and-play agents for Python.</p>

## Install

```bash
pip install dispersl-sdk
```

## Requirements

- Python `>=3.9`
- Async runtime (`asyncio`)

## Quick Start

```python
import asyncio

from dispersl import AgenticExecutor, AsyncDisperslClient


async def main() -> None:
    client = AsyncDisperslClient(
        base_url="https://api.dispersl.com/v1",
        api_key="YOUR_API_KEY",
        timeout_s=120.0,
        retry_attempts=3,
    )

    executor = AgenticExecutor(client)
    out = await executor.run_plan_and_agent_loop(
        prompt="Plan and implement a production webhook pipeline",
        agent_choices="auto",  # or ["architect", "security-auditor", "release-manager"]
    )

    print(out["task_id"], len(out["events"]), len(out["tool_results"]))
    await client.aclose()


asyncio.run(main())
```

## SDK Capabilities

- Async HTTP client with retries, timeout support, and structured error mapping.
- Full endpoint coverage for `agent/completion`, `agent/plan`, and agent lifecycle APIs.
- NDJSON async stream parsing for long-running multi-agent responses.
- Handover extraction for `handover_task`, `end_session`, and `finish_task` semantics.
- MCP config and runtime tool registry support for custom tool execution.
- Agentic loop orchestration with continuation prompts and max-loop safety.

## Client API Surface

### Agent execution endpoints

| Method | Request | Endpoint |
| --- | --- | --- |
| `agent_completion` | `dict[str, Any]` | `POST /agent/completion` |
| `agent_plan` | `dict[str, Any]` | `POST /agent/plan` |

### Agent plan choices

`agent_plan` accepts:

- `"auto"` for automatic custom-agent selection
- `list[str]` for explicit custom agent `name_id` values

When `"auto"` is passed, the SDK normalizes the request payload to `["auto"]` for API compatibility.

### Resource endpoints

| Domain | Method | Endpoint |
| --- | --- | --- |
| Agents | `agents(limit=20, next_token=None)` | `GET /agents?limit&nextToken` |
| Agents | `agents_create(body)` | `POST /agents/create` |
| Agents | `agents_edit(agent_id, body)` | `POST /agents/edit/{id}` |
| Agents | `agent_by_id(agent_id)` | `GET /agents/{agent_id}` |
| Agents | `agent_delete(agent_id)` | `DELETE /agents/{agent_id}` |

### Agent lifecycle fields and stats

`agents()` returns paginated data with:

- pagination: `limit`, `hasNext`, `hasPrev`, `nextToken`, `prevToken`
- per-agent lifecycle + stats fields such as `stars_count`, `clone_count`, and `created_at`

`agent_by_id()` returns richer lifecycle fields:

- `public`, `active`, `updated_at`

Create/edit request payload support:

- create: `name`, `prompt`, optional `description`, `model`, `category`, `public`
- edit: optional `name`, `prompt`, `description`, `model`, `category`, `public`, `active`

## Execution Loop Behavior

`AgenticExecutor.run_plan_and_agent_loop` includes:

- plan-first execution and automatic transition to selected specialist agent
- handover propagation across turns
- end detection using `end_session` and `finish_task`
- optional custom tool runner (`tool_executor`)
- deterministic termination with `max_loops`
- returned payload:
  - `task_id`
  - `events` (parsed NDJSON chunks)
  - `tool_results` (custom tool execution outcomes)

### Direct Single-Agent Completion Loop

Use `run_agent_completion_loop` to execute `POST /agent/completion` directly for one `name_id` until `end_session`.

```python
executor = AgenticExecutor(client)
result = await executor.run_agent_completion_loop(
    name_id="architect",
    prompt="Review this backend design and produce a migration plan",
    max_loops=50,
)
```

Behavior:

- fixed agent identity across turns (`name_id`)
- no handover transition to other agents
- continues until `end_session`, no tool calls, or `max_loops` reached

## Core Models and Helpers

| Component | Purpose |
| --- | --- |
| `NDJSONChunk` | typed stream chunk structure |
| `ToolCall` and `ToolFunction` | tool invocation envelope |
| `PaginationInfo` | cursor pagination metadata |
| `MCPConfigLoader` | load and merge MCP config |
| `MCPRegistry` | runtime MCP tool registration |
| `parse_ndjson_stream` | robust async NDJSON parser |

## Error Model

| Error | Trigger |
| --- | --- |
| `AuthenticationError` | auth failures |
| `NotFoundError` | `404` |
| `ConflictError` | `409` |
| `RateLimitError` | `429` |
| `ValidationError` | invalid request payload |
| `ServerError` | upstream `5xx` |
| `RequestTimeoutError` | timeout or deadline exceeded |
| `StreamParseError` | invalid stream payload |
| `ToolExecutionError` | tool callback failed |
| `HandoverError` | malformed handover contract |

## Development

```bash
python -m pip install -e ".[dev]"
python -m ruff check src tests
python -m ruff format --check src tests
python -m mypy src
python -m pytest -q
python -m build
```

## Example Quickstarts

End-to-end quickstarts live in root `examples/py`:

- `examples/py/plan_handover_loop.py`
- `examples/py/single_agent_completion.py`
- `examples/py/task_insight_progress.py`
- `examples/py/agent_lifecycle_and_stats.py`
- `examples/py/mcp_custom_agent_flow.py`

## Release

- Package name: `dispersl-sdk`
- Python release workflow: `.github/workflows/release-python.yml`
- Trigger: push tag `py-v*`
