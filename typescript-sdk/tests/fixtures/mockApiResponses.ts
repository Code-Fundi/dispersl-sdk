/**
 * Mock API responses for testing
 */

export class MockAPIResponses {
  static chatAgentResponse() {
    return {
      response: "I can help you with that task.",
      content: "This is a chat response",
      metadata: {
        model: "claude-3-sonnet",
        tokens: 150
      }
    };
  }

  static chatAgentStream() {
    return [
      { type: "content", delta: "I " },
      { type: "content", delta: "can " },
      { type: "content", delta: "help " },
      { type: "content", delta: "you" }
    ];
  }

  static planAgentResponse() {
    return {
      plan: {
        tasks: [
          { id: "1", name: "Setup", agent: "code" },
          { id: "2", name: "Implement", agent: "code" },
          { id: "3", name: "Test", agent: "test" }
        ]
      },
      agent_sequence: ["code", "test"]
    };
  }

  static codeAgentResponse() {
    return {
      code: "def hello():\n    return 'Hello, World!'",
      files: [
        { path: "src/hello.py", content: "def hello():\n    return 'Hello, World!'" }
      ],
      language: "python"
    };
  }

  static codeAgentStream() {
    return [
      { type: "content", delta: "def " },
      { type: "content", delta: "hello():" },
      { type: "content", delta: "\n    return 'Hello, World!'" }
    ];
  }

  static testAgentResponse() {
    return {
      tests: [
        { path: "tests/test_hello.py", content: "def test_hello():\n    assert hello() == 'Hello, World!'" }
      ],
      framework: "pytest"
    };
  }

  static gitAgentResponse() {
    return {
      action: "commit",
      message: "feat: add hello function",
      files: ["src/hello.py"],
      sha: "abc123def456"
    };
  }

  static docsAgentResponse() {
    return {
      documentation: {
        status: "generated",
        files: ["docs/api.md", "docs/guide.md"]
      },
      url: "https://github.com/user/repo"
    };
  }

  static taskCreated() {
    return {
      id: "task_123",
      name: "Test Task",
      description: "A test task",
      status: "pending",
      agent_type: "code",
      created_at: new Date().toISOString()
    };
  }

  static taskDetails() {
    return {
      id: "task_123",
      name: "Test Task",
      description: "A test task",
      status: "in_progress",
      progress: 50,
      agent_type: "code",
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString()
    };
  }

  static tasksList() {
    return [
      {
        id: "task_1",
        name: "Task 1",
        status: "completed",
        agent_type: "code"
      },
      {
        id: "task_2",
        name: "Task 2",
        status: "in_progress",
        agent_type: "test"
      },
      {
        id: "task_3",
        name: "Task 3",
        status: "pending",
        agent_type: "plan"
      }
    ];
  }

