<p align="center">
 <img width="300px" src="https://github.com/Code-Fundi/.github/blob/main/media/dispersl/banner-light.png?raw=true" align="center" alt="Dispersl MCP Server" />
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
  <a href="https://smithery.ai/server/@code-fundi/dispersl-mcp">
    <img src="https://smithery.ai/badge/@code-fundi/dispersl-mcp" />
  </a>
<br />
</p>


<!-- [![繁體中文](https://img.shields.io/badge/docs-繁體中文-yellow)](./docs/README.zh-TW.md) [![简体中文](https://img.shields.io/badge/docs-简体中文-yellow)](./docs/README.zh-CN.md) [![日本語](https://img.shields.io/badge/docs-日本語-b7003a)](./docs/README.ja.md) [![한국어 문서](https://img.shields.io/badge/docs-한국어-green)](./docs/README.ko.md) [![Documentación en Español](https://img.shields.io/badge/docs-Español-orange)](./docs/README.es.md) [![Documentation en Français](https://img.shields.io/badge/docs-Français-blue)](./docs/README.fr.md) [![Documentação em Português (Brasil)](<https://img.shields.io/badge/docs-Português%20(Brasil)-purple>)](./docs/README.pt-BR.md) [![Documentazione in italiano](https://img.shields.io/badge/docs-Italian-red)](./docs/README.it.md) [![Dokumentasi Bahasa Indonesia](https://img.shields.io/badge/docs-Bahasa%20Indonesia-pink)](./docs/README.id-ID.md) [![Dokumentation auf Deutsch](https://img.shields.io/badge/docs-Deutsch-darkgreen)](./docs/README.de.md) [![Документация на русском языке](https://img.shields.io/badge/docs-Русский-darkblue)](./docs/README.ru.md) [![Українська документація](https://img.shields.io/badge/docs-Українська-lightblue)](./docs/README.uk.md) [![Türkçe Doküman](https://img.shields.io/badge/docs-Türkçe-blue)](./docs/README.tr.md) [![Arabic Documentation](https://img.shields.io/badge/docs-Arabic-white)](./docs/README.ar.md) [![Tiếng Việt](https://img.shields.io/badge/docs-Tiếng%20Việt-red)](./docs/README.vi.md) -->


#

# Dispersl API SDKs

A comprehensive collection of production-grade SDKs for the Dispersl API  [Dispersl]("https://dispersl.com"), The AI Dev Team, to give you multi-agents that work together to build software.

> Built for modern AI-driven development, with support for multiple LLM models, multi-agent planning, and full SDLC automation.

---



## Overview

This monorepo contains official SDKs for the Dispersl API in multiple programming languages:

- **Python SDK** (`python-sdk/`) - Full-featured Python client with async support
- **TypeScript SDK** (`typescript-sdk/`) - Type-safe TypeScript/JavaScript client

## Features

### Core Capabilities
- ✅ **Agentic Workflows**: Multi-agent task orchestration with **true handover** (switches execution between agent endpoints)
- ✅ **MCP Integration**: Automatic loading and passing of MCP tools to supported endpoints
- ✅ **NDJSON Streaming**: Real-time response streaming with tool calls
- ✅ **Session Management**: Maintain conversation history across agent interactions
- ✅ **Tool Execution**: Built-in and custom tool support with validation
- ✅ **Type Safety**: Full type checking (TypeScript) and validation (Pydantic)
- ✅ **Error Handling**: Retry logic with exponential backoff and circuit breakers
- ✅ **Production-Ready**: 100% compatibility with `dispersl-mcp` server

### MCP (Model Context Protocol) Support
The SDKs automatically load MCP server configurations from `.dispersl/mcp.json` and pass tools to supported endpoints:
- `/agent/chat` - Chat with MCP tool access
- `/agent/code` - Code generation with MCP tools
- `/agent/test` - Test generation with MCP tools  
- `/agent/git` - Git operations with MCP tools

#### Custom MCP Tools
You can create custom MCP tools for any external API or service. Both SDKs support adding custom tools programmatically:

**Python Example - Weather API Tool:**
```python
from dispersl import AgenticExecutor, MCPTool
import requests

def get_weather(args):
    city = args.get("city", "London")
    api_key = os.getenv("WEATHER_API_KEY")
    response = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather",
        params={"q": city, "appid": api_key}
    )
    return response.json()

weather_tool = MCPTool(
    name="get_weather",
    description="Get weather information for a city",
    parameters={"city": {"type": "string"}},
    execute=get_weather
)

executor.mcp_tools["get_weather"] = weather_tool
```

**TypeScript Example - GitHub API Tool:**
```typescript
import { MCPTool } from '@dispersl/sdk';

const getGitHubUser = async (args: Record<string, any>) => {
  const response = await fetch(
    `https://api.github.com/users/${args.username}`
  );
  return response.json();
};

const githubTool: MCPTool = {
  name: 'get_github_user',
  description: 'Get GitHub user information',
  parameters: { username: { type: 'string' } },
  execute: getGitHubUser
};

