# MCP Agent Services - LOCAL LLM POWERED

**Three dockerized AI agent services accessible via FastMCP with streaming support - 100% LOCAL**

Run Open Interpreter, GPT Researcher, and Crawl4AI as microservices, all powered by local LLMs (Ollama), with a unified FastMCP client for easy integration.

## Architecture

```
┌────────────────────────────────────────────────────────┐
│                FastMCP Client                          │
│           (Streamable Support)                         │
└────────────┬──────────────┬──────────────┬─────────────┘
             │              │              │
    ┌────────▼──────┐  ┌───▼──────┐  ┌───▼──────────┐
    │ Open          │  │ GPT       │  │ Crawl4AI     │
    │ Interpreter   │  │ Researcher│  │ Service      │
    │ :8001         │  │ :8002     │  │ :8003        │
    │               │  │           │  │              │
    │ FastAPI       │  │ FastAPI   │  │ FastAPI      │
    │ + Docker      │  │ + Docker  │  │ + Docker     │
    └───────┬───────┘  └─────┬─────┘  └───────┬──────┘
            │                │                 │
            └────────────────┴─────────────────┘
                             │
                    ┌────────▼────────┐
                    │  Ollama (Host)  │
                    │  LOCAL LLMs     │
                    │  :11434         │
                    └─────────────────┘
```

## Services

### 1. Open Interpreter Service (:8001)
- **Purpose**: Execute code via natural language
- **Features**:
  - Config-based permissions (auto_run, safe_mode)
  - Python code execution
  - Local LLM powered
  - Sandboxed in Docker container
- **Endpoints**:
  - `POST /interpret` - Execute command
  - `POST /reset` - Clear history
  - `GET /config` - View settings
  - `GET /health` - Health check

### 2. GPT Researcher Service (:8002)
- **Purpose**: Automated research with **file upload support**
- **Features**:
  - 📤 **Upload files** for document-based research
  - Deep research on any topic
  - Session-based file management
  - Generates comprehensive reports
  - Auto-cleanup of old sessions
  - Local LLM powered (Ollama)
- **Endpoints**:
  - `POST /research` - Start research (with optional file uploads)
  - `POST /cleanup` - Manual cleanup
  - `DELETE /session/{id}` - Delete session
  - `GET /` - Health check

### 3. Crawl4AI Service (:8003)
- **Purpose**: Web scraping with anti-detection
- **Features**:
  - **Stealth mode** - Anti-detection crawling
  - **Basic mode** - Fast general crawling
  - **RSS support** - Feed parsing
  - Local LLM extraction (optional)
- **Endpoints**:
  - `POST /crawl/basic` - Basic crawl
  - `POST /crawl/stealth` - Stealth crawl
  - `POST /rss/fetch` - Fetch RSS
  - `GET /health` - Health check

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Ollama running on host
- Local LLM model (e.g., `ollama pull qwen2.5:7b`)

### 1. Setup Environment
```bash
cp .env.example .env
# Ensure Ollama is running on host
ollama serve
```

### 2. Setup GPT Researcher (if needed)
```bash
cd gpt-researcher-service
# Follow SETUP.md to clone from your GitHub
```

### 3. Start All Services
```bash
docker-compose up --build -d
```

### 4. Verify Services
```bash
# Check logs
docker-compose logs -f

# Health check
curl http://localhost:8001/health  # Open Interpreter
curl http://localhost:8002/health  # GPT Researcher
curl http://localhost:8003/health  # Crawl4AI
```

### 5. Use FastMCP Client
```bash
cd fastmcp-client
pip install -r requirements.txt
python client.py
```

## Usage

### FastMCP Client (Python)

```python
from client import MCPAgentClient
import asyncio

async def main():
    client = MCPAgentClient()
    
    # Open Interpreter
    result = await client.interpret(
        "Calculate fibonacci sequence up to 10"
    )
    print(result['output'])
    
    # Crawl4AI (Stealth)
    content = await client.crawl_stealth(
        url="https://example.com",
        extract_content=True
    )
    print(content['content'][:200])
    
    # GPT Researcher
    research = await client.research(
        query="What are the latest trends in AI?",
        stream=True
    )
    async for chunk in research:
        print(chunk, end='', flush=True)
    
    await client.close()

asyncio.run(main())
```

### Direct HTTP API

#### Open Interpreter
```bash
curl -X POST http://localhost:8001/interpret \
  -H "Content-Type: application/json" \
  -d '{
    "command": "List files in current directory",
    "auto_run": false
  }'
```

#### Crawl4AI (Basic Mode)
```bash
curl -X POST http://localhost:8003/crawl/basic \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com",
    "extract_content": true
  }'
```

#### Crawl4AI (Stealth Mode)
```bash
curl -X POST http://localhost:8003/crawl/stealth \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://protected-site.com",
    "extract_content": true,
    "llm_extract": true,
    "llm_prompt": "Extract all product names and prices"
  }'
```

