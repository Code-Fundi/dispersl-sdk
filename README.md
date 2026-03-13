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

# Dispersl API SDKs

A comprehensive collection of production-grade SDKs for the Dispersl API  [Dispersl]("https://dispersl.com"), The AI Dev Team, to give you multi-agents that work together to build software.

> Built for modern AI-driven development, with support for multiple LLM models, multi-agent planning, and full SDLC automation.

---



## Overview

Production monorepo for official Dispersl SDKs:

- `typescript-sdk` (Node.js 18+)
- `python-sdk` (Python 3.9+)

This implementation follows `DISPERSL_SDK_FULL IMPLEMENTATION.md` and includes:

- full route matrix support,
- robust timeout/retry and typed error mapping,
- NDJSON streaming parser with split-buffer safety,
- handover parsing and executor loop semantics,
- MCP config loading + runtime custom tool registry,
- CI/release workflows for both SDKs.

## Customizable Agent Choices

Agent selection is runtime-configurable. The plan/executor flow does **not**
assume fixed `code/test/git/docs` agents. You pass any compatible list in
`agent_choice` / `agentChoices`, and handovers drive subsequent turns.

TypeScript:

```ts
import { AgenticExecutor, DisperslClient } from "@codefundi/dispersl-sdk";

const client = new DisperslClient({
  baseUrl: process.env.DISPERSL_API_URL ?? "https://api.dispersl.com/v1",
  apiKey: process.env.DISPERSL_API_KEY ?? ""
});

const executor = new AgenticExecutor(client);
await executor.runPlanAndAgentLoop({
  prompt: "Plan and execute migration",
  agentChoices: ["architect", "implementer", "validator", "release-manager"]
});
```

Python:

```python
from dispersl import AgenticExecutor, AsyncDisperslClient

client = AsyncDisperslClient(base_url="https://api.dispersl.com/v1", api_key="")
executor = AgenticExecutor(client)

result = await executor.run_plan_and_agent_loop(
    prompt="Plan and execute migration",
    agent_choices=["architect", "implementer", "validator", "release-manager"],
)
```

## Repo Layout

```text
dispersl-sdk/
├── API-DOCS.yaml
├── DISPERSL_SDK_FULL IMPLEMENTATION.md
├── .github/workflows/
│   ├── ci.yml
│   ├── release-typescript.yml
│   └── release-python.yml
├── scripts/
│   ├── verify.sh
│   └── release_check.sh
├── typescript-sdk/
│   ├── package.json
│   ├── README.md
│   ├── src/
│   ├── tests/
│   └── examples/
└── python-sdk/
    ├── pyproject.toml
    ├── README.md
    ├── src/dispersl/
    └── tests/
```

## Local Verification

TypeScript:

```bash
cd typescript-sdk
pnpm install
pnpm run lint
pnpm run typecheck
pnpm run test -- --run
pnpm run build
```

Python:

```bash
cd python-sdk
python -m pip install -e ".[dev]"
python -m ruff check src tests
python -m ruff format --check src tests
python -m mypy src
python -m pytest -q
python -m build
```

## Package Names

- TypeScript: `@codefundi/dispersl-sdk`
- Python: `dispersl-sdk`