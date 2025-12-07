# GDELT Article Collector

> **Real-time news article collection from GDELT with advanced filtering**

FastAPI service + MCP tool for searching the [GDELT database](https://www.gdeltproject.org/) - the world's largest open database of human society. Monitor news from around the globe with filters for keywords, domains, countries, themes, and more.

## 🎯 Features

- **🔍 Advanced Search** - Keywords, domains, dates, countries, themes, languages
- **📊 Timeline Analysis** - Track article volume over time
- **📤 CSV Export** - Download results for further analysis
- **🤖 MCP Tool Support** - Direct integration with AI agents
- **⚡ FastAPI Service** - REST API with automatic docs
- **🐳 Docker Ready** - One-command deployment

## ⚠️ Recent Updates (2025-12-07)

The GDELT wrapper has been **completely rewritten** to fix critical API usage issues. If you're upgrading from an older version:

### What Changed
- **Fixed** incorrect `gdeltdoc` API usage (filters now properly initialized)
- **Fixed** timespan parameter handling (now uses built-in `"24h"`, `"7d"`, `"30d"`)
- **Updated** dependencies to resolve version conflicts
- **Verified** working with real GDELT API calls

### Migration
If you have existing code:
1. Update timespan from `"1d"` to `"24h"` (or keep `"7d"`, `"30d"`)
2. Rebuild Docker image: `docker compose build --no-cache`
3. Test your queries - they should now return results correctly

## 📦 Installation

### Quick Start (Docker)

```bash
# Clone or copy this directory
cd gdelt-article-collector

# Build and start the service
docker compose build
docker compose up -d

# Test the API
curl -X POST "http://localhost:8004/search" \
  -H "Content-Type: application/json" \
  -d '{"keywords": ["finance"], "timespan": "24h", "max_results": 3}'

# Access API docs
open http://localhost:8004/docs
```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the service
python main.py

# Or run MCP server for agent integration
python mcp_server.py
```

## 🚀 Usage

### 1. REST API

#### Search Articles

```bash
# Simple keyword search
curl -X POST http://localhost:8004/search \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["artificial intelligence"],
    "timespan": "7d",
    "max_results": 50
  }'

# Advanced filtering
curl -X POST http://localhost:8004/search \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["climate change", "renewable energy"],
    "domains": ["bbc.com", "reuters.com"],
    "countries": ["US", "GB", "DE"],
    "themes": ["ENV_CLIMATECHANGE"],
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "max_results": 100
  }'

# Korean news example
curl -X POST http://localhost:8004/search \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["인공지능"],
    "countries": ["KR"],
    "languages": ["kor"],
    "timespan": "30d",
    "max_results": 50
  }'
```

#### Get Timeline

```bash
# Track article volume over time
curl -X POST http://localhost:8004/timeline \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["AI"],
    "timespan": "30d",
    "mode": "TimelineVol"
  }'
```

#### Export to CSV

```bash
# First, get articles
ARTICLES=$(curl -X POST http://localhost:8004/search \
  -H "Content-Type: application/json" \
  -d '{"keywords": ["tech"], "timespan": "1d"}' | jq '.articles')

# Then export
curl -X POST http://localhost:8004/export \
  -H "Content-Type: application/json" \
  -d "{\"articles\": $ARTICLES, \"filename\": \"tech_news.csv\"}"

# Download the file
curl http://localhost:8004/download/20241207_123456_tech_news.csv -o tech_news.csv
```

#### Get Available Filters

```bash
# List GDELT themes
curl http://localhost:8004/themes

# List country codes
curl http://localhost:8004/countries
```

### 2. Python Client

```python
import requests

# Initialize client
API_URL = "http://localhost:8004"

def search_articles(keywords, timespan="7d", max_results=50):
    response = requests.post(f"{API_URL}/search", json={
        "keywords": keywords,
        "timespan": timespan,
        "max_results": max_results
    })
    return response.json()

# Example: Search tech news
result = search_articles(["AI", "machine learning"])

print(f"Found {result['count']} articles")
for article in result['articles'][:5]:
    print(f"- {article['title']}")
    print(f"  {article['url']}")
