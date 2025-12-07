# n8n Agent Hosting

> **Agent-to-Agent (A2A) workflows with n8n - orchestrate multi-agent systems**

Host n8n workflows for agent communication with structured APIs, webhook management, and template deployment. Perfect for coordinating multiple AI agents working together on complex tasks.

## 🎯 Features

- **🌐 n8n Workflow Engine** - Visual workflow builder for agents
- **🔗 A2A Wrapper API** - Structured agent communication
- **📋 Template Management** - Deploy workflows programmatically
- **🪝 Webhook System** - Agent-to-agent messaging
- **🐳 Docker Ready** - Full stack deployment
- **🔌 MCP Integration** - Connect to your LOCAL LLM tools

## 📦 Installation

### Quick Start

```bash
# Copy environment file
cp .env.example .env
# Edit with your credentials
nano .env

# Start services
docker-compose up -d

# Access n8n UI
open http://localhost:5678

# Access A2A API docs
open http://localhost:8005/docs
```

### What's Running

- **n8n** - Port 5678 (workflow engine)
- **A2A Wrapper** - Port 8005 (REST API for agents)

## 🚀 Usage

### 1. n8n UI - Build Workflows

Access n8n at `http://localhost:5678` and create workflows with:
- **Webhook Trigger** - Entry point for agents
- **HTTP Request** - Call MCP services (GDELT, GPT-researcher, etc.)
- **Code Node** - Process data
- **Respond to Webhook** - Return results to agent

### 2. A2A Wrapper API - Programmatic Access

#### Trigger Agent via Webhook

```bash
# Submit task to researcher agent
curl -X POST http://localhost:8005/webhook/trigger \
  -H "Content-Type: application/json" \
  -d '{
    "webhook_path": "agent-researcher",
    "data": {
      "query": "latest AI developments",
      "max_results": 10
    }
  }'
```

#### Submit Standardized Agent Task

```bash
# Uses convention: webhook = "agent-{type}"
curl -X POST http://localhost:8005/agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "researcher",
    "task": "Find recent news about quantum computing",
    "context": {"timespan": "7d"},
    "callback_url": "http://callback-service/results"
  }'
```

#### Deploy Workflow from Template

```python
import requests
import json

# Load template
with open('templates/agent-researcher.json') as f:
    workflow = json.load(f)

# Deploy to n8n
response = requests.post(
    'http://localhost:8005/workflow/deploy',
    json={
        'workflow_json': workflow,
        'activate': True
    }
)

result = response.json()
print(f"Deployed: {result['workflow_id']}")
print(f"Webhook: {result['webhook_url']}")
```

#### List Active Workflows

```bash
curl http://localhost:8005/workflows
```

### 3. Python Integration

```python
from n8n_client import N8NClient

# Initialize client
client = N8NClient(base_url="http://localhost:8005")

# Submit task to agent
result = client.submit_agent_task(
    agent_type="researcher",
    task="Research AI safety papers",
    context={"sources": ["arxiv", "scholar"]}
)

print(result)
```

## 📋 Workflow Templates

### Included Templates

**1. agent-researcher.json**
- Webhook trigger on `/webhook/agent-researcher`
- Calls GDELT service for news articles
- Processes and returns summarized results

### Creating Your Own

```json
{
  "name": "My Agent Workflow",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "my-agent",
        "responseMode": "responseNode"
      },
      "name": "Webhook",
      "type": "n8n-nodes-base.webhook",
      "position": [250, 300]
    },
    {
      "parameters": {
        "url": "http://host.docker.internal:8004/search",
        "sendBody": true,
        "jsonBody": "={{ $json.body }}"
      },
      "name": "Call Service",
      "type": "n8n-nodes-base.httpRequest",
      "position": [470, 300]
    },
    {
      "parameters": {
        "respondWith": "json",
        "responseBody": "={{ $json }}"
      },
      "name": "Respond",
      "type": "n8n-nodes-base.respondToWebhook",
      "position": [690, 300]
    }
  ],
  "connections": {
    "Webhook": {
      "main": [[{"node": "Call Service", "type": "main", "index": 0}]]
    },
    "Call Service": {
      "main": [[{"node": "Respond", "type": "main", "index": 0}]]
    }
  }
}
```

