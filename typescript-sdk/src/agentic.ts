/**
 * Agentic execution module for the Dispersl SDK.
 * 
 * This module provides functionality for agentic workflows including
 * handover between agents, tool execution, and iterative agent loops.
 */

import { randomUUID } from 'crypto';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';
import { HTTPClient } from './http';
import {
  AgenticSession,
  HandoverRequest,
  MCPClient,
  MCPTool,
  StandardNdjsonResponse,
  ToolCall,
  ToolResponse,
} from './models';
import { DisperslError } from './exceptions';

/**
 * Parse concatenated JSON objects from a string.
 * Matches server.ts lines 90-153 exactly.
 */
function parseConcatenatedJSON(jsonString: string): any[] {
  const results: any[] = [];
  let braceCount = 0;
  let startIndex = -1;
  let inString = false;
  let escapeNext = false;
  
  // Handle edge cases
  if (!jsonString || typeof jsonString !== 'string') {
    return results;
  }
  
  for (let i = 0; i < jsonString.length; i++) {
    const char = jsonString[i];
    
    if (escapeNext) {
      escapeNext = false;
      continue;
    }
    
    if (char === '\\') {
      escapeNext = true;
      continue;
    }
    
    if (char === '"' && !escapeNext) {
      inString = !inString;
      continue;
    }
    
    if (!inString) {
      if (char === '{') {
        if (braceCount === 0) {
          startIndex = i;
        }
        braceCount++;
      } else if (char === '}') {
        braceCount--;
        if (braceCount === 0 && startIndex !== -1) {
          // We have a complete JSON object
          const jsonObject = jsonString.substring(startIndex, i + 1);
          try {
            const parsed = JSON.parse(jsonObject);
            results.push(parsed);
          } catch (error) {
            console.warn(`Failed to parse JSON object at index ${startIndex}: ${jsonObject}`);
            // Add as raw string if parsing fails
            results.push({ raw: jsonObject });
          }
          startIndex = -1;
        }
      }
    }
  }
  
  // Log parsing results for debugging
  if (results.length > 0) {
    console.log(`Successfully parsed ${results.length} JSON objects from concatenated string`);
  } else {
    console.log('No valid JSON objects found in concatenated string');
  }
  
  return results;
}

/**
 * Executes agentic workflows with support for handover, tool execution, and loops.
 * 
 * This class manages agentic sessions, handles tool calls, and coordinates
 * handover between different agents in the workflow.
 */
export class AgenticExecutor {
  private sessions: Map<string, AgenticSession> = new Map();
  private mcpClients: Map<string, MCPClient> = new Map();
  private mcpTools: Map<string, MCPTool> = new Map();
  private mcpConfigPath: string;
  private mcpConfig: { mcpServers: Record<string, any> } | null = null;

  constructor(private httpClient: HTTPClient, autoLoadMcpConfig: boolean = true) {
    this.mcpConfigPath = this.findMCPConfigPath();

    // Auto-load MCP config if enabled
    if (autoLoadMcpConfig) {
      try {
        this.loadMCPConfig();
      } catch (error) {
        console.warn(`Failed to auto-load MCP config: ${error}`);
      }
    }
  }

  /**
   * Create a new agentic session.
   * 
   * @param sessionId - Optional session ID, generates UUID if not provided
   * @returns Session ID
   */
  createSession(sessionId?: string): string {
    const id = sessionId || randomUUID();

    const session: AgenticSession = {
      id,
      context: {},
      conversation_history: [],
      active_tools: [],
      tool_responses: [],
    };

    this.sessions.set(id, session);
    console.log(`Created agentic session: ${id}`);
    return id;
  }

  /**
   * Get an existing agentic session.
   * 
   * @param sessionId - Session ID
   * @returns AgenticSession or undefined if not found
   */
  getSession(sessionId: string): AgenticSession | undefined {
    return this.sessions.get(sessionId);
  }

