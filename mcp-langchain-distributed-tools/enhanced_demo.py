#!/usr/bin/env python3
"""
Enhanced Interactive Demo for MCP + LangChain System
Supports both structured output and tool binding modes
"""

import asyncio
import json
import os
from typing import Dict, Any, Literal

from enhanced_langchain_agent import EnhancedLangChainMCPAgent
from mcp_client import MCPClientManager, MCPServerConfig


def load_config(config_path: str = "config.json") -> Dict[str, Any]:
    """Load configuration from JSON file"""
    with open(config_path, 'r') as f:
        return json.load(f)


async def setup_mcp_system(config: Dict[str, Any]) -> MCPClientManager:
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
    
    return mcp_manager


async def run_comparison_tests(mcp_manager: MCPClientManager, ollama_base_url: str = None):
    """Run comparison tests between both modes"""
    test_cases = [
        "What is 5 + 3?",
        "Hello, how are you doing today?",
        "Calculate 15 - 7",
        "What's 20 divided by 4?",
        "Can you tell me about yourself?",
        "What is 100 + 50?"
    ]
    
    print("Comparison Tests: Structured vs Tools Mode")
    print("=" * 70)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case}")
        print("-" * 50)
        
        # Test structured mode
        print("🔧 STRUCTURED MODE:")
        structured_agent = EnhancedLangChainMCPAgent(
            mcp_manager, 
            mode="structured", 
            ollama_base_url=ollama_base_url
        )
        try:
            response = await structured_agent.process_request(test_case)
            print(f"   {response}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test tools mode
        print("\n⚒️  TOOLS MODE:")
        tools_agent = EnhancedLangChainMCPAgent(
            mcp_manager, 
            mode="tools", 
            ollama_base_url=ollama_base_url
        )
        try:
            response = await tools_agent.process_request(test_case)
            print(f"   {response}")
        except Exception as e:
            print(f"   Error: {e}")
        
        print()  # Empty line for readability


async def run_interactive_mode(mcp_manager: MCPClientManager, ollama_base_url: str = None):
    """Run interactive chat mode with mode switching"""
    print("\nInteractive Mode with Mode Switching")
    print("=" * 70)
    print("Commands:")
    print("- 'quit', 'exit', 'q': Stop the program")
    print("- 'mode structured': Switch to structured output mode")
    print("- 'mode tools': Switch to tool binding mode")
    print("- 'mode status': Show current mode")
    print("- 'help': Show this help message")
    print("- 'tools': Show available MCP tools")
    print("- Any other text: Send to the AI agent")
    print("-" * 70)
    
    # Start with structured mode
    agent = EnhancedLangChainMCPAgent(
        mcp_manager, 
        mode="structured", 
        ollama_base_url=ollama_base_url
    )
    
    print(f"Starting in {agent.get_mode()} mode")
    
    while True:
        try:
            user_input = input(f"\n[{agent.get_mode()}] You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            elif user_input.lower().startswith('mode '):
                command = user_input.lower().split(' ', 1)
                if len(command) == 2:
                    if command[1] == "structured":
                        agent.switch_mode("structured")
                    elif command[1] == "tools":
                        agent.switch_mode("tools")
                    elif command[1] == "status":
                        print(f"Current mode: {agent.get_mode()}")
                    else:
                        print("Available modes: structured, tools")
                else:
                    print("Usage: mode [structured|tools|status]")
                continue
            
            elif user_input.lower() == 'help':
                print("""
Available commands:
- mode structured: Switch to structured output mode
- mode tools: Switch to tool binding mode
- mode status: Show current mode
- help: Show this help message
- tools: Show available MCP tools
- quit/exit/q: Exit the program
- Any other text: Send to the AI agent

Mode differences:
- Structured: LLM outputs JSON to decide tool usage (custom implementation)
- Tools: Uses LangChain's native tool binding with llm.bind_tools()
                """)
                continue
            
            elif user_input.lower() == 'tools':
                tools = mcp_manager.get_available_tools()
                print("\nAvailable MCP Tools:")
                for tool_name, server_name in tools.items():
                    print(f"- {tool_name} (from {server_name})")
                continue
            
            elif not user_input:
                continue
            
            print(f"Agent [{agent.get_mode()}]: ", end="", flush=True)
            response = await agent.process_request(user_input)
            print(response)
            
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


async def run_mode_switching_demo(mcp_manager: MCPClientManager, ollama_base_url: str = None):
    """Demonstrate dynamic mode switching with the same agent"""
    print("\nMode Switching Demo")
    print("=" * 70)
    
    agent = EnhancedLangChainMCPAgent(
        mcp_manager, 
        mode="structured", 
        ollama_base_url=ollama_base_url
    )
    
    test_query = "What is 12 + 8?"
    
    print(f"Test Query: {test_query}")
    print("-" * 50)
    
    # Test in structured mode
    print(f"\n1. Testing in {agent.get_mode()} mode:")
    response = await agent.process_request(test_query)
    print(f"Response: {response}")
    
    # Switch to tools mode
    print(f"\n2. Switching to tools mode...")
    agent.switch_mode("tools")
    print(f"Testing in {agent.get_mode()} mode:")
    response = await agent.process_request(test_query)
    print(f"Response: {response}")
    
    # Switch back to structured mode
    print(f"\n3. Switching back to structured mode...")
    agent.switch_mode("structured")
    print(f"Testing in {agent.get_mode()} mode:")
    response = await agent.process_request(test_query)
    print(f"Response: {response}")


async def main():
    """Main enhanced demo function"""
    print("Enhanced MCP + LangChain Demo")
    print("Supports both Structured Output and Tool Binding modes")
    print("=" * 70)
    
    try:
        # Load configuration
        config = load_config()
        print("✓ Configuration loaded")
        
        # Setup MCP system
        print("Setting up MCP system...")
        mcp_manager = await setup_mcp_system(config)
        print("✓ MCP system initialized")
        
        # Show available tools
        tools = mcp_manager.get_available_tools()
        print(f"✓ Connected to {len(tools)} MCP tools:")
        for tool_name, server_name in tools.items():
            print(f"  - {tool_name} (from {server_name})")
        
        ollama_base_url = config.get("ollama", {}).get("base_url")
        
        # Show menu
        print("\nWhat would you like to do?")
        print("1. Run comparison tests (both modes)")
        print("2. Interactive chat mode with mode switching")
        print("3. Mode switching demo")
        print("4. All of the above")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice in ['1', '4']:
            await run_comparison_tests(mcp_manager, ollama_base_url)
        
        if choice in ['3', '4']:
            await run_mode_switching_demo(mcp_manager, ollama_base_url)
        
        if choice in ['2', '4']:
            await run_interactive_mode(mcp_manager, ollama_base_url)
        
        elif choice not in ['1', '2', '3', '4']:
            print("Invalid choice. Running comparison tests...")
            await run_comparison_tests(mcp_manager, ollama_base_url)
        
    except FileNotFoundError:
        print("Error: config.json not found. Please create configuration file.")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            await mcp_manager.close_connections()
            print("✓ Connections closed")
        except:
            pass


if __name__ == "__main__":
    asyncio.run(main())
