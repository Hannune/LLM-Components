"""
Agent-to-Agent (A2A) Wrapper for n8n
Provides structured API for agents to communicate via n8n workflows
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uvicorn
import requests
import os
import json
from datetime import datetime

app = FastAPI(
    title="n8n A2A Wrapper",
    description="Agent-to-Agent communication via n8n workflows",
    version="1.0.0"
)

# Configuration
N8N_URL = os.getenv("N8N_URL", "http://localhost:5678")
N8N_USER = os.getenv("N8N_USER", "admin")
N8N_PASSWORD = os.getenv("N8N_PASSWORD", "changeme")
N8N_API_KEY = os.getenv("N8N_API_KEY", "")


# Models
class WorkflowExecutionRequest(BaseModel):
    workflow_id: str = Field(..., description="n8n workflow ID")
    input_data: Dict[str, Any] = Field(..., description="Input data for workflow")
    wait_for_completion: bool = Field(True, description="Wait for workflow to complete")
    
    class Config:
        json_schema_extra = {
            "example": {
                "workflow_id": "workflow_123",
                "input_data": {"task": "research", "query": "AI trends"},
                "wait_for_completion": True
            }
        }


class WebhookTriggerRequest(BaseModel):
    webhook_path: str = Field(..., description="Webhook path (e.g., 'agent-task')")
    data: Dict[str, Any] = Field(..., description="Data to send to webhook")
    
    class Config:
        json_schema_extra = {
            "example": {
                "webhook_path": "agent-task",
                "data": {"agent_name": "researcher", "task": "analyze", "content": "..."}
            }
        }


class AgentTaskRequest(BaseModel):
    agent_type: str = Field(..., description="Type of agent (researcher, analyzer, writer)")
    task: str = Field(..., description="Task description")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context")
    callback_url: Optional[str] = Field(None, description="URL to callback when complete")


class WorkflowDeployRequest(BaseModel):
    workflow_json: Dict[str, Any] = Field(..., description="n8n workflow JSON")
    activate: bool = Field(True, description="Activate after deployment")


# Helper Functions
def get_n8n_auth():
    """Get n8n authentication"""
    if N8N_API_KEY:
        return {"X-N8N-API-KEY": N8N_API_KEY}
    return None


def get_n8n_basic_auth():
    """Get n8n basic auth tuple"""
    return (N8N_USER, N8N_PASSWORD)


# Endpoints
@app.get("/")
async def root():
    """Service info"""
    return {
        "service": "n8n A2A Wrapper",
        "status": "running",
        "version": "1.0.0",
        "n8n_url": N8N_URL,
        "endpoints": {
            "trigger_webhook": "/webhook/trigger",
            "execute_workflow": "/workflow/execute",
            "deploy_workflow": "/workflow/deploy",
            "list_workflows": "/workflows",
            "agent_task": "/agent/task"
        }
    }


@app.post("/webhook/trigger")
async def trigger_webhook(request: WebhookTriggerRequest):
    """
    Trigger an n8n webhook
    
    Example:
    ```
    POST /webhook/trigger
    {
        "webhook_path": "agent-task",
        "data": {"task": "research", "query": "AI trends"}
    }
    ```
    """
    webhook_url = f"{N8N_URL}/webhook/{request.webhook_path}"
    
    try:
        response = requests.post(
            webhook_url,
            json=request.data,
            timeout=30
        )
        response.raise_for_status()
        
        return {
            "success": True,
            "webhook_path": request.webhook_path,
            "response": response.json() if response.content else None,
            "status_code": response.status_code
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Webhook trigger failed: {str(e)}")


@app.post("/workflow/execute")
async def execute_workflow(request: WorkflowExecutionRequest):
    """
    Execute an n8n workflow by ID
    
    Requires n8n API access
    """
    api_url = f"{N8N_URL}/api/v1/workflows/{request.workflow_id}/execute"
    
    headers = get_n8n_auth() or {}
    auth = None if N8N_API_KEY else get_n8n_basic_auth()
    
    try:
        response = requests.post(
            api_url,
            json={"data": request.input_data},
            headers=headers,
            auth=auth,
            timeout=60 if request.wait_for_completion else 10
        )
        response.raise_for_status()
        
        result = response.json()
        
        return {
            "success": True,
            "workflow_id": request.workflow_id,
            "execution_id": result.get("id"),
            "data": result
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Workflow execution failed: {str(e)}")


@app.post("/workflow/deploy")
async def deploy_workflow(request: WorkflowDeployRequest):
    """
    Deploy a new workflow to n8n
    
    Requires n8n API access
    """
    api_url = f"{N8N_URL}/api/v1/workflows"
    
    headers = get_n8n_auth() or {}
    auth = None if N8N_API_KEY else get_n8n_basic_auth()
    
    try:
        # Set workflow as active if requested
        workflow_data = request.workflow_json.copy()
        workflow_data["active"] = request.activate
        
        response = requests.post(
            api_url,
            json=workflow_data,
            headers=headers,
            auth=auth,
            timeout=30
        )
        response.raise_for_status()
        
        result = response.json()
        
        return {
            "success": True,
            "workflow_id": result.get("id"),
            "name": result.get("name"),
            "active": result.get("active"),
            "webhook_url": f"{N8N_URL}/webhook/{result.get('id')}" if result.get("id") else None
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Workflow deployment failed: {str(e)}")


@app.get("/workflows")
async def list_workflows():
    """List all workflows in n8n"""
    api_url = f"{N8N_URL}/api/v1/workflows"
    
    headers = get_n8n_auth() or {}
    auth = None if N8N_API_KEY else get_n8n_basic_auth()
    
    try:
        response = requests.get(
            api_url,
            headers=headers,
            auth=auth,
            timeout=30
        )
        response.raise_for_status()
        
        workflows = response.json()
        
        return {
            "success": True,
            "count": len(workflows.get("data", [])),
            "workflows": workflows.get("data", [])
        }
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to list workflows: {str(e)}")


@app.post("/agent/task")
async def submit_agent_task(request: AgentTaskRequest):
    """
    Submit a task to an agent via standard webhook
    
    Uses convention: webhook path = 'agent-{agent_type}'
    """
    webhook_path = f"agent-{request.agent_type}"
    
    task_data = {
        "agent_type": request.agent_type,
        "task": request.task,
        "context": request.context,
        "timestamp": datetime.utcnow().isoformat(),
        "callback_url": request.callback_url
    }
    
    webhook_req = WebhookTriggerRequest(
        webhook_path=webhook_path,
        data=task_data
    )
    
    return await trigger_webhook(webhook_req)


@app.get("/health")
async def health_check():
    """Health check"""
    # Try to ping n8n
    try:
        response = requests.get(f"{N8N_URL}/healthz", timeout=5)
        n8n_healthy = response.status_code == 200
    except:
        n8n_healthy = False
    
    return {
        "status": "healthy" if n8n_healthy else "degraded",
        "n8n_connection": n8n_healthy
    }


if __name__ == "__main__":
    port = int(os.getenv("SERVICE_PORT", 8005))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