  /**
   * End an agentic session.
   * 
   * @param sessionId - Session ID
   * @returns True if session was ended, false if not found
   */
  endSession(sessionId: string): boolean {
    if (this.sessions.has(sessionId)) {
      this.sessions.delete(sessionId);
      console.log(`Ended agentic session: ${sessionId}`);
      return true;
    }
    return false;
  }

  /**
   * Add an MCP client for tool execution.
   * 
   * @param client - MCP client configuration
   */
  addMCPClient(client: MCPClient): void {
    this.mcpClients.set(client.name, client);
    console.log(`Added MCP client: ${client.name}`);
  }

  /**
   * Remove an MCP client.
   * 
   * @param name - Client name
   * @returns True if client was removed, false if not found
   */
  removeMCPClient(name: string): boolean {
    if (this.mcpClients.has(name)) {
      this.mcpClients.delete(name);
      console.log(`Removed MCP client: ${name}`);
      return true;
    }
    return false;
  }

  /**
   * Find MCP config file path in order of preference.
   * Matches server.ts lines 1824-1850 exactly.
   * 
   * @returns Path to MCP config file
   */
  private findMCPConfigPath(): string {
    const paths = [
      // Local project .dispersl directory
      path.join(process.cwd(), '.dispersl', 'mcp.json'),
      // User home directory
      path.join(os.homedir(), '.dispersl', 'mcp.json'),
      // XDG config directory (Linux)
      path.join(
        process.env.XDG_CONFIG_HOME || path.join(os.homedir(), '.config'),
        'dispersl',
        'mcp.json'
      ),
      // System-wide config (fallback) - Unix-like systems only
      '/etc/dispersl/mcp.json',
    ];

    for (const configPath of paths) {
      if (fs.existsSync(configPath)) {
        console.log(`Found MCP config at: ${configPath}`);
        return configPath;
      }
    }

  // Default to local project .dispersl directory
  const defaultPath = paths[0];
  if (!defaultPath) {
    throw new Error('No valid MCP configuration paths found');
  }
  console.log(`No existing MCP config found, will use: ${defaultPath}`);
  return defaultPath;
  }

  /**
   * Load MCP configuration from file.
   * Matches server.ts lines 1852-1868 exactly.
   * 
   * @param configPath - Optional custom config path, uses default if not provided
   * @returns Loaded MCP configuration
   */
  loadMCPConfig(configPath?: string): { mcpServers: Record<string, any> } {
    if (configPath) {
      this.mcpConfigPath = configPath;
    }

    try {
      const configContent = fs.readFileSync(this.mcpConfigPath, 'utf-8');
      this.mcpConfig = JSON.parse(configContent);

      console.log(`Loaded MCP config from: ${this.mcpConfigPath}`);
      if (this.mcpConfig && this.mcpConfig.mcpServers) {
        const serverCount = Object.keys(this.mcpConfig.mcpServers).length;
        console.log(`Found ${serverCount} server(s) in config`);

        // Auto-register MCP clients from config
        this.registerMCPClientsFromConfig();
      }

      return this.mcpConfig || { mcpServers: {} };
    } catch (error) {
      if ((error as NodeJS.ErrnoException).code === 'ENOENT') {
        console.log(`No MCP config found at ${this.mcpConfigPath}, creating default config`);
        // If config doesn't exist, create default
        this.mcpConfig = { mcpServers: {} };
        this.saveMCPConfig();
        return this.mcpConfig;
      } else if (error instanceof SyntaxError) {
        throw new DisperslError(`Invalid MCP config JSON: ${error.message}`);
      }
      throw error;
    }
  }

  /**
   * Save MCP configuration to file.
   * Matches server.ts lines 1908-1912 exactly.
   * 
   * @param configPath - Optional custom config path, uses default if not provided
   */
  saveMCPConfig(configPath?: string): void {
    if (configPath) {
      this.mcpConfigPath = configPath;
    }

    // Create directory if it doesn't exist
    const configDir = path.dirname(this.mcpConfigPath);
    if (!fs.existsSync(configDir)) {
      fs.mkdirSync(configDir, { recursive: true });
    }

    // Write config file
    fs.writeFileSync(this.mcpConfigPath, JSON.stringify(this.mcpConfig, null, 2), 'utf-8');

    console.log(`Saved MCP config to: ${this.mcpConfigPath}`);
  }

