/**
 * End-to-end tests for complete workflows
 */

import { Dispersl } from '../../src/client';
import { AgenticExecutor } from '../../src/agentic';
import { DisperslError } from '../../src/exceptions';

describe('Complete Code Generation Workflow E2E', () => {
  let client: Dispersl;
  let executor: AgenticExecutor;

  beforeEach(() => {
    const apiUrl = process.env.DISPERSL_API_URL || 'http://localhost:3001/v1';
    const apiKey = process.env.DISPERSL_API_KEY || 'test_key';
    
    client = new Dispersl({ apiKey, baseUrl: apiUrl });
    executor = new AgenticExecutor(client);
  });

  test('should complete full code generation workflow', async () => {
    if (process.env.RUN_E2E_TESTS !== 'true') {
      return;
    }

    // Step 1: Create task
    const task = await client.tasks.create({
      name: 'Generate Calculator Module',
      description: 'Create a complete calculator module with tests',
      agentType: 'code'
    });
    
    const taskId = task.id;
    
    try {
      // Step 2: Plan
      const planStep = await client.steps.create({
        taskId,
        name: 'Plan calculator module',
        action: 'plan'
      });
      
      const sessionId = executor.startSession();
      
      const planResult = await executor.executeWorkflow({
        sessionId,
        prompt: 'Plan a calculator module with add, subtract, multiply, divide functions',
        agentType: 'plan',
        defaultDir: '/tmp/test_project',
        currentDir: '/tmp/test_project',
        agentChoice: ['code', 'test']
      });
      
      expect(planResult).toBeDefined();
      
      // Step 3: Code generation
      const codeStep = await client.steps.create({
        taskId,
        name: 'Generate code',
        action: 'execute'
      });
      
      const codeResult = await executor.executeWorkflow({
        sessionId,
        prompt: 'Implement the calculator module based on the plan',
        agentType: 'code',
        defaultDir: '/tmp/test_project',
        currentDir: '/tmp/test_project'
      });
      
      expect(codeResult).toBeDefined();
      
      // Step 4: Test generation
      const testStep = await client.steps.create({
        taskId,
        name: 'Generate tests',
        action: 'test'
      });
      
      const testResult = await executor.executeWorkflow({
        sessionId,
        prompt: 'Create comprehensive tests for the calculator module',
        agentType: 'test',
        defaultDir: '/tmp/test_project',
        currentDir: '/tmp/test_project/tests'
      });
      
      expect(testResult).toBeDefined();
      
      // Step 5: Complete task
      const updatedTask = await client.tasks.update(taskId, {
        status: 'completed',
        progress: 100
      });
      
      expect(updatedTask.status).toBe('completed');
      
      // Step 6: Get result
      const result = await client.tasks.getResult(taskId);
      expect(result).toBeDefined();
      
      executor.endSession(sessionId);
    } finally {
      try {
        await client.tasks.delete(taskId);
      } catch {
        // Ignore cleanup errors
      }
    }
  });
});

