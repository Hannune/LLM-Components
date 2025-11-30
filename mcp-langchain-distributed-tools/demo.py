#!/usr/bin/env python3
"""
Interactive Demo for MCP + LangChain System
"""

import asyncio
import json
import os
from typing import Dict, Any

from langchain_agent import LangChainMCPAgent
from mcp_client import MCPClientManager, MCPServerConfig


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Load configuration from JSON file"""
    with open(config_path, 'r') as f:
        return json.load(f)


async def setup_mcp_system(config: Dict[str, Any]) -> tuple[MCPClientManager, LangChainMCPAgent]:
    """Set up the MCP system with configuration"""
    
    # Create server configs
    server_configs = []
    for server_config in config["mcp_servers"]:
        # Convert relative paths to absolute paths
        command = server_config["command"]
        if len(command) > 1 and not os.path.isabs(command[1]):
            command[1] = os.path.abspath(command[1])
        
        server_configs.append(MCPServerConfig(
            name=server_config["name"],
            host=server_config["host"],
            port=server_config["port"],
            command=command,
            tools=server_config["tools"]
        ))
    
    # Initialize MCP manager
    mcp_manager = MCPClientManager(server_configs)
    await mcp_manager.connect_to_servers()
    
    # Initialize agent
    agent = LangChainMCPAgent(
        mcp_manager=mcp_manager,
        ollama_base_url=config.get("ollama", {}).get("base_url")
    )
    
    return mcp_manager, agent


async def run_predefined_tests(agent: LangChainMCPAgent):
    """Run a set of predefined tests"""
    test_cases = [
        "What is 5 + 3?",
        "Hello, how are you doing today?",
        "Calculate 15 - 7",
        "What's 20 divided by 4?",
        "Can you tell me about yourself?",
        "What is 100 + 50?",
        "Divide 18 by 6",
        "Subtract 25 from 100",
        "What's the weather like?",
        "Calculate 7 + 8 - 5"  # This should require multiple steps
    ]
    
    print("Running Predefined Tests")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case}")
        print("-" * 40)
        
        try:
            response = await agent.process_request(test_case)
            print(f"Response: {response}")
        except Exception as e:
            print(f"Error: {e}")
        
        print()  # Empty line for readability


async def run_interactive_mode(agent: LangChainMCPAgent):
    """Run interactive chat mode"""
    print("\nInteractive Mode")
    print("=" * 60)
    print("Type 'quit', 'exit', or 'q' to stop")
    print("Type 'help' to see available commands")
    print("Type 'tools' to see available MCP tools")
    print("-" * 60)
    
    while True:
        try:
            user_input = input("\nYou: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            elif user_input.lower() == 'help':
                print("""
Available commands:
- help: Show this help message
- tools: Show available MCP tools
- quit/exit/q: Exit the program
- Any other text: Send to the AI agent
                """)
                continue
            
            elif user_input.lower() == 'tools':
                tools = agent.mcp_manager.get_available_tools()
                print("\nAvailable MCP Tools:")
                for tool_name, server_name in tools.items():
                    print(f"- {tool_name} (from {server_name})")
                continue
            
            elif not user_input:
                continue
            
            print("Agent: ", end="", flush=True)
            response = await agent.process_request(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


async def main():
    """Main demo function"""
    print("MCP + LangChain Demo")
    print("=" * 60)
    
    try:
        # Load configuration
        config = load_config()
        print("✓ Configuration loaded")
        
        # Setup MCP system
        print("Setting up MCP system...")
        mcp_manager, agent = await setup_mcp_system(config)
        print("✓ MCP system initialized")
        
        # Show available tools
        tools = mcp_manager.get_available_tools()
        print(f"✓ Connected to {len(tools)} MCP tools:")
        for tool_name, server_name in tools.items():
            print(f"  - {tool_name} (from {server_name})")
        
        # Ask user what they want to do
        print("\nWhat would you like to do?")
        print("1. Run predefined tests")
        print("2. Interactive chat mode") 
        print("3. Both")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice in ['1', '3']:
            await run_predefined_tests(agent)
        
        if choice in ['2', '3']:
            await run_interactive_mode(agent)
        
        elif choice not in ['1', '2', '3']:
            print("Invalid choice. Running predefined tests...")
            await run_predefined_tests(agent)
        
    except FileNotFoundError:
        print("Error: config.json not found. Please create configuration file.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        try:
            await mcp_manager.close_connections()
            print("✓ Connections closed")
        except:
            pass


if __name__ == "__main__":
    asyncio.run(main())
