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

# Dispersl Python SDK

Official Python SDK for the Dispersl API [Dispersl]("https://dispersl.com"), The AI Dev Team, to give you multi-agents that work together to build software.

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
- [Error Handling](#error-handling)

## Installation

### From PyPI (Recommended)
```bash
pip install dispersl-sdk
```

### From Source
```bash
git clone https://github.com/code-fundi/dispersl-sdk.git
cd dispersl-sdk/python-sdk
pip install -e .
```

### Development Installation
```bash
pip install -e .[dev]  # Includes testing and development tools
```

## Quick Start

```python
from dispersl import Client

# Initialize client
client = Client(api_key="your_api_key")

# Chat with AI
for chunk in client.agents.chat(prompt="Hello, world!"):
    if chunk.content:
        print(chunk.content)

# List available models
models = client.models.list()
for model in models.models:
    print(f"{model.name}: {model.description}")

# Create a new task
task = client.tasks.create()
print(f"Created task: {task.data[0].id}")
```

---

## Feature Guides

### 1. Using AI Agents

The SDK provides access to six specialized AI agents, each optimized for specific tasks.

#### 1.1 Chat Agent - General Conversations

**Purpose**: Chat, Q&A, codebase insights, and general assistance.

**Setup**:
```python
from dispersl import Client

client = Client(api_key="your_api_key")
```

**Basic Usage**:
```python
# Simple chat
for chunk in client.agents.chat(prompt="Explain how authentication works"):
    if chunk.content:
        print(chunk.content, end='', flush=True)
```

**With Context and Memory**:
```python
# Chat with code context and memory
for chunk in client.agents.chat(
    prompt="How can I improve the security of this auth module?",
    context=["src/auth.py", "src/middleware/auth_middleware.py"],
    memory=True,  # Remember conversation history
    default_dir="/path/to/project",
    current_dir="/path/to/project/src"
):
    if chunk.content:
        print(chunk.content, end='')
    
    if chunk.status == "complete":
        print(f"\n\nTokens used: {chunk.metadata.tokens}")
```

#### 1.2 Code Agent - Code Generation

**Purpose**: Generate, refactor, and modify code files.

**Setup**:
```python
from dispersl import Client

client = Client(api_key="your_api_key")
```

**Generate New Code**:
```python
# Generate a new Python module
for chunk in client.agents.code(
    prompt="Create a User model with fields: id, email, password_hash, created_at",
    default_dir="/path/to/project",
    current_dir="/path/to/project/src/models",
    context=["src/database.py"]  # Related files for context
):
    if chunk.content:
        print(chunk.content, end='')
    
    # Monitor tool calls (file writes, etc.)
    if chunk.tools:
        for tool in chunk.tools:
            print(f"\n[Tool Call] {tool.function['name']}")
```

**Refactor Existing Code**:
```python
# Refactor code with specific instructions
for chunk in client.agents.code(
    prompt="Refactor the authentication system to use JWT tokens instead of sessions",
    default_dir="/path/to/project",
    current_dir="/path/to/project/src/auth",
    context=["src/auth/session.py", "src/auth/middleware.py"]
):
    if chunk.content:
        print(chunk.content, end='')
```

#### 1.3 Test Agent - Test Generation

**Purpose**: Generate comprehensive test suites.

**Setup & Usage**:
```python
# Generate tests for a module
for chunk in client.agents.test(
    prompt="Generate unit tests for the User authentication flow",
    default_dir="/path/to/project",
    current_dir="/path/to/project/tests",
    context=["src/auth/user.py", "src/auth/login.py"]
):
    if chunk.content:
        print(chunk.content, end='')
    
    if chunk.status == "complete":
        print("\n✓ Tests generated successfully")
```

**Generate Integration Tests**:
```python
# Generate integration tests
for chunk in client.agents.test(
    prompt="Create integration tests for the REST API endpoints",
    default_dir="/path/to/project",
    current_dir="/path/to/project/tests/integration",
    context=["src/api/routes.py", "src/api/handlers.py"]
):
    if chunk.content:
        print(chunk.content, end='')
```

#### 1.4 Git Agent - Version Control

**Purpose**: Git operations, branching, commits, and repository management.

**Setup & Usage**:
```python
# Create feature branch and commit changes
for chunk in client.agents.git(
    prompt="Create a new feature branch 'feature/user-auth' and commit the authentication changes",
    default_dir="/path/to/project",
    current_dir="/path/to/project"
):
    if chunk.content:
        print(chunk.content, end='')
```

**Complex Git Operations**:
```python
# Multiple git operations
for chunk in client.agents.git(
    prompt="""
    1. Check current git status
    2. Create and switch to branch 'hotfix/security-patch'
    3. Stage all modified files
    4. Commit with message 'Fix: Security vulnerability in auth module'
    """,
    default_dir="/path/to/project",
    current_dir="/path/to/project"
):
    if chunk.content:
        print(chunk.content, end='')
```

#### 1.5 Plan Agent - Multi-Agent Orchestration

**Purpose**: Break down complex tasks and orchestrate multiple agents.

**Setup & Usage**:
```python
# Plan and execute a complete feature
for chunk in client.agents.plan(
    prompt="Build a REST API for user authentication with JWT tokens",
    agent_choice=["code", "test", "git"],  # Which agents can be used
    default_dir="/path/to/project",
    current_dir="/path/to/project"
):
    if chunk.content:
        print(chunk.content, end='')
    
    # Monitor agent handovers
    if chunk.tools:
        for tool in chunk.tools:
            if tool.function.get("name") == "handover_task":
                args = json.loads(tool.function.get('arguments', '{}'))
                print(f"\n🔄 Handing over to {args.get('agent_name')} agent")
```

#### 1.6 Documentation Agent - Repo Documentation

**Purpose**: Generate comprehensive documentation for repositories.

**Setup & Usage**:
```python
# Generate documentation for a GitHub repository
for chunk in client.agents.document_repo(
    url="https://github.com/username/repo",
    branch="main",
    team_access=True  # Enable for team collaboration
):
    if chunk.content:
        print(chunk.content, end='')
    
    if chunk.status == "complete":
        print(f"\n✓ Documentation generated")
        print(f"Files processed: {chunk.metadata.filesProcessed}")
```

---

### 2. Multi-Agent Handover

**What is Handover?** Handover allows agents to transfer tasks to other specialized agents seamlessly. When an agent completes its part, it can hand off to another agent - the SDK automatically switches execution to the new agent's endpoint.

#### 2.1 Setup for Handover

**Install & Initialize**:
```python
from dispersl import Client, AgenticExecutor

client = Client(api_key="your_api_key")
executor = AgenticExecutor(client.http)

# Create a session for state management
session_id = executor.create_session()
```

#### 2.2 Basic Handover Example

```python
# Start with plan agent, which will hand off to other agents
for response in executor.execute_agentic_workflow(
    endpoint="/agent/plan",
    request_data={
        "prompt": "Build a user authentication system with tests and git integration",
        "agent_choice": ["code", "test", "git"],
        "default_dir": "/path/to/project",
        "current_dir": "/path/to/project"
    },
    session_id=session_id,
    max_iterations=20
):
    # Display content
    if response.content:
        print(response.content, end='')
    
    # Monitor handovers
    if response.tools:
        for tool in response.tools:
            if tool.function.get("name") == "handover_task":
                args = json.loads(tool.function.get('arguments', '{}'))
                print(f"\n\n{'='*60}")
                print(f"🔄 HANDOVER DETECTED")
                print(f"From: Current agent")
                print(f"To: {args.get('agent_name')} agent")
                print(f"Task: {args.get('prompt')}")
                print(f"{'='*60}\n")
    
    if response.status == "completed":
        print("\n✓ All tasks completed!")
        break

# Clean up
executor.end_session(session_id)
```

#### 2.3 Custom Handover Flow

```python
# Define a custom multi-agent workflow
def build_feature_with_handover(feature_description):
    """Build a complete feature using multiple agents"""
    
    executor = AgenticExecutor(client.http)
    session_id = executor.create_session()
    
    print(f"🚀 Starting feature development: {feature_description}\n")
    
    # Track which agents were used
    agents_used = []
    
    try:
        for response in executor.execute_agentic_workflow(
            endpoint="/agent/plan",
            request_data={
                "prompt": f"Plan and implement: {feature_description}",
                "agent_choice": ["code", "test", "git"],
                "default_dir": "/path/to/project",
                "current_dir": "/path/to/project"
            },
            session_id=session_id,
            max_iterations=30,
            progress_callback=lambda msg: print(f"[Progress] {msg}")
        ):
            if response.content:
                print(response.content, end='')
            
            # Track agent handovers
            if response.tools:
                for tool in response.tools:
                    if tool.function.get("name") == "handover_task":
                        args = json.loads(tool.function.get('arguments', '{}'))
                        agent = args.get('agent_name')
                        if agent not in agents_used:
                            agents_used.append(agent)
                        print(f"\n→ Switching to {agent} agent...")
            
            if response.status == "completed":
                break
        
        # Summary
        print(f"\n\n{'='*60}")
        print("✓ Feature development complete!")
        print(f"Agents used: {', '.join(agents_used)}")
        
        # Get session details
        session = executor.get_session(session_id)
        print(f"Total interactions: {len(session.conversation_history)}")
        print(f"Tools executed: {len(session.tool_responses)}")
        print(f"{'='*60}")
        
    finally:
        executor.end_session(session_id)

# Use it
build_feature_with_handover("User authentication with email and password")
```

#### 2.4 Agent Handover Flow Chart

```
Plan Agent (Orchestrator)
    ↓ handover_task(agent="code", prompt="Generate auth module")
Code Agent (Implementation)
    ↓ handover_task(agent="test", prompt="Test auth module")
Test Agent (Verification)
    ↓ handover_task(agent="git", prompt="Commit auth feature")
Git Agent (Version Control)
    ↓ Complete
```

---

### 3. MCP Integration

**What is MCP?** Model Context Protocol allows you to connect external tools (file systems, databases, APIs) to AI agents.

#### 3.1 Quick Setup

**Step 1: Create MCP Configuration**

Create `.dispersl/mcp.json` in your project:

```bash
mkdir -p .dispersl
cat > .dispersl/mcp.json << 'EOF'
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"],
      "env": {}
    }
  }
}
EOF
```

**Step 2: Use SDK (MCP Auto-Loads)**

```python
from dispersl import Client

# MCP config is automatically loaded!
client = Client(api_key="your_api_key")

# MCP tools are automatically available to agents
for chunk in client.agents.code(
    prompt="Read the package.json file and list all dependencies",
    default_dir="/path/to/project",
    current_dir="/path/to/project"
):
    if chunk.content:
        print(chunk.content, end='')

# The filesystem MCP tool is automatically used by the agent
```

#### 3.2 Common MCP Servers

**Filesystem Server**:
```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"],
    "env": {}
  }
}
```

**GitHub Server**:
```json
{
  "github": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "env": {
      "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here"
    }
  }
}
```

**PostgreSQL Server**:
```json
{
  "postgres": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://connection"],
    "env": {}
  }
}
```

#### 3.3 Custom MCP Tools

Create your own tools for any API:

```python
import requests
from dispersl import AgenticExecutor, MCPTool
import os

# Initialize executor
executor = AgenticExecutor(client.http)

# Custom weather tool
def get_weather(args):
    city = args.get("city", "London")
    api_key = os.getenv("WEATHER_API_KEY")
    
    response = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather",
        params={"q": city, "appid": api_key, "units": "metric"}
    )
    data = response.json()
    
    return {
        "city": data["name"],
        "temperature": data["main"]["temp"],
        "description": data["weather"][0]["description"]
    }

# Register tool
weather_tool = MCPTool(
    name="get_weather",
    description="Get current weather for a city",
    parameters={"city": {"type": "string", "description": "City name"}},
    execute=get_weather
)

executor.mcp_tools["get_weather"] = weather_tool

# Use it
session_id = executor.create_session()
for response in executor.execute_agentic_workflow(
    endpoint="/agent/chat",
    request_data={"prompt": "What's the weather in Paris?"},
    session_id=session_id,
    max_iterations=5
):
    if response.content:
        print(response.content)
```

#### 3.4 Verify MCP Tools Loaded

```python
# Check what MCP tools are available
executor = client.agents.executor

print(f"Loaded MCP clients: {len(executor.mcp_clients)}")
for name, client_config in executor.mcp_clients.items():
    print(f"  - {name}: {client_config.command} {' '.join(client_config.args)}")

print(f"\nLoaded MCP tools: {len(executor.mcp_tools)}")
for tool_name, tool_def in executor.mcp_tools.items():
    print(f"  - {tool_name}: {tool_def['description']}")
```

---

### 4. Multi-LLM Support

**Switch between different AI models** for different tasks or cost optimization.

#### 4.1 List Available Models

```python
from dispersl import Client

client = Client(api_key="your_api_key")

# Get all available models
models = client.models.list()

print("Available Models:")
print(f"{'='*80}")
for model in models.models:
    print(f"ID: {model.id}")
    print(f"Name: {model.name}")
    print(f"Description: {model.description}")
    print(f"Context Length: {model.context_length:,} tokens")
    print(f"Free Model: {model.tier_requirements.free_model}")
    print(f"{'-'*80}")
```

#### 4.2 Use Different Models

**Chat with Different Models**:
```python
# Use GPT-4
for chunk in client.agents.chat(
    prompt="Explain quantum computing",
    model="gpt-4-turbo"
):
    if chunk.content:
        print(chunk.content, end='')

# Use Claude
for chunk in client.agents.chat(
    prompt="Explain quantum computing",
    model="claude-3-opus"
):
    if chunk.content:
        print(chunk.content, end='')

# Use smaller model for simple tasks
for chunk in client.agents.chat(
    prompt="What's 2+2?",
    model="gpt-3.5-turbo"  # Faster and cheaper
):
    if chunk.content:
        print(chunk.content, end='')
```

#### 4.3 Model Selection Strategy

```python
def select_model_for_task(task_complexity, context_size):
    """Intelligently select model based on task requirements"""
    
    if task_complexity == "high" or context_size > 8000:
        return "gpt-4-turbo"  # High intelligence, large context
    elif task_complexity == "medium":
        return "gpt-4"  # Balanced
    else:
        return "gpt-3.5-turbo"  # Fast and economical

# Use it
task = "simple code review"
model = select_model_for_task("low", 2000)

for chunk in client.agents.code(
    prompt="Review this function for bugs",
    model=model,
    context=["src/utils.py"],
    default_dir="/path/to/project",
    current_dir="/path/to/project/src"
):
    if chunk.content:
        print(chunk.content, end='')
```

#### 4.4 Model-Specific Workflows

```python
# Use different models for different agents
def multi_model_workflow():
    """Use optimal models for each agent"""
    
    # Plan with powerful model
    for chunk in client.agents.plan(
        prompt="Design a microservices architecture",
        model="gpt-4-turbo",  # Need strong reasoning
        agent_choice=["code"],
        default_dir="/path/to/project",
        current_dir="/path/to/project"
    ):
        if chunk.content:
            print(chunk.content, end='')
    
    # Code with balanced model
    for chunk in client.agents.code(
        prompt="Implement the API gateway",
        model="gpt-4",  # Good balance
        default_dir="/path/to/project",
        current_dir="/path/to/project/src"
    ):
        if chunk.content:
            print(chunk.content, end='')
    
    # Tests with economical model
    for chunk in client.agents.test(
        prompt="Generate unit tests",
        model="gpt-3.5-turbo",  # Tests don't need highest intelligence
        default_dir="/path/to/project",
        current_dir="/path/to/project/tests"
    ):
        if chunk.content:
            print(chunk.content, end='')

multi_model_workflow()
```

---

### 5. Session Management

**Sessions maintain conversation history and state** across multiple agent interactions.

#### 5.1 Basic Session Usage

```python
from dispersl import AgenticExecutor

executor = AgenticExecutor(client.http)

# Create session
session_id = executor.create_session()
print(f"Session ID: {session_id}")

# Use session across multiple calls
for i in range(3):
    for response in executor.execute_agentic_workflow(
        endpoint="/agent/chat",
        request_data={
            "prompt": f"Question {i+1}: Tell me more about the previous topic",
            "task_id": session_id  # Same session = remembers context
        },
        session_id=session_id,
        max_iterations=5
    ):
        if response.content:
            print(response.content, end='')
    print("\n" + "="*60 + "\n")

# Get session info
session = executor.get_session(session_id)
print(f"Total messages: {len(session.conversation_history)}")

# Clean up
executor.end_session(session_id)
```

#### 5.2 Session with Custom ID

```python
# Use custom session ID (useful for user sessions)
user_id = "user_12345"
session_id = executor.create_session(f"session_{user_id}")

# Now you can resume this session later using the same ID
```

#### 5.3 Session State Management

```python
def managed_session(task_description):
    """Context manager for automatic session cleanup"""
    
    executor = AgenticExecutor(client.http)
    session_id = executor.create_session()
    
    try:
        # Perform work
        for response in executor.execute_agentic_workflow(
            endpoint="/agent/chat",
            request_data={"prompt": task_description},
            session_id=session_id,
            max_iterations=10
        ):
            if response.content:
                print(response.content, end='')
        
        # Get final session state
        session = executor.get_session(session_id)
        return session
        
    finally:
        # Always clean up
        executor.end_session(session_id)
        print("\n✓ Session closed")

# Use it
session_data = managed_session("Explain design patterns")
print(f"\nSession had {len(session_data.conversation_history)} interactions")
```

---

### 6. Task Management

**Track and manage long-running tasks** through the API.

#### 6.1 Create and Track Tasks

```python
from dispersl import Client

client = Client(api_key="your_api_key")

# Create a task
task = client.tasks.create()
task_id = task.data[0].id
print(f"Created task: {task_id}")

# Get task status
task = client.tasks.getById(task_id)
print(f"Status: {task.data[0].status}")

# List all tasks
all_tasks = client.tasks.list()
for t in all_tasks.data:
    print(f"{t.id}: {t.name} - {t.status}")
```

#### 6.2 Edit and Update Tasks

```python
# Update task name and status
client.tasks.edit(
    task_id,
    name="User Authentication Implementation",
    status="in-progress"
)

# Later, mark as complete
client.tasks.edit(task_id, status="completed")
```

#### 6.3 Task with Steps

```python
# Create task
task = client.tasks.create()
task_id = task.data[0].id

# Get steps for this task
steps = client.steps.get_by_task_id(task_id)
for step in steps.data:
    print(f"Step {step.id}: {step.name} - {step.status}")

# Get specific step
step_id = steps.data[0].id
step = client.steps.getById(step_id)
print(f"Step details: {step.data[0].name}")
```

#### 6.4 Task History

```python
# Get task history
history = client.history.get_task_history(task_id, limit=10)

print("Task History:")
for entry in history.data:
    print(f"{entry.timestamp}: {entry.event}")
    print(f"  Details: {entry.details}")
```

---

### 7. Streaming Responses

**Process responses in real-time** as they're generated.

#### 7.1 Basic Streaming

```python
# Simple streaming
for chunk in client.agents.chat(prompt="Write a long essay about AI"):
    if chunk.status == "processing":
        if chunk.content:
            print(chunk.content, end='', flush=True)
    
    elif chunk.status == "complete":
        print(f"\n\n✓ Complete! Tokens: {chunk.metadata.tokens}")
        break
    
    elif chunk.status == "error":
        print(f"\n✗ Error: {chunk.error.message}")
        break
```

#### 7.2 Streaming with Tool Monitoring

```python
# Monitor content AND tool calls
for chunk in client.agents.code(
    prompt="Create a RESTful API with multiple endpoints",
    default_dir="/path/to/project",
    current_dir="/path/to/project/src"
):
    # Display content
    if chunk.content:
        print(chunk.content, end='', flush=True)
    
    # Monitor tool calls
    if chunk.tools:
        print(f"\n\n[{len(chunk.tools)} tool call(s) detected]")
        for tool in chunk.tools:
            tool_name = tool.function.get('name', 'unknown')
            print(f"  - {tool_name}")
    
    # Check for reasoning
    if hasattr(chunk, 'reasoning') and chunk.reasoning:
        print(f"\n[Reasoning] {chunk.reasoning}")
    
    # Final status
    if chunk.status == "complete":
        print(f"\n\n✓ Generation complete")
        if chunk.metadata:
            print(f"Tokens used: {chunk.metadata.tokens}")
            print(f"Cost: ${chunk.metadata.cost:.4f}")
        break
```

#### 7.3 Advanced Streaming with Progress

```python
import sys
from datetime import datetime

def stream_with_progress(prompt, agent_method):
    """Stream with visual progress indicators"""
    
    start_time = datetime.now()
    content_length = 0
    tool_calls = 0
    
    print(f"🚀 Starting at {start_time.strftime('%H:%M:%S')}")
    print("="*60)
    
    for chunk in agent_method(prompt=prompt):
        # Content
        if chunk.content:
            print(chunk.content, end='', flush=True)
            content_length += len(chunk.content)
        
        # Tools
        if chunk.tools:
            tool_calls += len(chunk.tools)
            print(f"\n[+{len(chunk.tools)} tools]", end='', flush=True)
        
        # Progress indicator
        if content_length % 100 == 0 and content_length > 0:
            sys.stdout.write('.')
            sys.stdout.flush()
        
        # Complete
        if chunk.status == "complete":
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"\n{'='*60}")
            print(f"✓ Complete in {duration:.2f}s")
            print(f"Content: {content_length} characters")
            print(f"Tools: {tool_calls} calls")
            if chunk.metadata:
                print(f"Tokens: {chunk.metadata.tokens}")
            break

# Use it
stream_with_progress(
    "Create a comprehensive user guide",
    client.agents.chat
)
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
| `context` | list[str] | Optional | Additional context strings for the conversation |
| `memory` | bool | Optional | Enable conversation memory across requests |
| `voice` | bool | Optional | Enable voice response generation |
| `task_id` | str | Optional | Session/task ID for continuity |
| `knowledge` | list[str] | Optional | Knowledge base IDs to reference |
| `os` | str | Optional | Operating system context (e.g., "linux", "darwin", "win32") |
| `default_dir` | str | Optional | Project root directory path |
| `current_dir` | str | Optional | Current working subdirectory |
| `mcp` | dict | Optional | MCP tools configuration |

**Example:**
```python
for chunk in client.agents.chat(
    prompt="Explain the authentication system",
    model="gpt-4",
    context=["src/auth.py", "src/middleware.py"],
    memory=True,
    default_dir="/path/to/project",
    current_dir="/path/to/project/src"
):
    if chunk.content:
        print(chunk.content, end='')
```

### Plan Agent (`/agent/plan`)
Multi-agent task distribution following SDLC principles.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | ✅ **Required** | Task description for planning |
| `agent_choice` | list[str] | ✅ **Required** | Agents to use: ['code', 'test', 'git', 'docs'] |
| `default_dir` | str | ✅ **Required** | Project root directory |
| `current_dir` | str | ✅ **Required** | Current working directory |
| `model` | str | Optional | Override default planning model |
| `context` | list[str] | Optional | Additional context for planning |
| `task_id` | str | Optional | Session ID for task continuity |
| `knowledge` | list[str] | Optional | Knowledge base references |
| `memory` | bool | Optional | Enable memory across planning sessions |
| `mcp` | dict | Optional | MCP tools configuration |

**Example:**
```python
for chunk in client.agents.plan(
    prompt="Build a REST API with authentication",
    agent_choice=["code", "test", "git"],
    default_dir="/path/to/project",
    current_dir="/path/to/project"
):
    if chunk.content:
        print(chunk.content, end='')
```

### Code Agent (`/agent/code`)
Generate and build code with agentic flow and tool execution.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | ✅ **Required** | Code generation prompt |
| `default_dir` | str | ✅ **Required** | Project root directory |
| `current_dir` | str | ✅ **Required** | Target subdirectory for code |
| `model` | str | Optional | Override default code model |
| `context` | list[str] | Optional | Existing code context |
| `task_id` | str | Optional | Session ID |
| `knowledge` | list[str] | Optional | Knowledge base references |
| `mcp` | dict | Optional | MCP tools for file operations |

**Example:**
```python
for chunk in client.agents.code(
    prompt="Create a User model with email and password fields",
    default_dir="/path/to/project",
    current_dir="/path/to/project/src/models",
    context=["src/database.py"]
):
    if chunk.content:
        print(chunk.content, end='')
```

### Test Agent (`/agent/test`)
Generate end-to-end tests with agentic flow.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | ✅ **Required** | Test generation prompt |
| `default_dir` | str | ✅ **Required** | Project root directory |
| `current_dir` | str | ✅ **Required** | Test directory path |
| `model` | str | Optional | Override default test model |
| `context` | list[str] | Optional | Code to test context |
| `task_id` | str | Optional | Session ID |
| `knowledge` | list[str] | Optional | Knowledge base references |
| `mcp` | dict | Optional | MCP tools for test execution |

**Example:**
```python
for chunk in client.agents.test(
    prompt="Generate tests for the User authentication flow",
    default_dir="/path/to/project",
    current_dir="/path/to/project/tests",
    context=["src/auth.py", "src/models/user.py"]
):
    if chunk.content:
        print(chunk.content, end='')
```

### Git Agent (`/agent/git`)
Git versioning operations with agentic flow.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | ✅ **Required** | Git operation prompt |
| `default_dir` | str | ✅ **Required** | Repository root directory |
| `current_dir` | str | ✅ **Required** | Working directory |
| `model` | str | Optional | Override default git model |
| `context` | list[str] | Optional | Repository context |
| `task_id` | str | Optional | Session ID |
| `knowledge` | list[str] | Optional | Knowledge base references |
| `mcp` | dict | Optional | MCP tools for git commands |

**Example:**
```python
for chunk in client.agents.git(
    prompt="Create a feature branch and commit the new auth module",
    default_dir="/path/to/project",
    current_dir="/path/to/project"
):
    if chunk.content:
        print(chunk.content, end='')
```

### Documentation Agent (`/agent/document/repo`)
Generate repository documentation with agentic flow.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | ✅ **Required** | Repository URL |
| `branch` | string | ✅ **Required** | Branch to document (e.g., "main") |
| `model` | str | Optional | Override default docs model |
| `team_access` | bool | Optional | Enable team collaboration features |
| `task_id` | str | Optional | Session ID |
| `context` | list[str] | Optional | Additional documentation context |
| `knowledge` | list[str] | Optional | Knowledge base references |
| `mcp` | dict | Optional | MCP tools configuration |

**Example:**
```python
for chunk in client.agents.document_repo(
    url="https://github.com/user/repo",
    branch="main",
    team_access=True
):
    if chunk.content:
        print(chunk.content, end='')
```

## Authentication

### API Key
```python
client = Client(api_key="sk_test_...")
```

### Environment Variables
```bash
export DISPERSL_API_KEY="sk_test_..."
```
```python
client = Client()  # Automatically uses DISPERSL_API_KEY env var
```

## Configuration

### Timeouts
```python
client = Client(
    api_key="...",
    timeout=30,  # seconds
    connect_timeout=10
)
```

### Retries
```python
client = Client(
    api_key="...",
    max_retries=3,
    backoff_factor=2.0
)
```

### Custom Base URL
```python
client = Client(
    api_key="...",
    base_url="https://api.staging.dispersl.com/v1"
)
```

## Error Handling

```python
from dispersl.exceptions import (
    AuthenticationError,
    RateLimitError,
    ServerError
)

try:
    response = client.agents.chat(prompt="Hello")
except AuthenticationError as e:
    print(f"Auth failed: {e.message}")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after}")
