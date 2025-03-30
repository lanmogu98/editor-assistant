"""
Content Chunker

Utility for splitting long research papers into manageable chunks
for processing with LLM services, focusing on character limits
and preserving paragraph integrity.
"""

import re
from typing import List, Dict, Any


class ContentChunker:
    """
    A simple class to split long research papers into manageable chunks.
    Focuses on character limits while preserving paragraph integrity.
    """
    
    def __init__(self, max_chunk_size: int = 8000, overlap: int = 200, min_chunk_size: int = 2000):
        """
        Initialize the chunker with size parameters.
        
        Args:
            max_chunk_size: Maximum size of each chunk in characters
            overlap: Number of characters to overlap between chunks for context
            min_chunk_size: Minimum size of a chunk to avoid very small chunks
        """
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap
        self.min_chunk_size = min_chunk_size
        # Approximate ratio of characters to tokens (varies by model)
        self.char_to_token_ratio = 4  # ~4 characters per token for English text
    
    def create_chunks(self, content: str) -> List[Dict[str, Any]]:
        """
        Create chunks from content based on paragraph boundaries.
        Simple approach: collect paragraphs until we reach max_chunk_size,
        then start a new chunk.
        
        Args:
            content: The paper content
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        current_chunk = ""
        
        # Split content into paragraphs (double newlines)
        paragraphs = re.split(r'\n\s*\n', content)
        
        for paragraph in paragraphs:
            # If adding this paragraph would exceed max_chunk_size and we already have content,
            # finish the current chunk and start a new one
            if len(current_chunk) + len(paragraph) > self.max_chunk_size and current_chunk:
                chunks.append(self._create_chunk_dict(current_chunk, len(chunks) + 1))
                current_chunk = paragraph + "\n\n"
            else:
                # Otherwise, add the paragraph to the current chunk
                if current_chunk:
                    current_chunk += "\n\n" + paragraph
                else:
                    current_chunk = paragraph
        
        # Add the last chunk if it has content
        if current_chunk:
            chunks.append(self._create_chunk_dict(current_chunk, len(chunks) + 1))
        
        # Handle small chunks by merging them with adjacent chunks
        self._merge_small_chunks(chunks)
        
        return chunks
    
    def _merge_small_chunks(self, chunks: List[Dict[str, Any]]) -> None:
        """
        Merge small chunks with adjacent chunks to avoid very small chunks.
        
        Args:
            chunks: List of chunk dictionaries to process
        """
        i = 0
        while i < len(chunks):
            # If this is a small chunk
            if len(chunks[i]['content']) < self.min_chunk_size:
                # If there's a previous chunk, merge with it
                if i > 0:
                    combined_content = chunks[i-1]['content'] + "\n\n" + chunks[i]['content']
                    chunks[i-1] = self._create_chunk_dict(combined_content, i)
                    chunks.pop(i)
                # Otherwise, if there's a next chunk, merge with it
                elif i < len(chunks) - 1:
                    combined_content = chunks[i]['content'] + "\n\n" + chunks[i+1]['content']
                    chunks[i] = self._create_chunk_dict(combined_content, i + 1)
                    chunks.pop(i+1)
                else:
                    # This is the only chunk, just keep it
                    i += 1
            else:
                i += 1
    
    def _create_chunk_dict(self, content: str, chunk_num: int) -> Dict[str, Any]:
        """
        Create a chunk dictionary with content and metadata.
        
        Args:
            content: The chunk content
            chunk_num: The chunk number
            
        Returns:
            Chunk dictionary with content, position, and estimated tokens
        """
        # Simple position identifier
        position = f"Chunk {chunk_num}"
        
        # Estimate tokens
        estimated_tokens = len(content) // self.char_to_token_ratio
        
        return {
            'content': content,
            'position': position,
            'estimated_tokens': estimated_tokens
        }
    
    def process_content(self, content: str) -> Dict[str, Any]:
        """
        Process the full paper content into manageable chunks.
        
        Args:
            content: The full paper content
            
        Returns:
            Dictionary with content chunks and statistics
        """
        # Create chunks
        chunks = self.create_chunks(content)
        
        # Calculate total tokens
        total_tokens = sum(chunk['estimated_tokens'] for chunk in chunks)
        
        return {
            'chunks': chunks,
            'total_chunks': len(chunks),
            'total_estimated_tokens': total_tokens
        }


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python content_chunker.py <markdown_file>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r', encoding='utf-8') as f:
        content = f.read()
    
    chunker = ContentChunker()
    result = chunker.process_content(content)
    
    print(f"Found {result['total_chunks']} chunks (est. {result['total_estimated_tokens']} tokens total):")
    
    for i, chunk in enumerate(result['chunks'], 1):
        print(f"\nChunk {i}: {chunk['position']}")
        print(f"Size: {len(chunk['content'])} characters (est. {chunk['estimated_tokens']} tokens)")
        print(f"Preview: {chunk['content'][:100]}...") 