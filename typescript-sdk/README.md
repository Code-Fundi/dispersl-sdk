# Dispersl TypeScript SDK

Production TypeScript SDK for the Dispersl API.

## Install

```bash
pnpm add @dispersl/sdk
```

## Quick Start

```ts
import { AgenticExecutor, DisperslClient } from "@dispersl/sdk";

const client = new DisperslClient({
  baseUrl: process.env.DISPERSL_API_URL ?? "https://api.dispersl.com/v1",
  apiKey: process.env.DISPERSL_API_KEY ?? ""
});

const executor = new AgenticExecutor(client);
const result = await executor.runPlanAndAgentLoop({
  prompt: "Plan and implement SDK improvements",
  agentChoices: ["code", "test", "git"]
});

console.log(result.taskId, result.events.length);
```

## Development

```bash
pnpm install
pnpm run lint
pnpm run typecheck
pnpm run test -- --run
pnpm run build
```
