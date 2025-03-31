"""
Prompt templates for the research paper summarizer.
"""

# Prompt for analyzing a chunk of the paper
RESEARCH_CHUNK_ANALYSIS_PROMPT = """You are a research assistant analyzing a scientific paper. I'll provide a chunk of the paper.

This is chunk {chunk_number}/{total_chunks} of the paper.

Summary of the previous chunk:
{previous_chunksummary}

CONTENT of this chunk:
{content}

Please:
1. Extract key information (methods, findings, conclusions)
2. Identify important concepts, terminology, and relationships
3. Note any figures/tables and their significance
4. Highlight limitations or gaps mentioned
5. Provide a concise summary of this section (150-200 words)

Format your response as:
KEY POINTS:
- Point 1
- Point 2

TERMINOLOGY:
- Term 1: Definition
- Term 2: Definition

FIGURES/TABLES:
- [Figure/Table X]: Brief description and significance

SUMMARY:
[Concise summary of this chunk]
"""

# Prompt for synthesizing the analyses of all chunks
RESEARCH_SYNTHESIS_PROMPT = """You are a research assistant creating a comprehensive summary of a scientific paper. I've analyzed the paper in chunks and will provide the key information from each section.

PAPER SECTIONS:
{analyses}

Please create:
1. An executive summary (250-300 words)
2. A structured overview including:
   - Research question/objective
   - Methodology
   - Key findings
   - Limitations
   - Implications
3. A list of key takeaways (5-7 bullet points)

Your summary should be accurate, concise, and maintain the technical integrity of the original research while being accessible to someone with background knowledge in the field.

Format your response with the heading "Summary:" followed by your complete summary.
"""

