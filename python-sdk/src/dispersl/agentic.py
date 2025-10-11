"""
Agentic execution module for the Dispersl SDK.

This module provides functionality for agentic workflows including
handover between agents, tool execution, and iterative agent loops.
"""

import json
import logging
import uuid
import os
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Union, Callable
from datetime import datetime

from .models.api import (
    AgenticSession,
    HandoverRequest,
    MCPClient,
    MCPTool,
    StandardNdjsonResponse,
    ToolCall,
    ToolResponse,
)
from .exceptions import DisperslError

logger = logging.getLogger(__name__)


def parse_concatenated_json(json_string: str) -> List[Any]:
    """
    Parse concatenated JSON objects from a string.
    
    This function handles cases where multiple JSON objects are concatenated
    together without delimiters, which can occur in tool call arguments.
    
    Args:
        json_string: String containing one or more JSON objects
    
    Returns:
        List of parsed JSON objects
    """
    results = []
    brace_count = 0
    start_index = -1
    in_string = False
    escape_next = False
    
    # Handle edge cases
    if not json_string or not isinstance(json_string, str):
        return results
    
    for i, char in enumerate(json_string):
        if escape_next:
            escape_next = False
            continue
        
        if char == '\\':
            escape_next = True
            continue
        
        if char == '"' and not escape_next:
            in_string = not in_string
            continue
        
        if not in_string:
            if char == '{':
                if brace_count == 0:
                    start_index = i
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0 and start_index != -1:
                    # We have a complete JSON object
                    json_object = json_string[start_index:i + 1]
                    try:
                        parsed = json.loads(json_object)
                        results.append(parsed)
                    except json.JSONDecodeError as error:
                        logger.warning(f"Failed to parse JSON object at index {start_index}: {json_object}")
                        # Add as raw string if parsing fails
                        results.append({"raw": json_object})
                    start_index = -1
    
    # Log parsing results for debugging
    if results:
        logger.debug(f"Successfully parsed {len(results)} JSON objects from concatenated string")
    else:
        logger.debug("No valid JSON objects found in concatenated string")
    
    return results