except ServerError as e:
    print(f"Server error: {e.status_code}")
```

## Agentic Workflows

The SDK provides powerful agentic workflow capabilities with support for handover, tool execution, and MCP client integration.

### Basic Agentic Execution

```python
from dispersl import Client, AgenticExecutor

client = Client(api_key="your_api_key")
executor = AgenticExecutor(client.http)

# Create a session
session_id = executor.create_session()

# Execute an agentic workflow
request_data = {
    "prompt": "Create a Python script to analyze CSV data",
    "context": {"project_type": "data_analysis"}
}

for response in executor.execute_agentic_workflow(
    endpoint="/agent/code",
    request_data=request_data,
    session_id=session_id,
    max_iterations=10
):
    print(f"Response: {response.content}")
    if response.status == "completed":
        break

# Clean up
executor.end_session(session_id)
```

### MCP Client Integration

```python
from dispersl import AgenticExecutor, MCPClient, MCPTool

executor = AgenticExecutor(client.http)

# Add an MCP client
mcp_client = MCPClient(
    name="file-operations",
    command="python",
    args=["-m", "file_ops_server"],
    env={"PYTHONPATH": "/path/to/server"}
)
executor.add_mcp_client(mcp_client)

# Define a custom tool
def custom_tool(args):
    filename = args.get("filename", "default.txt")
    content = args.get("content", "")
    return f"Created {filename} with content: {content}"

