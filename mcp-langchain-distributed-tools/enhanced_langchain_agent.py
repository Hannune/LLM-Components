#!/usr/bin/env python3
"""
Enhanced LangChain Agent with Both Structured Output and Tool Binding
Supports two modes:
1. Structured output (custom JSON response)
2. LangChain native tool binding with llm.bind()
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, Union, Literal
from pydantic import BaseModel, Field
from langchain_ollama import OllamaLLM
from langchain_core.tools import BaseTool, tool
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate

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


class MCPTool(BaseTool):
    """LangChain tool wrapper for MCP tools"""
    
    def __init__(self, tool_name: str, description: str, mcp_manager: MCPClientManager):
        super().__init__(
            name=tool_name,
            description=description,
        )
        self.mcp_manager = mcp_manager
        self.tool_name = tool_name
    
    def _run(self, a: float, b: float) -> str:
        """Synchronous version - not used in async context"""
        raise NotImplementedError("Use async version")
    
    async def _arun(self, a: float, b: float) -> str:
        """Run the MCP tool asynchronously"""
        try:
            result = await self.mcp_manager.call_tool(
                self.tool_name, 
                {"a": float(a), "b": float(b)}
            )
            return result
        except Exception as e:
            return f"Error calling {self.tool_name}: {e}"


class EnhancedLangChainMCPAgent:
    """Enhanced LangChain agent with both structured output and tool binding modes"""
    
    def __init__(
        self, 
        mcp_manager: MCPClientManager, 
        mode: Literal["structured", "tools"] = "structured",
        ollama_base_url: str = None
    ):
        # Initialize Ollama LLM
        self.llm = OllamaLLM(
            model="gpt-oss:20b",
            base_url=ollama_base_url
        )
        self.mcp_manager = mcp_manager
        self.mode = mode
        
        # Create LangChain tools from MCP tools
        self.langchain_tools = self._create_langchain_tools()
        
        # Bind tools to LLM if in tools mode
        if self.mode == "tools":
            self.llm_with_tools = self._bind_tools_to_llm()
        else:
            self.llm_with_tools = None
    
    def _create_langchain_tools(self) -> List[MCPTool]:
        """Create LangChain tools from available MCP tools"""
        tools = []
        available_tools = self.mcp_manager.get_available_tools()
        
        tool_descriptions = {
            "add": "Add two numbers together. Input: a (first number), b (second number)",
            "subtract": "Subtract second number from first number. Input: a (minuend), b (subtrahend)",
            "divide": "Divide first number by second number. Input: a (dividend), b (divisor)"
        }
        
        for tool_name, server_name in available_tools.items():
            description = tool_descriptions.get(tool_name, f"Tool: {tool_name}")
            mcp_tool = MCPTool(
                tool_name=tool_name,
                description=description,
                mcp_manager=self.mcp_manager
            )
            tools.append(mcp_tool)
        
        return tools
    
    def _bind_tools_to_llm(self):
        """Bind tools to the LLM for native tool calling"""
        try:
            # Create simple tool functions for binding
            bound_tools = []
            
            for tool in self.langchain_tools:
                if tool.tool_name == "add":
                    @tool
                    def add_numbers(a: float, b: float) -> str:
                        """Add two numbers together."""
                        return asyncio.run(self.mcp_manager.call_tool("add", {"a": a, "b": b}))
                    bound_tools.append(add_numbers)
                    
                elif tool.tool_name == "subtract":
                    @tool
                    def subtract_numbers(a: float, b: float) -> str:
                        """Subtract second number from first number."""
                        return asyncio.run(self.mcp_manager.call_tool("subtract", {"a": a, "b": b}))
                    bound_tools.append(subtract_numbers)
                    
                elif tool.tool_name == "divide":
                    @tool
                    def divide_numbers(a: float, b: float) -> str:
                        """Divide first number by second number."""
                        return asyncio.run(self.mcp_manager.call_tool("divide", {"a": a, "b": b}))
                    bound_tools.append(divide_numbers)
            
            return self.llm.bind_tools(bound_tools)
        except Exception as e:
            print(f"Warning: Could not bind tools to LLM: {e}")
            print("Falling back to structured output mode")
            return None
    
    def _create_structured_system_prompt(self) -> str:
        """Create system prompt for structured output mode"""
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

    def _create_tools_system_prompt(self) -> str:
        """Create system prompt for tools mode"""
        return """You are a helpful assistant with access to mathematical calculation tools.

You can use the following tools:
- add_numbers: Add two numbers together
- subtract_numbers: Subtract second number from first number  
- divide_numbers: Divide first number by second number

