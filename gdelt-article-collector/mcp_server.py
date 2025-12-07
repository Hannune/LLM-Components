"""
MCP Server for GDELT Article Collector
Exposes GDELT search as MCP tool for AI agent integration
"""

import json
import asyncio
from typing import Any, Dict, List, Optional
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import mcp.types as types

from gdelt_wrapper import GDELTCollector


# Initialize collector
collector = GDELTCollector()

# Create MCP server
mcp_server = Server("gdelt-article-collector")


@mcp_server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available GDELT tools"""
    return [
        Tool(
            name="gdelt_search_articles",
            description=(
                "Search GDELT database for news articles with advanced filtering. "
                "GDELT monitors news from around the world in real-time. "
                "Supports filtering by keywords, domains, countries, themes, dates, and languages."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Keywords to search for (e.g., ['AI', 'machine learning'])"
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Domain filters (e.g., ['bbc.com', 'cnn.com'])"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format"
                    },
                    "countries": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Country codes (e.g., ['US', 'GB', 'KR'])"
                    },
                    "themes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "GDELT themes (e.g., ['ECON', 'ENV_CLIMATECHANGE'])"
                    },
                    "languages": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Language codes (e.g., ['eng', 'kor'])"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results (1-1000)",
                        "default": 50
                    },
                    "timespan": {
                        "type": "string",
                        "enum": ["1d", "7d", "30d"],
                        "description": "Quick timespan option (overrides dates)"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="gdelt_get_timeline",
            description=(
                "Get timeline view of article volume over time for specific topics. "
                "Useful for analyzing trends and understanding when stories broke."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Keywords to track over time"
                    },
                    "domains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Domain filters"
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date in YYYY-MM-DD format"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date in YYYY-MM-DD format"
                    },
                    "timespan": {
                        "type": "string",
                        "enum": ["1d", "7d", "30d"],
                        "description": "Quick timespan option"
                    },
                    "mode": {
                        "type": "string",
                        "enum": ["ArtList", "TimelineVol"],
                        "description": "Timeline mode",
                        "default": "TimelineVol"
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="gdelt_get_themes",
            description="Get list of available GDELT themes for filtering",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        ),
        Tool(
            name="gdelt_get_countries",
            description="Get list of common country codes for filtering",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]


@mcp_server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: Dict[str, Any]
) -> List[TextContent]:
    """Handle tool execution"""
    
    if name == "gdelt_search_articles":
        result = collector.search_articles(
            keywords=arguments.get("keywords"),
            domains=arguments.get("domains"),
            start_date=arguments.get("start_date"),
            end_date=arguments.get("end_date"),
            countries=arguments.get("countries"),
            themes=arguments.get("themes"),
            languages=arguments.get("languages"),
            max_results=arguments.get("max_results", 50),
            timespan=arguments.get("timespan"),
            sort_by="date"
        )
        
        # Format response for agent
        if result["success"]:
            # Truncate articles for token efficiency
            articles = result["articles"][:10]  # Show first 10
            
            summary = f"""Found {result['count']} articles
            
Filters applied: {json.dumps(result['filters'], indent=2)}

Top {len(articles)} results:
"""
            for i, article in enumerate(articles, 1):
                summary += f"\n{i}. {article.get('title', 'No title')}"
                summary += f"\n   Source: {article.get('domain', 'Unknown')}"
                summary += f"\n   URL: {article.get('url', 'No URL')}"
                if 'seendate' in article:
                    summary += f"\n   Date: {article['seendate']}"
                summary += "\n"
            
            return [TextContent(
                type="text",
                text=summary
            )]
        else:
            return [TextContent(
                type="text",
                text=f"Error: {result.get('error', 'Unknown error')}"
            )]
    
    elif name == "gdelt_get_timeline":
        result = collector.get_timeline(
            keywords=arguments.get("keywords"),
            domains=arguments.get("domains"),
            start_date=arguments.get("start_date"),
            end_date=arguments.get("end_date"),
            timespan=arguments.get("timespan"),
            mode=arguments.get("mode", "TimelineVol")
        )
        
        if result["success"]:
            timeline_text = f"""Timeline Analysis ({result['mode']})

Filters: {json.dumps(result['filters'], indent=2)}

Data points: {result['count']}

{json.dumps(result['timeline'][:20], indent=2)}
"""
            return [TextContent(
                type="text",
                text=timeline_text
            )]
        else:
            return [TextContent(
                type="text",
                text=f"Error: {result.get('error', 'Unknown error')}"
            )]
    
    elif name == "gdelt_get_themes":
        themes = collector.get_available_themes()
        return [TextContent(
            type="text",
            text=f"Available GDELT Themes:\n\n" + "\n".join(f"- {theme}" for theme in themes)
        )]
    
    elif name == "gdelt_get_countries":
        countries = collector.get_available_countries()
        return [TextContent(
            type="text",
            text=f"Common Country Codes:\n\n" + "\n".join(f"- {code}" for code in countries)
        )]
    
    else:
        raise ValueError(f"Unknown tool: {name}")


async def main():
    """Run MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await mcp_server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="gdelt-article-collector",
                server_version="1.0.0",
                capabilities=mcp_server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