mcp_tool = MCPTool(
    name="create_file",
    description="Create a file with specified content",
    parameters={
        "filename": {"type": "string"},
        "content": {"type": "string"}
    },
    execute=custom_tool
)

# Add the tool to the executor
executor.mcp_tools["create_file"] = mcp_tool
```

### Handover Between Agents

```python
# Handover ACTUALLY switches execution to a different agent endpoint
# When an agent calls handover_task, the SDK:
# 1. Detects the handover tool call
# 2. Changes the endpoint to the target agent's endpoint
# 3. Creates a new request with the handover prompt
# 4. Continues execution at the NEW agent endpoint
# 5. Preserves session state throughout

for response in executor.execute_agentic_workflow(
    endpoint="/agent/plan",
    request_data={"prompt": "Plan and implement a web scraper"},
    session_id=session_id,
    max_iterations=20,
    progress_callback=lambda msg: print(f"Progress: {msg}")
):
    if response.tools:
        for tool in response.tools:
            if tool.function.get("name") == "handover_task":
                args = json.loads(tool.function.get('arguments', '{}'))
                print(f"🔄 Handing over to {args.get('agent_name')} agent")
                print(f"   New task: {args.get('prompt')}")

# Handover example: plan agent → code agent → test agent → git agent
# Each agent hands off when it completes its specialized task
```

### Session Management

```python
# Create a session with custom ID
session_id = executor.create_session("my-custom-session-id")

