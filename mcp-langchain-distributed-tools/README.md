# MCP-LangChain Distributed Tools

**LangChain agent with MCP (Model Context Protocol) for distributed tool execution - 100% LOCAL LLMs**

Enable LangChain agents to call tools running on different servers/machines using the Model Context Protocol, all powered by local LLMs like Ollama.

## Features

- **Distributed Tools** - Run MCP servers on different machines
- **LangChain Integration** - Use MCP tools with LangChain agents
- **Local LLM** - Powered by Ollama (no API costs)
- **Structured Output** - Clean JSON responses from LLM
- **Multi-Server** - Connect to multiple MCP servers simultaneously
- **Interactive Demo** - Test with CLI interface

## Architecture

```
┌──────────────────┐
│  LangChain Agent │  (Local Ollama LLM)
│  + Structured    │
│    Output        │
└────────┬─────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    │ MCP     │  MCP     │  MCP     │
    │ Client  │  Client  │  Client  │
    └────┬────┴──────┬───┴──────┬───┘
         │           │          │
    ┌────▼────┐ ┌───▼────┐ ┌───▼────┐
    │Add      │ │Subtract│ │Divide  │
    │Server   │ │Server  │ │Server  │
    │:8001    │ │:8002   │ │:8003   │
    └─────────┘ └────────┘ └────────┘
     LOCAL      LOCAL      LOCAL
   (Can be on different machines)
```

## What is MCP?

**Model Context Protocol (MCP)** is a standard for connecting AI models to external tools and data sources.

Benefits:
- Tools can run anywhere (different servers, languages, networks)
- Clean separation between AI and tool logic
- Easy to add new tools without modifying the agent
- Tools can be reused across different AI systems

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Ollama

```bash
# Pull a local model
ollama pull qwen2.5:7b

# Ensure Ollama is running
ollama serve
```

### 3. Configure

```bash
cp config.example.json config.json
# Edit config.json if needed
```

### 4. Run Demo

```bash
python demo.py
```

Choose from:
1. Run predefined tests
2. Interactive chat mode
3. Both

## Usage

### Basic Example

```python
from langchain_agent import LangChainMCPAgent
from mcp_client import MCPClientManager, MCPServerConfig

# Configure MCP servers
server_configs = [
    MCPServerConfig(
        name="add_server",
        host="localhost",
        port=8001,
        command=["python", "servers/add_server.py"],
        tools=["add"]
    )
]

# Initialize
mcp_manager = MCPClientManager(server_configs)
await mcp_manager.connect_to_servers()

agent = LangChainMCPAgent(mcp_manager)

# Use the agent
response = await agent.process_request("What is 5 + 3?")
print(response)
```

### Interactive Mode

```bash
python demo.py
# Choose option 2 for interactive mode

You: What is 100 + 50?
Agent: The sum of 100 and 50 is 150

You: Hello!
Agent: Hello! How can I help you today?

You: What is 20 divided by 4?
Agent: The result of dividing 20 by 4 is 5.0
```

## Configuration

### config.json

```json
{
  "ollama": {
    "model": "qwen2.5:7b",
    "base_url": "http://localhost:11434"
  },
  "mcp_servers": [
    {
      "name": "add_server",
      "host": "localhost",
      "port": 8001,
      "command": ["python", "servers/add_server.py"],
      "tools": ["add"]
    }
  ]
}
```

### Distributed Deployment

Run servers on different machines:

```json
{
  "mcp_servers": [
    {
      "name": "add_server",
      "host": "192.168.1.100",  // Different machine
      "port": 8001,
      "command": ["python", "servers/add_server.py"],
      "tools": ["add"]
    },
    {
      "name": "subtract_server",
      "host": "192.168.1.101",  // Another machine
      "port": 8002,
      "command": ["python", "servers/subtract_server.py"],
      "tools": ["subtract"]
    }
  ]
}
```

