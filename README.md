# LLM Components

> **Reusable building blocks for local LLM applications - 100% API-cost-free**

Production-ready components that integrate seamlessly with local LLM infrastructure. From RAG systems to vision models to distributed tool execution - everything runs locally with zero API costs.

## 🎯 Why This Repository?

**Plug & Play** - Drop into any project, works out of the box  
**100% Local** - No external API calls, complete privacy  
**Production Tested** - Used in real applications  
**Well Documented** - Comprehensive guides and examples  
**Framework Agnostic** - Works with LangChain, direct APIs, or custom code

## 📦 Components

### 🔍 [elasticsearch-rag-manager](./elasticsearch-rag-manager/)
**Full-stack RAG system with Elasticsearch + LOCAL LLMs**

Complete document management platform with FastAPI backend and Streamlit frontend. Upload PDFs, chunk documents, generate embeddings, and query with semantic search - all using local models.

**Features:**
- 3 indexing strategies (full-text, vector, hybrid)
- Document upload & processing pipeline
- Job queue for batch operations
- Admin dashboard with real-time monitoring
- OpenAI-compatible API (works with FastChat/vLLM/Ollama)

```python
# Upload and index documents
response = requests.post('http://localhost:8000/post/add-documents/',
    files={'file': open('doc.pdf', 'rb')},
    data={'index_name': 'knowledge_base', 'chunk_size': 512}
)

# Query with local LLM
results = requests.post('http://localhost:8000/post/search/',
    json={'query': 'What is quantum computing?', 'use_llm': True}
)
```

**Use Case**: Enterprise knowledge bases, document search, RAG chatbots

---

### 🎨 [local-llm-vlm-experiments](./local-llm-vlm-experiments/)
**Vision-Language Model experiments with LOCAL models**

Examples and patterns for using vision-capable LLMs locally. Includes Granite Vision and Ollama VLM implementations.

**Examples:**
- Image captioning with Granite Vision
- Visual question answering
- Document understanding (charts, diagrams)
- Multi-image reasoning

```python
from langchain_ollama import ChatOllama

vlm = ChatOllama(
    model="llava:13b",
    base_url="http://localhost:11434"
)

result = vlm.invoke([
    {"type": "text", "text": "What's in this image?"},
    {"type": "image_url", "image_url": "data:image/jpeg;base64,..."}
])
```

**Use Case**: Image analysis, document OCR, visual QA

---

### 🔧 [mcp-langchain-distributed-tools](./mcp-langchain-distributed-tools/)
**MCP (Model Context Protocol) + LangChain integration**

Distributed tool execution framework allowing LLMs to use tools across multiple servers. Combines MCP's server architecture with LangChain's agent framework.

**Features:**
- 9 production-ready tools
- Distributed architecture (tools run on separate servers)
- LangChain agent integration
- Async execution support

**Available Tools:**
- Filesystem operations
- Web scraping
- Database queries
- Git operations
- System commands

```python
from langchain_agent import create_agent

agent = create_agent(
    llm=local_llm,
    mcp_servers=["localhost:3000", "localhost:3001"]
)

result = agent.invoke("Search the web for Python tutorials and save to /tmp/")
```

**Use Case**: AI agents with tool use, automation workflows

---

### 🤖 [mcp-agent-services](./mcp-agent-services/)
**Three powerful MCP services for AI agents**

Microservices architecture providing agents with code execution, research, and web scraping capabilities.

#### 1. open-interpreter-service
FastAPI service wrapping Open Interpreter for safe code execution.

```bash
curl -X POST http://localhost:8001/execute \
  -d '{"code": "import pandas as pd; df.describe()"}'
```

#### 2. gpt-researcher-service
Deep research with **file upload support** - analyze documents or perform web research.

```bash
# Research with uploaded files
curl -X POST http://localhost:8002/research \
  -F "query=Analyze these documents" \
  -F "files=@report.pdf" \
  -F "files=@data.csv"

# Web research
curl -X POST http://localhost:8002/research \
  -d '{"query": "Latest developments in quantum computing"}'
```