describe('Multi-Agent Collaboration E2E', () => {
  let client: Dispersl;
  let executor: AgenticExecutor;

  beforeEach(() => {
    const apiUrl = process.env.DISPERSL_API_URL || 'http://localhost:3001/v1';
    const apiKey = process.env.DISPERSL_API_KEY || 'test_key';
    
    client = new Dispersl({ apiKey, baseUrl: apiUrl });
    executor = new AgenticExecutor(client);
  });

  test('should complete plan → code → test → git workflow', async () => {
    if (process.env.RUN_E2E_TESTS !== 'true') {
      return;
    }

    const task = await client.tasks.create({
      name: 'Complete Feature Implementation',
      description: 'Implement, test, and commit a feature',
      agentType: 'plan'
    });
    
    const taskId = task.id;
    const sessionId = executor.startSession();
    
    try {
      // Phase 1: Planning
      const planResult = await executor.executeWorkflow({
        sessionId,
        prompt: 'Plan implementation of a user authentication feature',
        agentType: 'plan',
        defaultDir: '/tmp/project',
        currentDir: '/tmp/project',
        agentChoice: ['code', 'test', 'git']
      });
      
      expect(planResult).toBeDefined();
      
      // Phase 2: Implementation
      const codeResult = await executor.executeWorkflow({
        sessionId,
        prompt: 'Implement user authentication with login and logout',
        agentType: 'code',
        defaultDir: '/tmp/project',
        currentDir: '/tmp/project/src'
      });
      
      expect(codeResult).toBeDefined();
      
      // Phase 3: Testing
      const testResult = await executor.executeWorkflow({
        sessionId,
        prompt: 'Create unit and integration tests for authentication',
        agentType: 'test',
        defaultDir: '/tmp/project',
        currentDir: '/tmp/project/tests'
      });
      
      expect(testResult).toBeDefined();
      
      // Phase 4: Git operations
      const gitResult = await executor.executeWorkflow({
        sessionId,
        prompt: 'Commit the authentication feature with proper message',
        agentType: 'git',
        defaultDir: '/tmp/project',
        currentDir: '/tmp/project'
      });
      
      expect(gitResult).toBeDefined();
      
      await client.tasks.update(taskId, { status: 'completed' });
      
      executor.endSession(sessionId);
    } finally {
      try {
        await client.tasks.delete(taskId);
      } catch {
        // Ignore cleanup errors
      }
    }
  });

  test('should handle agent handover', async () => {
    if (process.env.RUN_E2E_TESTS !== 'true') {
      return;
    }

    const sessionId = executor.startSession();
    
    try {
      // Start with chat agent
      const initialResult = await executor.executeWorkflow({
        sessionId,
        prompt: 'I need to create a REST API. Can you help?',
        agentType: 'chat',
        defaultDir: '/tmp/project',
        currentDir: '/tmp/project'
      });
      
      expect(initialResult).toBeDefined();
      
      // Handover to plan agent
      const handoverData = {
        from_agent: 'chat',
        to_agent: 'plan',
        context: { task: 'REST API implementation' },
        reason: 'requires detailed planning'
      };
      
      const handoverResult = await executor.handleHandover(sessionId, handoverData);
      expect(handoverResult).toBeDefined();
      
      // Continue with plan agent
      const planResult = await executor.executeWorkflow({
        sessionId,
        prompt: 'Create detailed plan for REST API with user endpoints',
        agentType: 'plan',
        defaultDir: '/tmp/project',
        currentDir: '/tmp/project',
        agentChoice: ['code', 'test']
      });
      
      expect(planResult).toBeDefined();
      
      executor.endSession(sessionId);
    } catch (error) {
      executor.endSession(sessionId);
      throw error;
    }
  });
});

describe('Streaming Workflows E2E', () => {
  let executor: AgenticExecutor;

  beforeEach(() => {
    const apiUrl = process.env.DISPERSL_API_URL || 'http://localhost:3001/v1';
    const apiKey = process.env.DISPERSL_API_KEY || 'test_key';
    
    const client = new Dispersl({ apiKey, baseUrl: apiUrl });
    executor = new AgenticExecutor(client);
  });

  test('should stream code generation', async () => {
    if (process.env.RUN_E2E_TESTS !== 'true') {
      return;
    }

    const sessionId = executor.startSession();
    
    try {
      const chunks: any[] = [];
      const contentParts: string[] = [];
      
      for await (const chunk of executor.executeWorkflowStream({
        sessionId,
        prompt: 'Create a Python function to sort a list using quicksort',
        agentType: 'code',
        defaultDir: '/tmp/project',
        currentDir: '/tmp/project'
      })) {
        chunks.push(chunk);
        
        if (chunk && typeof chunk === 'object' && 'delta' in chunk) {
          contentParts.push(chunk.delta);
        }
      }
      
      expect(chunks.length).toBeGreaterThan(0);
      
      const fullContent = contentParts.join('');
      expect(fullContent.length).toBeGreaterThan(0);
      
      executor.endSession(sessionId);
    } catch (error) {
      executor.endSession(sessionId);
      throw error;
    }
  });

  test('should stream with tool calls', async () => {
    if (process.env.RUN_E2E_TESTS !== 'true') {
      return;
    }

    executor.toolRegistry.register('search_docs', (query: string) => {
      return `Documentation results for: ${query}`;
    });
    
    const sessionId = executor.startSession();
    
    try {
      const chunks: any[] = [];
      let toolCallsDetected = false;
      
      for await (const chunk of executor.executeWorkflowStream({
        sessionId,
        prompt: 'Search documentation for "authentication" and implement it',
        agentType: 'code',
        defaultDir: '/tmp/project',
        currentDir: '/tmp/project'
      })) {
        chunks.push(chunk);
        
        if (chunk && typeof chunk === 'object' && chunk.type === 'tool_call') {
          toolCallsDetected = true;
        }
      }
      
      expect(chunks.length).toBeGreaterThan(0);
      
      executor.endSession(sessionId);
    } catch (error) {
      executor.endSession(sessionId);
      throw error;
    }
  });
});

