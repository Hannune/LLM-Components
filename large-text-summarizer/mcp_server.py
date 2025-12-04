"""
MCP Server for Large Text Summarizer

Exposes summarization functionality as an MCP tool that can be used by AI agents.
"""

import os
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
from summarizer import summarize_large_text, summarize_file

load_dotenv()

# Initialize server
app = Server("large-text-summarizer")

# Initialize LLM
llm = ChatOllama(
    model=os.getenv("LLM_MODEL", "qwen2.5:7b"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="summarize_text",
            description="""Summarize large text that exceeds LLM context window.
            
Uses map-reduce approach:
1. Splits text into optimal chunks
2. Summarizes each chunk
3. Combines summaries into final summary

Perfect for summarizing long documents, articles, transcripts, etc.
Works with text up to millions of tokens.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text to summarize"
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Target length of final summary in tokens (default: 500)",
                        "default": 500
                    },
                    "context_limit": {
                        "type": "integer",
                        "description": "LLM context window size (default: 4000)",
                        "default": 4000
                    }
                },
                "required": ["text"]
            }
        ),
        Tool(
            name="summarize_file",
            description="""Summarize text from a file using map-reduce approach.
            
Same functionality as summarize_text but reads from a file.
Supports .txt, .md, .log, and other text files.""",
            inputSchema={
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to text file to summarize"
                    },
                    "max_tokens": {
                        "type": "integer",
                        "description": "Target length of final summary in tokens (default: 500)",
                        "default": 500
                    }
                },
                "required": ["file_path"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Execute tool."""
    
    if name == "summarize_text":
        text = arguments["text"]
        max_tokens = arguments.get("max_tokens", 500)
        context_limit = arguments.get("context_limit", 4000)
        
        # Run summarization
        result = summarize_large_text(
            text=text,
            llm=llm,
            max_final_tokens=max_tokens,
            context_limit=context_limit,
            show_progress=False  # Disable progress in MCP mode
        )
        
        # Format response
        stats = result['stats']
        response = f"""Summary:
{result['summary']}

---
Statistics:
- Original: {stats['original_tokens']:,} tokens
- Chunks: {stats['num_chunks']}
- Compression: {stats['compression_ratio']*100:.1f}%
"""
        
        return [TextContent(type="text", text=response)]
    
    elif name == "summarize_file":
        file_path = arguments["file_path"]
        max_tokens = arguments.get("max_tokens", 500)
        
        # Check file exists
        if not os.path.exists(file_path):
            return [TextContent(
                type="text",
                text=f"Error: File not found: {file_path}"
            )]
        
        # Run summarization
        result = summarize_file(
            file_path=file_path,
            llm=llm,
            max_final_tokens=max_tokens
        )
        
        # Format response
        stats = result['stats']
        response = f"""Summary of {os.path.basename(file_path)}:
{result['summary']}

---
Statistics:
- Original: {stats['original_tokens']:,} tokens
- Chunks: {stats['num_chunks']}
- Compression: {stats['compression_ratio']*100:.1f}%
"""
        
        return [TextContent(type="text", text=response)]
    
    else:
        return [TextContent(
            type="text",
            text=f"Error: Unknown tool: {name}"
        )]


if __name__ == "__main__":
    import asyncio
    import mcp.server.stdio
    
    async def main():
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    
    asyncio.run(main())