## Creating Custom MCP Tools

### 1. Create Tool Server

```python
from mcp.server import Server
import mcp.types as types

server = Server("my-tool")

@server.list_tools()
async def handle_list_tools():
    return [
        types.Tool(
            name="my_tool",
            description="Description of what it does",
            inputSchema={
                "type": "object",
                "properties": {
                    "param": {"type": "string"}
                },
                "required": ["param"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict):
    if name == "my_tool":
        result = do_something(arguments["param"])
        return [types.TextContent(type="text", text=result)]
```

### 2. Add to Configuration

Update `config.json`:
```json
{
  "name": "my_tool_server",
  "host": "localhost",
  "port": 8004,
  "command": ["python", "servers/my_tool_server.py"],
  "tools": ["my_tool"]
}
```

### 3. Update Agent Prompt

Edit `langchain_agent.py` to describe your new tool in the system prompt.

## Examples

### Example 1: Simple Math
```
User: What is 25 + 75?
Agent: The sum of 25 and 75 is 100
```

### Example 2: Conversational
```
User: Hello! How are you?
Agent: Hello! I'm doing great, thank you!
```

### Example 3: Chain Operations
```
User: Add 10 and 20, then divide by 5
Agent: [Calls add tool: 30]
       [Calls divide tool: 6]
       First I added 10 and 20 to get 30, then divided by 5 to get 6.
```

## Components

### langchain_agent.py
- LangChain agent with structured output
- Decides when to call MCP tools
- Powered by local Ollama LLM

### mcp_client.py
- Manages connections to MCP servers
- Routes tool calls to correct server
- Handles multiple simultaneous connections

### demo.py
- Interactive demo interface
- Predefined test cases
- Configuration loader

### servers/
Example MCP tool servers:
- `add_server.py` - Addition operations
- `subtract_server.py` - Subtraction
- `divide_server.py` - Division

## Use Cases

### 1. Distributed AI Tools
Run computation-heavy tools on GPU servers, lightweight tools locally

### 2. Microservices for AI
Each tool as a separate service, easily scalable

### 3. Multi-Language Tools
Python agent calling Rust/Go/Node.js tools via MCP

### 4. Enterprise Integration
Connect AI to existing internal APIs/services

### 5. Local-First AI
All processing on your hardware, no cloud dependencies

## Troubleshooting

### Connection errors
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Test MCP server directly
python servers/add_server.py
```

### Tool not found
- Verify server is listed in `config.json`
- Check server started successfully
- Review logs for connection errors

### LLM not responding correctly
- Ensure model supports structured output
- Try different model: `qwen2.5:7b`, `llama3.1:8b`
- Check temperature setting (0.1 for deterministic)

### JSON parsing errors
- LLM may not return valid JSON
- Try more capable model
- Adjust system prompt for clarity

## Performance

- **Latency**: ~200-500ms per request (local LLM)
- **Throughput**: Depends on Ollama setup
- **Scalability**: Add more MCP servers as needed

## Requirements

- Python 3.8+
- Ollama installed and running
- Local LLM model (qwen2.5, llama3.1, etc.)

## Advantages Over Direct LangChain Tools

| Feature | MCP Tools | Direct LangChain Tools |
|---------|-----------|----------------------|
| Distribution | ✓ Can run on different servers | ✗ Must be in same process |
| Language | ✓ Any language | ✗ Python only |
| Reusability | ✓ Works with any MCP client | ✗ LangChain-specific |
| Scalability | ✓ Easy to scale per-tool | ✗ Limited by single process |
| Maintenance | ✓ Update tools independently | ✗ Requires agent restart |

## Future Enhancements

- [ ] Add more example tool servers
- [ ] Support for streaming responses
- [ ] Tool result caching
- [ ] Health monitoring for MCP servers
- [ ] Auto-reconnection on failure
- [ ] Tool execution timeout handling

## License

MIT
