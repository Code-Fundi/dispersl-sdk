/**
 * Example usage of the Dispersl TypeScript SDK for agentic workflows.
 * 
 * This example demonstrates how to use the AgenticExecutor to create
 * agentic workflows with handover, tool execution, and MCP client integration.
 */

import { Client, AgenticExecutor, MCPClient, MCPTool } from '../src';

async function main(): Promise<void> {
  // Initialize the Dispersl client
  const client = new Client({ apiKey: 'your-api-key-here' });
  
  // Create an agentic executor
  const executor = new AgenticExecutor(client.http);
  
  // Create a new session
  const sessionId = executor.createSession();
  console.log(`Created session: ${sessionId}`);
  
  // Add an MCP client for external tool integration
  const mcpClient: MCPClient = {
    name: 'file-operations',
    command: 'node',
    args: ['file-ops-server.js'],
    env: { NODE_ENV: 'production' }
  };
  executor.addMCPClient(mcpClient);
  
  // Define a custom MCP tool
  const customFileTool = (args: Record<string, any>): string => {
    const filename = args.filename || 'default.txt';
    const content = args.content || 'Hello, World!';
    return `Created file ${filename} with content: ${content}`;
  };
  
  const mcpTool: MCPTool = {
    name: 'create_file',
    description: 'Create a new file with specified content',
    parameters: {
      filename: { type: 'string', description: 'Name of the file to create' },
      content: { type: 'string', description: 'Content to write to the file' }
    },
    execute: customFileTool
  };
  
  // Add the custom tool to the executor
  executor.mcpTools.set('create_file', mcpTool);
  
  // Define a progress callback
  const progressCallback = (message: string): void => {
    console.log(`Progress: ${message}`);
  };
  
  // Execute an agentic workflow
  console.log('Starting agentic workflow...');
  
  const requestData = {
    prompt: 'Create a TypeScript script that reads a JSON file and generates a summary report',
    context: {
      projectType: 'data_analysis',
      requirements: ['fs', 'path', 'util']
    }
  };
  
  try {
    // Execute the workflow with progress tracking
    for await (const response of executor.executeAgenticWorkflow(
      '/agent/code',
      requestData,
      sessionId,
      10,
      progressCallback
    )) {
      console.log(`Response: ${response.content}`);
      
      if (response.tools) {
        console.log(`Tool calls: ${response.tools.length}`);
        for (const tool of response.tools) {
          console.log(`  - ${tool.function?.name}: ${tool.function?.arguments}`);
        }
      }
      
      if (response.status === 'completed') {
        console.log('Workflow completed successfully!');
        break;
      } else if (response.status === 'error') {
        console.log(`Workflow error: ${response.message}`);
        break;
      }
    }
  } catch (error) {
    console.error(`Error executing workflow: ${error}`);
  }
  
  // Get session information
  const session = executor.getSession(sessionId);
  if (session) {
    console.log(`\nSession ${sessionId} summary:`);
    console.log(`  - Conversation history: ${session.conversation_history.length} entries`);
    console.log(`  - Tool responses: ${session.tool_responses.length} responses`);
    console.log(`  - Active tools: ${session.active_tools.join(', ')}`);
  }
  
  // Parse text-based tool calls from content
  const textWithTools = `
  I need to create a file. Let me use the file creation tool:
  
  <｜tool▁calls▁begin｜><｜tool▁call▁begin｜>function<｜tool▁sep｜>create_file
  json
  {"filename": "example.ts", "content": "console.log('Hello, World!');"}
  <｜tool▁call▁end｜><｜tool▁calls▁end｜>
  
  The file has been created successfully.
  `;
  
  const toolCalls = executor.parseTextToolCalls(textWithTools);
  console.log(`\nParsed ${toolCalls.length} tool calls from text:`);
  for (const toolCall of toolCalls) {
    console.log(`  - ${toolCall.function.name}: ${toolCall.function.arguments}`);
  }
  
  // Clean up
  executor.endSession(sessionId);
  console.log(`\nEnded session: ${sessionId}`);
}

async function simpleExample(): Promise<void> {
  // Initialize the Dispersl client
  const client = new Client({ apiKey: 'your-api-key-here' });
  
  // Create an agentic executor
  const executor = new AgenticExecutor(client.http);
  
  // Create a session
  const sessionId = executor.createSession();
  
  // Simple workflow execution
  const requestData = {
    prompt: 'Write a simple TypeScript function to calculate fibonacci numbers',
    context: { language: 'typescript', complexity: 'beginner' }
  };
  
  console.log('Executing simple workflow...');
  
  try {
    for await (const response of executor.executeAgenticWorkflow(
      '/agent/code',
      requestData,
      sessionId,
      5
    )) {
      console.log(`Response: ${response.content}`);
      
      if (response.status === 'completed') {
        console.log('Workflow completed!');
        break;
      }
    }
  } catch (error) {
    console.error(`Error: ${error}`);
  } finally {
    executor.endSession(sessionId);
  }
}

// Run examples
(async () => {
  console.log('=== Main Example ===');
  await main();
  
  console.log('\n=== Simple Example ===');
  await simpleExample();
})();