# Get session information
session = executor.get_session(session_id)
print(f"Conversation history: {len(session.conversation_history)} entries")
print(f"Tool responses: {len(session.tool_responses)} responses")

# End session
executor.end_session(session_id)
```

### Parsing Text-Based Tool Calls

```python
text = """
<｜tool▁call▁begin｜>function<｜tool▁sep｜>write_to_file
json
{"path": "example.py", "content": "print('Hello')"}
<｜tool▁call▁end｜>
"""

tool_calls = executor.parse_text_tool_calls(text)
for tool_call in tool_calls:
    print(f"Tool: {tool_call.function['name']}")
    print(f"Args: {tool_call.function['arguments']}")
```

### Creating Custom MCP Tools

You can create custom MCP tools for external APIs like weather services:

#### Example: Weather API Tool

```python
import requests
from dispersl import AgenticExecutor, MCPTool

executor = AgenticExecutor(client.http)

# Define custom weather tool
def get_weather(args):
    """Fetch weather data from external API"""
    city = args.get("city", "London")
    api_key = os.getenv("WEATHER_API_KEY")  # Store API keys securely!
    
    try:
        response = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather",
            params={"q": city, "appid": api_key, "units": "metric"}
        )
        response.raise_for_status()
        data = response.json()
        
        return {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"]
        }
    except Exception as e:
        return {"error": str(e)}