#### 3. crawl4ai-service
Advanced web scraping with stealth mode and JavaScript rendering.

```bash
curl -X POST http://localhost:8003/crawl \
  -d '{"url": "https://example.com", "mode": "stealth"}'
```

**Docker Compose** orchestrates all three services with proper networking.

```yaml
# docker-compose.yml
services:
  open-interpreter:
    ports: ["8001:8001"]
  gpt-researcher:
    ports: ["8002:8002"]
  crawl4ai:
    ports: ["8003:8003"]
```

**Use Case**: AI agents, automated research, data collection

---

### 📝 [large-text-summarizer](./large-text-summarizer/)
**Summarize text larger than LLM context windows with smart chunking**

Map-reduce approach for handling documents of any size. Automatically calculates optimal chunk size and performs two-stage summarization.

**Features:**
- Smart chunking algorithm (ensures combined summaries fit)
- Two-stage map-reduce summarization
- Token counting and compression stats
- Works with any OpenAI-compatible LOCAL LLM
- Available as Python function or MCP tool

```python
from summarizer import summarize_large_text
from langchain_ollama import ChatOllama

llm = ChatOllama(model="qwen2.5:7b", base_url="http://localhost:11434")

# Summarize 100K+ token document
result = summarize_large_text(
    text=huge_document,
    llm=llm,
    max_final_tokens=500
)

print(result['summary'])
# Compression: 100,234 → 487 tokens (0.5%)
```

**Use Case**: Research papers, transcripts, log files, multi-document summarization

---

### 📰 [gdelt-article-collector](./gdelt-article-collector/)
**Real-time global news collection with advanced filtering**

FastAPI service + MCP tool for searching the GDELT database - the world's largest open database of human society. Monitor news from around the globe with filters for keywords, domains, countries, themes, and more.

**Features:**
- Advanced search (keywords, domains, dates, countries, themes, languages)
- Timeline analysis for tracking article volume over time
- CSV export functionality
- MCP tool integration for AI agents
- REST API with automatic docs
- Docker deployment ready

```bash
# Search AI news from last 7 days
curl -X POST http://localhost:8004/search \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["artificial intelligence"],
    "domains": ["bbc.com", "reuters.com"],
    "timespan": "7d",
    "max_results": 50
  }'
```

```python
# Use as MCP tool in LangChain
from langchain.tools import tool

@tool
def gdelt_search(query: str) -> str:
    """Search global news via GDELT"""
    response = requests.post("http://localhost:8004/search",
        json={"keywords": [query], "timespan": "7d"})
    return response.json()
```

**Use Case**: News monitoring, trend analysis, research data collection, agent tool

---

### 🔗 [n8n-agent-hosting](./n8n-agent-hosting/)
**Agent-to-Agent (A2A) workflows with n8n for orchestrating multi-agent systems**

Host n8n workflows for agent communication with structured APIs, webhook management, and template deployment. Perfect for coordinating multiple AI agents working together on complex tasks.

**Features:**
- n8n workflow engine for visual agent orchestration
- A2A Wrapper API for structured agent communication
- Template management for deploying workflows programmatically
- Webhook system for agent-to-agent messaging
- MCP integration with your LOCAL LLM tools
- Docker-ready full stack

```bash
# Submit task to researcher agent via webhook
curl -X POST http://localhost:8005/agent/task \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "researcher",
    "task": "Find recent news about quantum computing",
    "context": {"timespan": "7d"},
    "callback_url": "http://callback-service/results"
  }'
```

```python
# Multi-agent coordination
researcher_result = client.submit_agent_task(
    agent_type="researcher",
    task="Find quantum computing papers"
)

analyzer_result = client.submit_agent_task(
    agent_type="analyzer",
    task="Analyze these papers",
    context={"papers": researcher_result['articles']}
)
```

**Use Case**: Multi-agent systems, workflow orchestration, agent coordination, A2A communication

