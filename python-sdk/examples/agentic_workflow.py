"""
Example usage of the Dispersl Python SDK for agentic workflows.

This example demonstrates how to use the AgenticExecutor to create
agentic workflows with handover, tool execution, and MCP client integration.
"""

import asyncio
from dispersl import Client, AgenticExecutor, MCPClient, MCPTool


async def main():
    """Main example function."""
    # Initialize the Dispersl client
    client = Client(api_key="your-api-key-here")
    
    # Create an agentic executor
    executor = AgenticExecutor(client.http)
    
    # Create a new session
    session_id = executor.create_session()
    print(f"Created session: {session_id}")
    
    # Add an MCP client for external tool integration
    mcp_client = MCPClient(
        name="file-operations",
        command="python",
        args=["-m", "file_ops_server"],
        env={"PYTHONPATH": "/path/to/file/ops"}
    )
    executor.add_mcp_client(mcp_client)
    
    # Define a custom MCP tool
    def custom_file_tool(args):
        """Custom file operation tool."""
        filename = args.get("filename", "default.txt")
        content = args.get("content", "Hello, World!")
        return f"Created file {filename} with content: {content}"
    
    mcp_tool = MCPTool(
        name="create_file",
        description="Create a new file with specified content",
        parameters={
            "filename": {"type": "string", "description": "Name of the file to create"},
            "content": {"type": "string", "description": "Content to write to the file"}
        },
        execute=custom_file_tool
    )
    
    # Add the custom tool to the executor
    executor.mcp_tools["create_file"] = mcp_tool
    
    # Define a progress callback
    def progress_callback(message):
        print(f"Progress: {message}")
    
    # Execute an agentic workflow
    print("Starting agentic workflow...")
    
    request_data = {
        "prompt": "Create a Python script that reads a CSV file and generates a summary report",
        "context": {
            "project_type": "data_analysis",
            "requirements": ["pandas", "matplotlib"]
        }
    }
    
    try:
        # Execute the workflow with progress tracking
        for response in executor.execute_agentic_workflow(
            endpoint="/agent/code",
            request_data=request_data,
            session_id=session_id,
            max_iterations=10,
            progress_callback=progress_callback
        ):
            print(f"Response: {response.content}")
            
            if response.tools:
                print(f"Tool calls: {len(response.tools)}")
                for tool in response.tools:
                    print(f"  - {tool.function['name']}: {tool.function['arguments']}")
            
            if response.status == "completed":
                print("Workflow completed successfully!")
                break
            elif response.status == "error":
                print(f"Workflow error: {response.message}")
                break
    
    except Exception as e:
        print(f"Error executing workflow: {e}")
    
    # Get session information
    session = executor.get_session(session_id)
    if session:
        print(f"\nSession {session_id} summary:")
        print(f"  - Conversation history: {len(session.conversation_history)} entries")
        print(f"  - Tool responses: {len(session.tool_responses)} responses")
        print(f"  - Active tools: {session.active_tools}")
    
    # Parse text-based tool calls from content
    text_with_tools = """
    I need to create a file. Let me use the file creation tool:
    
    <｜tool▁call▁begin｜>function<｜tool▁sep｜>create_file
    json
    {"filename": "example.py", "content": "print('Hello, World!')"}
    <｜tool▁call▁end｜>
    
    The file has been created successfully.
    """
    
    tool_calls = executor.parse_text_tool_calls(text_with_tools)
    print(f"\nParsed {len(tool_calls)} tool calls from text:")
    for tool_call in tool_calls:
        print(f"  - {tool_call.function['name']}: {tool_call.function['arguments']}")
    
    # Clean up
    executor.end_session(session_id)
    print(f"\nEnded session: {session_id}")


def sync_example():
    """Synchronous example using the regular Client."""
    # Initialize the Dispersl client
    client = Client(api_key="your-api-key-here")
    
    # Create an agentic executor
    executor = AgenticExecutor(client.http)
    
    # Create a session
    session_id = executor.create_session()
    
    # Simple workflow execution
    request_data = {
        "prompt": "Write a simple Python function to calculate fibonacci numbers",
        "context": {"language": "python", "complexity": "beginner"}
    }
    
    print("Executing simple workflow...")
    
    try:
        for response in executor.execute_agentic_workflow(
            endpoint="/agent/code",
            request_data=request_data,
            session_id=session_id,
            max_iterations=5
        ):
            print(f"Response: {response.content}")
            
            if response.status == "completed":
                print("Workflow completed!")
                break
    
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        executor.end_session(session_id)


if __name__ == "__main__":
    print("=== Async Example ===")
    asyncio.run(main())
    
    print("\n=== Sync Example ===")
    sync_example()
