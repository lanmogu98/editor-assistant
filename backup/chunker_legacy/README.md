# Chunker Module Backup

This directory contains the original ContentChunker implementation that was used before migrating to single-context processing for 128k+ token models.

## Files:
- `content_chunker.py`: Original chunker implementation
- `test_content_chunker.py`: Unit tests for the chunker

## Context:
The chunker was originally designed when LLM context windows were much smaller (4k-8k tokens). With modern models having 128k+ tokens, most documents can be processed in a single request, eliminating the need for chunking in 99% of cases.

## Future Use Cases:
- Processing extremely large documents (>300k characters)
- Batch processing multiple documents
- Memory-constrained environments
- Custom chunking strategies for specific document types

## Integration Notes:
If reintegrating this module:
1. Add back the ContentChunker import in md_processesor.py
2. Restore the chunk analysis + synthesis workflow
3. Update the prompts to handle multi-chunk scenarios
4. Re-enable chunk-related tests

Backup created: 2025-07-29