## 🏗️ Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────────┐
│   Agent A   │────────▶│  A2A Wrapper │────────▶│  n8n Workflow   │
│  (Python)   │         │  (Port 8005) │         │  (Port 5678)    │
└─────────────┘         └──────────────┘         └─────────────────┘
                                                           │
                                                           ▼
                                                  ┌─────────────────┐
                                                  │  MCP Services   │
                                                  │  - GDELT        │
                                                  │  - GPT Research │
                                                  │  - Crawl4AI     │
                                                  └─────────────────┘
                                                           │
                                                           ▼
                                                  ┌─────────────────┐
                                                  │   Agent B       │
                                                  │   (Callback)    │
                                                  └─────────────────┘
```

## 🔧 Advanced Usage

### Multi-Agent Coordination

```python
# Agent 1: Researcher
researcher_result = client.submit_agent_task(
    agent_type="researcher",
    task="Find quantum computing papers"
)

# Agent 2: Analyzer (uses researcher's output)
analyzer_result = client.submit_agent_task(
    agent_type="analyzer",
    task="Analyze these papers",
    context={"papers": researcher_result['articles']}
)

# Agent 3: Writer (synthesizes both)
writer_result = client.submit_agent_task(
    agent_type="writer",
    task="Write summary",
    context={
        "research": researcher_result,
        "analysis": analyzer_result
    }
)
```

### Workflow Chaining

```javascript
// In n8n Code Node
const researchData = $('Research Agent').first().json;
const analysisData = $('Analysis Agent').first().json;

// Combine and pass to next agent
return {
  json: {
    combined_insights: {
      research: researchData,
      analysis: analysisData,
      next_action: "write_report"
    }
  }
};
```

### Callback Pattern

```python
# Agent submits task with callback
client.submit_agent_task(
    agent_type="long-running-task",
    task="Process large dataset",
    callback_url="http://my-service/webhook/results"
)

# Your service receives callback when complete
@app.post("/webhook/results")
async def handle_results(data: dict):
    print(f"Task complete: {data}")
    # Process results...
```

## 🔗 Integration with LangChain

```python
from langchain.tools import tool
import requests

@tool
def research_via_n8n(query: str) -> str:
    """Research news using n8n agent workflow"""
    response = requests.post(
        "http://localhost:8005/agent/task",
        json={
            "agent_type": "researcher",
            "task": query,
            "context": {"timespan": "7d"}
        }
    )
    return response.json()

# Use in agent
from langchain.agents import initialize_agent

agent = initialize_agent(
    tools=[research_via_n8n],
    llm=your_llm,
    agent="zero-shot-react-description"
)

agent.run("What's happening in AI this week?")
```

## 📊 A2A API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/webhook/trigger` | POST | Trigger n8n webhook |
| `/workflow/execute` | POST | Execute workflow by ID |
| `/workflow/deploy` | POST | Deploy new workflow |
| `/workflows` | GET | List all workflows |
| `/agent/task` | POST | Submit agent task |
| `/health` | GET | Health check |

## 🛠️ Development

### Adding Custom Workflow

1. Create workflow in n8n UI
2. Export as JSON (Settings → Export)
3. Save to `templates/` directory
4. Deploy via API or mount in docker-compose

### Environment Variables

```bash
# n8n
N8N_USER=admin
N8N_PASSWORD=your_password
N8N_HOST=localhost
N8N_API_KEY=optional_api_key

# A2A Wrapper
SERVICE_PORT=8005
```

### Accessing Host Services

n8n can access services on your host machine:
```
http://host.docker.internal:8004  # GDELT
http://host.docker.internal:8002  # GPT-researcher
http://host.docker.internal:11434 # Ollama
```

## 🐛 Troubleshooting

### n8n Not Accessible

```bash
# Check if running
docker ps | grep n8n

# View logs
docker-compose logs n8n

# Restart
docker-compose restart n8n
```

### Webhook Not Triggering

1. Check workflow is active in n8n UI
2. Verify webhook path matches request
3. Check n8n logs for errors
4. Test directly: `curl http://localhost:5678/webhook/test`

### Can't Access Host Services

Make sure you're using `host.docker.internal` in workflow URLs, not `localhost`.

## 📝 Best Practices

1. **Use Descriptive Webhook Paths** - `agent-researcher` not `webhook1`
2. **Return Structured Data** - Always return JSON from workflows
3. **Add Error Handling** - Use n8n's error workflows
4. **Log Executions** - Keep execution data for debugging
5. **Version Your Workflows** - Save templates to git

## 📚 Resources

- [n8n Documentation](https://docs.n8n.io/)
- [n8n Workflow Templates](https://n8n.io/workflows/)
- [n8n API Reference](https://docs.n8n.io/api/)

## 🤝 Contributing

Add your workflow templates to the `templates/` directory!

---

**Built for coordinating LOCAL LLM agents**
