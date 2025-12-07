# GDELT Article Collector - Updated Version

This is the updated and working version of the GDELT Article Collector, rebuilt using the correct `gdeltdoc` API pattern.

## What Changed

The main issue with the previous version was incorrect usage of the `gdeltdoc` library. This version has been fixed to:

1. **Correct Filter Initialization**: Using `Filters(**kwargs)` to properly initialize filters
2. **Proper Timespan Usage**: Using the library's built-in `timespan` parameter (e.g., "24h", "7d", "30d")
3. **Simplified API Calls**: Removing the incorrect `max_records` parameter in favor of client-side limiting
4. **Updated Dependencies**: Fixed version conflicts in requirements.txt

## Quick Start

### Using Docker (Recommended)

```bash
# Build and start the service
docker compose up -d

# Test the API
curl -X POST "http://localhost:8004/search" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["finance"],
    "timespan": "24h",
    "max_results": 3
  }'

# Stop the service
docker compose down
```

### Using Python Directly

```python
from gdelt_wrapper import GDELTCollector

# Initialize collector
collector = GDELTCollector()

# Search for articles
result = collector.search_articles(
    keywords=["finance"],
    timespan="24h",
    max_results=3
)

# Display results
if result["success"]:
    for article in result["articles"]:
        print(f"Title: {article['title']}")
        print(f"URL: {article['url']}")
        print(f"Date: {article['seendate']}")
        print("-" * 50)
```

## API Endpoints

The service runs on port 8004 and provides the following endpoints:

### 1. Search Articles
```bash
POST /search
{
  "keywords": ["artificial intelligence"],
  "timespan": "7d",
  "max_results": 10,
  "domains": ["bbc.com", "cnn.com"],
  "countries": ["US", "GB"],
  "languages": ["eng"]
}
```

### 2. Get Timeline
```bash
POST /timeline
{
  "keywords": ["climate change"],
  "timespan": "30d",
  "mode": "TimelineVol"
}
```

### 3. Export to CSV
```bash
POST /export
{
  "articles": [...],
  "filename": "my_export.csv"
}
```

### 4. Get Available Filters
```bash
GET /themes       # Get available GDELT themes
GET /countries    # Get country codes
```

### 5. Health Check
```bash
GET /health       # Check service status
GET /             # API info
```

## Examples

### Example 1: Simple Search
See `examples/simple_search.py`
```bash
python3 examples/simple_search.py
```

### Example 2: API Usage
See `examples/api_usage.py`
```bash
python3 examples/api_usage.py
```

## Supported Parameters

### Timespan Options
- `"24h"` - Last 24 hours
- `"7d"` - Last 7 days
- `"30d"` - Last 30 days
- Or use custom `start_date` and `end_date` (YYYY-MM-DD format)

### Filter Options
- `keywords`: List of search terms
- `domains`: Filter by website domains
- `countries`: Filter by country codes (ISO 3166-1 alpha-2)
- `themes`: Filter by GDELT themes
- `languages`: Filter by language codes
- `max_results`: Limit number of results (default: 250)
- `sort_by`: Sort by "date" or "relevance"

## Common GDELT Themes
- `ECON` - Economy
- `ENV_CLIMATECHANGE` - Climate Change
- `HEALTH` - Health
- `TERROR` - Terrorism
- `WB_2737_TECHNOLOGY_AND_INNOVATION` - Technology
- `MILITARY` - Military
- `CRISIS` - Crisis
- `SCANDAL` - Scandal

## Testing

The collector has been tested and verified working with:
- Finance news search (24h timespan)
- Multiple keyword queries
- Domain filtering
- Country-based filtering

## Dependencies

Core dependencies:
- `gdeltdoc==1.5` - GDELT document search library
- `pandas>=2.0.0` - Data manipulation
- `fastapi>=0.115.0` - REST API framework
- `uvicorn>=0.30.0` - ASGI server
- `pydantic>=2.7.2` - Data validation

## Files Modified

1. `gdelt_wrapper.py` - Fixed filter initialization and API usage
2. `requirements.txt` - Updated dependency versions to resolve conflicts
3. `examples/` - Added working example scripts

## License

Same as original project.
