#!/usr/bin/env python3
"""
MCP Server for Addition Operations
Runs as a standalone server that can be deployed on different machines
"""

import asyncio
import argparse
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
from pydantic import AnyUrl
import mcp.types as types


# Create server instance
server = Server("add-calculator")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="add",
            description="Add two numbers together",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number"
                    }
                },
                "required": ["a", "b"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """Handle tool calls."""
    if name != "add":
        raise ValueError(f"Unknown tool: {name}")
    
    if not arguments:
        raise ValueError("Missing arguments")
    
    a = arguments.get("a")
    b = arguments.get("b")
    
    if a is None or b is None:
        raise ValueError("Missing required arguments 'a' and 'b'")
    
    try:
        result = float(a) + float(b)
        return [types.TextContent(
            type="text",
            text=f"The sum of {a} and {b} is {result}"
        )]
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid number arguments: {e}")

async def main():
    parser = argparse.ArgumentParser(description="Addition MCP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
    args = parser.parse_args()
    
    # For network deployment, you would use a different transport
    # This example uses stdio for simplicity, but you can extend it
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="add-calculator",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
