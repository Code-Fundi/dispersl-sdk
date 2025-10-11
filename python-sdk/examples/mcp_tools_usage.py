"""
Example demonstrating MCP tools usage in Dispersl SDK.

This example shows how to:
1. Load MCP configuration from mcp.json
2. View loaded MCP tools
3. Use agentic endpoints with MCP tools automatically included
4. Manage MCP clients programmatically
"""

import os
import json
from dispersl import Client
from dispersl.models import MCPClient

def example_automatic_mcp_loading():
    """Example 1: Automatic MCP tool loading from mcp.json"""
    print("=" * 60)
    print("Example 1: Automatic MCP Loading")
    print("=" * 60)
    
    # The client automatically loads mcp.json on initialization
    client = Client(api_key=os.getenv('DISPERSL_API_KEY'))
    
    # Access the agentic executor to see loaded MCP clients
    executor = client.agents.executor
    
    print(f"\n✓ Loaded {len(executor.mcp_clients)} MCP client(s)")
    for name, client_info in executor.mcp_clients.items():
        print(f"  - {name}")
        print(f"    Command: {client_info.command}")
        print(f"    Args: {' '.join(client_info.args or [])}")
    
    print(f"\n✓ Generated {len(executor.mcp_tools)} MCP tool(s)")
    for tool_name, tool_def in executor.mcp_tools.items():
        print(f"  - {tool_name}: {tool_def['description']}")
    
    # MCP tools are automatically included in supported endpoints
    print("\n✓ Using chat agent with MCP tools...")
    try:
        response = client.agents.chat(
            prompt="What MCP tools are available to you?",
            # MCP tools are automatically added to the request
        )
        
        print("\nAgent Response:")
        for chunk in response:
            if hasattr(chunk, 'content') and chunk.content:
                print(chunk.content, end='', flush=True)
        print("\n")
    except Exception as e:
        print(f"Error: {e}")

def example_manual_mcp_management():
    """Example 2: Manual MCP client and tool management"""
    print("=" * 60)
    print("Example 2: Manual MCP Management")
    print("=" * 60)
    
    # Initialize client without auto-loading
    client = Client(api_key=os.getenv('DISPERSL_API_KEY'))
    executor = client.agents.executor
    
    # Add MCP client programmatically
    print("\n✓ Adding filesystem MCP client...")
    filesystem_client = MCPClient(
        name="filesystem",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-filesystem", os.getcwd()],
        env={"PYTHONUNBUFFERED": "1"}
    )
    
    executor.add_mcp_client(filesystem_client)
    
    # Add another MCP client
    print("✓ Adding GitHub MCP client...")
    github_client = MCPClient(
        name="github",
        command="npx",
        args=["-y", "@modelcontextprotocol/server-github"],
        env={"GITHUB_PERSONAL_ACCESS_TOKEN": os.getenv('GITHUB_TOKEN', '')}
    )
    
    executor.add_mcp_client(github_client)
    
    # Update tools to reflect new clients
    executor.update_mcp_tools()
    
    print(f"\n✓ Total MCP clients: {len(executor.mcp_clients)}")
    print(f"✓ Total MCP tools: {len(executor.mcp_tools)}")
    
    # Save configuration
    print("\n✓ Saving MCP configuration...")
    executor.save_mcp_config()
    print(f"  Saved to: {executor.mcp_config_path}")

def example_mcp_with_code_agent():
    """Example 3: Using MCP tools with code agent"""
    print("=" * 60)
    print("Example 3: MCP Tools with Code Agent")
    print("=" * 60)
    
    client = Client(api_key=os.getenv('DISPERSL_API_KEY'))
    
    # Code agent automatically receives MCP tools
    print("\n✓ Using code agent with MCP tools...")
    try:
        response = client.agents.code(
            prompt="Read the package.json file and tell me the project name",
            default_dir=os.getcwd(),
            current_dir=os.getcwd(),
            # MCP filesystem tools are automatically included
        )
        
        print("\nAgent Response:")
        for chunk in response:
            if hasattr(chunk, 'content') and chunk.content:
                print(chunk.content, end='', flush=True)
            if hasattr(chunk, 'tools') and chunk.tools:
                print(f"\n\n🔧 Tool calls: {len(chunk.tools)}")
                for tool in chunk.tools:
                    print(f"  - {tool.get('function', {}).get('name')}")
        print("\n")
    except Exception as e:
        print(f"Error: {e}")

