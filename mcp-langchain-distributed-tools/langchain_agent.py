#!/usr/bin/env python3
"""
LangChain Agent with Structured Output and MCP Integration
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field
from langchain_ollama import OllamaLLM
from langchain.schema import HumanMessage, SystemMessage
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

from mcp_client import MCPClientManager, MCPServerConfig


class ToolCall(BaseModel):
    """Structured output for tool calls"""
    tool_name: str = Field(description="Name of the tool to call")
    arguments: Dict[str, Any] = Field(description="Arguments for the tool call")
    reasoning: str = Field(description="Brief explanation of why this tool is needed")


class AgentResponse(BaseModel):
    """Structured output for the agent"""
    needs_tool: bool = Field(description="Whether a tool call is needed")
    tool_call: Optional[ToolCall] = Field(default=None, description="Tool call details if needed")
    message: str = Field(description="Response message to the user")


class LangChainMCPAgent:
    """LangChain agent that uses structured output to decide when to call MCP tools"""
    
    def __init__(self, mcp_manager: MCPClientManager, ollama_base_url: str = None):
        # Initialize Ollama LLM - you'll configure the details
        self.llm = OllamaLLM(
            model="gpt-oss:20b",
            # base_url will be set by you when configuring
        )
        self.mcp_manager = mcp_manager
        
    def _create_system_prompt(self) -> str:
        """Create system prompt with available tools information"""
        available_tools = self.mcp_manager.get_available_tools()
        
        tools_description = []
        for tool_name, server_name in available_tools.items():
            if tool_name == "add":
                tools_description.append("- add: Add two numbers together (requires: a, b)")
            elif tool_name == "subtract":
                tools_description.append("- subtract: Subtract second number from first (requires: a, b)")
            elif tool_name == "divide":
                tools_description.append("- divide: Divide first number by second (requires: a, b)")
        
        tools_list = "\n".join(tools_description)
        
        return f"""You are a helpful assistant with access to mathematical calculation tools.

Available tools:
{tools_list}

Your task is to:
1. Analyze the user's request
2. Determine if you need to use a tool to answer their question
3. If a tool is needed, specify which tool and its arguments
4. Provide a helpful response

IMPORTANT: You must respond with valid JSON in the following format:
{{
    "needs_tool": true/false,
    "tool_call": {{
        "tool_name": "name_of_tool",
        "arguments": {{"a": number, "b": number}},
        "reasoning": "why this tool is needed"
    }} or null,
    "message": "your response to the user"
}}

Examples:
- If user asks "What is 5 + 3?", you need the add tool
- If user asks "Hello, how are you?", no tool is needed
- If user asks "What's 10 - 4?", you need the subtract tool
- If user asks "What is 15 divided by 3?", you need the divide tool

Always respond with valid JSON only."""

    async def process_request(self, user_input: str) -> str:
        """Process user request and return response"""
        try:
            system_prompt = self._create_system_prompt()
            
            # Create the prompt
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_input)
            ]
            
            # Get LLM response
            response = self.llm.invoke([msg.content for msg in messages])
            
            # Parse structured output
            try:
                response_data = json.loads(response)
                agent_response = AgentResponse(**response_data)
            except (json.JSONDecodeError, Exception) as e:
                return f"Error parsing LLM response: {e}. Raw response: {response}"
            
            # Handle tool call if needed
            if agent_response.needs_tool and agent_response.tool_call:
                tool_result = await self.mcp_manager.call_tool(
                    agent_response.tool_call.tool_name,
                    agent_response.tool_call.arguments
                )
                
                # Combine the reasoning, tool result, and message
                final_response = f"{agent_response.message}\n\nTool used: {agent_response.tool_call.tool_name}\nReasoning: {agent_response.tool_call.reasoning}\nResult: {tool_result}"
                return final_response
            else:
                return agent_response.message
                
        except Exception as e:
            return f"Error processing request: {e}"


async def main():
    """Example usage of the LangChain MCP Agent"""
    
    # Configure MCP servers (these would run on different machines in practice)
    server_configs = [
        MCPServerConfig(
            name="add_server",
            host="localhost",  # Change to actual server IP for distributed setup
            port=8001,
            command=["python", "servers/add_server.py"],
            tools=["add"]
        ),
        MCPServerConfig(
            name="subtract_server",
            host="localhost",
            port=8002,
            command=["python", "servers/subtract_server.py"],
            tools=["subtract"]
        ),
        MCPServerConfig(
            name="divide_server",
            host="localhost",
            port=8003,
            command=["python", "servers/divide_server.py"],
            tools=["divide"]
        )
    ]
    
    # Initialize MCP manager
    mcp_manager = MCPClientManager(server_configs)
    await mcp_manager.connect_to_servers()
    
    # Initialize agent
    agent = LangChainMCPAgent(mcp_manager)
    
    # Test examples
    test_queries = [
        "What is 5 + 3?",
        "Hello, how are you?",
        "Calculate 10 - 4",
        "What's 15 divided by 3?",
        "Tell me a joke",
        "What is 7 + 2 and then subtract 5 from that result?"
    ]
    
    print("Testing LangChain MCP Agent:")
    print("=" * 50)
    
    for query in test_queries:
        print(f"\nUser: {query}")
        response = await agent.process_request(query)
        print(f"Agent: {response}")
        print("-" * 30)
    
    # Cleanup
    await mcp_manager.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