Use these tools when users ask for mathematical calculations. For general conversation, respond normally without using tools."""

    async def process_request_structured(self, user_input: str) -> str:
        """Process request using structured output mode"""
        try:
            system_prompt = self._create_structured_system_prompt()
            
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
                final_response = f"{agent_response.message}\n\n[Structured Mode] Tool used: {agent_response.tool_call.tool_name}\nReasoning: {agent_response.tool_call.reasoning}\nResult: {tool_result}"
                return final_response
            else:
                return f"[Structured Mode] {agent_response.message}"
                
        except Exception as e:
            return f"Error processing request in structured mode: {e}"

    async def process_request_tools(self, user_input: str) -> str:
        """Process request using LangChain tools binding mode"""
        try:
            if not self.llm_with_tools:
                return "Tools mode not available, falling back to structured mode"
            
            system_prompt = self._create_tools_system_prompt()
            
            # Create prompt template
            prompt = ChatPromptTemplate.from_messages([
                ("system", system_prompt),
                ("human", "{input}")
            ])
            
            # Create chain
            chain = prompt | self.llm_with_tools
            
            # Invoke the chain
            response = await chain.ainvoke({"input": user_input})
            
            # Handle the response based on its type
            if hasattr(response, 'tool_calls') and response.tool_calls:
                # LLM decided to use tools
                tool_results = []
                for tool_call in response.tool_calls:
                    tool_name = tool_call['name']
                    tool_args = tool_call['args']
                    
                    # Execute the tool
                    if tool_name == "add_numbers":
                        result = await self.mcp_manager.call_tool("add", tool_args)
                    elif tool_name == "subtract_numbers":
                        result = await self.mcp_manager.call_tool("subtract", tool_args)
                    elif tool_name == "divide_numbers":
                        result = await self.mcp_manager.call_tool("divide", tool_args)
                    else:
                        result = f"Unknown tool: {tool_name}"
                    
                    tool_results.append(f"[Tools Mode] Used {tool_name} with args {tool_args}: {result}")
                
                return "\n".join(tool_results)
            else:
                # LLM responded without tools
                return f"[Tools Mode] {response.content if hasattr(response, 'content') else str(response)}"
                
        except Exception as e:
            return f"Error processing request in tools mode: {e}"

    async def process_request(self, user_input: str) -> str:
        """Process user request using the configured mode"""
        if self.mode == "structured":
            return await self.process_request_structured(user_input)
        elif self.mode == "tools":
            return await self.process_request_tools(user_input)
        else:
            return f"Unknown mode: {self.mode}"

    def switch_mode(self, mode: Literal["structured", "tools"]):
        """Switch between structured and tools modes"""
        if mode in ["structured", "tools"]:
            self.mode = mode
            print(f"Switched to {mode} mode")
        else:
            print(f"Invalid mode: {mode}. Available modes: structured, tools")

    def get_mode(self) -> str:
        """Get current mode"""
        return self.mode


async def main():
    """Example usage of the Enhanced LangChain MCP Agent"""
    
    # Configure MCP servers
    server_configs = [
        MCPServerConfig(
            name="add_server",
            host="localhost",
            port=8001,
            command=["python", "/home/tetae/Projects/mcp-example/servers/add_server.py"],
            tools=["add"]
        ),
        MCPServerConfig(
            name="subtract_server",
            host="localhost",
            port=8002,
            command=["python", "/home/tetae/Projects/mcp-example/servers/subtract_server.py"],
            tools=["subtract"]
        ),
        MCPServerConfig(
            name="divide_server",
            host="localhost",
            port=8003,
            command=["python", "/home/tetae/Projects/mcp-example/servers/divide_server.py"],
            tools=["divide"]
        )
    ]
    
    # Initialize MCP manager
    mcp_manager = MCPClientManager(server_configs)
    await mcp_manager.connect_to_servers()
    
    # Test both modes
    test_queries = [
        "What is 5 + 3?",
        "Hello, how are you?",
        "Calculate 10 - 4",
        "What's 15 divided by 3?"
    ]
    
    print("Testing Enhanced LangChain MCP Agent:")
    print("=" * 60)
    
    for mode in ["structured", "tools"]:
        print(f"\n--- Testing {mode.upper()} MODE ---")
        
        # Initialize agent with specific mode
        agent = EnhancedLangChainMCPAgent(mcp_manager, mode=mode)
        
        for query in test_queries:
            print(f"\nUser: {query}")
            response = await agent.process_request(query)
            print(f"Agent: {response}")
            print("-" * 30)
    
    # Test mode switching
    print("\n--- Testing MODE SWITCHING ---")
    agent = EnhancedLangChainMCPAgent(mcp_manager, mode="structured")
    
    query = "What is 7 + 2?"
    
    print(f"\nUser: {query}")
    response = await agent.process_request(query)
    print(f"Agent ({agent.get_mode()} mode): {response}")
    
    agent.switch_mode("tools")
    response = await agent.process_request(query)
    print(f"Agent ({agent.get_mode()} mode): {response}")
    
    # Cleanup
    await mcp_manager.close_connections()


if __name__ == "__main__":
    asyncio.run(main())
