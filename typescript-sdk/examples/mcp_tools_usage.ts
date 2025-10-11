/**
 * Example demonstrating MCP tools usage in Dispersl SDK.
 *
 * This example shows how to:
 * 1. Load MCP configuration from mcp.json
 * 2. View loaded MCP tools
 * 3. Use agentic endpoints with MCP tools automatically included
 * 4. Manage MCP clients programmatically
 */

import { Client } from '../src';
import { MCPClient } from '../src/models';
import * as fs from 'fs';
import * as path from 'path';
import * as os from 'os';

async function exampleAutomaticMCPLoading(): Promise<void> {
  console.log('='.repeat(60));
  console.log('Example 1: Automatic MCP Loading');
  console.log('='.repeat(60));

  // The client automatically loads mcp.json on initialization
  const client = new Client({ apiKey: process.env.DISPERSL_API_KEY! });

  // Access the agentic executor to see loaded MCP clients
  const executor = client.agents.executor;

  console.log(`\n✓ Loaded ${executor.mcpClients.size} MCP client(s)`);
  for (const [name, clientInfo] of executor.mcpClients) {
    console.log(`  - ${name}`);
    console.log(`    Command: ${clientInfo.command}`);
    console.log(`    Args: ${(clientInfo.args || []).join(' ')}`);
  }

  console.log(`\n✓ Generated ${executor.mcpTools.size} MCP tool(s)`);
  for (const [toolName, toolDef] of executor.mcpTools) {
    console.log(`  - ${toolName}: ${toolDef.description}`);
  }

  // MCP tools are automatically included in supported endpoints
  console.log('\n✓ Using chat agent with MCP tools...');
  try {
    const response = client.agents.chat({
      prompt: 'What MCP tools are available to you?',
      // MCP tools are automatically added to the request
    });

    console.log('\nAgent Response:');
    for await (const chunk of response) {
      if (chunk.content) {
        process.stdout.write(chunk.content);
      }
    }
    console.log('\n');
  } catch (error) {
    console.log(`Error: ${error}`);
  }
}

async function exampleManualMCPManagement(): Promise<void> {
  console.log('='.repeat(60));
  console.log('Example 2: Manual MCP Management');
  console.log('='.repeat(60));

  // Initialize client
  const client = new Client({ apiKey: process.env.DISPERSL_API_KEY! });
  const executor = client.agents.executor;

  // Add MCP client programmatically
  console.log('\n✓ Adding filesystem MCP client...');
  const filesystemClient: MCPClient = {
    name: 'filesystem',
    command: 'npx',
    args: ['-y', '@modelcontextprotocol/server-filesystem', process.cwd()],
    env: { PYTHONUNBUFFERED: '1' },
  };

  executor.addMCPClient(filesystemClient);

  // Add another MCP client
  console.log('✓ Adding GitHub MCP client...');
  const githubClient: MCPClient = {
    name: 'github',
    command: 'npx',
    args: ['-y', '@modelcontextprotocol/server-github'],
    env: { GITHUB_PERSONAL_ACCESS_TOKEN: process.env.GITHUB_TOKEN || '' },
  };

  executor.addMCPClient(githubClient);

  // Update tools to reflect new clients
  executor.updateMCPTools();

  console.log(`\n✓ Total MCP clients: ${executor.mcpClients.size}`);
  console.log(`✓ Total MCP tools: ${executor.mcpTools.size}`);

  // Save configuration
  console.log('\n✓ Saving MCP configuration...');
  executor.saveMCPConfig();
  console.log(`  Saved to: ${executor['mcpConfigPath']}`);
}

async function exampleMCPWithCodeAgent(): Promise<void> {
  console.log('='.repeat(60));
  console.log('Example 3: MCP Tools with Code Agent');
  console.log('='.repeat(60));

  const client = new Client({ apiKey: process.env.DISPERSL_API_KEY! });

  // Code agent automatically receives MCP tools
  console.log('\n✓ Using code agent with MCP tools...');
  try {
    const response = client.agents.code({
      prompt: 'Read the package.json file and tell me the project name',
      default_dir: process.cwd(),
      current_dir: process.cwd(),
      // MCP filesystem tools are automatically included
    });

    console.log('\nAgent Response:');
    for await (const chunk of response) {
      if (chunk.content) {
        process.stdout.write(chunk.content);
      }
      if (chunk.tools && Array.isArray(chunk.tools)) {
        console.log(`\n\n🔧 Tool calls: ${chunk.tools.length}`);
        for (const tool of chunk.tools) {
          const toolName = (tool as any)?.function?.name;
          if (toolName) {
            console.log(`  - ${toolName}`);
          }
        }
      }
    }
    console.log('\n');
  } catch (error) {
    console.log(`Error: ${error}`);
  }
}