---

## 🏗️ Architecture Patterns

### Pattern 1: RAG Pipeline
```
Documents → elasticsearch-rag-manager → Indexed Knowledge Base
                                              ↓
User Query → Retrieval → Context → LOCAL LLM → Answer
```

### Pattern 2: Agentic Workflow
```
User Task → LangChain Agent → mcp-langchain-tools
                    ↓
            [Research via gpt-researcher-service]
            [Code via open-interpreter-service]
            [Web via crawl4ai-service]
                    ↓
            Synthesized Result
```

### Pattern 3: Vision + RAG
```
Image → local-llm-vlm → Description
                ↓
        elasticsearch-rag-manager → Store
                ↓
        Searchable Image Database
```

### Pattern 4: Large Document Summarization
```
Large Text (100K+ tokens)
        ↓
  large-text-summarizer
        ↓
  [📝 Smart Chunking]
        ↓
  [⚙️  Map: Summarize chunks]
        ↓
  [⚙️  Reduce: Final summary]
        ↓
  Concise Summary (500 tokens)
```

### Pattern 5: Multi-Agent A2A Workflow
```
User Input → n8n-agent-hosting → Agent Workflow
                    ↓
            [Agent 1: Research via GDELT]
                    ↓
            [Agent 2: Analysis via LLM]
                    ↓
            [Agent 3: Writing/Summary]
                    ↓
            Final Result (via webhook callback)
```

### Pattern 6: News Intelligence Pipeline
```
Query → gdelt-article-collector → Articles
            ↓
    elasticsearch-rag-manager → Index
            ↓
    LOCAL LLM → Analysis
            ↓
    n8n-agent-hosting → Distribute to agents
            ↓
    Comprehensive Report
```

## 🚀 Quick Start

### 1. RAG System (Most Popular)

```bash
# Start Elasticsearch
docker run -d -p 9200:9200 -e "discovery.type=single-node" \
  elasticsearch:8.12.0

# Start local LLM server (FastChat example)
python -m fastchat.serve.model_worker --model-path BAAI/bge-m3

# Deploy RAG manager
cd elasticsearch-rag-manager
docker-compose up -d

# Access dashboard at http://localhost:8501
```

### 2. Agent Services

```bash
cd mcp-agent-services
docker-compose up -d

# All services available:
# - Open Interpreter: localhost:8001
# - GPT Researcher: localhost:8002  
# - Crawl4AI: localhost:8003
```

### 3. Vision Models

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull vision model
ollama pull llava:13b

# Run experiments
cd local-llm-vlm-experiments
python granite_vision_example.py
```

## 💡 Integration Examples

### RAG + Agent Workflow

```python
from elasticsearch_rag import RAGManager
from langchain_agent import create_agent
from fleet_manager import get_model

# Initialize components
rag = RAGManager(es_url="http://localhost:9200")
llm = get_model("qwen2.5:32b")
agent = create_agent(llm, tools=["search_docs", "crawl_web"])

# Workflow: Research → Store → Query
def research_and_store(topic):
    # Agent researches topic
    research = agent.invoke(f"Research {topic} from multiple sources")
    
    # Store in RAG
    rag.add_documents(research['documents'])
    
    # Query with context
    answer = rag.query(f"Summarize key findings about {topic}")
    return answer
```

### Vision + Tools

```python
from langchain_ollama import ChatOllama
from mcp_client import MCPClient

# Vision model
vlm = ChatOllama(model="llava:13b", base_url="http://localhost:11434")

# Tool client
mcp = MCPClient(servers=["localhost:8003"])

def analyze_and_extract(image_url):
    # Understand image
    description = vlm.invoke([
        {"type": "text", "text": "Describe this webpage screenshot"},
        {"type": "image_url", "image_url": image_url}
    ])
    
    # Extract data based on understanding
    if "table" in description.content.lower():
        data = mcp.call_tool("crawl", {
            "url": image_url,
            "extract": "tables"
        })
        return data