  /**
   * Register MCP clients from loaded configuration.
   * Matches server.ts lines 1870-1896 logic.
   */
  private registerMCPClientsFromConfig(): void {
    if (!this.mcpConfig || !this.mcpConfig.mcpServers) {
      return;
    }

    for (const [name, serverConfig] of Object.entries(this.mcpConfig.mcpServers)) {
      try {
        // Convert config object to MCPClient
        const mcpClient: MCPClient = {
          name,
          command: serverConfig.command,
          args: serverConfig.args || [],
          env: serverConfig.env,
          url: serverConfig.url,
          headers: serverConfig.headers,
        };

        this.addMCPClient(mcpClient);
        console.log(`✓ Registered MCP client from config: ${name}`);
      } catch (error) {
        console.warn(`✗ Failed to register MCP client ${name}: ${error}`);
      }
    }

    // Update MCP tools after registering all clients
    this.updateMCPTools();
  }

  /**
   * Update the list of available MCP tools from connected clients.
   * Matches server.ts lines 1898-1906 exactly.
   * 
   * Creates a flat list of tools from all MCP clients with their name,
   * description, and parameters in the format expected by the API.
   */
  updateMCPTools(): void {
    this.mcpTools.clear();

    for (const [clientName, client] of this.mcpClients.entries()) {
      // Convert MCPClient to tool format expected by API
      // Each client can provide multiple tools
      // For now, we register the client info as metadata
      const toolKey = `${clientName}_client`;
      this.mcpTools.set(toolKey, {
        name: clientName,
        description: `MCP client: ${clientName}`,
        parameters: {
          type: 'object',
          properties: {
            command: { type: 'string', description: client.command || '' },
            args: { type: 'array', items: { type: 'string' } },
          },
        },
        execute: undefined,
      });
    }

    console.log(`Updated MCP tools: ${this.mcpTools.size} tool(s) from ${this.mcpClients.size} client(s)`);

    // Log available tools for debugging
    if (this.mcpTools.size > 0) {
      const toolNames = Array.from(this.mcpTools.keys()).join(', ');
      console.log(`Available MCP tools: ${toolNames}`);
    }
  }