describe('Error Handling and Recovery E2E', () => {
  let client: Dispersl;
  let executor: AgenticExecutor;

  beforeEach(() => {
    const apiUrl = process.env.DISPERSL_API_URL || 'http://localhost:3001/v1';
    const apiKey = process.env.DISPERSL_API_KEY || 'test_key';
    
    client = new Dispersl({ apiKey, baseUrl: apiUrl });
    executor = new AgenticExecutor(client);
  });

  test('should retry workflow on failure', async () => {
    if (process.env.RUN_E2E_TESTS !== 'true') {
      return;
    }

    const task = await client.tasks.create({
      name: 'Retry Test Task',
      description: 'Task to test retry mechanism',
      agentType: 'code'
    });
    
    const taskId = task.id;
    const sessionId = executor.startSession();
    
    try {
      const result = await executor.executeWorkflow({
        sessionId,
        prompt: 'Execute a complex operation',
        agentType: 'code',
        defaultDir: '/tmp/project',
        currentDir: '/tmp/project',
        maxIterations: 3
      });
      
      expect(result).toBeDefined();
      
      executor.endSession(sessionId);
    } catch (error) {
      expect(error).toBeInstanceOf(DisperslError);
      executor.endSession(sessionId);
    } finally {
      try {
        await client.tasks.delete(taskId);
      } catch {
        // Ignore cleanup errors
      }
    }
  });

  test('should recover session after error', async () => {
    if (process.env.RUN_E2E_TESTS !== 'true') {
      return;
    }

    const sessionId = executor.startSession();
    
    try {
      try {
        await executor.executeWorkflow({
          sessionId,
          prompt: 'Invalid operation that might fail',
          agentType: 'code',
          defaultDir: '/tmp/project',
          currentDir: '/tmp/project'
        });
      } catch {
        // Expected to potentially fail
      }
      
      expect(executor.hasSession(sessionId)).toBe(true);
      
      const result2 = await executor.executeWorkflow({
        sessionId,
        prompt: 'Simple valid operation',
        agentType: 'chat',
        defaultDir: '/tmp/project',
        currentDir: '/tmp/project'
      });
      
      expect(result2).toBeDefined();
      
      executor.endSession(sessionId);
    } catch (error) {
      executor.endSession(sessionId);
      throw error;
    }
  });
});

describe('Documentation Generation E2E', () => {
  let client: Dispersl;

  beforeEach(() => {
    const apiUrl = process.env.DISPERSL_API_URL || 'http://localhost:3001/v1';
    const apiKey = process.env.DISPERSL_API_KEY || 'test_key';
    
    client = new Dispersl({ apiKey, baseUrl: apiUrl });
  });

  test('should generate documentation', async () => {
    if (process.env.RUN_E2E_TESTS !== 'true') {
      return;
    }

    const result = await client.agents.docs({
      url: 'https://github.com/example/test-repo',
      branch: 'main'
    });
    
    expect(result).toBeDefined();
    expect(result).toHaveProperty('documentation' || 'status');
  });

  test('should generate docs with team access', async () => {
    if (process.env.RUN_E2E_TESTS !== 'true') {
      return;
    }

    const result = await client.agents.docs({
      url: 'https://github.com/example/private-repo',
      branch: 'develop',
      teamAccess: true
    });
    
    expect(result).toBeDefined();
  });
});

describe('Concurrent Workflows E2E', () => {
  let executor: AgenticExecutor;

  beforeEach(() => {
    const apiUrl = process.env.DISPERSL_API_URL || 'http://localhost:3001/v1';
    const apiKey = process.env.DISPERSL_API_KEY || 'test_key';
    
    const client = new Dispersl({ apiKey, baseUrl: apiUrl });
    executor = new AgenticExecutor(client);
  });

  test('should handle multiple concurrent sessions', async () => {
    if (process.env.RUN_E2E_TESTS !== 'true') {
      return;
    }

    const runWorkflow = async (taskName: string) => {
      const sessionId = executor.startSession();
      try {
        const result = await executor.executeWorkflow({
          sessionId,
          prompt: `Execute ${taskName}`,
          agentType: 'chat',
          defaultDir: '/tmp/project',
          currentDir: '/tmp/project'
        });
        return result;
      } finally {
        executor.endSession(sessionId);
      }
    };
    
    const results = await Promise.all([
      runWorkflow('Task 1'),
      runWorkflow('Task 2'),
      runWorkflow('Task 3')
    ]);
    
    expect(results.length).toBe(3);
    expect(results.every(r => r !== undefined)).toBe(true);
  });
});

