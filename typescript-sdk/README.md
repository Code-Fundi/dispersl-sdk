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

<h2 align="center">Dispersl TypeScript SDK</h2>
<p align="center">Flexible workflow automation with plug-and-play agents for TypeScript.</p>

## Install

```bash
pnpm add @codefundi/dispersl-sdk
```

## Requirements

- Node.js `>=18`
- TypeScript `>=5` (recommended for best type support)

## Quick Start

```ts
import { AgenticExecutor, DisperslClient } from "@codefundi/dispersl-sdk";

const client = new DisperslClient({
  baseUrl: process.env.DISPERSL_API_URL ?? "https://api.dispersl.com/v1",
  apiKey: process.env.DISPERSL_API_KEY ?? "",
  timeoutMs: 120_000,
  retryAttempts: 3
});

const executor = new AgenticExecutor(client);
const result = await executor.runPlanAndAgentLoop({
  prompt: "Plan and implement a production webhook pipeline",
  agentChoices: ["auto"]
});

console.log(result.taskId, result.events.length, result.toolResults.length);
```

## SDK Capabilities

- Typed HTTP client with bearer auth, timeout, retry, and status-to-error mapping.
- Full endpoint coverage for `agent/completion`, `agent/plan`, and agent lifecycle APIs.
- Incremental NDJSON stream parser with split-buffer handling and parse errors.
- Handover parser supporting nested and double-serialized tool arguments.
- MCP config loading from `.dispersl/mcp.json` with env interpolation and runtime overrides.
- Agentic execution loop with plan-to-agent transitions, tool execution, and end-session detection.

## Client API Surface

### Agent execution endpoints

| Method | Request | Endpoint | Returns |
| --- | --- | --- | --- |
| `executeAgentCompletion` | `AgentCompletionRequest` | `POST /agent/completion` | `ReadableStream<Uint8Array>` |
| `executePlan` | `AgentPlanRequest` | `POST /agent/plan` | `ReadableStream<Uint8Array>` |

### Resource endpoints

| Domain | Method | Endpoint |
| --- | --- | --- |
| Agents | `getAgents` | `GET /agents?limit&nextToken` |
| Agents | `createAgent` | `POST /agents/create` |
| Agents | `editAgent` | `POST /agents/edit/{id}` |
| Agents | `getAgent` | `GET /agents/{id}` |
| Agents | `deleteAgent` | `DELETE /agents/{id}` |

## Execution Loop Behavior

`AgenticExecutor.runPlanAndAgentLoop` provides:

- start state: `plan`
- max loop guard (`maxLoops`, default `50`)
- handover handling (`handover_task`)
- explicit completion handling (`end_session` and `finish_task`)
- continuation prompts when tools run without explicit handover/end
- optional tool execution callback via `ToolExecutorFn`

### Direct Single-Agent Completion Loop

Use `runAgentCompletionLoop` to execute `POST /agent/completion` directly for one `name_id` until `end_session`.

```ts
const executor = new AgenticExecutor(client);
const result = await executor.runAgentCompletionLoop({
  nameId: "architect",
  prompt: "Review this backend design and produce a migration plan",
  maxLoops: 50
});
```

Behavior:

- fixed agent identity across turns (`nameId`)
- no handover transition to other agents
- continues until `end_session`, no tool calls, or `maxLoops` reached

## Core Types

| Type | Purpose |
| --- | --- |
| `DisperslConfig` | client init config (`baseUrl`, `apiKey`, timeout, retries) |
| `AgentCompletionRequest` | completion request (`name_id` + base fields) |
| `AgentRequestBase` | common fields for agent endpoints |
| `AgentPlanRequest` | plan request (`agent_choice` + base fields) |
| `AgentCreateRequest` | create payload (`name`, `prompt`, optional metadata) |
| `AgentEditRequest` | editable lifecycle fields (`name`, `prompt`, `model`, `active`, ...) |
| `NDJSONChunk` | stream chunk payload format |
| `ToolCall` | tool invocation structure from stream chunks |
| `PaginatedResponse<T>` | list endpoints with pagination envelope |

## Error Model

| Error | Trigger |
| --- | --- |
| `AuthenticationError` | `401` or `403` |
| `NotFoundError` | `404` |
| `ConflictError` | `409` |
| `RateLimitError` | `429` |
| `ValidationError` | other `4xx` |
| `ServerError` | `5xx` |
| `TimeoutError` | request timeout/abort |
| `StreamParseError` | NDJSON line/tail parse failure |
| `ToolExecutionError` | tool callback returns error status |
| `HandoverError` | handover contract failure (reserved class) |

## MCP Support

`McpConfigLoader` and `McpRegistry` support:

- loading `.dispersl/mcp.json`
- `${ENV_VAR}` interpolation
- merge of local config with runtime overrides
- runtime custom tool registration:
  - `register(tool)`
  - `unregister(name)`
  - `list()`

## Development

```bash
pnpm install
pnpm run lint
pnpm run typecheck
pnpm run test -- --run
pnpm run build
```

## Release

- Package name: `@codefundi/dispersl-sdk`
- TS release workflow: `.github/workflows/release-typescript.yml`
- Trigger: push tag `ts-v*`
