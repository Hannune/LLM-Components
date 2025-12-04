"""
Large Text Summarizer - Map-Reduce approach with smart chunking

Summarizes text larger than LLM context window using a two-stage process:
1. Split text → summarize each chunk
2. Combine chunk summaries → final summary

Works with 100% LOCAL LLMs (Ollama, vLLM, LiteLLM)
"""

from typing import List, Optional
import tiktoken
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage


def count_tokens(text: str, encoding_name: str = "cl100k_base") -> int:
    """
    Count tokens in text using tiktoken.
    
    Args:
        text: Text to count tokens for
        encoding_name: Tiktoken encoding (cl100k_base for GPT-3.5/4)
    
    Returns:
        Number of tokens
    """
    encoding = tiktoken.get_encoding(encoding_name)
    return len(encoding.encode(text))


def calculate_optimal_chunks(
    total_tokens: int,
    context_limit: int = 4000,
    target_combined_tokens: int = 6000,
    summary_compression_ratio: float = 0.15
) -> tuple[int, int]:
    """
    Calculate optimal chunk size to ensure combined summaries fit in final call.
    
    Args:
        total_tokens: Total tokens in original text
        context_limit: LLM context window size
        target_combined_tokens: Target total tokens for combined summaries
        summary_compression_ratio: Expected compression ratio (summary/original)
    
    Returns:
        (num_chunks, tokens_per_chunk)
    
    Example:
        100K tokens → 80 chunks of 1250 tokens
        → 80 summaries × 100 tokens = 8K tokens
        → Fits in 8K context for final summary
    """
    # Estimate tokens in combined summaries
    expected_summary_tokens = total_tokens * summary_compression_ratio
    
    # If already small enough, use minimal chunks
    if expected_summary_tokens <= target_combined_tokens:
        num_chunks = max(1, total_tokens // context_limit)
        tokens_per_chunk = total_tokens // num_chunks if num_chunks > 0 else total_tokens
        return num_chunks, tokens_per_chunk
    
    # Calculate chunks needed to fit combined summaries in target
    num_chunks = int((expected_summary_tokens / target_combined_tokens) * 
                     (total_tokens / context_limit)) + 1
    
    # Ensure chunks aren't too small (minimum 500 tokens)
    num_chunks = min(num_chunks, total_tokens // 500)
    num_chunks = max(1, num_chunks)
    
    tokens_per_chunk = total_tokens // num_chunks
    
    return num_chunks, tokens_per_chunk


def chunk_text_by_tokens(text: str, chunk_size: int, overlap: int = 100) -> List[str]:
    """
    Split text into chunks by token count with overlap.
    
    Args:
        text: Text to chunk
        chunk_size: Target tokens per chunk
        overlap: Overlap tokens between chunks
    
    Returns:
        List of text chunks
    """
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    
    chunks = []
    start = 0
    
    while start < len(tokens):
        end = start + chunk_size
        chunk_tokens = tokens[start:end]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append(chunk_text)
        
        # Move start with overlap
        start = end - overlap
        if start >= len(tokens):
            break
    
    return chunks


def summarize_large_text(
    text: str,
    llm: ChatOllama,
    max_final_tokens: int = 500,
    context_limit: int = 4000,
    show_progress: bool = True
) -> dict:
    """
    Summarize text larger than LLM context using map-reduce approach.
    
    Process:
    1. Calculate optimal chunking
    2. Summarize each chunk (map stage)
    3. Combine summaries → final summary (reduce stage)
    
    Args:
        text: Large text to summarize
        llm: LangChain LLM instance (ChatOllama, ChatOpenAI, etc.)
        max_final_tokens: Target tokens for final summary
        context_limit: LLM context window size
        show_progress: Print progress messages
    
    Returns:
        {
            'summary': Final summary text,
            'stats': {
                'original_tokens': int,
                'num_chunks': int,
                'chunk_summaries': List[str],
                'combined_tokens': int,
                'final_tokens': int
            }
        }
    """
    # Count tokens
    total_tokens = count_tokens(text)
    
    if show_progress:
        print(f"Original text: {total_tokens:,} tokens")
    
    # Check if text is small enough for direct summary
    if total_tokens <= context_limit:
        if show_progress:
            print("Text fits in context - using direct summary")
        
        prompt = f"""Summarize the following text concisely in approximately {max_final_tokens} tokens:

{text}"""
        
        response = llm.invoke([HumanMessage(content=prompt)])
        summary = response.content
        
        return {
            'summary': summary,
            'stats': {
                'original_tokens': total_tokens,
                'num_chunks': 1,
                'chunk_summaries': [summary],
                'combined_tokens': count_tokens(summary),
                'final_tokens': count_tokens(summary)
            }
        }
    
    # Calculate optimal chunking
    num_chunks, chunk_size = calculate_optimal_chunks(
        total_tokens,
        context_limit=context_limit,
        target_combined_tokens=context_limit - 500  # Leave room for prompt
    )
    
    if show_progress:
        print(f"Strategy: {num_chunks} chunks × ~{chunk_size:,} tokens")
    
    # Split text into chunks
    chunks = chunk_text_by_tokens(text, chunk_size)
    
    if show_progress:
        print(f"Created {len(chunks)} chunks")
    
    # Stage 1: Summarize each chunk
    chunk_summaries = []
    for i, chunk in enumerate(chunks, 1):
        if show_progress:
            print(f"Summarizing chunk {i}/{len(chunks)}...", end=" ", flush=True)
        
        prompt = f"""Summarize the following text section concisely, preserving key information:

{chunk}

Summary:"""
        
        response = llm.invoke([HumanMessage(content=prompt)])
        chunk_summary = response.content
        chunk_summaries.append(chunk_summary)
        
        if show_progress:
            print(f"✓ ({count_tokens(chunk_summary)} tokens)")
    
    # Combine all chunk summaries
    combined = "\n\n".join([f"Section {i+1}:\n{s}" for i, s in enumerate(chunk_summaries)])
    combined_tokens = count_tokens(combined)
    
    if show_progress:
        print(f"\nCombined summaries: {combined_tokens:,} tokens")
    
    # Stage 2: Final summary
    if show_progress:
        print("Creating final summary...", end=" ", flush=True)
    
    final_prompt = f"""Create a comprehensive summary of the following section summaries in approximately {max_final_tokens} tokens.
Focus on main themes, key points, and important conclusions:

{combined}

Final Summary:"""
    
    response = llm.invoke([HumanMessage(content=final_prompt)])
    final_summary = response.content
    final_tokens = count_tokens(final_summary)
    
    if show_progress:
        print(f"✓ ({final_tokens} tokens)")
        print(f"\nCompression: {total_tokens:,} → {final_tokens} tokens ({final_tokens/total_tokens*100:.1f}%)")
    
    return {
        'summary': final_summary,
        'stats': {
            'original_tokens': total_tokens,
            'num_chunks': len(chunks),
            'chunk_summaries': chunk_summaries,
            'combined_tokens': combined_tokens,
            'final_tokens': final_tokens,
            'compression_ratio': final_tokens / total_tokens
        }
    }


def summarize_file(
    file_path: str,
    llm: ChatOllama,
    max_final_tokens: int = 500,
    encoding: str = 'utf-8'
) -> dict:
    """
    Summarize text from a file.
    
    Args:
        file_path: Path to text file
        llm: LangChain LLM instance
        max_final_tokens: Target tokens for final summary
        encoding: File encoding
    
    Returns:
        Same as summarize_large_text()
    """
    with open(file_path, 'r', encoding=encoding) as f:
        text = f.read()
    
    return summarize_large_text(text, llm, max_final_tokens=max_final_tokens)