```

### 3. MCP Tool (Agent Integration)

Add to your MCP config (e.g., `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "gdelt": {
      "command": "python",
      "args": ["/path/to/gdelt-article-collector/mcp_server.py"]
    }
  }
}
```

Then agents can use:

```python
# Agent can call:
# gdelt_search_articles(keywords=["AI"], timespan="7d")
# gdelt_get_timeline(keywords=["climate"], timespan="30d")
# gdelt_get_themes()
# gdelt_get_countries()
```

## 📖 API Reference

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Service info and health check |
| POST | `/search` | Search articles with filters |
| POST | `/timeline` | Get timeline analysis |
| POST | `/export` | Export articles to CSV |
| GET | `/download/{filename}` | Download exported file |
| GET | `/themes` | List available GDELT themes |
| GET | `/countries` | List common country codes |
| GET | `/health` | Health check |
| GET | `/docs` | Interactive API documentation (Swagger UI) |

### Search Parameters

| Parameter | Type | Description | Example |
|-----------|------|-------------|---------|
| `keywords` | List[str] | Keywords to search | `["AI", "robotics"]` |
| `domains` | List[str] | Domain filters | `["bbc.com", "cnn.com"]` |
| `start_date` | str | Start date (YYYY-MM-DD) | `"2024-01-01"` |
| `end_date` | str | End date (YYYY-MM-DD) | `"2024-12-31"` |
| `countries` | List[str] | Country codes (ISO 3166-1 alpha-2) | `["US", "KR"]` |
| `themes` | List[str] | GDELT themes | `["ECON", "HEALTH"]` |
| `languages` | List[str] | Language codes | `["eng", "kor"]` |
| `max_results` | int | Maximum results (1-1000) | `100` |
| `timespan` | str | Quick timespan shortcut | `"24h"`, `"7d"`, `"30d"` |

### Available Themes

Common GDELT themes for filtering:

- `ECON` - Economy
- `ECON_BANKRUPTCY` - Bankruptcy news
- `ENV_CLIMATECHANGE` - Climate change
- `HEALTH` - Health news
- `TERROR` - Terrorism
- `WB_2737_TECHNOLOGY_AND_INNOVATION` - Technology
- `LEADER` - World leaders
- `MILITARY` - Military news
- `CRISIS` - Crisis events
- `SCANDAL` - Political scandals
- `DIPLOMACY` - Diplomatic events

See `/themes` endpoint for full list.

## 🏗️ Architecture

```
gdelt-article-collector/
├── gdelt_wrapper.py      # Core GDELT API wrapper (UPDATED)
├── main.py               # FastAPI service
├── mcp_server.py         # MCP tool server
├── Dockerfile            # Container definition
├── docker-compose.yml    # Service orchestration
├── requirements.txt      # Dependencies (UPDATED)
├── examples/             # Usage examples
│   ├── simple_search.py  # Basic search example
│   └── api_usage.py      # API client examples
├── test_collector.py     # Quick test script
└── README_UPDATED.md     # Detailed change notes
```

### Key Components

- **gdelt_wrapper.py**: Handles all GDELT API interactions using the `gdeltdoc` library
- **main.py**: FastAPI REST API server with automatic OpenAPI documentation
- **mcp_server.py**: MCP (Model Context Protocol) server for AI agent integration
- **examples/**: Working code examples demonstrating different use cases

## 🔧 Advanced Usage

### Custom Time Ranges

```python
# Specific date range
search_articles(
    keywords=["quantum computing"],
    start_date="2024-06-01",
    end_date="2024-06-30"
)

# Last 24 hours
search_articles(
    keywords=["breaking news"],
    timespan="24h"
)
```

### Multi-Domain Filtering

```python
# Only from trusted sources
search_articles(
    keywords=["election"],
    domains=[
        "bbc.com",
        "reuters.com",
        "apnews.com",
        "theguardian.com"
    ]
)
```

### Theme-Based Monitoring

```python
# Track economic news
search_articles(
    themes=["ECON", "ECON_BANKRUPTCY"],
    countries=["US"],
    timespan="7d"
)

# Environmental monitoring
search_articles(
    themes=["ENV_CLIMATECHANGE"],
    timespan="30d"
)
```

### Timeline Analysis

```python
# Analyze trend over time
timeline = get_timeline(
    keywords=["AI regulation"],
    timespan="30d",
    mode="TimelineVol"
)

