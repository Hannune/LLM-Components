"""
FastAPI Service for GDELT Article Collection
Provides REST API endpoints for searching and exporting GDELT articles
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
import os
from datetime import datetime

from gdelt_wrapper import GDELTCollector


app = FastAPI(
    title="GDELT Article Collector API",
    description="Search and collect news articles from GDELT database with advanced filtering",
    version="1.0.0"
)

collector = GDELTCollector()


# Request Models
class SearchRequest(BaseModel):
    keywords: Optional[List[str]] = Field(None, description="Keywords to search for")
    domains: Optional[List[str]] = Field(None, description="Domain filters (e.g., ['bbc.com'])")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    countries: Optional[List[str]] = Field(None, description="Country codes (e.g., ['US', 'KR'])")
    themes: Optional[List[str]] = Field(None, description="GDELT themes (e.g., ['ECON'])")
    languages: Optional[List[str]] = Field(None, description="Language codes (e.g., ['eng'])")
    max_results: int = Field(250, ge=1, le=1000, description="Maximum results")
    timespan: Optional[str] = Field(None, description="Quick timespan: '1d', '7d', '30d'")
    sort_by: str = Field("date", description="Sort by: 'date' or 'relevance'")
    
    class Config:
        json_schema_extra = {
            "example": {
                "keywords": ["artificial intelligence", "machine learning"],
                "domains": ["bbc.com", "cnn.com"],
                "timespan": "7d",
                "countries": ["US", "GB"],
                "max_results": 100
            }
        }


class TimelineRequest(BaseModel):
    keywords: Optional[List[str]] = Field(None, description="Keywords to search for")
    domains: Optional[List[str]] = Field(None, description="Domain filters")
    start_date: Optional[str] = Field(None, description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="End date (YYYY-MM-DD)")
    timespan: Optional[str] = Field(None, description="Quick timespan: '1d', '7d', '30d'")
    mode: str = Field("ArtList", description="Mode: 'ArtList' or 'TimelineVol'")


class ExportRequest(BaseModel):
    articles: List[Dict[str, Any]] = Field(..., description="Articles to export")
    filename: str = Field("gdelt_export.csv", description="Output filename")


# Response Models
class SearchResponse(BaseModel):
    success: bool
    articles: List[Dict[str, Any]]
    count: int
    filters: Dict[str, Any]
    columns: Optional[List[str]] = None
    message: Optional[str] = None
    error: Optional[str] = None


class TimelineResponse(BaseModel):
    success: bool
    timeline: List[Dict[str, Any]]
    count: int
    mode: str
    filters: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Endpoints
@app.get("/")
async def root():
    """Health check and API info"""
    return {
        "service": "GDELT Article Collector",
        "status": "running",
        "version": "1.0.0",
        "endpoints": {
            "search": "/search",
            "timeline": "/timeline",
            "export": "/export",
            "themes": "/themes",
            "countries": "/countries"
        }
    }


@app.post("/search", response_model=SearchResponse)
async def search_articles(request: SearchRequest):
    """
    Search GDELT articles with filters
    
    Example:
    ```
    POST /search
    {
        "keywords": ["climate change"],
        "domains": ["bbc.com"],
        "timespan": "7d",
        "max_results": 50
    }
    ```
    """
    result = collector.search_articles(
        keywords=request.keywords,
        domains=request.domains,
        start_date=request.start_date,
        end_date=request.end_date,
        countries=request.countries,
        themes=request.themes,
        languages=request.languages,
        max_results=request.max_results,
        timespan=request.timespan,
        sort_by=request.sort_by
    )
    
    return result


@app.post("/timeline", response_model=TimelineResponse)
async def get_timeline(request: TimelineRequest):
    """
    Get timeline of articles over time
    
    Example:
    ```
    POST /timeline
    {
        "keywords": ["AI"],
        "timespan": "30d",
        "mode": "TimelineVol"
    }
    ```
    """
    result = collector.get_timeline(
        keywords=request.keywords,
        domains=request.domains,
        start_date=request.start_date,
        end_date=request.end_date,
        timespan=request.timespan,
        mode=request.mode
    )
    
    return result


@app.post("/export")
async def export_articles(request: ExportRequest):
    """
    Export articles to CSV
    
    Example:
    ```
    POST /export
    {
        "articles": [...],
        "filename": "my_articles.csv"
    }
    ```
    """
    # Create exports directory if needed
    os.makedirs("exports", exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"exports/{timestamp}_{request.filename}"
    
    result = collector.export_to_csv(request.articles, filename)
    
    if result["success"]:
        return {
            "success": True,
            "filepath": filename,
            "count": result["count"],
            "download_url": f"/download/{os.path.basename(filename)}"
        }
    else:
        raise HTTPException(status_code=500, detail=result["error"])


@app.get("/download/{filename}")
async def download_file(filename: str):
    """Download exported CSV file"""
    filepath = f"exports/{filename}"
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        filepath,
        media_type="text/csv",
        filename=filename
    )


@app.get("/themes")
async def get_themes():
    """Get list of available GDELT themes"""
    return {
        "themes": collector.get_available_themes(),
        "description": "Common GDELT themes for filtering"
    }


@app.get("/countries")
async def get_countries():
    """Get list of common country codes"""
    return {
        "countries": collector.get_available_countries(),
        "description": "Common country codes (ISO 3166-1 alpha-2)"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    port = int(os.getenv("SERVICE_PORT", 8004))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