#### RSS Feed
```bash
curl -X POST http://localhost:8003/rss/fetch \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/feed.xml",
    "max_entries": 5
  }'
```

## Configuration

### Open Interpreter (config.yaml)

```yaml
permissions:
  auto_run: false      # Auto-execute code
  safe_mode: 'ask'     # 'ask', 'auto', or 'off'

llm:
  model: 'ollama/qwen2.5:7b'
  api_base: 'http://host.docker.internal:11434'
  temperature: 0.1
```

**Safety Levels:**
- `safe_mode: 'ask'` - Prompts before running code (safest)
- `safe_mode: 'auto'` - Only safe operations
- `safe_mode: 'off'` - No restrictions (use with caution!)

### Docker Resource Limits

Edit `docker-compose.yml` to add resource limits:
```yaml
services:
  open-interpreter:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

## Streaming Support

The FastMCP client supports streaming for real-time feedback:

```python
# Streaming example
async for chunk in client.interpret(
    "Generate a long report",
    stream=True
):
    print(chunk, end='', flush=True)
```

## Use Cases

### 1. Automated Research Pipeline
```python
# Research → Crawl → Analyze
query = "Latest AI breakthroughs"
research = await client.research(query)
urls = extract_urls_from_research(research)

for url in urls:
    content = await client.crawl_stealth(url)
    analysis = await client.interpret(
        f"Analyze this content: {content}"
    )
```

### 2. Data Collection + Processing
```python
# Crawl RSS → Extract → Process with code
feeds = await client.fetch_rss("https://news.site/rss")
for entry in feeds['entries']:
    content = await client.crawl_basic(entry['link'])
    result = await client.interpret(
        f"Summarize and save: {content}"
    )
```

### 3. Stealth Web Scraping
```python
# Anti-detection scraping with LLM extraction
result = await client.crawl_stealth(
    url="https://protected-site.com",
    llm_extract=True,
    llm_prompt="Extract all product details as JSON"
)
```

## Management

### Start Services
```bash
docker-compose up -d
```

### Stop Services
```bash
docker-compose down
```

### View Logs
```bash
docker-compose logs -f open-interpreter
docker-compose logs -f gpt-researcher
docker-compose logs -f crawl4ai
```

### Rebuild After Changes
```bash
docker-compose up --build -d
```

### Clean Volumes
```bash
docker-compose down -v
```

## Troubleshooting

### Services won't start
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Check Docker logs
docker-compose logs
```

### Open Interpreter permission errors
- Check `config.yaml` permissions settings
- Verify `auto_run` and `safe_mode` values
- Check Docker container has necessary permissions

### Crawl4AI stealth mode fails
- Increase `shm_size` in docker-compose.yml
- Check Playwright installation in container
- Verify network connectivity

### GPT Researcher missing
- Follow `gpt-researcher-service/SETUP.md`
- Clone from your GitHub repository
- Ensure Dockerfile exists

### Cannot connect to Ollama
- Verify `extra_hosts` in docker-compose.yml
- Test: `curl http://host.docker.internal:11434`
- Ensure Ollama running: `ollama serve`

## Security Considerations

### Open Interpreter
- **Runs in container** - Has access to container filesystem only
- **Configure permissions** - Use `safe_mode: 'ask'` for safety
- **Don't auto-run** - Set `auto_run: false` unless trusted

### Crawl4AI
- **Rate limiting** - Be respectful of target sites
- **Legal compliance** - Only crawl allowed content
- **User agents** - Stealth mode uses realistic UA strings

### Network
- **Internal network** - Services communicate via Docker network
- **Host access** - Only Ollama is accessed on host
- **No external APIs** - Everything runs locally

## Performance

| Service | Startup Time | Memory Usage | CPU Usage |
|---------|-------------|--------------|-----------|
| Open Interpreter | ~10s | ~500MB | Low |
| GPT Researcher | ~15s | ~1GB | Medium |
| Crawl4AI | ~20s | ~1.5GB | Medium-High |

**Total System Requirements:**
- RAM: 4GB minimum (8GB recommended)
- Disk: 5GB for images
- CPU: 4 cores recommended
- GPU: Optional (for Ollama)

## Advantages

- **100% Local** - No API costs, complete privacy
- **Microservices** - Easy to scale and maintain
- **Unified Client** - Single interface for all agents
- **Streaming** - Real-time feedback
- **Docker** - Consistent deployments
- **Flexible** - Mix and match agents as needed

## Future Enhancements

- [ ] WebSocket support for streaming
- [ ] Authentication/API keys
- [ ] Rate limiting
- [ ] Result caching
- [ ] Multi-language support
- [ ] Kubernetes deployment configs

## License

MIT
