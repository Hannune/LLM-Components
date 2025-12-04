# GPT Researcher Service

> **FastAPI wrapper for GPT Researcher with file upload support - Works with 100% LOCAL LLMs**

Research agent service that accepts file uploads and performs comprehensive research using LOCAL LLMs (Ollama). Perfect for document-based research with zero API costs.

## 🎯 Features

- 📤 **File Upload Support** - Send documents for research context
- 🧑‍💻 **100% LOCAL LLMs** - Works with Ollama (qwen, llama, mistral, etc.)
- 🔄 **Session Management** - Isolated file storage per research task
- 🧹 **Auto Cleanup** - Automatic cleanup of old sessions
- 🐳 **Docker Ready** - Full Docker Compose setup
- 🔌 **MCP Compatible** - Works as MCP tool for agents

## Setup

### 1. Prerequisites

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull required models
ollama pull qwen2.5:7b
ollama pull qwen2.5:32b
ollama pull nomic-embed-text
```

### 2. Environment Variables

Copy the example environment file and configure:

```bash
cp .env.example .env
```

Edit `.env` for LOCAL LLM setup:

```env
# Tavily API (for web search)
TAVILY_API_KEY=your_tavily_api_key_here

# LOCAL LLM (Ollama)
OLLAMA_BASE_URL=http://localhost:11434
FAST_LLM=ollama:qwen2.5:7b
SMART_LLM=ollama:qwen2.5:32b
STRATEGIC_LLM=ollama:qwen2.5:32b
EMBEDDING=ollama:nomic-embed-text
```

### 2. Build and Run with Docker Compose

```bash
docker-compose up -d
```

The service will be available at `http://localhost:8000`

### 3. Check Service Health

```bash
curl http://localhost:8000/
```

## API Endpoints

### POST /research

Perform research with optional file uploads.

**Request:**
- `session_id` (required): Unique identifier for the research session
- `query` (required): Research query/question
- `files` (optional): List of files to upload for context
- `report_type` (optional): Type of report (default: "research_report")
- `tone` (optional): Tone of the report (default: "Objective")

**Example with curl:**

```bash
# Simple research without files
curl -X POST "http://localhost:8000/research" \
  -F "session_id=session-123" \
  -F "query=What are the latest developments in AI?"

# Research with file uploads
curl -X POST "http://localhost:8000/research" \
  -F "session_id=session-456" \
  -F "query=Analyze the trends in this document" \
  -F "files=@document1.pdf" \
  -F "files=@document2.txt"
```

**Example with Python:**

```python
import requests

# Simple research
response = requests.post(
    "http://localhost:8000/research",
    data={
        "session_id": "session-123",
        "query": "What are the latest developments in AI?"
    }
)
print(response.json())

# With file uploads
files = [
    ("files", open("document1.pdf", "rb")),
    ("files", open("document2.txt", "rb"))
]
data = {
    "session_id": "session-456",
    "query": "Analyze the trends in these documents"
}
response = requests.post(
    "http://localhost:8000/research",
    data=data,
    files=files
)
print(response.json())
```

### POST /cleanup

Manually trigger cleanup of old sessions (older than 24 hours).

```bash
curl -X POST "http://localhost:8000/cleanup"
```

### DELETE /session/{session_id}

Delete a specific session and its files.

```bash
curl -X DELETE "http://localhost:8000/session/session-123"
```

## Session Management

- **Session Files**: Uploaded files are stored in `session-files/{session_id}/`
- **Automatic Cleanup**: Sessions are cleaned up 1 hour after research completion
- **Periodic Cleanup**: Old sessions (>24 hours) are cleaned up on service startup
- **Manual Cleanup**: Use the `/cleanup` endpoint or delete specific sessions

## Docker Commands

```bash
# Start the service
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the service
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Remove all data (including session files)
docker-compose down -v
```

## Development

### Local Development (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TAVILY_API_KEY=your_key
export OPENAI_API_KEY=your_key

# Run the server
python main.py
```

## Configuration

### Session Cleanup

You can adjust cleanup timing in [main.py](main.py):

- `SESSION_MAX_AGE_HOURS`: Maximum age for sessions before periodic cleanup (default: 24 hours)
- `schedule_session_cleanup`: Individual session cleanup delay (default: 1 hour)

### Report Types

Available report types:
- `research_report` (default)
- `outline_report`
- `custom_report`
- And others supported by gpt-researcher

### Tones

Available tones:
- `Objective` (default)
- `Formal`
- `Analytical`
- `Persuasive`
- `Informative`
- And others supported by gpt-researcher

## Troubleshooting

### Port Already in Use

If port 8000 is already in use, modify [docker-compose.yml](docker-compose.yml):

```yaml
ports:
  - "8001:8000"  # Change 8001 to your preferred port
```

### Session Files Growing Too Large

Reduce cleanup delays in [main.py](main.py) or run manual cleanup more frequently:

```bash
curl -X POST "http://localhost:8000/cleanup"
```

## License

MIT