```

## 🔧 Configuration

Components use consistent configuration patterns:

```env
# Local LLM endpoint (OpenAI-compatible)
OLLAMA_BASE_URL=http://localhost:11434
FASTCHAT_API_BASE=http://localhost:8000/v1
VLLM_API_BASE=http://localhost:8001/v1

# Elasticsearch (for RAG)
ELASTICSEARCH_URL=http://localhost:9200
ELASTICSEARCH_PASSWORD=changeme

# MCP Services
OPEN_INTERPRETER_URL=http://localhost:8001
GPT_RESEARCHER_URL=http://localhost:8002
CRAWL4AI_URL=http://localhost:8003
GDELT_COLLECTOR_URL=http://localhost:8004
N8N_A2A_WRAPPER_URL=http://localhost:8005
N8N_UI_URL=http://localhost:5678
```

## 📊 Component Matrix

| Component | Backend | Frontend | Docker | MCP Tool | Complexity | Setup Time |
|-----------|---------|----------|--------|----------|------------|------------|
| elasticsearch-rag-manager | ✅ FastAPI | ✅ Streamlit | ✅ | - | High | 30 min |
| local-llm-vlm-experiments | - | - | - | - | Low | 5 min |
| mcp-langchain-distributed-tools | - | - | - | ✅ | Medium | 15 min |
| mcp-agent-services | ✅ FastAPI | - | ✅ | - | Medium | 20 min |
| large-text-summarizer | - | - | - | ✅ | Low | 5 min |
| gdelt-article-collector | ✅ FastAPI | - | ✅ | ✅ | Medium | 15 min |
| n8n-agent-hosting | ✅ FastAPI | ✅ n8n UI | ✅ | - | Medium | 20 min |

## 🛠️ Development

### Adding New Components

Components should follow this structure:

```
component-name/
├── README.md              # Comprehensive documentation
├── .env.example          # Configuration template
├── requirements.txt      # Python dependencies
├── docker-compose.yml    # Optional: containerization
└── src/                  # Implementation
```

### Best Practices

1. **Always use environment variables** - No hardcoded URLs/keys
2. **Default to localhost** - Easy local testing
3. **Document thoroughly** - Examples, use cases, troubleshooting
4. **Test with multiple LLM backends** - FastChat, vLLM, Ollama
5. **Provide Docker configs** - Simplify deployment

## 🐛 Troubleshooting

### Elasticsearch connection failed
```bash
# Check Elasticsearch is running
curl http://localhost:9200

# Check credentials in .env
grep ELASTICSEARCH .env
```

### MCP services not responding
```bash
# Check all services are up
docker-compose ps

# Check logs
docker-compose logs -f open-interpreter-service
```

### Vision models not working
```bash
# Verify model supports vision
ollama show llava:13b

# Check image format (base64 encoded)
# Images must be in base64 format for Ollama
```

## 🤝 Contributing

Personal portfolio project showcasing reusable LLM components. Feedback welcome:

1. Share your integration examples
2. Report issues or bugs
3. Suggest new component ideas

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

## 🙏 Acknowledgments

Built with:
- [Elasticsearch](https://www.elastic.co/) - Search and vector database
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python API framework
- [LangChain](https://langchain.com/) - LLM application framework
- [MCP](https://modelcontextprotocol.org/) - Model Context Protocol
- [Open Interpreter](https://github.com/KillianLucas/open-interpreter) - Code execution
- [GPT Researcher](https://github.com/assafelovic/gpt-researcher) - Automated research

## 🔗 Related Repositories

**Infrastructure**: [local-llm-infrastructure](https://github.com/Hannune/Local-LLM-Infrastructure) - Deploy and manage local LLMs  
**Applications**: [llm-applications](https://github.com/Hannune/LLM-Applications) - Complete apps using these components

---

**Reusable, production-ready components for building with LOCAL LLMs** 🔧

Mix and match components to build powerful AI applications without API costs.