executor.mcpTools.set('get_github_user', githubTool);
```

See [MCP_CONFIGURATION_GUIDE.md](./MCP_CONFIGURATION_GUIDE.md) for complete setup instructions and more examples.

## Project Structure

```
dispersl-sdk/
├── README.md                    # This file
├── .github/
│   └── workflows/
│       ├── python-ci.yml        # Python SDK CI/CD
│       └── typescript-ci.yml    # TypeScript SDK CI/CD
├── python-sdk/
│   ├── README.md
│   ├── pyproject.toml
│   ├── setup.py
│   ├── pytest.ini
│   ├── .pylintrc
│   ├── mypy.ini
│   ├── src/
│   │   └── dispersl/
│   │       ├── __init__.py
│   │       ├── client.py
│   │       ├── auth.py
│   │       ├── http.py
│   │       ├── exceptions.py
│   │       ├── retry.py
│   │       ├── serializers.py
│   │       ├── utils.py
│   │       ├── models/
│   │       └── resources/
│   └── tests/
└── typescript-sdk/
    ├── README.md
    ├── package.json
    ├── tsconfig.json
    ├── jest.config.js
    ├── .eslintrc.json
    ├── src/
    │   ├── index.ts
    │   ├── client.ts
    │   ├── auth.ts
    │   ├── http.ts
    │   ├── exceptions.ts
    │   ├── retry.ts
    │   ├── serializers.ts
    │   ├── utils.ts
    │   ├── models/
    │   └── resources/
    └── tests/
```

## Quick Start

### Python SDK
```bash
cd python-sdk
pip install -e .
```

### TypeScript SDK
```bash
cd typescript-sdk
npm install
npm run build
```

## Development Setup

### Prerequisites
- Python 3.9+
- Node.js 18+
- Git

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/code-fundi/dispersl-sdk.git
cd dispersl-sdk
```

2. Set up Python SDK:
```bash
cd python-sdk
pip install -e .[dev]
pytest
```

3. Set up TypeScript SDK:
```bash
cd typescript-sdk
npm install
npm run test
```

## CI/CD & Deployment

This repository uses GitHub Actions for continuous integration and automated deployment:

### Python CI/CD (`python-ci.yml`)
- **Testing**: Multi-OS (Ubuntu, macOS, Windows) × Multi-Python (3.9-3.12)
- **Quality**: Ruff linting, Mypy type checking, Pylint
- **Coverage**: Automated test coverage with Codecov
- **Deployment**:
  - Test PyPI (develop branch)
  - PyPI (main branch with `[release]` or GitHub Release)

### TypeScript CI/CD (`typescript-ci.yml`)
- **Testing**: Multi-OS (Ubuntu, macOS, Windows) × Multi-Node (18, 20, 21)
- **Quality**: ESLint, TypeScript compiler, Prettier
- **Coverage**: Automated test coverage with Codecov
- **Deployment**:
  - npm with `next` tag (develop branch)
  - npm production (main branch with `[release]` or GitHub Release)

### Pre-commit Hooks
- **Python**: Ruff linting/formatting, Mypy type checking via pre-commit
- **TypeScript**: ESLint, Type checking, Building via Husky

### Dynamic Testing
Both SDKs support testing against different API URLs:
```bash
# Python
DISPERSL_API_URL=http://localhost:3001 pytest

# TypeScript
DISPERSL_API_URL=http://localhost:3001 npm test
```

See [DEPLOYMENT_SETUP_GUIDE.md](./DEPLOYMENT_SETUP_GUIDE.md) for complete setup instructions.

## Versioning Strategy

We follow [Semantic Versioning](https://semver.org/) (SemVer):

- **MAJOR** version for incompatible API changes
- **MINOR** version for backwards-compatible functionality additions
- **PATCH** version for backwards-compatible bug fixes

Both SDKs are versioned independently but maintain API compatibility.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See individual SDK READMEs for language-specific contribution guidelines.

## Documentation

### SDK Documentation
- **Python SDK**: [python-sdk/README.md](./python-sdk/README.md)
- **TypeScript SDK**: [typescript-sdk/README.md](./typescript-sdk/README.md)

### Deployment & CI/CD
- **Deployment Setup Guide**: [DEPLOYMENT_SETUP_GUIDE.md](./DEPLOYMENT_SETUP_GUIDE.md)
- **Deployment Implementation**: [DEPLOYMENT_IMPLEMENTATION_COMPLETE.md](./DEPLOYMENT_IMPLEMENTATION_COMPLETE.md)

### MCP Configuration
- **MCP Configuration Guide**: [MCP_CONFIGURATION_GUIDE.md](./MCP_CONFIGURATION_GUIDE.md)
- **MCP Tools Automatic Passing**: [MCP_TOOLS_AUTOMATIC_PASSING.md](./MCP_TOOLS_AUTOMATIC_PASSING.md)
- **MCP Implementation Complete**: [MCP_TOOLS_IMPLEMENTATION_COMPLETE.md](./MCP_TOOLS_IMPLEMENTATION_COMPLETE.md)

### Implementation Details
- **Implementation Summary**: [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)
- **Production Verification**: [PRODUCTION_VERIFICATION.md](./PRODUCTION_VERIFICATION.md)
- **API Parameters**: [API_PARAMETERS_DOCUMENTATION.md](./API_PARAMETERS_DOCUMENTATION.md)
- **Production Status**: [SDK_PRODUCTION_STATUS.md](./SDK_PRODUCTION_STATUS.md)

### API Specification
- **OpenAPI Specification**: [API-DOCS.yaml](./API-DOCS.yaml)

### Examples
- **Python MCP Tools**: [python-sdk/examples/mcp_tools_usage.py](./python-sdk/examples/mcp_tools_usage.py)
- **TypeScript MCP Tools**: [typescript-sdk/examples/mcp_tools_usage.ts](./typescript-sdk/examples/mcp_tools_usage.ts)
- **Python Agentic Workflow**: [python-sdk/examples/agentic_workflow.py](./python-sdk/examples/agentic_workflow.py)
- **TypeScript Agentic Workflow**: [typescript-sdk/examples/agentic_workflow.ts](./typescript-sdk/examples/agentic_workflow.ts)

## Support

- Documentation: [docs.dispersl.com](https://docs.dispersl.com)
- Issues: [GitHub Issues](https://github.com/code-fundi/dispersl-sdk/issues)
- Community: [Discord](https://discord.gg/dispersl)