# Create MCP tool definition
weather_tool = MCPTool(
    name="get_weather",
    description="Get current weather information for a city",
    parameters={
        "city": {
            "type": "string",
            "description": "City name (e.g., 'London', 'New York')"
        }
    },
    execute=get_weather
)

# Add tool to executor
executor.mcp_tools["get_weather"] = weather_tool

# Use in workflow
for response in executor.execute_agentic_workflow(
    endpoint="/agent/chat",
    request_data={
        "prompt": "What's the weather like in Paris?",
    },
    session_id=session_id,
    max_iterations=5
):
    if response.content:
        print(response.content)
```

#### Example: Database Query Tool

```python
import psycopg2
from dispersl import MCPTool

def query_database(args):
    """Execute safe database queries"""
    query_type = args.get("query_type", "users")
    
    conn = psycopg2.connect(os.getenv("DATABASE_URL"))
    cursor = conn.cursor()
    
    try:
        if query_type == "users":
            cursor.execute("SELECT id, name, email FROM users LIMIT 10")
            results = cursor.fetchall()
            return {"users": [{"id": r[0], "name": r[1], "email": r[2]} for r in results]}
        
        elif query_type == "count":
            cursor.execute("SELECT COUNT(*) FROM users")
            count = cursor.fetchone()[0]
            return {"count": count}
        
        else:
            return {"error": "Unknown query type"}
    
    except Exception as e:
        return {"error": str(e)}
    
    finally:
        cursor.close()
        conn.close()