# Plot with matplotlib
import matplotlib.pyplot as plt
dates = [t['date'] for t in timeline['timeline']]
counts = [t['count'] for t in timeline['timeline']]
plt.plot(dates, counts)
plt.show()
```

## 🔗 Integration Examples

### With LangChain Agent

```python
from langchain.agents import initialize_agent
from langchain.tools import Tool

def gdelt_tool(query: str) -> str:
    result = requests.post("http://localhost:8004/search", json={
        "keywords": query.split(),
        "timespan": "7d",
        "max_results": 10
    })
    data = result.json()
    return f"Found {data['count']} articles: " + str(data['articles'][:3])

tool = Tool(
    name="GDELT News Search",
    func=gdelt_tool,
    description="Search global news articles from GDELT database"
)

agent = initialize_agent([tool], llm, agent="zero-shot-react-description")
agent.run("What's the latest news about AI?")
```

### With CrewAI

```python
from crewai import Agent, Task, Tool

gdelt_search = Tool(
    name="GDELT Search",
    description="Search news articles from GDELT",
    func=lambda q: search_articles(q.split())
)

researcher = Agent(
    role="News Researcher",
    goal="Find and analyze recent news",
    tools=[gdelt_search]
)

task = Task(
    description="Research latest AI developments",
    agent=researcher
)
```

## 📊 Response Format

### Search Response

```json
{
  "success": true,
  "articles": [
    {
      "title": "Article Title",
      "url": "https://example.com/article",
      "domain": "example.com",
      "seendate": "2024-12-07T10:30:00Z",
      "language": "eng",
      "sourcecountry": "US"
    }
  ],
  "count": 42,
  "filters": {
    "keywords": "AI OR \"machine learning\"",
    "timespan": "7d"
  },
  "columns": ["title", "url", "domain", "seendate", "language"]
}
```

## 🛠️ Development

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

### Adding New Features

1. Update `gdelt_wrapper.py` for new GDELT functionality
2. Add endpoint in `main.py`
3. Add MCP tool in `mcp_server.py` (if needed)
4. Update README with examples

## 🐛 Troubleshooting

### Common Issues

#### 1. "No articles found" or Empty Results
- **Check timespan format**: Use `"24h"`, `"7d"`, or `"30d"` (NOT `"1d"`)
- Keywords might be too specific - try broader terms
- Verify domain names are correct (e.g., "bbc.com" not "www.bbc.com")
- Check GDELT's data availability for your region/language

#### 2. Dependency Errors
If you get `ModuleNotFoundError` or version conflicts:
```bash
# Reinstall with correct versions
pip install -r requirements.txt --upgrade

# Or rebuild Docker
docker compose build --no-cache
```

#### 3. API Not Working After Update
If upgrading from old version:
```bash
# Stop old containers
docker compose down

# Remove old images
docker rmi gdelt-article-collector-gdelt-collector

# Rebuild fresh
docker compose build --no-cache
docker compose up -d
```

#### 4. Rate Limiting

GDELT API has rate limits. If you hit them:
- Reduce `max_results`
- Add delays between requests
- Use more specific filters to reduce data volume

#### 5. Docker Issues

```bash
# Check logs
docker compose logs -f

# Restart service
docker compose restart

# Rebuild
docker compose build --no-cache
docker compose up -d
```

#### 6. Test Your Installation

Run the test script to verify everything works:
```bash
# Inside Docker container
docker exec -it gdelt-article-collector python test_collector.py

# Or locally
python3 test_collector.py
```

## 📝 License

MIT License - See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch
3. Add tests for new features
4. Submit pull request

## 🔗 Resources

- [GDELT Project](https://www.gdeltproject.org/)
- [gdeltdoc Documentation](https://github.com/alex9smith/gdelt-doc-api)
- [GDELT API Guide](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/)
- [MCP Documentation](https://github.com/modelcontextprotocol)

## 📧 Support

For issues or questions:
- Open an issue on GitHub
- Check existing issues for solutions
- Review GDELT documentation

---

**Built for real-time global news monitoring and analysis**
