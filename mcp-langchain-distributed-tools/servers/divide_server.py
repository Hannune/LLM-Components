#!/usr/bin/env python3
"""
MCP Server for Division Operations
Runs as a standalone server that can be deployed on different machines
"""

import asyncio
import argparse
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
import mcp.types as types


# Create server instance
server = Server("divide-calculator")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="divide",
            description="Divide first number by second number",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "First number (dividend)"
                    },
                    "b": {
                        "type": "number",
                        "description": "Second number (divisor)"
                    }
                },
                "required": ["a", "b"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict | None) -> list[types.TextContent]:
    """Handle tool calls."""
    if name != "divide":
        raise ValueError(f"Unknown tool: {name}")
    
    if not arguments:
        raise ValueError("Missing arguments")
    
    a = arguments.get("a")
    b = arguments.get("b")
    
    if a is None or b is None:
        raise ValueError("Missing required arguments 'a' and 'b'")
    
    try:
        divisor = float(b)
        if divisor == 0:
            return [types.TextContent(
                type="text",
                text="Error: Division by zero is not allowed"
            )]
        
        result = float(a) / divisor
        return [types.TextContent(
            type="text",
            text=f"The division of {a} / {b} is {result}"
        )]
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid number arguments: {e}")

async def main():
    parser = argparse.ArgumentParser(description="Division MCP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8003, help="Port to bind to")
    args = parser.parse_args()
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="divide-calculator",
                server_version="0.1.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    asyncio.run(main())