# Create tool
db_tool = MCPTool(
    name="query_database",
    description="Query the user database",
    parameters={
        "query_type": {
            "type": "string",
            "enum": ["users", "count"],
            "description": "Type of query to execute"
        }
    },
    execute=query_database
)

executor.mcp_tools["query_database"] = db_tool
```

#### Best Practices for Custom Tools

1. **Security**:
   - Never hardcode API keys - use environment variables
   - Validate and sanitize all inputs
   - Use allowlists for allowed operations
   - Implement rate limiting

2. **Error Handling**:
   - Always wrap tool execution in try-except blocks
   - Return structured error responses
   - Log errors for debugging

3. **Documentation**:
   - Provide clear descriptions
   - Document all parameters with types
   - Include usage examples

4. **Testing**:
   - Test tools independently before integration
   - Mock external APIs in tests
   - Validate response formats

## Advanced Usage

### Async Support
```python
import asyncio
from dispersl import AsyncClient

async def main():
    async with AsyncClient(api_key="...") as client:
        for chunk in client.agents.chat(prompt="Hello"):
            if chunk.content:
                print(chunk.content)
        
asyncio.run(main())
```

### Streaming Responses
```python
# Chat with streaming
for chunk in client.agents.chat(prompt="Explain quantum computing"):
    if chunk.status == "processing" and chunk.content:
        print(chunk.content, end="", flush=True)
    elif chunk.status == "complete":
        print(f"\nCompleted. Tokens used: {chunk.metadata.tokens}")

