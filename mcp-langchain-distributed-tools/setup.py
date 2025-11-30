#!/usr/bin/env python3
"""
Setup script for MCP + LangChain example project
"""

import os
import subprocess
import sys
import json
from pathlib import Path


def run_command(command: str, cwd: str = None) -> bool:
    """Run a shell command and return success status"""
    try:
        result = subprocess.run(
            command.split(),
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True
        )
        print(f"✓ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {command}")
        print(f"Error: {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("Error: Python 3.8+ is required")
        sys.exit(1)
    print(f"✓ Python {sys.version.split()[0]} detected")


def setup_virtual_environment():
    """Set up Python virtual environment"""
    if not os.path.exists("venv"):
        if not run_command("python -m venv venv"):
            return False
    
    # Activate venv and install requirements
    if os.name == 'nt':  # Windows
        pip_cmd = "venv/Scripts/pip"
    else:  # Unix/Linux/macOS
        pip_cmd = "venv/bin/pip"
    
    return run_command(f"{pip_cmd} install -r requirements.txt")


def create_directories():
    """Create necessary directories"""
    directories = ["logs", "data", "tests"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")


def verify_files():
    """Verify all required files exist"""
    required_files = [
        "requirements.txt",
        "config.json", 
        "mcp_client.py",
        "langchain_agent.py",
        "demo.py",
        "servers/add_server.py",
        "servers/subtract_server.py",
        "servers/divide_server.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
        else:
            print(f"✓ {file_path}")
    
    if missing_files:
        print("\n✗ Missing required files:")
        for file_path in missing_files:
            print(f"  - {file_path}")
        return False
    
    return True


def test_mcp_imports():
    """Test if MCP packages can be imported"""
    try:
        import mcp
        print("✓ MCP package available")
        return True
    except ImportError:
        print("✗ MCP package not available")
        print("You may need to install it manually:")
        print("pip install mcp")
        return False


def create_run_scripts():
    """Create convenience scripts for running the system"""
    
    # Create run_demo.sh (Unix/Linux/macOS)
    run_demo_sh = """#!/bin/bash
echo "Starting MCP + LangChain Demo"
echo "Make sure Ollama is running with gpt-oss:20b model"
echo "Press Ctrl+C to stop"
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

python demo.py
"""
    
    with open("run_demo.sh", "w") as f:
        f.write(run_demo_sh)
    os.chmod("run_demo.sh", 0o755)
    print("✓ Created run_demo.sh")
    
    # Create run_demo.bat (Windows)
    run_demo_bat = """@echo off
echo Starting MCP + LangChain Demo
echo Make sure Ollama is running with gpt-oss:20b model
echo Press Ctrl+C to stop
echo.

REM Activate virtual environment if it exists
if exist venv (
    call venv\\Scripts\\activate
)

python demo.py
pause
"""
    
    with open("run_demo.bat", "w") as f:
        f.write(run_demo_bat)
    print("✓ Created run_demo.bat")


def print_next_steps():
    """Print instructions for next steps"""
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    
    print("\nNext steps:")
    print("1. Make sure Ollama is running:")
    print("   ollama serve")
    
    print("\n2. Pull the required model:")
    print("   ollama pull gpt-oss:20b")
    print("   (or update config.json with your preferred model)")
    
    print("\n3. Update config.json if needed:")
    print("   - Change server hosts/ports for remote deployment")
    print("   - Update Ollama base URL if different")
    
    print("\n4. Run the demo:")
    print("   ./run_demo.sh      (Linux/macOS)")
    print("   run_demo.bat       (Windows)")
    print("   python demo.py     (Any OS)")
    
    print("\n5. For Docker deployment:")
    print("   docker-compose up")
    
    print("\nProject structure:")
    print("├── servers/           # MCP server implementations")
    print("├── mcp_client.py      # MCP client manager")
    print("├── langchain_agent.py # LangChain integration")
    print("├── demo.py            # Interactive demo")
    print("├── config.json        # Configuration file")
    print("└── requirements.txt   # Python dependencies")


def main():
    """Main setup function"""
    print("MCP + LangChain Project Setup")
    print("="*60)
    
    # Check Python version
    check_python_version()
    
    # Verify required files
    if not verify_files():
        print("\nSetup failed: Missing required files")
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Set up virtual environment
    print("\nSetting up virtual environment...")
    if not setup_virtual_environment():
        print("Warning: Failed to set up virtual environment")
        print("You may need to install requirements manually:")
        print("pip install -r requirements.txt")
    
    # Test imports
    test_mcp_imports()
    
    # Create run scripts
    create_run_scripts()
    
    # Print next steps
    print_next_steps()


if __name__ == "__main__":
    main()
