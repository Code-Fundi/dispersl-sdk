/**
 * Integration tests for complete agentic workflows
 */

import { Dispersl } from '../../src/client';
import { AgenticExecutor } from '../../src/agentic';
import { DisperslError } from '../../src/exceptions';

describe('Agentic Workflow Integration', () => {
  let client: Dispersl;
  let executor: AgenticExecutor;

  beforeEach(() => {
    const apiUrl = process.env.DISPERSL_API_URL || 'http://localhost:3001/v1';
    const apiKey = process.env.DISPERSL_API_KEY || 'test_key';
    
    client = new Dispersl({ apiKey, baseUrl: apiUrl });
    executor = new AgenticExecutor(client);
  });

  describe('Simple Chat Workflow', () => {
    test('should execute simple chat workflow', async () => {
      if (process.env.RUN_INTEGRATION_TESTS !== 'true') {
        return;
      }

      const sessionId = executor.startSession();
      
      try {
        const result = await executor.executeWorkflow({
          sessionId,
          prompt: 'Hello, how are you?',
          agentType: 'chat',
          defaultDir: '/tmp/test',
          currentDir: '/tmp/test'
        });
        
        expect(result).toBeDefined();
        expect(typeof result).toBe('object');
      } finally {
        executor.endSession(sessionId);
      }
    });
  });

  describe('Code Generation Workflow', () => {
    test('should execute code generation workflow', async () => {
      if (process.env.RUN_INTEGRATION_TESTS !== 'true') {
        return;
      }

      const sessionId = executor.startSession();
      
      try {
        const result = await executor.executeWorkflow({
          sessionId,
          prompt: 'Create a simple Python function to calculate factorial',
          agentType: 'code',
          defaultDir: '/tmp/test',
          currentDir: '/tmp/test'
        });
        
        expect(result).toBeDefined();
        expect(result.toString().toLowerCase()).toContain('function' || 'code');
      } finally {
        executor.endSession(sessionId);
      }
    });
  });

  describe('Multi-Step Workflow', () => {
    test('should execute multi-step workflow', async () => {
      if (process.env.RUN_INTEGRATION_TESTS !== 'true') {
        return;
      }

      const task = await client.tasks.create({
        name: 'Integration Test Task',
        description: 'Test multi-step workflow',
        agentType: 'code'
      });
      
      const taskId = task.id;
      
      try {
        const step1 = await client.steps.create({
          taskId,
          name: 'Step 1: Prepare',
          action: 'prepare'
        });
        
        const step2 = await client.steps.create({
          taskId,
          name: 'Step 2: Execute',
          action: 'execute'
        });
        
        expect(step1.taskId).toBe(taskId);
        expect(step2.taskId).toBe(taskId);
        
        const taskStatus = await client.tasks.getStatus(taskId);
        expect(taskStatus.status).toBeDefined();
      } finally {
        try {
          await client.tasks.cancel(taskId);
        } catch {
          // Ignore cleanup errors
        }
      }
    });
  });

  describe('Streaming Workflow', () => {
    test('should execute streaming workflow', async () => {
      if (process.env.RUN_INTEGRATION_TESTS !== 'true') {
        return;
      }

      const sessionId = executor.startSession();
      
      try {
        const chunks: any[] = [];
        
        for await (const chunk of executor.executeWorkflowStream({
          sessionId,
          prompt: 'Generate a simple function',
          agentType: 'code',
          defaultDir: '/tmp/test',
          currentDir: '/tmp/test'
        })) {
          chunks.push(chunk);
        }
        
        expect(chunks.length).toBeGreaterThan(0);
      } finally {
        executor.endSession(sessionId);
      }
    });
  });

  describe('Workflow with Context', () => {
    test('should execute workflow with context', async () => {
      if (process.env.RUN_INTEGRATION_TESTS !== 'true') {
        return;
      }

      const sessionId = executor.startSession();
      const session = executor.getSession(sessionId);
      
      session.updateContext({
        language: 'python',
        framework: 'pytest',
        task: 'create tests'
      });
      
      try {
        const result = await executor.executeWorkflow({
          sessionId,
          prompt: 'Create unit tests using the specified framework',
          agentType: 'test',
          defaultDir: '/tmp/test',
          currentDir: '/tmp/test'
        });
        
        expect(result).toBeDefined();
      } finally {
        executor.endSession(sessionId);
      }
    });
  });

  describe('Workflow with Tools', () => {
    test('should execute workflow with custom tools', async () => {
      if (process.env.RUN_INTEGRATION_TESTS !== 'true') {
        return;
      }

      const sessionId = executor.startSession();
      
      // Register a custom tool
      executor.toolRegistry.register('calculator', (operation: string, a: number, b: number) => {
        switch (operation) {
          case 'add': return a + b;
          case 'subtract': return a - b;
          case 'multiply': return a * b;
          case 'divide': return b !== 0 ? a / b : 0;
          default: return 0;
        }
      });
      
      try {
        const result = await executor.executeWorkflow({
          sessionId,
          prompt: 'Calculate 10 plus 5 using the calculator tool',
          agentType: 'chat',
          defaultDir: '/tmp/test',
          currentDir: '/tmp/test'
        });
        
        expect(result).toBeDefined();
      } finally {
        executor.endSession(sessionId);
      }
    });
  });

  describe('Error Recovery', () => {
    test('should handle workflow errors gracefully', async () => {
      if (process.env.RUN_INTEGRATION_TESTS !== 'true') {
        return;
      }

      const sessionId = executor.startSession();
      
      try {
        const result = await executor.executeWorkflow({
          sessionId,
          prompt: 'Execute invalid command',
          agentType: 'code',
          defaultDir: '/tmp/test',
          currentDir: '/tmp/test',
          maxIterations: 2
        });
        
        expect(result).toBeDefined();
      } catch (error) {
        expect(error).toBeInstanceOf(DisperslError);
      } finally {
        executor.endSession(sessionId);
      }
    });
  });
});

