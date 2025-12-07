"""
Open Interpreter MCP Service - LOCAL LLM

FastAPI wrapper around Open Interpreter for secure code execution
with configurable permissions and local LLM support.
"""

import os
import yaml
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from interpreter import interpreter
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Open Interpreter MCP Service")

# Load configuration
def load_config(config_path: str = "config.yaml") -> Dict[str, Any]:
    """Load service configuration."""
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    return {}

config = load_config()

# Configure Open Interpreter with new API
permissions = config.get('permissions', {})
interpreter.auto_run = permissions.get('auto_run', False)
interpreter.offline = True  # Use local models

# Local LLM configuration
llm_config = config.get('llm', {})
model_name = llm_config.get('model', 'ollama/qwen2.5:7b')
api_base = llm_config.get('api_base', 'http://host.docker.internal:11434')
temperature = llm_config.get('temperature', 0.1)

# Set model configuration
interpreter.model = model_name
interpreter.api_base = api_base
interpreter.temperature = temperature

# Set system message
system_message = config.get('system_message',
    'You are a helpful AI assistant with access to Python code execution. '
    'Be careful and explain what code you will run before executing.'
)
interpreter.system_message = system_message


class InterpretRequest(BaseModel):
    """Request model for interpretation."""
    command: str
    context: Optional[str] = None
    auto_run: Optional[bool] = None


class InterpretResponse(BaseModel):
    """Response model from interpreter."""
    success: bool
    output: str
    code_executed: Optional[str] = None
    error: Optional[str] = None


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "open-interpreter",
        "model": interpreter.model,
        "auto_run": interpreter.auto_run
    }


@app.post("/interpret", response_model=InterpretResponse)
async def interpret_command(request: InterpretRequest):
    """
    Execute a command using Open Interpreter.
    
    Args:
        command: Natural language command to interpret
        context: Optional context for the command
        auto_run: Override auto_run setting for this request
    """
    try:
        # Prepare input
        full_input = request.command
        if request.context:
            full_input = f"Context: {request.context}\n\nTask: {request.command}"
        
        # Override auto_run if specified
        original_auto_run = interpreter.auto_run
        if request.auto_run is not None:
            interpreter.auto_run = request.auto_run
        
        # Execute
        result = interpreter.chat(full_input, return_messages=True)
        
        # Restore original setting
        interpreter.auto_run = original_auto_run
        
        # Extract output and code
        output_parts = []
        code_executed = []
        
        for message in result:
            if message.get('type') == 'message':
                output_parts.append(message.get('content', ''))
            elif message.get('type') == 'code':
                code_executed.append(message.get('content', ''))
        
        return InterpretResponse(
            success=True,
            output='\n'.join(output_parts),
            code_executed='\n'.join(code_executed) if code_executed else None
        )
        
    except Exception as e:
        return InterpretResponse(
            success=False,
            output="",
            error=str(e)
        )


@app.post("/reset")
async def reset_interpreter():
    """Reset interpreter conversation history."""
    try:
        interpreter.messages = []
        return {"status": "reset", "message": "Conversation history cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/config")
async def get_config():
    """Get current configuration."""
    return {
        "model": interpreter.model,
        "api_base": interpreter.api_base,
        "temperature": interpreter.temperature,
        "auto_run": interpreter.auto_run,
        "offline": interpreter.offline
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("SERVICE_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
