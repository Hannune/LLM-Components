"""
Basic Usage Example - Large Text Summarizer

Demonstrates simple text summarization with LOCAL LLM.
"""

import sys
sys.path.append('..')

from summarizer import summarize_large_text
from langchain_ollama import ChatOllama
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize LOCAL LLM
llm = ChatOllama(
    model=os.getenv("LLM_MODEL", "qwen2.5:7b"),
    base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
)

# Example: Long article about AI
long_text = """
Artificial Intelligence: A Comprehensive Overview

Introduction to Artificial Intelligence
Artificial intelligence (AI) represents one of the most transformative technologies of the 21st century. From its humble beginnings in the 1950s to today's sophisticated deep learning systems, AI has evolved dramatically.

[... imagine this continues for 50+ paragraphs covering:]
- History of AI
- Machine Learning fundamentals
- Deep Learning architectures
- Natural Language Processing
- Computer Vision
- Reinforcement Learning
- AI Ethics and Safety
- Future of AI
- Applications in various industries
- Challenges and limitations

""" * 20  # Repeat to make it long

print("=" * 60)
print("LARGE TEXT SUMMARIZER - Basic Example")
print("=" * 60)
print()

# Summarize
result = summarize_large_text(
    text=long_text,
    llm=llm,
    max_final_tokens=300,  # Target 300-token summary
    context_limit=4000,     # Assume 4K context window
    show_progress=True
)

print("\n" + "=" * 60)
print("FINAL SUMMARY")
print("=" * 60)
print(result['summary'])
print()
print("=" * 60)
print(f"Compression: {result['stats']['original_tokens']:,} → {result['stats']['final_tokens']} tokens")
print(f"Ratio: {result['stats']['compression_ratio']*100:.2f}%")
print("=" * 60)