def example_check_supported_endpoints():
    """Example 4: Check which endpoints support MCP tools"""
    print("=" * 60)
    print("Example 4: MCP Support by Endpoint")
    print("=" * 60)
    
    mcp_supported = {
        '/agent/chat': 'Chat agent - Full MCP tool support',
        '/agent/code': 'Code agent - Full MCP tool support',
        '/agent/test': 'Test agent - Full MCP tool support',
        '/agent/git': 'Git agent - Full MCP tool support',
    }
    
    mcp_not_supported = {
        '/agent/plan': 'Plan agent - MCP not supported',
        '/agent/document/repo': 'Documentation agent - MCP not supported',
    }
    
    print("\n✅ Endpoints WITH MCP support:")
    for endpoint, description in mcp_supported.items():
        print(f"  - {endpoint}")
        print(f"    {description}")
    
    print("\n❌ Endpoints WITHOUT MCP support:")
    for endpoint, description in mcp_not_supported.items():
        print(f"  - {endpoint}")
        print(f"    {description}")
    
    print("\nNote: When you call a supported endpoint, MCP tools from mcp.json")
    print("are automatically included in the API request.")

def example_create_mcp_config():
    """Example 5: Create a sample mcp.json configuration"""
    print("=" * 60)
    print("Example 5: Create Sample MCP Configuration")
    print("=" * 60)
    
    # Sample configuration
    config = {
        "mcpServers": {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", os.getcwd()],
                "env": {}
            },
            "github": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "env": {
                    "GITHUB_PERSONAL_ACCESS_TOKEN": "your_token_here"
                }
            },
            "brave-search": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-brave-search"],
                "env": {
                    "BRAVE_API_KEY": "your_key_here"
                }
            }
        }
    }
    
    # Create .dispersl directory if it doesn't exist
    config_dir = os.path.join(os.getcwd(), '.dispersl')
    os.makedirs(config_dir, exist_ok=True)
    
    # Save configuration
    config_path = os.path.join(config_dir, 'mcp.json')
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✓ Created sample MCP configuration at:")
    print(f"  {config_path}")
    print("\nConfiguration includes:")
    for server_name in config['mcpServers'].keys():
        print(f"  - {server_name}")
    
    print("\n⚠️  Remember to:")
    print("  1. Replace placeholder tokens with real values")
    print("  2. Add .dispersl/mcp.json to .gitignore")
    print("  3. Install required MCP servers: npm install -g @modelcontextprotocol/server-*")

if __name__ == "__main__":
    # Check if API key is set
    if not os.getenv('DISPERSL_API_KEY'):
        print("⚠️  Please set DISPERSL_API_KEY environment variable")
        print("   export DISPERSL_API_KEY='your_api_key'")
        exit(1)
    
    # Run examples
    print("\n" + "=" * 60)
    print("DISPERSL SDK - MCP TOOLS USAGE EXAMPLES")
    print("=" * 60 + "\n")
    
    # Example 1: Automatic loading
    example_automatic_mcp_loading()
    print("\n")
    
    # Example 2: Manual management
    example_manual_mcp_management()
    print("\n")
    
    # Example 3: Code agent with MCP
    example_mcp_with_code_agent()
    print("\n")
    
    # Example 4: Check supported endpoints
    example_check_supported_endpoints()
    print("\n")
    
    # Example 5: Create sample config
    example_create_mcp_config()
    print("\n")
    
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)

