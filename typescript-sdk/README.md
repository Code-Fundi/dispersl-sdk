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

# Dispersl TypeScript SDK

Production TypeScript SDK for the Dispersl API.

## Install

```bash
pnpm add @codefundi/dispersl-sdk
```

## Quick Start

```ts
import { AgenticExecutor, DisperslClient } from "@codefundi/dispersl-sdk";

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
