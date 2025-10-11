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

# Dispersl TypeScript SDK

Official TypeScript SDK for the Dispersl API [Dispersl]("https://dispersl.com"), The AI Dev Team, to give you multi-agents that work together to build software.

> Built for modern AI-driven development, with support for multiple LLM models, multi-agent planning, and full SDLC automation.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Feature Guides](#feature-guides)
  - [1. Using AI Agents](#1-using-ai-agents)
  - [2. Multi-Agent Handover](#2-multi-agent-handover)
  - [3. MCP Integration](#3-mcp-integration)
  - [4. Multi-LLM Support](#4-multi-llm-support)
  - [5. Session Management](#5-session-management)
  - [6. Task Management](#6-task-management)
  - [7. Streaming Responses](#7-streaming-responses)
- [API Parameters Reference](#api-parameters-reference)
- [Advanced Usage](#advanced-usage)
- [Type Safety](#type-safety)
- [Error Handling](#error-handling)

## Installation

```bash
npm install @dispersl/sdk
# or
yarn add @dispersl/sdk
# or
pnpm add @dispersl/sdk
```

## Quick Start

```typescript
import { Client } from '@dispersl/sdk';

const client = new Client({ apiKey: 'your_api_key' });

// Chat with AI
for await (const chunk of client.agents.chat({ prompt: 'Hello, world!' })) {
  if (chunk.content) {
    console.log(chunk.content);
  }
}

// List available models
const models = await client.models.list();
models.models.forEach(model => {
  console.log(`${model.name}: ${model.description}`);
});

// Create a new task
const task = await client.tasks.create();
console.log(`Created task: ${task.data[0].id}`);
```

---

## Feature Guides

Complete step-by-step guides for setting up and using all SDK features.

### 1. Using AI Agents

The SDK provides six specialized AI agents. Each agent is accessible via `client.agents.*`.

#### 1.1 Chat Agent

**Purpose**: General conversation, Q&A, and code explanations.

```typescript
import { Client } from '@dispersl/sdk';

const client = new Client({ apiKey: process.env.DISPERSL_API_KEY });

// Basic chat
for await (const chunk of client.agents.chat({ 
  prompt: 'Explain how TypeScript interfaces work' 
})) {
  if (chunk.content) process.stdout.write(chunk.content);
}

// Chat with project context
for await (const chunk of client.agents.chat({
  prompt: 'How can I improve the performance of this module?',
  context: ['src/auth.ts', 'src/middleware/rate-limiter.ts'],
  memory: true,  // Remember conversation
  default_dir: '/path/to/project',
  current_dir: '/path/to/project/src'
})) {
  if (chunk.content) process.stdout.write(chunk.content);
  if (chunk.status === 'complete') {
    console.log(`\nTokens: ${chunk.metadata?.tokens}`);
  }
}
```

#### 1.2 Code Agent

**Purpose**: Generate, modify, and refactor code files.

```typescript
// Generate new code
for await (const chunk of client.agents.code({
  prompt: 'Create a User interface with id, email, and createdAt fields',
  default_dir: '/path/to/project',
  current_dir: '/path/to/project/src/types',
  context: ['src/database.ts']
})) {
  if (chunk.content) process.stdout.write(chunk.content);
  
  // See what files are being created/modified
  if (chunk.tools) {
    chunk.tools.forEach(tool => {
      console.log(`\n[Tool] ${tool.function?.name}`);
    });
  }
}

// Refactor existing code
for await (const chunk of client.agents.code({
  prompt: 'Convert this Express app to use Fastify',
  default_dir: '/path/to/project',
  current_dir: '/path/to/project/src',
  context: ['src/app.ts', 'src/routes/*.ts']
})) {
  if (chunk.content) process.stdout.write(chunk.content);
}
```

#### 1.3 Test Agent

**Purpose**: Generate comprehensive test suites.

```typescript
// Generate unit tests
for await (const chunk of client.agents.test({
  prompt: 'Create Jest tests for the authentication service',
  default_dir: '/path/to/project',
  current_dir: '/path/to/project/tests',
  context: ['src/auth/service.ts', 'src/auth/utils.ts']
})) {
  if (chunk.content) process.stdout.write(chunk.content);
}

// Generate integration tests
for await (const chunk of client.agents.test({
  prompt: 'Create E2E tests for user registration flow',
  default_dir: '/path/to/project',
  current_dir: '/path/to/project/tests/e2e',
  context: ['src/api/routes/auth.ts']
})) {
  if (chunk.content) process.stdout.write(chunk.content);
}
```

#### 1.4 Git Agent

**Purpose**: Version control operations.

```typescript
// Simple git operations
for await (const chunk of client.agents.git({
  prompt: "Create branch 'feature/user-auth' and commit all changes",
  default_dir: '/path/to/project',
  current_dir: '/path/to/project'
})) {
  if (chunk.content) process.stdout.write(chunk.content);
}

// Complex git workflow
for await (const chunk of client.agents.git({
  prompt: `
    1. Check git status
    2. Create hotfix/security branch
    3. Stage modified files
    4. Commit with message 'Fix: Auth vulnerability'
    5. Push to origin
  `,
  default_dir: '/path/to/project',
  current_dir: '/path/to/project'
})) {
  if (chunk.content) process.stdout.write(chunk.content);
}
```

#### 1.5 Plan Agent

**Purpose**: Orchestrate multiple agents for complex tasks.

```typescript
// Multi-agent workflow
for await (const chunk of client.agents.plan({
  prompt: 'Build user authentication with JWT, tests, and documentation',
  agent_choice: ['code', 'test', 'git'],
  default_dir: '/path/to/project',
  current_dir: '/path/to/project'
})) {
  if (chunk.content) process.stdout.write(chunk.content);
  
  // Track agent handovers
  if (chunk.tools) {
    chunk.tools.forEach(tool => {
      if (tool.function?.name === 'handover_task') {
        const args = JSON.parse(tool.function.arguments || '{}');
        console.log(`\n🔄 Handover → ${args.agent_name} agent`);
      }
    });
  }
}
```

#### 1.6 Documentation Agent

**Purpose**: Generate repository documentation.

```typescript
// Document a GitHub repository
for await (const chunk of client.agents.documentRepo({
  url: 'https://github.com/username/repo',
  branch: 'main',
  team_access: true
})) {
  if (chunk.content) process.stdout.write(chunk.content);
  if (chunk.status === 'complete') {
    console.log('\n✓ Documentation complete');
    console.log(`Files processed: ${chunk.metadata?.filesProcessed}`);
  }
}
```

---

### 2. Multi-Agent Handover

**Handover enables agents to transfer tasks seamlessly**. The SDK automatically switches execution between agent endpoints.

#### 2.1 Setup

```typescript
import { Client, AgenticExecutor } from '@dispersl/sdk';

const client = new Client({ apiKey: process.env.DISPERSL_API_KEY });
const executor = new AgenticExecutor(client.http);

// Create session for state tracking
const sessionId = executor.createSession();
```

#### 2.2 Basic Handover

```typescript
// Plan agent will hand off to code and test agents
for await (const response of executor.executeAgenticWorkflow(
  '/agent/plan',
  {
    prompt: 'Build auth system with tests',
    agent_choice: ['code', 'test', 'git'],
    default_dir: '/path/to/project',
    current_dir: '/path/to/project'
  },
  sessionId,
  20  // max iterations
)) {
  if (response.content) process.stdout.write(response.content);
  
  // Detect handovers
  if (response.tools) {
    response.tools.forEach(tool => {
      if (tool.function?.name === 'handover_task') {
        const args = JSON.parse(tool.function.arguments || '{}');
        console.log(`\n${'='.repeat(60)}`);
        console.log(`🔄 HANDOVER: ${args.agent_name} agent`);
        console.log(`Task: ${args.prompt}`);
        console.log('='.repeat(60));
      }
    });
  }
}

executor.endSession(sessionId);
```

#### 2.3 Custom Handover Workflow

```typescript
async function buildFeatureWithHandover(feature: string) {
  const executor = new AgenticExecutor(client.http);
  const sessionId = executor.createSession();
  const agentsUsed: string[] = [];
  
  console.log(`🚀 Building: ${feature}\n`);
  
  try {
    for await (const response of executor.executeAgenticWorkflow(
      '/agent/plan',
      {
        prompt: `Build: ${feature}`,
        agent_choice: ['code', 'test', 'git'],
        default_dir: '/path/to/project',
        current_dir: '/path/to/project'
      },
      sessionId,
      30
    )) {
      if (response.content) process.stdout.write(response.content);
      
      if (response.tools) {
        response.tools.forEach(tool => {
          if (tool.function?.name === 'handover_task') {
            const args = JSON.parse(tool.function.arguments || '{}');
            if (!agentsUsed.includes(args.agent_name)) {
              agentsUsed.push(args.agent_name);
            }
            console.log(`\n→ ${args.agent_name} agent...`);
          }
        });
      }
    }
    
    console.log(`\n\n✓ Complete! Agents used: ${agentsUsed.join(', ')}`);
  } finally {
    executor.endSession(sessionId);
  }
}

await buildFeatureWithHandover('User authentication with OAuth');
```

---

### 3. MCP Integration

**MCP (Model Context Protocol) connects external tools to agents.**

#### 3.1 Quick Setup

**Step 1**: Create `.dispersl/mcp.json`:

```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"],
      "env": {}
    }
  }
}
```

**Step 2**: SDK auto-loads MCP tools:

```typescript
// MCP tools automatically available!
const client = new Client({ apiKey: process.env.DISPERSL_API_KEY });

for await (const chunk of client.agents.code({
  prompt: 'Read package.json and analyze dependencies',
  default_dir: '/path/to/project',
  current_dir: '/path/to/project'
})) {
  if (chunk.content) process.stdout.write(chunk.content);
}
// Filesystem MCP tool is automatically used
```

#### 3.2 Common MCP Servers

**GitHub**:
```json
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "token" }
  }
}
```

**PostgreSQL**:
```json
{
  "postgres": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://url"],
    "env": {}
  }
}
```

#### 3.3 Custom MCP Tools

```typescript
import { AgenticExecutor, MCPTool } from '@dispersl/sdk';
import axios from 'axios';

const executor = new AgenticExecutor(client.http);

// Custom weather tool
const getWeather = async (args: Record<string, any>) => {
  const response = await axios.get(
    'https://api.openweathermap.org/data/2.5/weather',
    { params: { q: args.city || 'London', appid: process.env.WEATHER_API_KEY } }
  );
  return {
    city: response.data.name,
    temp: response.data.main.temp,
    description: response.data.weather[0].description
  };
};

const weatherTool: MCPTool = {
  name: 'get_weather',
  description: 'Get current weather for a city',
  parameters: {
    city: { type: 'string', description: 'City name' }
  },
  execute: getWeather
};

executor.mcpTools.set('get_weather', weatherTool);

// Use it
const sessionId = executor.createSession();
for await (const response of executor.executeAgenticWorkflow(
  '/agent/chat',
  { prompt: "What's the weather in Paris?" },
  sessionId,
  5
)) {
  if (response.content) console.log(response.content);
}
```

#### 3.4 Verify MCP Tools

```typescript
const executor = client.agents.executor;

console.log(`MCP Clients: ${executor.mcpClients.size}`);
executor.mcpClients.forEach((config, name) => {
  console.log(`  - ${name}: ${config.command}`);
});

console.log(`\nMCP Tools: ${executor.mcpTools.size}`);
executor.mcpTools.forEach((tool, name) => {
  console.log(`  - ${name}: ${tool.description}`);
});
```

---

### 4. Multi-LLM Support

**Switch models** for different tasks or cost optimization.

#### 4.1 List Models

```typescript
const models = await client.models.list();

console.log('Available Models:');
models.models.forEach(model => {
  console.log(`- ${model.id}: ${model.name}`);
  console.log(`  Context: ${model.context_length.toLocaleString()} tokens`);
  console.log(`  Free: ${model.tier_requirements.free_model}`);
});
```

#### 4.2 Use Different Models

```typescript
// High intelligence task
for await (const chunk of client.agents.chat({
  prompt: 'Design a distributed system architecture',
  model: 'gpt-4-turbo'
})) {
  if (chunk.content) process.stdout.write(chunk.content);
}

// Simple task
for await (const chunk of client.agents.chat({
  prompt: 'Fix typo in README',
  model: 'gpt-3.5-turbo'  // Faster & cheaper
})) {
  if (chunk.content) process.stdout.write(chunk.content);
}
```

#### 4.3 Smart Model Selection

```typescript
function selectModel(complexity: 'low' | 'medium' | 'high', contextSize: number): string {
  if (complexity === 'high' || contextSize > 8000) return 'gpt-4-turbo';
  if (complexity === 'medium') return 'gpt-4';
  return 'gpt-3.5-turbo';
}

const model = selectModel('medium', 3000);
for await (const chunk of client.agents.code({
  prompt: 'Add error handling to this module',
  model,
  context: ['src/api.ts'],
  default_dir: '/path/to/project',
  current_dir: '/path/to/project/src'
})) {
  if (chunk.content) process.stdout.write(chunk.content);
}
```

---

### 5. Session Management

**Sessions preserve conversation history** across multiple calls.

#### 5.1 Basic Session

```typescript
import { AgenticExecutor } from '@dispersl/sdk';

const executor = new AgenticExecutor(client.http);
const sessionId = executor.createSession();

// Multiple calls with shared context
for (let i = 0; i < 3; i++) {
  for await (const response of executor.executeAgenticWorkflow(
    '/agent/chat',
    { prompt: `Question ${i+1}: Continue the previous discussion`, task_id: sessionId },
    sessionId,
    5
  )) {
    if (response.content) process.stdout.write(response.content);
  }
  console.log('\n' + '='.repeat(60) + '\n');
}

// Check session state
const session = executor.getSession(sessionId);
console.log(`Messages: ${session.conversation_history.length}`);

executor.endSession(sessionId);
```

#### 5.2 Custom Session ID

```typescript
const userId = 'user_12345';
const sessionId = executor.createSession(`session_${userId}`);
// Resume later with same ID
```

#### 5.3 Auto-Cleanup

```typescript
async function withSession(task: string) {
  const executor = new AgenticExecutor(client.http);
  const sessionId = executor.createSession();
  
  try {
    for await (const response of executor.executeAgenticWorkflow(
      '/agent/chat',
      { prompt: task },
      sessionId,
      10
    )) {
      if (response.content) process.stdout.write(response.content);
    }
    return executor.getSession(sessionId);
  } finally {
    executor.endSession(sessionId);
  }
}

const result = await withSession('Explain design patterns');
console.log(`\nInteractions: ${result.conversation_history.length}`);
```

---

### 6. Task Management

**Track long-running tasks** through the API.

#### 6.1 Create & Track

```typescript
// Create task
const task = await client.tasks.create();
const taskId = task.data[0].id;
console.log(`Task ID: ${taskId}`);

// Check status
const taskData = await client.tasks.getById(taskId);
console.log(`Status: ${taskData.data[0].status}`);

// List all tasks
const allTasks = await client.tasks.list();
allTasks.data.forEach(t => {
  console.log(`${t.id}: ${t.name} - ${t.status}`);
});
```

#### 6.2 Update Tasks

```typescript
// Update task
await client.tasks.edit(taskId, {
  name: 'User Authentication Implementation',
  status: 'in-progress'
});

// Mark complete
await client.tasks.edit(taskId, { status: 'completed' });
```

#### 6.3 Task Steps

```typescript
// Get steps
const steps = await client.steps.getByTaskId(taskId);
steps.data.forEach(step => {
  console.log(`Step ${step.id}: ${step.name} - ${step.status}`);
});

// Get specific step
const step = await client.steps.getById(steps.data[0].id);
console.log(`Details: ${step.data[0].name}`);
```

#### 6.4 Task History

```typescript
const history = await client.history.getTaskHistory(taskId, { limit: 10 });
history.data.forEach(entry => {
  console.log(`${entry.timestamp}: ${entry.event}`);
  console.log(`  ${entry.details}`);
});
```

---

### 7. Streaming Responses

**Real-time response processing.**

#### 7.1 Basic Streaming

```typescript
for await (const chunk of client.agents.chat({ 
  prompt: 'Write a comprehensive guide to TypeScript' 
})) {
  if (chunk.status === 'processing') {
    if (chunk.content) process.stdout.write(chunk.content);
  } else if (chunk.status === 'complete') {
    console.log(`\n✓ Tokens: ${chunk.metadata?.tokens}`);
  } else if (chunk.status === 'error') {
    console.log(`\n✗ Error: ${chunk.error?.message}`);
  }
}
```

#### 7.2 Monitor Tools

```typescript
for await (const chunk of client.agents.code({
  prompt: 'Create a REST API with multiple endpoints',
  default_dir: '/path/to/project',
  current_dir: '/path/to/project/src'
})) {
  if (chunk.content) process.stdout.write(chunk.content);
  
  if (chunk.tools) {
    console.log(`\n[${chunk.tools.length} tool calls]`);
    chunk.tools.forEach(tool => {
      console.log(`  - ${tool.function?.name}`);
    });
  }
  
  if (chunk.status === 'complete') {
    console.log('\n✓ Complete');
    if (chunk.metadata) {
      console.log(`Tokens: ${chunk.metadata.tokens}`);
      console.log(`Cost: $${chunk.metadata.cost?.toFixed(4)}`);
    }
  }
}
```

#### 7.3 Advanced Progress

```typescript
async function streamWithProgress(prompt: string, agent: any) {
  const start = Date.now();
  let chars = 0;
  let tools = 0;
  
  console.log('🚀 Starting...');
  console.log('='.repeat(60));
  
  for await (const chunk of agent({ prompt })) {
    if (chunk.content) {
      process.stdout.write(chunk.content);
      chars += chunk.content.length;
    }
    
    if (chunk.tools) {
      tools += chunk.tools.length;
      process.stdout.write(`\n[+${chunk.tools.length} tools]`);
    }
    
    if (chunk.status === 'complete') {
      const duration = (Date.now() - start) / 1000;
      console.log(`\n${'='.repeat(60)}`);
      console.log(`✓ Complete in ${duration.toFixed(2)}s`);
      console.log(`Content: ${chars} chars, Tools: ${tools}`);
      if (chunk.metadata) console.log(`Tokens: ${chunk.metadata.tokens}`);
    }
  }
}

await streamWithProgress('Create user documentation', client.agents.chat);
```

---

## API Parameters Reference

All agentic endpoints accept request parameters as documented below. Parameters marked as **Required** must be provided.

### Chat Agent (`/agent/chat`)
Interact with AI for codebase insights, task progress, and documentation.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | ✅ **Required** | The chat prompt or question |
| `model` | string | Optional | Override default model (e.g., "gpt-4", "claude-3") |
| `context` | string[] | Optional | Additional context strings for the conversation |
| `memory` | boolean | Optional | Enable conversation memory across requests |
| `voice` | boolean | Optional | Enable voice response generation |
| `task_id` | string | Optional | Session/task ID for continuity |
| `knowledge` | string[] | Optional | Knowledge base IDs to reference |
| `os` | string | Optional | Operating system context (e.g., "linux", "darwin", "win32") |
| `default_dir` | string | Optional | Project root directory path |
| `current_dir` | string | Optional | Current working subdirectory |
| `mcp` | object | Optional | MCP tools configuration |

**Example:**
```typescript
for await (const chunk of client.agents.chat({
  prompt: "Explain the authentication system",
  model: "gpt-4",
  context: ["src/auth.ts", "src/middleware.ts"],
  memory: true,
  default_dir: "/path/to/project",
  current_dir: "/path/to/project/src"
})) {
  if (chunk.content) {
    process.stdout.write(chunk.content);
  }
}
```

### Plan Agent (`/agent/plan`)
Multi-agent task distribution following SDLC principles.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | ✅ **Required** | Task description for planning |
| `agent_choice` | string[] | ✅ **Required** | Agents to use: ['code', 'test', 'git', 'docs'] |
| `default_dir` | string | ✅ **Required** | Project root directory |
| `current_dir` | string | ✅ **Required** | Current working directory |
| `model` | string | Optional | Override default planning model |
| `context` | string[] | Optional | Additional context for planning |
| `task_id` | string | Optional | Session ID for task continuity |
| `knowledge` | string[] | Optional | Knowledge base references |
| `memory` | boolean | Optional | Enable memory across planning sessions |
| `mcp` | object | Optional | MCP tools configuration |

**Example:**
```typescript
for await (const chunk of client.agents.plan({
  prompt: "Build a REST API with authentication",
  agent_choice: ["code", "test", "git"],
  default_dir: "/path/to/project",
  current_dir: "/path/to/project"
})) {
  if (chunk.content) {
    process.stdout.write(chunk.content);
  }
}
```

### Code Agent (`/agent/code`)
Generate and build code with agentic flow and tool execution.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | ✅ **Required** | Code generation prompt |
| `default_dir` | string | ✅ **Required** | Project root directory |
| `current_dir` | string | ✅ **Required** | Target subdirectory for code |
| `model` | string | Optional | Override default code model |
| `context` | string[] | Optional | Existing code context |
| `task_id` | string | Optional | Session ID |
| `knowledge` | string[] | Optional | Knowledge base references |
| `mcp` | object | Optional | MCP tools for file operations |

**Example:**
```typescript
for await (const chunk of client.agents.code({
  prompt: "Create a User model with email and password fields",
  default_dir: "/path/to/project",
  current_dir: "/path/to/project/src/models",
  context: ["src/database.ts"]
})) {
  if (chunk.content) {
    process.stdout.write(chunk.content);
  }
}
```

### Test Agent (`/agent/test`)
Generate end-to-end tests with agentic flow.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | ✅ **Required** | Test generation prompt |
| `default_dir` | string | ✅ **Required** | Project root directory |
| `current_dir` | string | ✅ **Required** | Test directory path |
| `model` | string | Optional | Override default test model |
| `context` | string[] | Optional | Code to test context |
| `task_id` | string | Optional | Session ID |
| `knowledge` | string[] | Optional | Knowledge base references |
| `mcp` | object | Optional | MCP tools for test execution |

**Example:**
```typescript
for await (const chunk of client.agents.test({
  prompt: "Generate tests for the User authentication flow",
  default_dir: "/path/to/project",
  current_dir: "/path/to/project/tests",
  context: ["src/auth.ts", "src/models/user.ts"]
})) {
  if (chunk.content) {
    process.stdout.write(chunk.content);
  }
}
```

### Git Agent (`/agent/git`)
Git versioning operations with agentic flow.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | ✅ **Required** | Git operation prompt |
| `default_dir` | string | ✅ **Required** | Repository root directory |
| `current_dir` | string | ✅ **Required** | Working directory |
| `model` | string | Optional | Override default git model |
| `context` | string[] | Optional | Repository context |
| `task_id` | string | Optional | Session ID |
| `knowledge` | string[] | Optional | Knowledge base references |
| `mcp` | object | Optional | MCP tools for git commands |

**Example:**
```typescript
for await (const chunk of client.agents.git({
  prompt: "Create a feature branch and commit the new auth module",
  default_dir: "/path/to/project",
  current_dir: "/path/to/project"
})) {
  if (chunk.content) {
    process.stdout.write(chunk.content);
  }
}
```

### Documentation Agent (`/agent/document/repo`)
Generate repository documentation with agentic flow.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | ✅ **Required** | Repository URL |
| `branch` | string | ✅ **Required** | Branch to document (e.g., "main") |
| `model` | string | Optional | Override default docs model |
| `team_access` | boolean | Optional | Enable team collaboration features |
| `task_id` | string | Optional | Session ID |
| `context` | string[] | Optional | Additional documentation context |
| `knowledge` | string[] | Optional | Knowledge base references |
| `mcp` | object | Optional | MCP tools configuration |

**Example:**
```typescript
for await (const chunk of client.agents.documentRepo({
  url: "https://github.com/user/repo",
  branch: "main",
  team_access: true
})) {
  if (chunk.content) {
    process.stdout.write(chunk.content);
  }
}
```

## Authentication

### API Key
```typescript
const client = new Client({ apiKey: 'sk_test_...' });
```

### Environment Variables
```bash
export DISPERSL_API_KEY="sk_test_..."
```
```typescript
const client = new Client(); // Automatically uses DISPERSL_API_KEY env var
```

## Configuration

### Timeouts
```typescript
const client = new Client({
  apiKey: '...',
  timeout: 30000, // milliseconds
  connectTimeout: 10000
});
```

### Retries
```typescript
const client = new Client({
  apiKey: '...',
  maxRetries: 3,
  backoffFactor: 2.0
});
```

### Custom Base URL
```typescript
const client = new Client({
  apiKey: '...',
  baseURL: 'https://api.staging.dispersl.com/v1'
});
```

## Error Handling

```typescript
import {
  AuthenticationError,
  RateLimitError,
  ServerError
} from '@dispersl/sdk';

try {
  const response = await client.agents.chat({ prompt: 'Hello' });
} catch (error) {
  if (error instanceof AuthenticationError) {
    console.log(`Auth failed: ${error.message}`);
  } else if (error instanceof RateLimitError) {
    console.log(`Rate limited. Retry after: ${error.retryAfter}`);
  } else if (error instanceof ServerError) {
    console.log(`Server error: ${error.statusCode}`);
  }
}
```

## Agentic Workflows

The SDK provides powerful agentic workflow capabilities with support for handover, tool execution, and MCP client integration.

### Basic Agentic Execution

```typescript
import { Client, AgenticExecutor } from '@dispersl/sdk';

const client = new Client({ apiKey: 'your_api_key' });
const executor = new AgenticExecutor(client.http);

// Create a session
const sessionId = executor.createSession();

// Execute an agentic workflow
const requestData = {
  prompt: 'Create a TypeScript script to analyze JSON data',
  context: { projectType: 'data_analysis' }
};

for await (const response of executor.executeAgenticWorkflow(
  '/agent/code',
  requestData,
  sessionId,
  10
)) {
  console.log(`Response: ${response.content}`);
  if (response.status === 'completed') {
    break;
  }
}

// Clean up
executor.endSession(sessionId);
```

### MCP Client Integration

```typescript
import { AgenticExecutor, MCPClient, MCPTool } from '@dispersl/sdk';

const executor = new AgenticExecutor(client.http);

// Add an MCP client
const mcpClient: MCPClient = {
  name: 'file-operations',
  command: 'node',
  args: ['file-ops-server.js'],
  env: { NODE_ENV: 'production' }
};
executor.addMCPClient(mcpClient);

// Define a custom tool
const customTool = (args: Record<string, any>): string => {
  const filename = args.filename || 'default.txt';
  const content = args.content || '';
  return `Created ${filename} with content: ${content}`;
};

const mcpTool: MCPTool = {
  name: 'create_file',
  description: 'Create a file with specified content',
  parameters: {
    filename: { type: 'string' },
    content: { type: 'string' }
  },
  execute: customTool
};

// Add the tool to the executor
executor.mcpTools.set('create_file', mcpTool);
```

### Handover Between Agents

```typescript
// Handover ACTUALLY switches execution to a different agent endpoint
// When an agent calls handover_task, the SDK:
// 1. Detects the handover tool call
// 2. Changes the endpoint to the target agent's endpoint
// 3. Creates a new request with the handover prompt
// 4. Continues execution at the NEW agent endpoint
// 5. Preserves session state throughout

for await (const response of executor.executeAgenticWorkflow(
  '/agent/plan',
  { prompt: 'Plan and implement a web scraper' },
  sessionId,
  20,
  (msg) => console.log(`Progress: ${msg}`)
)) {
  if (response.tools) {
    for (const tool of response.tools) {
      if (tool.function?.name === 'handover_task') {
        const args = JSON.parse(tool.function.arguments || '{}');
        console.log(`🔄 Handing over to ${args.agent_name} agent`);
        console.log(`   New task: ${args.prompt}`);
      }
    }
  }
}

// Handover example: plan agent → code agent → test agent → git agent
// Each agent hands off when it completes its specialized task
```

### Session Management

```typescript
// Create a session with custom ID
const sessionId = executor.createSession('my-custom-session-id');

// Get session information
const session = executor.getSession(sessionId);
if (session) {
  console.log(`Conversation history: ${session.conversation_history.length} entries`);
  console.log(`Tool responses: ${session.tool_responses.length} responses`);
}

// End session
executor.endSession(sessionId);
```

### Parsing Text-Based Tool Calls

```typescript
const text = `
<｜tool▁call▁begin｜>function<｜tool▁sep｜>write_to_file
json
{"path": "example.ts", "content": "console.log('Hello');"}
<｜tool▁call▁end｜>
`;

const toolCalls = executor.parseTextToolCalls(text);
for (const toolCall of toolCalls) {
  console.log(`Tool: ${toolCall.function.name}`);
  console.log(`Args: ${toolCall.function.arguments}`);
}
```

### Creating Custom MCP Tools

You can create custom MCP tools for external APIs like weather services:

#### Example: Weather API Tool

```typescript
import axios from 'axios';
import { AgenticExecutor, MCPTool } from '@dispersl/sdk';

const executor = new AgenticExecutor(client.http);

// Define custom weather tool
const getWeather = async (args: Record<string, any>): Promise<any> => {
  const city = args.city || 'London';
  const apiKey = process.env.WEATHER_API_KEY; // Store API keys securely!
  
  try {
    const response = await axios.get(
      'https://api.openweathermap.org/data/2.5/weather',
      {
        params: { q: city, appid: apiKey, units: 'metric' }
      }
    );
    
    const data = response.data;
    return {
      city: data.name,
      temperature: data.main.temp,
      description: data.weather[0].description,
      humidity: data.main.humidity
    };
  } catch (error) {
    return { error: error.message };
  }
};

// Create MCP tool definition
const weatherTool: MCPTool = {
  name: 'get_weather',
  description: 'Get current weather information for a city',
  parameters: {
    city: {
      type: 'string',
      description: "City name (e.g., 'London', 'New York')"
    }
  },
  execute: getWeather
};

// Add tool to executor
executor.mcpTools.set('get_weather', weatherTool);

// Use in workflow
for await (const response of executor.executeAgenticWorkflow(
  '/agent/chat',
  { prompt: "What's the weather like in Paris?" },
  sessionId,
  5
)) {
  if (response.content) {
    console.log(response.content);
  }
}
```

#### Example: Database Query Tool

```typescript
import { Pool } from 'pg';
import { MCPTool } from '@dispersl/sdk';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL
});

const queryDatabase = async (args: Record<string, any>): Promise<any> => {
  const queryType = args.query_type || 'users';
  
  try {
    if (queryType === 'users') {
      const result = await pool.query(
        'SELECT id, name, email FROM users LIMIT 10'
      );
      return {
        users: result.rows.map(row => ({
          id: row.id,
          name: row.name,
          email: row.email
        }))
      };
    } else if (queryType === 'count') {
      const result = await pool.query('SELECT COUNT(*) FROM users');
      return { count: parseInt(result.rows[0].count) };
    } else {
      return { error: 'Unknown query type' };
    }
  } catch (error) {
    return { error: error.message };
  }
};

// Create tool
const dbTool: MCPTool = {
  name: 'query_database',
  description: 'Query the user database',
  parameters: {
    query_type: {
      type: 'string',
      enum: ['users', 'count'],
      description: 'Type of query to execute'
    }
  },
  execute: queryDatabase
};

executor.mcpTools.set('query_database', dbTool);
```

#### Example: REST API Integration

```typescript
import { MCPTool } from '@dispersl/sdk';

// GitHub API tool
const getGitHubUser = async (args: Record<string, any>): Promise<any> => {
  const username = args.username;
  const token = process.env.GITHUB_TOKEN;
  
  try {
    const response = await fetch(`https://api.github.com/users/${username}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Accept': 'application/vnd.github.v3+json'
      }
    });
    
    if (!response.ok) {
      return { error: `GitHub API error: ${response.statusText}` };
    }
    
    const data = await response.json();
    return {
      username: data.login,
      name: data.name,
      bio: data.bio,
      public_repos: data.public_repos,
      followers: data.followers
    };
  } catch (error) {
    return { error: error.message };
  }
};

const githubTool: MCPTool = {
  name: 'get_github_user',
  description: 'Get GitHub user information',
  parameters: {
    username: {
      type: 'string',
      description: 'GitHub username'
    }
  },
  execute: getGitHubUser
};

executor.mcpTools.set('get_github_user', githubTool);
```

#### Best Practices for Custom Tools

1. **Security**:
   - Never hardcode API keys - use environment variables
   - Validate and sanitize all inputs
   - Use allowlists for allowed operations
   - Implement rate limiting

2. **Error Handling**:
   - Always wrap tool execution in try-catch blocks
   - Return structured error responses
   - Log errors for debugging

3. **Type Safety**:
   - Use TypeScript types for tool parameters
   - Validate input types at runtime
   - Document expected return types

4. **Async Operations**:
   - Use async/await for asynchronous operations
   - Handle promise rejections properly
   - Implement timeouts for long-running operations

5. **Testing**:
   - Test tools independently before integration
   - Mock external APIs in tests
   - Validate response formats

## Advanced Usage

### Streaming Responses
```typescript
// Chat with streaming
for await (const chunk of client.agents.chat({ prompt: 'Explain quantum computing' })) {
  if (chunk.status === 'processing' && chunk.content) {
    process.stdout.write(chunk.content);
  } else if (chunk.status === 'complete') {
    console.log(`\nCompleted. Tokens used: ${chunk.metadata?.tokens}`);
  }
}

// Code generation with streaming
for await (const chunk of client.agents.code({ prompt: 'Create a TypeScript calculator' })) {
  if (chunk.tools) {
    chunk.tools.forEach(tool => {
      console.log(`Tool call: ${tool.function.name}`);
    });
  }
}
```

### Type Safety
This SDK is fully typed with TypeScript:

```typescript
import { ChatRequest, StandardNdjsonResponse } from '@dispersl/sdk';

// Full IntelliSense support
const request: ChatRequest = {
  prompt: 'Hello',
  model: 'gpt-4',
  memory: true
};

for await (const chunk of client.agents.chat(request)) {
  // chunk is fully typed as StandardNdjsonResponse
  if (chunk.content) {
    console.log(chunk.content);
  }
}
```

### Custom Headers
```typescript
const response = await client.models.list(
  undefined,
  { 'X-Custom-Header': 'value' }
);
```

## API Reference

### Agents
- `client.agents.chat(request)` - Chat with AI
- `client.agents.plan(request)` - Multi-agent task dispersion
- `client.agents.code(request)` - Code generation
- `client.agents.test(request)` - Test generation
- `client.agents.git(request)` - Git operations
- `client.agents.documentRepo(request)` - Repository documentation

### Models
- `client.models.list()` - List available models

### Authentication
- `client.auth.getKeys()` - Get API keys
- `client.auth.generateNewKey(request)` - Generate new API key

### Tasks
- `client.tasks.create()` - Create new task
- `client.tasks.list()` - List all tasks
- `client.tasks.getById(id)` - Get task by ID
- `client.tasks.edit(id, request)` - Edit task
- `client.tasks.cancel(id)` - Cancel task

### Steps
- `client.steps.getById(id)` - Get step by ID
- `client.steps.getByTaskId(taskId)` - Get steps by task ID
- `client.steps.cancel(id)` - Cancel step

### History
- `client.history.getTaskHistory(taskId, request?)` - Get task history
- `client.history.getStepHistory(stepId, request?)` - Get step history

## Testing

Run tests locally:
```bash
# Install dependencies
npm install

# Run all tests
npm test

# Run with coverage
npm run test:coverage

# Run specific test categories
npm test -- --testNamePattern="unit"
npm test -- --testNamePattern="integration"
npm test -- --testNamePattern="e2e"
```

## Development

```bash
# Install dependencies
npm install

# Build the project
npm run build

# Run linting
npm run lint

# Run type checking
npm run type-check

# Watch mode for development
npm run dev
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Install dependencies (`npm install`)
4. Make your changes
5. Run tests (`npm test`)
6. Run linting (`npm run lint`)
7. Run type checking (`npm run type-check`)
8. Commit your changes (`git commit -m 'Add amazing feature'`)
9. Push to the branch (`git push origin feature/amazing-feature`)
10. Open a Pull Request

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- Documentation: [docs.dispersl.com](https://docs.dispersl.com)
- Issues: [GitHub Issues](https://github.com/code-fundi/dispersl-sdk/issues)
- Community: [Discord](https://discord.gg/dispersl)
