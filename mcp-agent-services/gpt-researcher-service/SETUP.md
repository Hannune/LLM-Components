# GPT-Researcher Service Setup

**This service needs to be cloned from your GitHub repository.**

## Setup Instructions

1. Clone your gpt-researcher-wrapper from GitHub:
```bash
cd mcp-agent-services/gpt-researcher-service
git clone https://github.com/Hannune/Host-Multi-Agents.git temp
cp -r temp/gpt-researcher-wrapper/* .
rm -rf temp
```

2. The wrapper should include:
   - FastAPI server
   - File sending capability
   - Local LLM integration
   - Docker configuration

3. Create Dockerfile if not present (example):
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8002

CMD ["python", "server.py"]
```

4. Ensure it's configured for local LLM (Ollama)

## Expected API

The service should expose:
- `POST /research` - Start research task
- `GET /research/{task_id}` - Get research status
- `GET /research/{task_id}/files` - Download research files

## Integration Points

- Port: 8002
- Communicates with Ollama at `http://host.docker.internal:11434`
- Outputs research files to shared volume
- Accessible via FastMCP client