function exampleCheckSupportedEndpoints(): void {
  console.log('='.repeat(60));
  console.log('Example 4: MCP Support by Endpoint');
  console.log('='.repeat(60));

  const mcpSupported: Record<string, string> = {
    '/agent/chat': 'Chat agent - Full MCP tool support',
    '/agent/code': 'Code agent - Full MCP tool support',
    '/agent/test': 'Test agent - Full MCP tool support',
    '/agent/git': 'Git agent - Full MCP tool support',
  };

  const mcpNotSupported: Record<string, string> = {
    '/agent/plan': 'Plan agent - MCP not supported',
    '/agent/document/repo': 'Documentation agent - MCP not supported',
  };

  console.log('\n✅ Endpoints WITH MCP support:');
  for (const [endpoint, description] of Object.entries(mcpSupported)) {
    console.log(`  - ${endpoint}`);
    console.log(`    ${description}`);
  }

  console.log('\n❌ Endpoints WITHOUT MCP support:');
  for (const [endpoint, description] of Object.entries(mcpNotSupported)) {
    console.log(`  - ${endpoint}`);
    console.log(`    ${description}`);
  }

  console.log('\nNote: When you call a supported endpoint, MCP tools from mcp.json');
  console.log('are automatically included in the API request.');
}

function exampleCreateMCPConfig(): void {
  console.log('='.repeat(60));
  console.log('Example 5: Create Sample MCP Configuration');
  console.log('='.repeat(60));

  // Sample configuration
  const config = {
    mcpServers: {
      filesystem: {
        command: 'npx',
        args: ['-y', '@modelcontextprotocol/server-filesystem', process.cwd()],
        env: {},
      },
      github: {
        command: 'npx',
        args: ['-y', '@modelcontextprotocol/server-github'],
        env: {
          GITHUB_PERSONAL_ACCESS_TOKEN: 'your_token_here',
        },
      },
      'brave-search': {
        command: 'npx',
        args: ['-y', '@modelcontextprotocol/server-brave-search'],
        env: {
          BRAVE_API_KEY: 'your_key_here',
        },
      },
    },
  };

  // Create .dispersl directory if it doesn't exist
  const configDir = path.join(process.cwd(), '.dispersl');
  if (!fs.existsSync(configDir)) {
    fs.mkdirSync(configDir, { recursive: true });
  }

  // Save configuration
  const configPath = path.join(configDir, 'mcp.json');
  fs.writeFileSync(configPath, JSON.stringify(config, null, 2), 'utf-8');

  console.log('\n✓ Created sample MCP configuration at:');
  console.log(`  ${configPath}`);
  console.log('\nConfiguration includes:');
  for (const serverName of Object.keys(config.mcpServers)) {
    console.log(`  - ${serverName}`);
  }

  console.log('\n⚠️  Remember to:');
  console.log('  1. Replace placeholder tokens with real values');
  console.log('  2. Add .dispersl/mcp.json to .gitignore');
  console.log('  3. Install required MCP servers: npm install -g @modelcontextprotocol/server-*');
}

async function main(): Promise<void> {
  // Check if API key is set
  if (!process.env.DISPERSL_API_KEY) {
    console.log('⚠️  Please set DISPERSL_API_KEY environment variable');
    console.log("   export DISPERSL_API_KEY='your_api_key'");
    process.exit(1);
  }

  // Run examples
  console.log('\n' + '='.repeat(60));
  console.log('DISPERSL SDK - MCP TOOLS USAGE EXAMPLES');
  console.log('='.repeat(60) + '\n');

  // Example 1: Automatic loading
  await exampleAutomaticMCPLoading();
  console.log('\n');

  // Example 2: Manual management
  await exampleManualMCPManagement();
  console.log('\n');

  // Example 3: Code agent with MCP
  await exampleMCPWithCodeAgent();
  console.log('\n');

  // Example 4: Check supported endpoints
  exampleCheckSupportedEndpoints();
  console.log('\n');

  // Example 5: Create sample config
  exampleCreateMCPConfig();
  console.log('\n');

  console.log('='.repeat(60));
  console.log('All examples completed!');
  console.log('='.repeat(60));
}

// Run main function
main().catch(console.error);