  static paginatedTasksList() {
    return {
      status: "success",
      message: "Data retrieved.",
      data: [
        {
          id: "task_1",
          name: "Task 1",
          status: "completed",
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: "task_2",
          name: "Task 2",
          status: "in_progress",
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ],
      pagination: {
        page: 1,
        pageSize: 20,
        total: 50,
        totalPages: 3,
        hasNext: true,
        hasPrev: false
      }
    };
  }

  static taskUpdated() {
    return {
      id: "task_123",
      name: "Test Task",
      status: "in_progress",
      progress: 75,
      updated_at: new Date().toISOString()
    };
  }

  static taskCancelled() {
    return {
      id: "task_123",
      status: "cancelled",
      cancelled_at: new Date().toISOString()
    };
  }

  static taskResult() {
    return {
      task_id: "task_123",
      result: {
        output: "Task completed successfully",
        files: ["output.txt"],
        status: "success"
      }
    };
  }

  static stepCreated() {
    return {
      id: "step_123",
      task_id: "task_123",
      name: "Test Step",
      action: "execute",
      status: "pending",
      created_at: new Date().toISOString()
    };
  }

  static stepDetails() {
    return {
      id: "step_123",
      task_id: "task_123",
      name: "Test Step",
      action: "execute",
      status: "completed",
      output: "Step completed",
      created_at: new Date().toISOString(),
      completed_at: new Date().toISOString()
    };
  }

  static stepsList() {
    return [
      {
        id: "step_1",
        task_id: "task_123",
        name: "Step 1",
        status: "completed"
      },
      {
        id: "step_2",
        task_id: "task_123",
        name: "Step 2",
        status: "in_progress"
      }
    ];
  }

  static paginatedStepsList() {
    return {
      status: "success",
      message: "Data retrieved.",
      data: [
        {
          id: "step_1",
          task_id: "task_123",
          name: "Step 1",
          status: "completed",
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: "step_2",
          task_id: "task_123",
          name: "Step 2",
          status: "in_progress",
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ],
      pagination: {
        page: 1,
        pageSize: 20,
        total: 25,
        totalPages: 2,
        hasNext: true,
        hasPrev: false
      }
    };
  }

  static stepUpdated() {
    return {
      id: "step_123",
      status: "completed",
      output: "Step completed successfully",
      updated_at: new Date().toISOString()
    };
  }

  static stepCancelled() {
    return {
      id: "step_123",
      status: "cancelled",
      cancelled_at: new Date().toISOString()
    };
  }

  static agenticWorkflowStream() {
    return [
      { type: "step_start", step_id: "step_1" },
      { type: "content", delta: "Starting workflow" },
      { type: "content", delta: "..." },
      { type: "step_complete", step_id: "step_1", status: "completed" }
    ];
  }

  static agenticWorkflowWithTools() {
    return [
      { type: "step_start", step_id: "step_1" },
      { type: "content", delta: "I'll use a tool" },
      {
        type: "tool_call",
        function: {
          name: "search",
          arguments: JSON.stringify({ query: "test" })
        }
      },
      { type: "tool_response", result: "Search results" },
      { type: "step_complete", step_id: "step_1" }
    ];
  }

  static agenticWorkflowWithHandover() {
    return [
      { type: "step_start", step_id: "step_1" },
      { type: "content", delta: "Analyzing task" },
      {
        type: "handover",
        from_agent: "chat",
        to_agent: "code",
        context: { task: "implement feature" },
        reason: "requires code execution"
      },
      { type: "step_complete", step_id: "step_1" }
    ];
  }

  static modelsList() {
    return [
      { id: "claude-3-opus", name: "Claude 3 Opus", provider: "anthropic" },
      { id: "claude-3-sonnet", name: "Claude 3 Sonnet", provider: "anthropic" },
      { id: "gpt-4", name: "GPT-4", provider: "openai" }
    ];
  }

  static historyList() {
    return [
      {
        id: "history_1",
        task_id: "task_123",
        event_type: "task_created",
        timestamp: new Date().toISOString()
      },
      {
        id: "history_2",
        task_id: "task_123",
        event_type: "task_updated",
        timestamp: new Date().toISOString()
      }
    ];
  }

  static paginatedHistoryList() {
    return {
      status: "success",
      message: "Data retrieved.",
      data: [
        {
          id: "history_1",
          event: "task_created",
          timestamp: new Date().toISOString(),
          details: { task_id: "task_123" }
        },
        {
          id: "history_2",
          event: "task_updated",
          timestamp: new Date().toISOString(),
          details: { task_id: "task_123", status: "in_progress" }
        }
      ],
      pagination: {
        page: 1,
        pageSize: 20,
        total: 15,
        totalPages: 1,
        hasNext: false,
        hasPrev: false
      }
    };
  }

  static paginatedAgentsList() {
    return {
      status: "success",
      message: "Data retrieved.",
      data: [
        {
          id: "agent_1",
          name: "Code Agent",
          description: "Generates and builds code",
          status: "active",
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        },
        {
          id: "agent_2",
          name: "Test Agent",
          description: "Generates and runs tests",
          status: "active",
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        }
      ],
      pagination: {
        page: 1,
        pageSize: 20,
        total: 5,
        totalPages: 1,
        hasNext: false,
        hasPrev: false
      }
    };
  }

  static errorResponse(statusCode: number, message: string) {
    return {
      error: {
        code: statusCode,
        message: message,
        details: {}
      }
    };
  }
}