describe('API Endpoints Integration', () => {
  let client: Dispersl;

  beforeEach(() => {
    const apiUrl = process.env.DISPERSL_API_URL || 'http://localhost:3001/v1';
    const apiKey = process.env.DISPERSL_API_KEY || 'test_key';
    
    client = new Dispersl({ apiKey, baseUrl: apiUrl });
  });

  describe('Models Endpoint', () => {
    test('should list models', async () => {
      if (process.env.RUN_INTEGRATION_TESTS !== 'true') {
        return;
      }

      const models = await client.models.list();
      
      expect(Array.isArray(models)).toBe(true);
      if (models.length > 0) {
        expect(models[0]).toHaveProperty('id' || 'name');
      }
    });
  });

  describe('Health Endpoint', () => {
    test('should check health', async () => {
      if (process.env.RUN_INTEGRATION_TESTS !== 'true') {
        return;
      }

      const health = await client.healthCheck();
      
      expect(health).toBeDefined();
      expect(health).toHaveProperty('status');
    });
  });

  describe('Auth Verification', () => {
    test('should verify authentication', async () => {
      if (process.env.RUN_INTEGRATION_TESTS !== 'true') {
        return;
      }

      const result = await client.verifyConnection();
      
      expect(result).toBe(true);
    });
  });

  describe('Task CRUD Operations', () => {
    test('should perform complete CRUD on tasks', async () => {
      if (process.env.RUN_INTEGRATION_TESTS !== 'true') {
        return;
      }

      // Create
      const task = await client.tasks.create({
        name: 'CRUD Test Task',
        description: 'Testing CRUD operations',
        agentType: 'code'
      });
      
      expect(task.id).toBeDefined();
      const taskId = task.id;
      
      try {
        // Read
        const retrievedTask = await client.tasks.get(taskId);
        expect(retrievedTask.id).toBe(taskId);
        
        // Update
        const updatedTask = await client.tasks.update(taskId, {
          status: 'in_progress'
        });
        expect(updatedTask.status).toBe('in_progress');
        
        // List
        const tasks = await client.tasks.list();
        expect(Array.isArray(tasks)).toBe(true);
        expect(tasks.some(t => t.id === taskId)).toBe(true);
      } finally {
        // Delete
        try {
          await client.tasks.delete(taskId);
        } catch {
          // Ignore cleanup errors
        }
      }
    });
  });
});

describe('MCP Integration', () => {
  let executor: AgenticExecutor;

  beforeEach(() => {
    const apiUrl = process.env.DISPERSL_API_URL || 'http://localhost:3001/v1';
    const apiKey = process.env.DISPERSL_API_KEY || 'test_key';
    
    const client = new Dispersl({ apiKey, baseUrl: apiUrl });
    executor = new AgenticExecutor(client);
  });

  describe('MCP Client Management', () => {
    test('should manage MCP clients', async () => {
      if (process.env.RUN_INTEGRATION_TESTS !== 'true') {
        return;
      }

      const mockMCPClient = {
        executeTool: jest.fn().mockResolvedValue({ result: 'MCP tool executed' })
      };
      
      executor.addMCPClient('test_server', mockMCPClient as any);
      expect(executor.hasMCPClient('test_server')).toBe(true);
      
      executor.removeMCPClient('test_server');
      expect(executor.hasMCPClient('test_server')).toBe(false);
    });
  });

  describe('Workflow with MCP', () => {
    test('should execute workflow with MCP tools', async () => {
      if (process.env.RUN_INTEGRATION_TESTS !== 'true') {
        return;
      }

      const mockMCPClient = {
        executeTool: jest.fn().mockResolvedValue({ result: 'MCP tool executed' })
      };
      
      executor.addMCPClient('test_server', mockMCPClient as any);
      
      const sessionId = executor.startSession();
      
      try {
        const mcpConfig = {
          server: 'test_server',
          tools: ['test_tool']
        };
        
        const result = await executor.executeWorkflow({
          sessionId,
          prompt: 'Use MCP tool',
          agentType: 'chat',
          defaultDir: '/tmp/test',
          currentDir: '/tmp/test',
          mcpConfig
        });
        
        expect(result).toBeDefined();
      } finally {
        executor.endSession(sessionId);
        executor.removeMCPClient('test_server');
      }
    });
  });
});

