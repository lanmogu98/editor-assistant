"""
Tests for the ContentChunker class.
"""

import pytest
from editor_assistant.content_chunker import ContentChunker

def test_chunker_does_not_split_short_content():
    """
    Ensures that content smaller than the max_chunk_size is not split
    and returned as a single chunk.
    """
    # Arrange: Create a chunker and provide a short piece of text.
    # Using a high max_chunk_size to ensure the content is smaller.
    chunker = ContentChunker(max_chunk_size=5000)
    short_text = "This is a short piece of text that should not be chunked."

    # Act: Process the content.
    chunks = chunker.create_chunks(short_text)

    # Assert: Check that the result is a single chunk.
    assert len(chunks) == 1
    assert chunks[0]['content'] == short_text

def test_chunker_splits_long_content():
    """
    Ensures that content larger than the max_chunk_size is split
    into multiple chunks.
    """
    # Arrange: Create a chunker with a small max_chunk_size and min_chunk_size.
    # The min_chunk_size is lowered from its default to prevent it from merging
    # our small test chunks back together.
    chunker = ContentChunker(max_chunk_size=100, min_chunk_size=10)
    long_text = (
        "This is the first paragraph and it is intentionally made to be very long, "
        "definitely over one hundred characters, to ensure that it correctly triggers the "
        "chunking mechanism all by itself.\n\n"
        "This is the second paragraph. It should be in a separate, second chunk."
    )

    # Act: Process the content.
    chunks = chunker.create_chunks(long_text)

    # Assert: Check that the text was split into two chunks.
    assert len(chunks) == 2
    assert "first paragraph" in chunks[0]['content']
    assert "second paragraph" in chunks[1]['content']


def test_chunker_handles_empty_content():
    """
    Ensures that providing empty content results in zero chunks.
    """
    # Arrange
    chunker = ContentChunker(max_chunk_size=100)
    empty_text = ""

    # Act
    chunks = chunker.create_chunks(empty_text)

    # Assert
    assert len(chunks) == 0