"""
Crawl4AI MCP Service - LOCAL LLM

FastAPI wrapper around Crawl4AI for web scraping with stealth mode,
basic mode, and RSS feed support.
"""

import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, HttpUrl
import asyncio
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import LLMExtractionStrategy
import feedparser
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Crawl4AI MCP Service")


class CrawlRequest(BaseModel):
    """Request model for crawling."""
    url: HttpUrl
    extract_content: bool = True
    extract_links: bool = False
    llm_extract: bool = False
    llm_prompt: Optional[str] = None


class CrawlResponse(BaseModel):
    """Response model from crawler."""
    success: bool
    url: str
    content: Optional[str] = None
    links: Optional[List[str]] = None
    llm_extracted: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class RSSRequest(BaseModel):
    """Request model for RSS feeds."""
    url: HttpUrl
    max_entries: int = 10


class RSSResponse(BaseModel):
    """Response model from RSS parser."""
    success: bool
    feed_title: Optional[str] = None
    entries: List[Dict[str, Any]]
    error: Optional[str] = None


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "crawl4ai"
    }


@app.post("/crawl/basic", response_model=CrawlResponse)
async def crawl_basic(request: CrawlRequest):
    """
    Basic web crawling mode.
    
    Standard crawling without anti-detection measures.
    Faster but may be blocked by some sites.
    """
    try:
        async with AsyncWebCrawler(verbose=False) as crawler:
            result = await crawler.arun(
                url=str(request.url),
                bypass_cache=True
            )
            
            response_data = {
                "success": True,
                "url": str(request.url),
                "content": result.markdown if request.extract_content else None,
                "links": result.links.get("external", []) if request.extract_links else None
            }
            
            # LLM extraction if requested
            if request.llm_extract and request.llm_prompt:
                # Use local LLM for extraction
                llm_strategy = LLMExtractionStrategy(
                    provider="ollama/qwen2.5:7b",
                    api_base=os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"),
                    instruction=request.llm_prompt
                )
                extracted = await crawler.arun(
                    url=str(request.url),
                    extraction_strategy=llm_strategy
                )
                response_data["llm_extracted"] = extracted.extracted_content
            
            return CrawlResponse(**response_data)
            
    except Exception as e:
        return CrawlResponse(
            success=False,
            url=str(request.url),
            error=str(e)
        )


@app.post("/crawl/stealth", response_model=CrawlResponse)
async def crawl_stealth(request: CrawlRequest):
    """
    Stealth web crawling mode.
    
    Uses anti-detection techniques to avoid being blocked.
    Slower but more reliable for protected sites.
    """
    try:
        # Stealth configuration
        browser_config = {
            "headless": True,
            "viewport": {"width": 1920, "height": 1080},
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        async with AsyncWebCrawler(
            verbose=False,
            browser_type="chromium",
            **browser_config
        ) as crawler:
            result = await crawler.arun(
                url=str(request.url),
                bypass_cache=True,
                wait_for="networkidle",  # Wait for page to fully load
                delay_before_return_html=2.0  # Extra delay for JS rendering
            )
            
            response_data = {
                "success": True,
                "url": str(request.url),
                "content": result.markdown if request.extract_content else None,
                "links": result.links.get("external", []) if request.extract_links else None
            }
            
            # LLM extraction if requested
            if request.llm_extract and request.llm_prompt:
                llm_strategy = LLMExtractionStrategy(
                    provider="ollama/qwen2.5:7b",
                    api_base=os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434"),
                    instruction=request.llm_prompt
                )
                extracted = await crawler.arun(
                    url=str(request.url),
                    extraction_strategy=llm_strategy
                )
                response_data["llm_extracted"] = extracted.extracted_content
            
            return CrawlResponse(**response_data)
            
    except Exception as e:
        return CrawlResponse(
            success=False,
            url=str(request.url),
            error=str(e)
        )


@app.post("/rss/fetch", response_model=RSSResponse)
async def fetch_rss(request: RSSRequest):
    """
    Fetch and parse RSS feed.
    
    Returns feed metadata and entries.
    """
    try:
        feed = feedparser.parse(str(request.url))
        
        if feed.bozo:  # Error parsing feed
            return RSSResponse(
                success=False,
                entries=[],
                error=f"Failed to parse RSS feed: {feed.bozo_exception}"
            )
        
        entries = []
        for entry in feed.entries[:request.max_entries]:
            entries.append({
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "published": entry.get("published", ""),
                "summary": entry.get("summary", ""),
                "author": entry.get("author", "")
            })
        
        return RSSResponse(
            success=True,
            feed_title=feed.feed.get("title", ""),
            entries=entries
        )
        
    except Exception as e:
        return RSSResponse(
            success=False,
            entries=[],
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVICE_PORT", 8003))
    uvicorn.run(app, host="0.0.0.0", port=port)
