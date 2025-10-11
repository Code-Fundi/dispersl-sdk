/**
 * Tests for the agentic execution module.
 */

import { AgenticExecutor } from '../../src/agentic';
import {
  AgenticSession,
  HandoverRequest,
  MCPClient,
  MCPTool,
  StandardNdjsonResponse,
  ToolCall,
  ToolResponse,
} from '../../src/models';
import { DisperslError } from '../../src/exceptions';

// Mock HTTP client
const mockHTTPClient = {
  post: jest.fn(),
};

describe('AgenticExecutor', () => {
  let executor: AgenticExecutor;

  beforeEach(() => {
    executor = new AgenticExecutor(mockHTTPClient as any);
    jest.clearAllMocks();
  });

  describe('Session Management', () => {
    test('should create a new session', () => {
      const sessionId = executor.createSession();
      expect(sessionId).toBeDefined();
      expect(executor.getSession(sessionId)).toBeDefined();
    });

    test('should create a session with custom ID', () => {
      const customId = 'test-session-123';
      const sessionId = executor.createSession(customId);
      expect(sessionId).toBe(customId);
      expect(executor.getSession(customId)).toBeDefined();
    });

    test('should get an existing session', () => {
      const sessionId = executor.createSession();
      const session = executor.getSession(sessionId);
      expect(session).toBeDefined();
      expect(session?.id).toBe(sessionId);
    });

    test('should return undefined for non-existent session', () => {
      const session = executor.getSession('nonexistent');
      expect(session).toBeUndefined();
    });

    test('should end a session', () => {
      const sessionId = executor.createSession();
      expect(executor.getSession(sessionId)).toBeDefined();
      
      const result = executor.endSession(sessionId);
      expect(result).toBe(true);
      expect(executor.getSession(sessionId)).toBeUndefined();
    });

    test('should return false when ending non-existent session', () => {
      const result = executor.endSession('nonexistent');
      expect(result).toBe(false);
    });
  });

  describe('MCP Client Management', () => {
    test('should add an MCP client', () => {
      const client: MCPClient = {
        name: 'test-client',
        command: 'test-command',
        args: ['arg1', 'arg2'],
        env: { TEST_ENV: 'test_value' },
      };

      executor.addMCPClient(client);
      expect(executor.getSession('test-client')).toBeUndefined(); // This should be undefined since it's not a session
    });

    test('should remove an MCP client', () => {
      const client: MCPClient = {
        name: 'test-client',
      };

      executor.addMCPClient(client);
      const result = executor.removeMCPClient('test-client');
      expect(result).toBe(true);
    });

    test('should return false when removing non-existent MCP client', () => {
      const result = executor.removeMCPClient('nonexistent');
      expect(result).toBe(false);
    });
  });

  describe('Agentic Workflow Execution', () => {
    test('should execute basic agentic workflow', async () => {
      const mockResponse = {
        data: JSON.stringify({
          content: 'Test response',
          tools: [],
          status: 'completed',
          message: 'Success',
        }),
      };

      mockHTTPClient.post.mockResolvedValue(mockResponse);

      const requestData = { prompt: 'Test prompt' };
      const responses: StandardNdjsonResponse[] = [];

      for await (const response of executor.executeAgenticWorkflow(
        '/agent/chat',
        requestData,
        undefined,
        1
      )) {
        responses.push(response);
      }

      expect(responses).toHaveLength(1);
      expect(responses[0].content).toBe('Test response');
      expect(responses[0].status).toBe('completed');

      expect(mockHTTPClient.post).toHaveBeenCalledWith(
        '/agent/chat',
        expect.objectContaining({
          prompt: 'Test prompt',
          task_id: expect.any(String),
        }),
        undefined,
        { Accept: 'application/x-ndjson' }
      );
    });

    test('should execute workflow with tool calls', async () => {
      const toolCall: ToolCall = {
        function: {
          name: 'test_tool',
          arguments: '{"arg": "value"}',
        },
        arguments: '{"arg": "value"}',
      };

      const mockResponse = {
        data: JSON.stringify({
          content: 'Tool call response',
          tools: [toolCall],
          status: 'in_progress',
          message: 'Processing',
        }),
      };

      mockHTTPClient.post.mockResolvedValue(mockResponse);

      const requestData = { prompt: 'Test prompt' };
      const responses: StandardNdjsonResponse[] = [];

      for await (const response of executor.executeAgenticWorkflow(
        '/agent/chat',
        requestData,
        undefined,
        1
      )) {
        responses.push(response);
      }

      expect(responses).toHaveLength(1);
      expect(responses[0].content).toBe('Tool call response');
    });

    test('should execute workflow with handover', async () => {
      const handoverToolCall: ToolCall = {
        function: {
          name: 'handover_task',
          arguments: '{"agent_name": "code", "prompt": "New task"}',
        },
        arguments: '{"agent_name": "code", "prompt": "New task"}',
      };

      const mockResponse = {
        data: JSON.stringify({
          content: 'Handover response',
          tools: [handoverToolCall],
          status: 'in_progress',
          message: 'Handing over',
        }),
      };

      mockHTTPClient.post.mockResolvedValue(mockResponse);

      const requestData = { prompt: 'Test prompt' };
      const responses: StandardNdjsonResponse[] = [];

      for await (const response of executor.executeAgenticWorkflow(
        '/agent/chat',
        requestData,
        undefined,
        1
      )) {
        responses.push(response);
      }

      expect(responses).toHaveLength(1);
      expect(responses[0].content).toBe('Handover response');
    });

    test('should handle max iterations', async () => {
      const toolCall: ToolCall = {
        function: {
          name: 'test_tool',
          arguments: '{"arg": "value"}',
        },
        arguments: '{"arg": "value"}',
      };

      const mockResponse = {
        data: JSON.stringify({
          content: 'Tool call response',
          tools: [toolCall],
          status: 'in_progress',
          message: 'Processing',
        }),
      };

      mockHTTPClient.post.mockResolvedValue(mockResponse);

      const requestData = { prompt: 'Test prompt' };
      const responses: StandardNdjsonResponse[] = [];

      for await (const response of executor.executeAgenticWorkflow(
        '/agent/chat',
        requestData,
        undefined,
        2
      )) {
        responses.push(response);
      }

      expect(mockHTTPClient.post).toHaveBeenCalledTimes(2);
    });

    test('should handle errors gracefully', async () => {
      mockHTTPClient.post.mockRejectedValue(new Error('Network error'));

      const requestData = { prompt: 'Test prompt' };
      const responses: StandardNdjsonResponse[] = [];

      for await (const response of executor.executeAgenticWorkflow(
        '/agent/chat',
        requestData,
        undefined,
        1
      )) {
        responses.push(response);
      }

      expect(responses).toHaveLength(0);
    });
  });

  describe('Tool Call Parsing', () => {
    test('should parse text-based tool calls', () => {
      const text = `Some text before
<｜tool▁call▁begin｜>function<｜tool▁sep｜>test_tool
json
{"arg": "value"}
<｜tool▁call▁end｜>`;

      const toolCalls = executor.parseTextToolCalls(text);

      expect(toolCalls).toHaveLength(1);
      expect(toolCalls[0].function.name).toBe('test_tool');
      expect(toolCalls[0].function.arguments).toBe('{"arg":"value"}');
    });

    test('should parse multiple text-based tool calls', () => {
      const text = `Text before
<｜tool▁call▁begin｜>function<｜tool▁sep｜>tool1
json
{"arg1": "value1"}
<｜tool▁call▁end｜>Middle text
<｜tool▁call▁begin｜>function<｜tool▁sep｜>tool2
json
{"arg2": "value2"}
<｜tool▁call▁end｜>Text after`;

      const toolCalls = executor.parseTextToolCalls(text);

      expect(toolCalls).toHaveLength(2);
      expect(toolCalls[0].function.name).toBe('tool1');
      expect(toolCalls[1].function.name).toBe('tool2');
    });

    test('should handle invalid tool call format', () => {
      const text = 'Invalid tool call format';
      const toolCalls = executor.parseTextToolCalls(text);
      expect(toolCalls).toHaveLength(0);
    });
  });

  describe('Built-in Tools', () => {
    test('should get built-in tools list', () => {
      const tools = executor['getBuiltInTools']();
      expect(Array.isArray(tools)).toBe(true);
      expect(tools).toContain('list_files');
      expect(tools).toContain('read_file');
      expect(tools).toContain('write_to_file');
    });

    test('should execute built-in tools', () => {
      const session: AgenticSession = {
        id: 'test',
        context: {},
        conversation_history: [],
        active_tools: [],
        tool_responses: [],
      };

      const result = executor['executeBuiltInTool']('list_files', {}, session);
      expect(JSON.parse(result)).toHaveProperty('files');

      const readResult = executor['executeBuiltInTool']('read_file', {}, session);
      expect(readResult).toBe('File content here');
    });

    test('should throw error for non-existent tool', () => {
      const session: AgenticSession = {
        id: 'test',
        context: {},
        conversation_history: [],
        active_tools: [],
        tool_responses: [],
      };

      expect(() => {
        executor['executeTool']('nonexistent', {}, session);
      }).toThrow(DisperslError);
    });
  });

  describe('Agent Endpoints', () => {
    test('should get correct endpoint for different agents', () => {
      expect(executor['getEndpointForAgent']('code')).toBe('/agent/code');
      expect(executor['getEndpointForAgent']('test')).toBe('/agent/tests');
      expect(executor['getEndpointForAgent']('git')).toBe('/agent/git');
      expect(executor['getEndpointForAgent']('docs')).toBe('/docs/repo');
      expect(executor['getEndpointForAgent']('chat')).toBe('/agent/chat');
      expect(executor['getEndpointForAgent']('plan')).toBe('/agent/plan');
      expect(executor['getEndpointForAgent']('unknown')).toBe('/agent/chat');
    });
  });

  describe('Tool Call Processing', () => {
    test('should process end_session tool call', () => {
      const session: AgenticSession = {
        id: 'test',
        context: {},
        conversation_history: [],
        active_tools: [],
        tool_responses: [],
      };

      const toolCall: ToolCall = {
        function: {
          name: 'end_session',
          arguments: '{}',
        },
        arguments: '{}',
      };

      const { toolResponses, handover } = executor['processToolCalls']([toolCall], session);

      expect(toolResponses).toHaveLength(1);
      expect(toolResponses[0].tool).toBe('end_session');
      expect(toolResponses[0].status).toBe('SUCCESS');
      expect(handover).toBeUndefined();
    });

    test('should process handover tool call', () => {
      const session: AgenticSession = {
        id: 'test',
        context: {},
        conversation_history: [],
        active_tools: [],
        tool_responses: [],
      };

      const toolCall: ToolCall = {
        function: {
          name: 'handover_task',
          arguments: '{"agent_name": "code", "prompt": "New task"}',
        },
        arguments: '{"agent_name": "code", "prompt": "New task"}',
      };

      const { toolResponses, handover } = executor['processToolCalls']([toolCall], session);

      expect(toolResponses).toHaveLength(1);
      expect(toolResponses[0].tool).toBe('handover_task');
      expect(toolResponses[0].status).toBe('SUCCESS');
      expect(handover).toBeDefined();
      expect(handover?.agent_name).toBe('code');
      expect(handover?.prompt).toBe('New task');
    });

    test('should handle tool call errors', () => {
      const session: AgenticSession = {
        id: 'test',
        context: {},
        conversation_history: [],
        active_tools: [],
        tool_responses: [],
      };

      const toolCall: ToolCall = {
        function: {
          name: 'invalid_tool',
          arguments: '{}',
        },
        arguments: '{}',
      };

      const { toolResponses, handover } = executor['processToolCalls']([toolCall], session);

      expect(toolResponses).toHaveLength(1);
      expect(toolResponses[0].tool).toBe('invalid_tool');
      expect(toolResponses[0].status).toBe('FAILURE');
      expect(toolResponses[0].message).toContain('Error executing tool');
      expect(handover).toBeUndefined();
    });
  });
});
