"""
Prompt templates for the research paper summarizer.
"""

# Prompt for analyzing a chunk of the paper
NEWS_CHUNK_ANALYSIS_PROMPT = """Summarize this science/technology news article in 250 words or less:

This is chunk {chunk_number}/{total_chunks} of the paper.

Summary of the previous chunk:
{previous_chunksummary}

Content of this chunk:
{content}

1. Begin with a one-sentence TL;DR highlighting the core innovation or discovery
2. Explain the key technical details and quantitative results in accessible language
3. Describe the real-world implications and potential applications
4. Note any significant limitations or scientific controversies 
5. Identify the key researchers/organizations and funding sources

Present factual information only, 
maintain technical accuracy while being accessible to an educated non-specialist, 
and avoid exaggerating claims beyond what's directly supported by the article.
"""
# Prompt for synthesizing the analyses of all chunks
NEWS_SYNTHESIS_PROMPT = """Create a comprehensive summary of science/tech news. I've analyzed the paper in chunks and will provide the key information from each section.

PAPER SECTIONS:
{analyses}

Please create:
1. A one-sentence TL;DR highlighting the core innovation or discovery
2. The key technical details and quantitative results in accessible language
3. The real-world implications and potential applications
4. Any significant limitations or scientific controversies 
5. The key researchers/organizations and funding sources

Present factual information only, maintain technical accuracy while being accessible to an educated non-specialist, and avoid exaggerating claims beyond what's directly supported by the article.

Format your response with the heading "Summary:" followed by your complete summary.
"""