  /**
   * Execute an agentic workflow with tool calls and handover support.
   * 
   * @param endpoint - API endpoint to call
   * @param requestData - Request data
   * @param sessionId - Optional session ID
   * @param maxIterations - Maximum number of iterations
   * @param progressCallback - Optional progress callback
   * @returns Async generator yielding streaming response chunks
   */
  async *executeAgenticWorkflow(
    endpoint: string,
    requestData: Record<string, any>,
    sessionId?: string,
    maxIterations: number = 30,
    progressCallback?: (message: string) => void
  ): AsyncGenerator<StandardNdjsonResponse, void, unknown> {
    if (!sessionId) {
      sessionId = this.createSession();
    }

    const session = this.getSession(sessionId);
    if (!session) {
      throw new DisperslError(`Session ${sessionId} not found`);
    }

    // Add session ID to request
    requestData.task_id = sessionId;

    // Add MCP tools to request if available and endpoint supports it
    // MCP tools are supported by: /agent/chat, /agent/code, /agent/test, /agent/git
    const mcpSupportedEndpoints = ['/agent/chat', '/agent/code', '/agent/test', '/agent/git'];
    if (this.mcpTools.size > 0 && mcpSupportedEndpoints.some(ep => endpoint.endsWith(ep))) {
      requestData.mcp = { tools: Array.from(this.mcpTools.values()) };
      console.log(`Added ${this.mcpTools.size} MCP tool(s) to request`);
    }

    let iteration = 0;
    let currentEndpoint = endpoint;
    let currentRequest = { ...requestData };

    console.log(`Starting agentic workflow for ${endpoint}`);

    while (iteration < maxIterations) {
      iteration++;
      console.log(`Starting iteration ${iteration}/${maxIterations}`);

      if (progressCallback) {
        progressCallback(`Starting iteration ${iteration}/${maxIterations}`);
      }

      try {
        // Make API request
        const response = await this.httpClient.post(
          currentEndpoint,
          currentRequest,
          undefined,
          { 'Accept': 'application/x-ndjson' }
        );

        // Parse NDJSON stream
        let fullResponse = '';
        const toolCalls: ToolCall[] = [];

        const lines = (response.data as string).split('\n');
        for (const line of lines) {
          if (line.trim()) {
            try {
              const chunkData = JSON.parse(line);
              const chunk = chunkData as StandardNdjsonResponse;

              // Accumulate content
              if (chunk.content) {
                fullResponse += chunk.content;
              }

      // Collect tool calls
      if (chunk.tools && Array.isArray(chunk.tools)) {
        toolCalls.push(...(chunk.tools as ToolCall[]));
      }

              yield chunk;
            } catch (error) {
              console.warn(`Failed to parse NDJSON line: ${line}, error: ${error}`);
              continue;
            }
          }
        }

        // Update session with response
        session.conversation_history.push({
          role: 'assistant',
          content: fullResponse,
          timestamp: new Date().toISOString(),
        });

        // Process tool calls
        if (toolCalls.length > 0) {
          if (progressCallback) {
            progressCallback(`Processing ${toolCalls.length} tool calls`);
          }

          const { toolResponses, handover } = this.processToolCalls(toolCalls, session);

          // Update session with tool responses
          session.tool_responses.push(...toolResponses);

          // Handle handover
          if (handover) {
            if (progressCallback) {
              progressCallback(`Handing over to ${handover.agent_name}`);
            }

            currentEndpoint = this.getEndpointForAgent(handover.agent_name);
            currentRequest = {
              prompt: handover.prompt,
              task_id: sessionId,
              ...(handover.additional_args || {}),
            };

            // Add MCP tools to new request
            if (this.mcpTools.size > 0) {
              currentRequest.mcp = { tools: Array.from(this.mcpTools.values()) };
            }

            continue;
          }

          // Continue with same endpoint, include tool responses
          currentRequest = {
            prompt: JSON.stringify({
              tool_responses: toolResponses.map(tr => tr),
              context: session.context,
            }),
            task_id: sessionId,
          };

          // Add MCP tools to request
          if (this.mcpTools.size > 0) {
            currentRequest.mcp = { tools: Array.from(this.mcpTools.values()) };
          }

          continue;
        }

        // No tool calls, workflow complete
        console.log(`Workflow completed after ${iteration} iterations`);
        if (progressCallback) {
          progressCallback('Workflow completed');
        }
        break;
      } catch (error) {
        console.error(`Error in iteration ${iteration}:`, error);
        if (progressCallback) {
          progressCallback(`Error in iteration ${iteration}: ${error}`);
        }

        // Add error to session
        session.conversation_history.push({
          role: 'assistant',
          content: `Error: ${error}`,
          timestamp: new Date().toISOString(),
        });
        break;
      }
    }

    if (iteration >= maxIterations) {
      console.warn(`Workflow reached maximum iterations (${maxIterations})`);
      if (progressCallback) {
        progressCallback(`Maximum iterations reached (${maxIterations})`);
      }
    }
  }

