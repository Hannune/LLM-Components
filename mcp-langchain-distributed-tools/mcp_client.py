#!/usr/bin/env python3
"""
MCP Client for connecting to multiple MCP servers
"""

import asyncio
import subprocess
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    name: str
    host: str
    port: int
    command: List[str]
    tools: List[str]


class MCPClientManager:
    """Manages connections to multiple MCP servers"""
    
    def __init__(self, server_configs: List[MCPServerConfig]):
        self.server_configs = server_configs
        self.clients: Dict[str, ClientSession] = {}
        self.available_tools: Dict[str, str] = {}  # tool_name -> server_name
    
    async def connect_to_servers(self):
        """Connect to all configured MCP servers"""
        for config in self.server_configs:
            try:
                # For stdio-based servers, we use subprocess to start them
                server_params = StdioServerParameters(
                    command=config.command[0],
                    args=config.command[1:] if len(config.command) > 1 else [],
                )
                
                stdio_transport = stdio_client(server_params)
                stdio, write = await stdio_transport.__aenter__()
                
                session = ClientSession(stdio, write)
                await session.initialize()
                
                self.clients[config.name] = session
                
                # Get available tools from this server
                tools_result = await session.list_tools()
                for tool in tools_result.tools:
                    self.available_tools[tool.name] = config.name
                    
                print(f"Connected to {config.name} server")
                    
            except Exception as e:
                print(f"Failed to connect to {config.name}: {e}")
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """Call a tool on the appropriate MCP server"""
        if tool_name not in self.available_tools:
            return f"Tool '{tool_name}' not found in any connected server"
        
        server_name = self.available_tools[tool_name]
        client = self.clients.get(server_name)
        
        if not client:
            return f"Server '{server_name}' not connected"
        
        try:
            result = await client.call_tool(tool_name, arguments)
            if result.content and len(result.content) > 0:
                return result.content[0].text
            return "No result returned"
        except Exception as e:
            return f"Error calling tool '{tool_name}': {e}"
    
    def get_available_tools(self) -> Dict[str, str]:
        """Get mapping of available tools to their servers"""
        return self.available_tools.copy()
    
    async def close_connections(self):
        """Close all server connections"""
        for client in self.clients.values():
            try:
                await client.close()
            except:
                pass
