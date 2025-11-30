"""
Ollama Vision-Language Model (VLM) Example - LOCAL INFERENCE

Test vision-language models via Ollama API.
Supports models like llama3.2-vision, gemma3, and others.
"""

import os
import time
from ollama import Client
from dotenv import load_dotenv

load_dotenv()

# Configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
MODEL = os.getenv("VLM_MODEL", "llama3.2-vision:latest")
IMAGE_PATH = os.getenv("IMAGE_PATH", "example.jpg")


def analyze_image_simple(client, model, image_path, query, temperature=0.1):
    """Simple image analysis with text query."""
    messages = [{
        'role': 'user',
        'content': query,
        'images': [image_path]
    }]
    
    response = client.chat(
        model=model,
        messages=messages,
        options={"temperature": temperature}
    )
    
    return response["message"]["content"]


def analyze_image_with_system(client, model, image_path, query, system_prompt, temperature=0.1):
    """Image analysis with custom system prompt."""
    messages = [
        {'role': 'system', 'content': system_prompt},
        {
            'role': 'user',
            'content': query,
            'images': [image_path]
        }
    ]
    
    response = client.chat(
        model=model,
        messages=messages,
        options={"temperature": temperature}
    )
    
    return response["message"]["content"]


def main():
    client = Client(host=OLLAMA_HOST)
    
    print(f"Connecting to Ollama at {OLLAMA_HOST}")
    print(f"Using model: {MODEL}")
    
    if not os.path.exists(IMAGE_PATH):
        print(f"Error: Image not found at {IMAGE_PATH}")
        print("Set IMAGE_PATH environment variable")
        return
    
    # Example 1: Simple query
    print("\n=== Example 1: Simple Image Description ===")
    start = time.time()
    result = analyze_image_simple(
        client, MODEL, IMAGE_PATH,
        "Describe what you see in this image"
    )
    print(f"Response: {result}")
    print(f"Time: {time.time() - start:.2f}s")
    
    # Example 2: With system prompt
    print("\n=== Example 2: Risk Assessment ===")
    start = time.time()
    system_prompt = (
        "You are a safety inspector analyzing images for potential hazards. "
        "Rate risks on a scale of 0-10 and explain your reasoning."
    )
    query = (
        "Analyze this image for safety hazards. "
        "Rate the risk level (0-10) and identify specific concerns."
    )
    result = analyze_image_with_system(
        client, MODEL, IMAGE_PATH, query, system_prompt
    )
    print(f"Response: {result}")
    print(f"Time: {time.time() - start:.2f}s")
    
    # Interactive mode
    print("\n=== Interactive Mode ===")
    while True:
        query = input("\nAsk about the image (or 'quit' to exit): ")
        if query.lower() == 'quit':
            break
        
        start = time.time()
        result = analyze_image_simple(client, MODEL, IMAGE_PATH, query)
        print(f"\nResponse: {result}")
        print(f"Time: {time.time() - start:.2f}s")


if __name__ == "__main__":
    main()