  /**
   * Clean terminal escape sequences and normalize output.
   * Matches server.ts lines 2098-2125 exactly.
   */
  private cleanOutput(input: string): string {
    if (!input) return '';

    try {
      // Clean terminal escape sequences and normalize line breaks
      let cleaned = input.replace(/\u001b\[[0-9;]*[a-zA-Z]/g, '');
      cleaned = cleaned.replace(/\\u001b/g, '');
      cleaned = cleaned.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
      cleaned = cleaned.replace(/\s+\n/g, '\n').replace(/\n+/g, '\n').trim();

      // Handle JSON responses
      if (cleaned.includes('"status"') && cleaned.includes('"content"')) {
        try {
          const parsedResponse = JSON.parse(cleaned);
          if (typeof parsedResponse === 'object') {
            return JSON.stringify(parsedResponse, null, 2);
          }
        } catch (error) {
          console.log('Failed to parse as JSON, returning cleaned text');
        }
      }

      return cleaned;
    } catch (error) {
      console.error('Error in cleanOutput:', error);
      return input;
    }
  }

  /**
   * Compile all responses from a session into a formatted string.
   * Matches server.ts lines 2294-2332 exactly.
   */
  private compileSessionResponses(session: AgenticSession, toolName: string): string {
    const responses: string[] = [];
    
    // Add conversation history
    if (session.conversation_history.length > 0) {
      responses.push("## 📝 Conversation History\n");
      session.conversation_history.forEach((message: any, index: number) => {
        responses.push(`**${message.role.toUpperCase()} (${index + 1}):** ${message.content}\n`);
      });
      responses.push("\n");
    }
    
    // Add tool responses
    const sessionTool = (session as any).tools?.get(toolName);
    if (sessionTool?.lastResponse?.content) {
      responses.push("## 🎯 Final Response\n");
      if (typeof sessionTool.lastResponse.content === 'string') {
        responses.push(sessionTool.lastResponse.content);
      } else if (Array.isArray(sessionTool.lastResponse.content)) {
        sessionTool.lastResponse.content.forEach((content: any) => {
          if (content.type === 'text' && 'text' in content) {
            responses.push(content.text);
          }
        });
      }
      responses.push("\n");
    }
    
    // Add tool calls if available
    if (sessionTool?.lastResponse?.tools && sessionTool.lastResponse.tools.length > 0) {
      responses.push("## 🔧 Tool Calls Executed\n");
      sessionTool.lastResponse.tools.forEach((tool: any, index: number) => {
        responses.push(`**${index + 1}. ${tool.name}**\n`);
        responses.push(`Arguments: ${JSON.stringify(tool.arguments, null, 2)}\n\n`);
      });
    }
    
    return responses.join("\n");
  }

  /**
   * Process tool calls and return responses.
   * 
   * @param toolCalls - List of tool calls to process
   * @param session - Current session
   * @returns Object with tool responses and handover request
   */
  private processToolCalls(
    toolCalls: ToolCall[],
    session: AgenticSession
  ): { toolResponses: ToolResponse[]; handover?: HandoverRequest } {
    const toolResponses: ToolResponse[] = [];
    let handover: HandoverRequest | undefined;

    for (const toolCall of toolCalls) {
      try {
        const functionName = (toolCall.function?.name as string) || '';
        
        // Parse function arguments - try regular JSON first, then concatenated JSON
        let args: Record<string, any>;
        try {
          args = JSON.parse(toolCall.arguments);
        } catch (parseError) {
          // If regular JSON parsing fails, try concatenated JSON parsing
          console.log(`Regular JSON parsing failed for ${functionName}, trying concatenated JSON parsing`);
          console.log(`Arguments string: ${toolCall.arguments}`);
          const parsedObjects = parseConcatenatedJSON(toolCall.arguments);
          
          if (parsedObjects.length === 0) {
            throw new Error(`Failed to parse arguments as JSON or concatenated JSON: ${toolCall.arguments}`);
          }
          
          // Use the first parsed object as the main arguments
          args = parsedObjects[0];
          
          // If there are multiple objects, log them for debugging
          if (parsedObjects.length > 1) {
            console.log(`Found ${parsedObjects.length} concatenated JSON objects for ${functionName}`);
            for (let i = 1; i < parsedObjects.length; i++) {
              console.log(`Additional object ${i}: ${JSON.stringify(parsedObjects[i])}`);
            }
          }
        }

        console.log(`Executing tool: ${functionName} with args: ${JSON.stringify(args)}`);

        // Handle special control tools
        if (functionName === 'end_session') {
          toolResponses.push({
            status: 'SUCCESS',
            message: 'Session ended',
            tool: functionName,
            output: '',
          });
          return { toolResponses, handover };
        }

        if (functionName === 'handover_task') {
          const agentName = args.agent_name || '';
          const handoverPrompt = args.prompt || '';
          const additionalArgs = Object.keys(args)
            .filter(k => k !== 'agent_name' && k !== 'prompt')
            .reduce((acc, k) => ({ ...acc, [k]: args[k] }), {});
          
          // Map agent names to endpoints - MUST match server.ts exactly (lines 2395-2417)
          const endpointMap: Record<string, string> = {
            code: '/agent/code',
            test: '/agent/tests',  // CRITICAL: server.ts uses /agent/tests NOT /agent/test
            git: '/agent/git',
            docs: '/docs/repo',    // CRITICAL: server.ts uses /docs/repo NOT /agent/document/repo
            chat: '/agent/chat',
            plan: '/agent/plan',
          };
          
          const endpoint = endpointMap[agentName];
          if (!endpoint) {
            throw new Error(`Unknown agent for handover: ${agentName}`);
          }
          
          handover = {
            agent_name: agentName,
            prompt: handoverPrompt,
            additional_args: additionalArgs,
          };
          toolResponses.push({
            status: 'SUCCESS',
            message: `Task handed over to ${agentName} at ${endpoint}`,
            tool: functionName,
            output: JSON.stringify({ endpoint, prompt: handoverPrompt, additionalArgs }),
          });
          continue;
        }

        // Execute tool
        const response = this.executeTool(functionName, args, session);

        // Handle different response types exactly like server.ts lines 2433-2448
        let cleanedOutput: string;
        if (response && typeof response === 'object') {
          const resp = response as Record<string, any>;
          if ('type' in resp && resp.type === 'data' && 'data' in resp) {
            cleanedOutput = JSON.stringify(resp.data, null, 2);
          } else if ('type' in resp && resp.type === 'text' && 'text' in resp) {
            cleanedOutput = this.cleanOutput(resp.text || '');
          } else if ('content' in resp) {
            cleanedOutput = this.cleanOutput(resp.content || '');
          } else if ('output' in resp) {
            cleanedOutput = this.cleanOutput(resp.output || '');
          } else {
            cleanedOutput = this.cleanOutput(JSON.stringify(response));
          }
        } else {
          cleanedOutput = this.cleanOutput(response?.toString() || '');
        }

        toolResponses.push({
          status: 'SUCCESS',
          message: 'Operation completed successfully',
          tool: functionName,
          output: cleanedOutput,
        });
        console.log(`Tool response for ${functionName}: ${cleanedOutput}`);
      } catch (error) {
        console.error(`Error executing tool ${(toolCall.function?.name as string) || 'unknown'}:`, error);
        toolResponses.push({
          status: 'FAILURE',
          message: `Error executing tool: ${error}`,
          tool: (toolCall.function?.name as string) || 'unknown',
          output: '',
        });
      }
    }

    return { toolResponses, handover };
  }

  /**
   * Execute a tool by name.
   * 
   * @param toolName - Name of the tool to execute
   * @param args - Tool arguments
   * @param session - Current session
   * @returns Tool output as string
   */
  private executeTool(
    toolName: string,
    args: Record<string, any>,
    session: AgenticSession
  ): string {
    // Check if it's a built-in tool
    if (this.getBuiltInTools().includes(toolName)) {
      return this.executeBuiltInTool(toolName, args, session);
    }

    // Check MCP tools
    const tool = this.mcpTools.get(toolName);
    if (tool?.execute) {
      const result = tool.execute(args);
      return String(result);
    }

    // Tool not found
    throw new DisperslError(`Tool ${toolName} not found`);
  }

  /**
   * Get list of built-in tool names.
   * 
   * @returns List of built-in tool names
   */
  private getBuiltInTools(): string[] {
    return [
      'list_files',
      'read_file',
      'write_to_file',
      'edit_file',
      'execute_command',
      'detect_test_frameworks',
      'write_test_file',
      'setup_branch_environment',
      'execute_git_command',
      'git_status',
      'git_diff',
      'git_add',
      'git_branch',
      'git_log',
      'git_repo_info',
      'edit_git_infra_file',
    ];
  }

  /**
   * Execute a built-in tool.
   * 
   * @param toolName - Name of the tool
   * @param args - Tool arguments
   * @param session - Current session
   * @returns Tool output
   */
  private executeBuiltInTool(
    toolName: string,
    args: Record<string, any>,
    session: AgenticSession
  ): string {
    // This is a placeholder implementation
    // In a real implementation, these would execute actual operations
    console.log(`Executing built-in tool: ${toolName} with args:`, args);

    switch (toolName) {
      case 'list_files':
        return JSON.stringify({ files: ['file1.txt', 'file2.txt'] });
      case 'read_file':
        return 'File content here';
      case 'write_to_file':
        return 'File written successfully';
      case 'execute_command':
        return 'Command executed successfully';
      default:
        return `Tool ${toolName} executed with args: ${JSON.stringify(args)}`;
    }
  }

  /**
   * Get API endpoint for agent name.
   * 
   * @param agentName - Name of the agent
   * @returns API endpoint path
   */
  /**
   * Get API endpoint for agent name.
   * MUST match server.ts lines 2395-2417 exactly.
   */
  private getEndpointForAgent(agentName: string): string {
    const agentEndpoints: Record<string, string> = {
      code: '/agent/code',
      test: '/agent/tests',          // CRITICAL: server.ts uses /agent/tests
      git: '/agent/git',
      docs: '/docs/repo',             // CRITICAL: server.ts uses /docs/repo
      chat: '/agent/chat',
      plan: '/agent/plan',
    };

    return agentEndpoints[agentName] || '/agent/chat';
  }

  /**
   * Parse text-based tool calls from content - matches server.ts exactly.
   * Server.ts lines 2718-2777
   * 
   * @param text - Text content containing tool calls
   * @returns List of parsed tool calls
   */
  parseTextToolCalls(text: string): ToolCall[] {
    const parsed: any[] = [];

    // Split by tool call boundaries - exact pattern from server.ts
    const toolCallPattern = /<｜tool▁call▁begin｜>/g;
    const toolCallsText = text.split(toolCallPattern).slice(1); // Remove first empty element

    toolCallsText.forEach((toolCallText, index) => {
      try {
        // Extract function name - exact pattern from server.ts line 2728
      const functionMatch = toolCallText.match(/^function<｜tool▁sep｜>([^\n]+)/);
      if (!functionMatch || !functionMatch[1]) return;

      const functionName = functionMatch[1].trim();

        // Extract format (json/text/etc) - exact pattern from server.ts line 2734
        const formatMatch = toolCallText.match(/\n([a-z]+)\n/);
        const formatType = formatMatch?.[1] || 'json';

        // Extract arguments - everything after the format line - server.ts line 2738
        const formatLine = '\n' + formatType + '\n';
        const argsStart = toolCallText.indexOf(formatLine) + formatLine.length;
        let argsText = toolCallText.substring(argsStart).trim();

        // Clean up any trailing markers - server.ts line 2742
        argsText = argsText.replace(/<｜[^｜]+｜>/g, '').trim();

        // Parse arguments based on format - server.ts lines 2745-2755
        let parsedArgs: Record<string, any> = {};
        if (formatType === 'json') {
          try {
            parsedArgs = JSON.parse(argsText);
          } catch (e) {
            console.warn(`Failed to parse JSON args: ${argsText}`);
            parsedArgs = { raw: argsText };
          }
        } else {
          parsedArgs = { raw: argsText };
        }

        // Create standardized tool call object - server.ts lines 2757-2766
        const standardizedCall = {
          index: index,
          id: `call_${Date.now()}_${index}`, // Generate unique ID
          type: 'function',
          function: {
            name: functionName,
            arguments: JSON.stringify(parsedArgs),
          },
        };

        parsed.push(standardizedCall);
        console.log(`Parsed tool call: ${functionName} with args: ${JSON.stringify(parsedArgs)}`);
      } catch (error) {
        console.error(`Error parsing tool call:`, error);
      }
    });

    // Convert to ToolCall objects
    const toolCalls: ToolCall[] = parsed.map((call) => ({
      function: call.function,
      arguments: call.function.arguments,
    }));

    return toolCalls;
  }
}
