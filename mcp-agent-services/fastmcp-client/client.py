"""
FastMCP Client with Streamable Support - LOCAL LLM AGENTS

Client to interact with all 3 MCP agent services:
- Open Interpreter
- GPT Researcher  
- Crawl4AI

Supports streaming responses for real-time feedback.
"""

import asyncio
import os
from typing import AsyncGenerator, Optional, Dict, Any
import httpx
from fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv()

# Service endpoints
OPEN_INTERPRETER_URL = os.getenv("OPEN_INTERPRETER_URL", "http://localhost:8001")
GPT_RESEARCHER_URL = os.getenv("GPT_RESEARCHER_URL", "http://localhost:8002")
CRAWL4AI_URL = os.getenv("CRAWL4AI_URL", "http://localhost:8003")


class MCPAgentClient:
    """Client for MCP agent services with streaming support."""
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=300.0)
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    # Open Interpreter methods
    async def interpret(
        self, 
        command: str,
        context: Optional[str] = None,
        auto_run: Optional[bool] = None,
        stream: bool = False
    ) -> AsyncGenerator[str, None] | Dict[str, Any]:
        """
        Execute command with Open Interpreter.
        
        Args:
            command: Natural language command
            context: Optional context
            auto_run: Auto-execute code without asking
            stream: Stream response chunks
        """
        payload = {
            "command": command,
            "context": context,
            "auto_run": auto_run
        }
        
        if stream:
            async for chunk in self._stream_post(
                f"{OPEN_INTERPRETER_URL}/interpret", 
                payload
            ):
                yield chunk
        else:
            response = await self.client.post(
                f"{OPEN_INTERPRETER_URL}/interpret",
                json=payload
            )
            return response.json()
    
    # GPT Researcher methods
    async def research(
        self,
        query: str,
        report_type: str = "research_report",
        stream: bool = False
    ) -> AsyncGenerator[str, None] | Dict[str, Any]:
        """
        Start research task with GPT Researcher.
        
        Args:
            query: Research question
            report_type: Type of report to generate
            stream: Stream research progress
        """
        payload = {
            "query": query,
            "report_type": report_type
        }
        
        if stream:
            async for chunk in self._stream_post(
                f"{GPT_RESEARCHER_URL}/research",
                payload
            ):
                yield chunk
        else:
            response = await self.client.post(
                f"{GPT_RESEARCHER_URL}/research",
                json=payload
            )
            return response.json()
    
    async def get_research_files(self, task_id: str) -> Dict[str, Any]:
        """Get research output files."""
        response = await self.client.get(
            f"{GPT_RESEARCHER_URL}/research/{task_id}/files"
        )
        return response.json()
    
    # Crawl4AI methods
    async def crawl_basic(
        self,
        url: str,
        extract_content: bool = True,
        extract_links: bool = False,
        llm_extract: bool = False,
        llm_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Crawl URL in basic mode (fast, may be blocked).
        """
        payload = {
            "url": url,
            "extract_content": extract_content,
            "extract_links": extract_links,
            "llm_extract": llm_extract,
            "llm_prompt": llm_prompt
        }
        
        response = await self.client.post(
            f"{CRAWL4AI_URL}/crawl/basic",
            json=payload
        )
        return response.json()
    
    async def crawl_stealth(
        self,
        url: str,
        extract_content: bool = True,
        extract_links: bool = False,
        llm_extract: bool = False,
        llm_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Crawl URL in stealth mode (slower, more reliable).
        """
        payload = {
            "url": url,
            "extract_content": extract_content,
            "extract_links": extract_links,
            "llm_extract": llm_extract,
            "llm_prompt": llm_prompt
        }
        
        response = await self.client.post(
            f"{CRAWL4AI_URL}/crawl/stealth",
            json=payload
        )
        return response.json()
    
    async def fetch_rss(self, url: str, max_entries: int = 10) -> Dict[str, Any]:
        """Fetch RSS feed."""
        payload = {
            "url": url,
            "max_entries": max_entries
        }
        
        response = await self.client.post(
            f"{CRAWL4AI_URL}/rss/fetch",
            json=payload
        )
        return response.json()
    
    # Helper methods
    async def _stream_post(
        self, 
        url: str, 
        payload: Dict[str, Any]
    ) -> AsyncGenerator[str, None]:
        """Stream POST response."""
        async with self.client.stream("POST", url, json=payload) as response:
            async for chunk in response.aiter_text():
                if chunk:
                    yield chunk
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all services."""
        services = {
            "open_interpreter": f"{OPEN_INTERPRETER_URL}/health",
            "gpt_researcher": f"{GPT_RESEARCHER_URL}/health",
            "crawl4ai": f"{CRAWL4AI_URL}/health"
        }
        
        results = {}
        for name, url in services.items():
            try:
                response = await self.client.get(url)
                results[name] = response.status_code == 200
            except:
                results[name] = False
        
        return results


# Example usage
async def main():
    """Example usage of MCP agent client."""
    client = MCPAgentClient()
    
    try:
        # Health check
        print("Checking service health...")
        health = await client.health_check_all()
        for service, status in health.items():
            print(f"  {service}: {'✓' if status else '✗'}")
        
        # Example 1: Open Interpreter
        print("\n=== Open Interpreter Example ===")
        result = await client.interpret(
            "Calculate the fibonacci sequence up to 10"
        )
        print(f"Result: {result.get('output', 'N/A')}")
        
        # Example 2: Crawl4AI (Basic)
        print("\n=== Crawl4AI Basic Example ===")
        crawl_result = await client.crawl_basic(
            url="https://example.com",
            extract_content=True
        )
        print(f"Content length: {len(crawl_result.get('content', ''))}")
        
        # Example 3: Streaming
        print("\n=== Streaming Example ===")
        async for chunk in client.interpret(
            "List files in current directory",
            stream=True
        ):
            print(chunk, end='', flush=True)
        
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