# Code generation with streaming
for chunk in client.agents.code(prompt="Create a Python calculator"):
    if chunk.tools:
        for tool in chunk.tools:
            print(f"Tool call: {tool.function['name']}")
```

### Custom Headers
```python
response = client.models.list(
    headers={"X-Custom-Header": "value"}
)
```

## API Reference

### Agents
- `client.agents.chat()` - Chat with AI
- `client.agents.plan()` - Multi-agent task dispersion
- `client.agents.code()` - Code generation
- `client.agents.test()` - Test generation
- `client.agents.git()` - Git operations
- `client.agents.document_repo()` - Repository documentation

### Models
- `client.models.list()` - List available models

### Authentication
- `client.auth_resource.get_keys()` - Get API keys
- `client.auth_resource.generate_new_key()` - Generate new API key

### Tasks
- `client.tasks.create()` - Create new task
- `client.tasks.list()` - List all tasks
- `client.tasks.get(id)` - Get task by ID
- `client.tasks.edit(id, **kwargs)` - Edit task
- `client.tasks.delete(id)` - Delete task

### Steps
- `client.steps.get(id)` - Get step by ID
- `client.steps.get_by_task_id(task_id)` - Get steps by task ID
- `client.steps.delete(id)` - Delete step

### History
- `client.history.get_task_history(task_id)` - Get task history
- `client.history.get_step_history(step_id)` - Get step history

## Testing

Run tests locally:
```bash
# Install development dependencies
pip install -e .[dev]

# Run all tests
pytest

# Run with coverage
pytest --cov=src/dispersl --cov-report=html

# Run specific test categories
pytest -m unit
pytest -m integration
pytest -m e2e
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Install development dependencies (`pip install -e .[dev]`)
4. Make your changes
5. Run tests (`pytest`)
6. Run linting (`ruff check src/ tests/`)
7. Run type checking (`mypy src/`)
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