class AgenticExecutor:
    """
    Executes agentic workflows with support for handover, tool execution, and loops.
    
    This class manages agentic sessions, handles tool calls, and coordinates
    handover between different agents in the workflow.
    """
    
    def __init__(self, http_client, auto_load_mcp_config: bool = True):
        """
        Initialize the agentic executor.
        
        Args:
            http_client: HTTP client for API requests
            auto_load_mcp_config: Automatically load MCP config from file system (default: True)
        """
        self.http_client = http_client
        self.sessions: Dict[str, AgenticSession] = {}
        self.mcp_clients: Dict[str, MCPClient] = {}
        self.mcp_tools: Dict[str, MCPTool] = {}
        self.mcp_config_path = self._find_mcp_config_path()
        self.mcp_config: Optional[Dict[str, Any]] = None
        
        # Auto-load MCP config if enabled
        if auto_load_mcp_config:
            try:
                self.load_mcp_config()
            except Exception as e:
                logger.warning(f"Failed to auto-load MCP config: {e}")
    
    def create_session(self, session_id: Optional[str] = None) -> str:
        """
        Create a new agentic session.
        
        Args:
            session_id: Optional session ID, generates UUID if not provided
        
        Returns:
            Session ID
        """
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        session = AgenticSession(
            id=session_id,
            context={},
            conversation_history=[],
            active_tools=[],
            tool_responses=[]
        )
        
        self.sessions[session_id] = session
        logger.info(f"Created agentic session: {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[AgenticSession]:
        """
        Get an existing agentic session.
        
        Args:
            session_id: Session ID
        
        Returns:
            AgenticSession or None if not found
        """
        return self.sessions.get(session_id)
    
    def end_session(self, session_id: str) -> bool:
        """
        End an agentic session.
        
        Args:
            session_id: Session ID
        
        Returns:
            True if session was ended, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Ended agentic session: {session_id}")
            return True
        return False
    
    def add_mcp_client(self, client: MCPClient) -> None:
        """
        Add an MCP client for tool execution.
        
        Args:
            client: MCP client configuration
        """
        self.mcp_clients[client.name] = client
        logger.info(f"Added MCP client: {client.name}")
    
    def remove_mcp_client(self, name: str) -> bool:
        """
        Remove an MCP client.
        
        Args:
            name: Client name
        
        Returns:
            True if client was removed, False if not found
        """
        if name in self.mcp_clients:
            del self.mcp_clients[name]
            logger.info(f"Removed MCP client: {name}")
            return True
        return False
    
    def _find_mcp_config_path(self) -> str:
        """
        Find MCP config file path in order of preference.
        Matches server.ts lines 1824-1850 exactly.
        
        Returns:
            Path to MCP config file
        """
        paths = [
            # Local project .dispersl directory
            os.path.join(os.getcwd(), ".dispersl", "mcp.json"),
            # User home directory
            os.path.join(os.path.expanduser("~"), ".dispersl", "mcp.json"),
            # XDG config directory (Linux)
            os.path.join(
                os.environ.get("XDG_CONFIG_HOME", os.path.join(os.path.expanduser("~"), ".config")),
                "dispersl",
                "mcp.json"
            ),
            # System-wide config (fallback) - Unix-like systems only
            "/etc/dispersl/mcp.json"
        ]
        
        for path in paths:
            if os.path.exists(path):
                logger.info(f"Found MCP config at: {path}")
                return path
        
        # Default to local project .dispersl directory
        default_path = paths[0]
        logger.info(f"No existing MCP config found, will use: {default_path}")
        return default_path
    
    def load_mcp_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load MCP configuration from file.
        Matches server.ts lines 1852-1868 exactly.
        
        Args:
            config_path: Optional custom config path, uses default if not provided
        
        Returns:
            Loaded MCP configuration
        """
        if config_path:
            self.mcp_config_path = config_path
        
        try:
            with open(self.mcp_config_path, 'r', encoding='utf-8') as f:
                self.mcp_config = json.load(f)
            
            logger.info(f"Loaded MCP config from: {self.mcp_config_path}")
            if self.mcp_config and 'mcpServers' in self.mcp_config:
                server_count = len(self.mcp_config['mcpServers'])
                logger.info(f"Found {server_count} server(s) in config")
                
                # Auto-register MCP clients from config
                self._register_mcp_clients_from_config()
            
            return self.mcp_config
            
        except FileNotFoundError:
            logger.info(f"No MCP config found at {self.mcp_config_path}, creating default config")
            # If config doesn't exist, create default
            self.mcp_config = {"mcpServers": {}}
            self.save_mcp_config()
            return self.mcp_config
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse MCP config: {e}")
            raise DisperslError(f"Invalid MCP config JSON: {e}")
    
    def save_mcp_config(self, config_path: Optional[str] = None) -> None:
        """
        Save MCP configuration to file.
        Matches server.ts lines 1908-1912 exactly.
        
        Args:
            config_path: Optional custom config path, uses default if not provided
        """
        if config_path:
            self.mcp_config_path = config_path
        
        # Create directory if it doesn't exist
        config_dir = os.path.dirname(self.mcp_config_path)
        os.makedirs(config_dir, exist_ok=True)
        
        # Write config file
        with open(self.mcp_config_path, 'w', encoding='utf-8') as f:
            json.dump(self.mcp_config, f, indent=2)
        
        logger.info(f"Saved MCP config to: {self.mcp_config_path}")
    
    def _register_mcp_clients_from_config(self) -> None:
        """
        Register MCP clients from loaded configuration.
        Matches server.ts lines 1870-1896 logic.
        """
        if not self.mcp_config or 'mcpServers' not in self.mcp_config:
            return
        
        for name, server_config in self.mcp_config['mcpServers'].items():
            try:
                # Convert config dict to MCPClient
                mcp_client = MCPClient(
                    name=name,
                    command=server_config.get('command'),
                    args=server_config.get('args', []),
                    env=server_config.get('env'),
                    url=server_config.get('url'),
                    headers=server_config.get('headers')
                )
                
                self.add_mcp_client(mcp_client)
                logger.info(f"✓ Registered MCP client from config: {name}")
                
            except Exception as e:
                logger.warning(f"✗ Failed to register MCP client {name}: {e}")
        
        # Update MCP tools after registering all clients
        self.update_mcp_tools()
    
    def update_mcp_tools(self) -> None:
        """
        Update the list of available MCP tools from connected clients.
        Matches server.ts lines 1898-1906 exactly.
        
        Creates a flat list of tools from all MCP clients with their name,
        description, and parameters in the format expected by the API.
        """
        self.mcp_tools = {}
        
        for client_name, client in self.mcp_clients.items():
            # Convert MCPClient to tool format expected by API
            # Each client can provide multiple tools
            # For now, we register the client info as metadata
            tool_key = f"{client_name}_client"
            self.mcp_tools[tool_key] = {
                "name": client_name,
                "description": f"MCP client: {client_name}",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "command": {"type": "string", "description": client.command or ""},
                        "args": {"type": "array", "items": {"type": "string"}},
                    }
                }
            }
        
        logger.info(f"Updated MCP tools: {len(self.mcp_tools)} tool(s) from {len(self.mcp_clients)} client(s)")
        
        # Log available tools for debugging
        if self.mcp_tools:
            logger.debug(f"Available MCP tools: {', '.join(self.mcp_tools.keys())}")
    
    def execute_agentic_workflow(
        self,
        endpoint: str,
        request_data: Dict[str, Any],
        session_id: Optional[str] = None,
        max_iterations: int = 30,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Generator[StandardNdjsonResponse, None, None]:
        """
        Execute an agentic workflow with tool calls and handover support.
        
        Args:
            endpoint: API endpoint to call
            request_data: Request data
            session_id: Optional session ID
            max_iterations: Maximum number of iterations
            progress_callback: Optional progress callback
        
        Yields:
            StandardNdjsonResponse: Streaming response chunks
        """
        if session_id is None:
            session_id = self.create_session()
        
        session = self.get_session(session_id)
        if session is None:
            raise DisperslError(f"Session {session_id} not found")
        
        # Add session ID to request
        request_data["task_id"] = session_id
        
        # Add MCP tools to request if available and endpoint supports it
        # MCP tools are supported by: /agent/chat, /agent/code, /agent/test, /agent/git
        mcp_supported_endpoints = ['/agent/chat', '/agent/code', '/agent/test', '/agent/git']
        if self.mcp_tools and any(endpoint.endswith(ep) for ep in mcp_supported_endpoints):
            request_data["mcp"] = {"tools": list(self.mcp_tools.values())}
            logger.debug(f"Added {len(self.mcp_tools)} MCP tool(s) to request")
        
        iteration = 0
        current_endpoint = endpoint
        current_request = request_data.copy()
        
        logger.info(f"Starting agentic workflow for {endpoint}")
        
        while iteration < max_iterations:
            iteration += 1
            logger.info(f"Starting iteration {iteration}/{max_iterations}")
            
            if progress_callback:
                progress_callback(f"Starting iteration {iteration}/{max_iterations}")
            
            try:
                # Make API request
                response = self.http_client.post(
                    current_endpoint,
                    json_data=current_request,
                    headers={"Accept": "application/x-ndjson"}
                )
                
                # Parse NDJSON stream
                full_response = ""
                tool_calls: List[ToolCall] = []
                
                for line in response.text.splitlines():
                    if line.strip():
                        try:
                            chunk_data = json.loads(line)
                            chunk = StandardNdjsonResponse(**chunk_data)
                            
                            # Accumulate content
                            if chunk.content:
                                full_response += chunk.content
                            
                            # Collect tool calls
                            if hasattr(chunk, 'tools') and chunk.tools:
                                tool_calls.extend(chunk.tools)
                            
                            yield chunk
                            
                        except Exception as e:
                            logger.warning(f"Failed to parse NDJSON line: {line}, error: {e}")
                            continue
                
                # Update session with response
                session.conversation_history.append({
                    "role": "assistant",
                    "content": full_response,
                    "timestamp": datetime.now().isoformat()
                })
                
                # Process tool calls
                if tool_calls:
                    if progress_callback:
                        progress_callback(f"Processing {len(tool_calls)} tool calls")
                    
                    tool_responses, handover = self._process_tool_calls(
                        tool_calls, session
                    )
                    
                    # Update session with tool responses
                    session.tool_responses.extend(tool_responses)
                    
                    # Handle handover
                    if handover:
                        if progress_callback:
                            progress_callback(f"Handing over to {handover.agent_name}")
                        
                        current_endpoint = self._get_endpoint_for_agent(handover.agent_name)
                        current_request = {
                            "prompt": handover.prompt,
                            "task_id": session_id,
                            **(handover.additional_args or {})
                        }
                        
                        # Add MCP tools to new request
                        if self.mcp_tools:
                            current_request["mcp"] = {"tools": list(self.mcp_tools.values())}
                        
                        continue
                    
                    # Continue with same endpoint, include tool responses
                    current_request = {
                        "prompt": json.dumps({
                            "tool_responses": [tr.dict() for tr in tool_responses],
                            "context": session.context
                        }),
                        "task_id": session_id
                    }
                    
                    # Add MCP tools to request
                    if self.mcp_tools:
                        current_request["mcp"] = {"tools": list(self.mcp_tools.values())}
                    
                    continue
                
                # No tool calls, workflow complete
                logger.info(f"Workflow completed after {iteration} iterations")
                if progress_callback:
                    progress_callback("Workflow completed")
                break
                
            except Exception as error:
                logger.error(f"Error in iteration {iteration}: {error}")
                if progress_callback:
                    progress_callback(f"Error in iteration {iteration}: {error}")
                
                # Add error to session
                session.conversation_history.append({
                    "role": "assistant",
                    "content": f"Error: {error}",
                    "timestamp": datetime.now().isoformat()
                })
                break
        
        if iteration >= max_iterations:
            logger.warning(f"Workflow reached maximum iterations ({max_iterations})")
            if progress_callback:
                progress_callback(f"Maximum iterations reached ({max_iterations})")
    
    def _clean_output(self, input_str: str) -> str:
        """
        Clean terminal escape sequences and normalize output.
        
        Args:
            input_str: Raw output string
        
        Returns:
            Cleaned output string
        """
        if not input_str:
            return ''
        
        try:
            import re
            
            # Clean terminal escape sequences and normalize line breaks
            cleaned = re.sub(r'\x1b\[[0-9;]*[a-zA-Z]', '', input_str)
            cleaned = cleaned.replace('\\u001b', '')
            cleaned = cleaned.replace('\r\n', '\n').replace('\r', '\n')
            cleaned = re.sub(r'\s+\n', '\n', cleaned)
            cleaned = re.sub(r'\n+', '\n', cleaned).strip()
            
            # Handle JSON responses
            if '"status"' in cleaned and '"content"' in cleaned:
                try:
                    parsed_response = json.loads(cleaned)
                    if isinstance(parsed_response, dict):
                        return json.dumps(parsed_response, indent=2)
                except json.JSONDecodeError:
                    logger.debug('Failed to parse as JSON, returning cleaned text')
            
            return cleaned
        except Exception as error:
            logger.error(f'Error in cleanOutput: {error}')
            return input_str
    
    def _compile_session_responses(self, session: AgenticSession, tool_name: str) -> str:
        """
        Compile all responses from a session into a formatted string.
        
        Args:
            session: The agentic session
            tool_name: Name of the tool to compile responses for
        
        Returns:
            Formatted response string
        """
        responses = []
        
        # Add conversation history
        if session.conversation_history:
            responses.append("## 📝 Conversation History\n")
            for i, message in enumerate(session.conversation_history, 1):
                responses.append(f"**{message['role'].upper()} ({i}):** {message['content']}\n")
            responses.append("\n")
        
        # Add tool responses
        session_tool = getattr(session, 'tools', {}).get(tool_name)
        if session_tool and hasattr(session_tool, 'lastResponse') and session_tool.lastResponse:
            responses.append("## 🎯 Final Response\n")
            content = session_tool.lastResponse.get('content', '')
            if isinstance(content, str):
                responses.append(content)
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get('type') == 'text' and 'text' in item:
                        responses.append(item['text'])
            responses.append("\n")
        
        # Add tool calls if available
        if session_tool and hasattr(session_tool, 'lastResponse') and session_tool.lastResponse:
            tools = session_tool.lastResponse.get('tools', [])
            if tools:
                responses.append("## 🔧 Tool Calls Executed\n")
                for i, tool in enumerate(tools, 1):
                    tool_name_str = tool.get('name', 'unknown')
                    tool_args = tool.get('arguments', {})
                    responses.append(f"**{i}. {tool_name_str}**\n")
                    responses.append(f"Arguments: {json.dumps(tool_args, indent=2)}\n\n")
        
        return "\n".join(responses)
    
    def _process_tool_calls(
        self, 
        tool_calls: List[ToolCall], 
        session: AgenticSession
    ) -> tuple[List[ToolResponse], Optional[HandoverRequest]]:
        """
        Process tool calls and return responses.
        
        Args:
            tool_calls: List of tool calls to process
            session: Current session
        
        Returns:
            Tuple of (tool_responses, handover_request)
        """
        tool_responses: List[ToolResponse] = []
        handover: Optional[HandoverRequest] = None
        
        for tool_call in tool_calls:
            try:
                function_name = tool_call.function.get("name", "")
                
                # Parse function arguments - try regular JSON first, then concatenated JSON
                try:
                    args = json.loads(tool_call.arguments)
                except json.JSONDecodeError as parse_error:
                    # If regular JSON parsing fails, try concatenated JSON parsing
                    logger.debug(f"Regular JSON parsing failed for {function_name}, trying concatenated JSON parsing")
                    logger.debug(f"Arguments string: {tool_call.arguments}")
                    parsed_objects = parse_concatenated_json(tool_call.arguments)
                    
                    if not parsed_objects:
                        raise Exception(f"Failed to parse arguments as JSON or concatenated JSON: {tool_call.arguments}")
                    
                    # Use the first parsed object as the main arguments
                    args = parsed_objects[0]
                    
                    # If there are multiple objects, log them for debugging
                    if len(parsed_objects) > 1:
                        logger.debug(f"Found {len(parsed_objects)} concatenated JSON objects for {function_name}")
                        for i in range(1, len(parsed_objects)):
                            logger.debug(f"Additional object {i}: {json.dumps(parsed_objects[i])}")
                
                logger.debug(f"Executing tool: {function_name} with args: {json.dumps(args)}")
                
                # Handle special control tools
                if function_name == "end_session":
                    tool_responses.append(ToolResponse(
                        status="SUCCESS",
                        message="Session ended",
                        tool=function_name,
                        output=""
                    ))
                    return tool_responses, handover
                
                if function_name == "handover_task":
                    agent_name = args.get("agent_name", "")
                    handover_prompt = args.get("prompt", "")
                    additional_args = {k: v for k, v in args.items() if k not in ["agent_name", "prompt"]}
                    
                    # Map agent names to endpoints - MUST match server.ts exactly (lines 2395-2417)
                    endpoint_map = {
                        "code": "/agent/code",
                        "test": "/agent/tests",  # CRITICAL: server.ts uses /agent/tests NOT /agent/test
                        "git": "/agent/git",
                        "docs": "/docs/repo",    # CRITICAL: server.ts uses /docs/repo NOT /agent/document/repo
                        "chat": "/agent/chat",
                        "plan": "/agent/plan"
                    }
                    
                    endpoint = endpoint_map.get(agent_name)
                    if not endpoint:
                        raise Exception(f"Unknown agent for handover: {agent_name}")
                    
                    handover = HandoverRequest(
                        agent_name=agent_name,
                        prompt=handover_prompt,
                        additional_args=additional_args
                    )
                    tool_responses.append(ToolResponse(
                        status="SUCCESS",
                        message=f"Task handed over to {agent_name} at {endpoint}",
                        tool=function_name,
                        output=json.dumps({"endpoint": endpoint, "prompt": handover_prompt, "additionalArgs": additional_args})
                    ))
                    continue
                
                # Execute tool
                response = self._execute_tool(function_name, args, session)
                
                # Handle different response types exactly like server.ts
                if response and isinstance(response, dict):
                    if "type" in response and response["type"] == "data" and "data" in response:
                        cleaned_output = json.dumps(response["data"], indent=2)
                    elif "type" in response and response["type"] == "text" and "text" in response:
                        cleaned_output = self._clean_output(response.get("text", ""))
                    elif "content" in response:
                        cleaned_output = self._clean_output(response.get("content", ""))
                    elif "output" in response:
                        cleaned_output = self._clean_output(response.get("output", ""))
                    else:
                        cleaned_output = self._clean_output(json.dumps(response))
                else:
                    cleaned_output = self._clean_output(str(response) if response else "")
                
                tool_responses.append(ToolResponse(
                    status="SUCCESS",
                    message="Operation completed successfully",
                    tool=function_name,
                    output=cleaned_output
                ))
                logger.debug(f"Tool response for {function_name}: {cleaned_output}")
                
            except Exception as error:
                logger.error(f"Error executing tool {tool_call.function.get('name', 'unknown')}: {error}")
                tool_responses.append(ToolResponse(
                    status="FAILURE",
                    message=f"Error executing tool: {error}",
                    tool=tool_call.function.get("name", "unknown"),
                    output=""
                ))
        
        return tool_responses, handover
    
    def _execute_tool(
        self, 
        tool_name: str, 
        args: Dict[str, Any], 
        session: AgenticSession
    ) -> str:
        """
        Execute a tool by name.
        
        Args:
            tool_name: Name of the tool to execute
            args: Tool arguments
            session: Current session
        
        Returns:
            Tool output as string
        """
        # Check if it's a built-in tool
        if tool_name in self._get_built_in_tools():
            return self._execute_built_in_tool(tool_name, args, session)
        
        # Check MCP tools
        if tool_name in self.mcp_tools:
            tool = self.mcp_tools[tool_name]
            if tool.execute:
                result = tool.execute(args)
                return str(result)
        
        # Tool not found
        raise DisperslError(f"Tool {tool_name} not found")
    
    def _get_built_in_tools(self) -> List[str]:
        """Get list of built-in tool names."""
        return [
            "list_files",
            "read_file", 
            "write_to_file",
            "edit_file",
            "execute_command",
            "detect_test_frameworks",
            "write_test_file",
            "setup_branch_environment",
            "execute_git_command",
            "git_status",
            "git_diff",
            "git_add",
            "git_branch",
            "git_log",
            "git_repo_info",
            "edit_git_infra_file"
        ]
    
    def _execute_built_in_tool(
        self, 
        tool_name: str, 
        args: Dict[str, Any], 
        session: AgenticSession
    ) -> str:
        """
        Execute a built-in tool.
        
        Args:
            tool_name: Name of the tool
            args: Tool arguments
            session: Current session
        
        Returns:
            Tool output
        """
        # This is a placeholder implementation
        # In a real implementation, these would execute actual operations
        logger.info(f"Executing built-in tool: {tool_name} with args: {args}")
        
        if tool_name == "list_files":
            return json.dumps({"files": ["file1.txt", "file2.txt"]})
        elif tool_name == "read_file":
            return "File content here"
        elif tool_name == "write_to_file":
            return "File written successfully"
        elif tool_name == "execute_command":
            return "Command executed successfully"
        else:
            return f"Tool {tool_name} executed with args: {args}"
    
    def _get_endpoint_for_agent(self, agent_name: str) -> str:
        """
        Get API endpoint for agent name.
        MUST match server.ts lines 2395-2417 exactly.
        
        Args:
            agent_name: Name of the agent
        
        Returns:
            API endpoint path
        """
        agent_endpoints = {
            "code": "/agent/code",
            "test": "/agent/tests",          # CRITICAL: server.ts uses /agent/tests
            "git": "/agent/git",
            "docs": "/docs/repo",             # CRITICAL: server.ts uses /docs/repo
            "chat": "/agent/chat",
            "plan": "/agent/plan"
        }
        
        return agent_endpoints.get(agent_name, "/agent/chat")
    
    def parse_text_tool_calls(self, text: str) -> List[ToolCall]:
        """
        Parse text-based tool calls from content - matches server.ts exactly.
        
        Args:
            text: Text content containing tool calls
        
        Returns:
            List of parsed tool calls
        """
        import re
        import time
        
        parsed = []
        
        # Split by tool call boundaries - exact pattern from server.ts
        tool_call_pattern = r'<｜tool▁call▁begin｜>'
        tool_calls_text = re.split(tool_call_pattern, text)[1:]  # Remove first empty element
        
        for index, tool_call_text in enumerate(tool_calls_text):
            try:
                # Extract function name - exact pattern from server.ts line 2728
                function_match = re.search(r'^function<｜tool▁sep｜>([^\n]+)', tool_call_text)
                if not function_match:
                    continue
                
                function_name = function_match.group(1).strip()
                
                # Extract format (json/text/etc) - exact pattern from server.ts line 2734
                format_match = re.search(r'\n([a-z]+)\n', tool_call_text)
                format_type = format_match.group(1) if format_match else 'json'
                
                # Extract arguments - everything after the format line - server.ts line 2738
                args_start = tool_call_text.find('\n' + format_type + '\n') + len(format_type) + 2
                args_text = tool_call_text[args_start:].strip()
                
                # Clean up any trailing markers - server.ts line 2742
                args_text = re.sub(r'<｜[^｜]+｜>', '', args_text).strip()
                
                # Parse arguments based on format - server.ts lines 2745-2755
                parsed_args = {}
                if format_type == 'json':
                    try:
                        parsed_args = json.loads(args_text)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Failed to parse JSON args: {args_text}")
                        parsed_args = {"raw": args_text}
                else:
                    parsed_args = {"raw": args_text}
                
                # Create standardized tool call object - server.ts lines 2757-2766
                standardized_call = {
                    "index": index,
                    "id": f"call_{int(time.time() * 1000)}_{index}",  # Generate unique ID
                    "type": "function",
                    "function": {
                        "name": function_name,
                        "arguments": json.dumps(parsed_args)
                    }
                }
                
                parsed.append(standardized_call)
                logger.debug(f"Parsed tool call: {function_name} with args: {json.dumps(parsed_args)}")
                
            except Exception as error:
                logger.error(f"Error parsing tool call: {error}")
        
        # Convert to ToolCall objects
        tool_calls = []
        for call in parsed:
            tool_call = ToolCall(
                function=call["function"],
                arguments=call["function"]["arguments"]
            )
            tool_calls.append(tool_call)
        
        return tool_calls
