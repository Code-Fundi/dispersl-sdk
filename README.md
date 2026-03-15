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

A comprehensive collection of production-grade SDKs for the Dispersl API [Dispersl](https://dispersl.com).

> Flexible Workflow Automation with Plug-and-Play Agents. Dispersl helps you create flexible workflow automations powered by teams of AI, giving you intelligent and flexible automations with no-code workflows.

---



## Overview

Production monorepo for official Dispersl SDKs:

- `typescript-sdk` (Node.js 18+)
- `python-sdk` (Python 3.9+)

This implementation follows `DISPERSL_SDK_FULL IMPLEMENTATION.md` and includes:

- full support for the current production API surface,
- robust timeout/retry and typed error mapping,
- NDJSON streaming parser with split-buffer safety,
- handover parsing and executor loop semantics,
- MCP config loading + runtime custom tool registry,
- CI/release workflows for both SDKs.

## Current API Coverage

The SDKs currently target the updated API with these endpoint groups:

- agent execution:
  - `POST /agent/plan`
  - `POST /agent/completion`
  
- custom agent lifecycle:
  - `GET /agents`
  - `POST /agents/create`
  - `POST /agents/edit/{id}`
  - `GET /agents/{id}`
  - `DELETE /agents/{id}`

Plan endpoint agent choices are fully supported as:

- `"auto"` for automatic custom-agent selection
- array/list of explicit custom-agent `name_id` values

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
  agentChoices: ["auto"]
});
```

Python:

```python
from dispersl import AgenticExecutor, AsyncDisperslClient

client = AsyncDisperslClient(base_url="https://api.dispersl.com/v1", api_key="")
executor = AgenticExecutor(client)

result = await executor.run_plan_and_agent_loop(
    prompt="Plan and execute migration",
    agent_choices=["auto"],
)
```

## Direct Completion Loop (Single Agent)

Both SDKs support direct looping against `POST /agent/completion` for a single agent by `name_id` until `end_session`.

TypeScript:

```ts
const out = await executor.runAgentCompletionLoop({
  nameId: "architect",
  prompt: "Review backend architecture and propose hardening steps",
});
```

Python:

```python
out = await executor.run_agent_completion_loop(
    name_id="architect",
    prompt="Review backend architecture and propose hardening steps",
)
```

## Quickstart Examples

Multiple real-world quickstarts are available in root `examples/`:

- TypeScript: `examples/ts`
- Python: `examples/py`

Coverage includes:

- plan -> handover -> completion multi-agent flow
- direct single-agent completion loop
- task insight/progress continuation using `task_id`
- lifecycle CRUD and agent stats inspection
- MCP custom-tool orchestration with plan + completion flows

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
│   ├── release_check.sh
├── examples/
│   ├── README.md
│   ├── ts/
│   └── py/
├── package.json
├── pnpm-workspace.yaml
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

## Monorepo Release Scripts (pnpm)

Root release scripts read versions directly from:

- `typescript-sdk/package.json`
- `python-sdk/pyproject.toml`

They enforce semver format, check local/remote tag collisions, and create immutable annotated tags:

- `ts-v<typescript-sdk.version>`
- `py-v<python-sdk.version>`

Commands:

```bash
# Print resolved versions + tags
pnpm release:versions

# Create local tags only
pnpm release:tag:ts
pnpm release:tag:py
pnpm release:tag:all

# Create and push tags to origin (triggers release workflows)
pnpm release:deploy:ts
pnpm release:deploy:py
pnpm release:deploy:all
```

This is the standard semver release pattern used in high-scale teams:

- package manifests are the source of truth for versioning
- tags are immutable release artifacts
- CI/CD is tag-driven for deterministic deploys

## Package Names

- TypeScript: `@codefundi/dispersl-sdk`
- Python: `dispersl-sdk`