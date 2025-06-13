#!/usr/bin/env python3
"""
Research Paper Summarizer

Uses the ContentChunker to split input markdown content into manageable chunks,
then processes each chunk with an LLM to generate a comprehensive summary.

Workflow is as follows:
1. Split the input markdown content into chunks
2. Analyze each chunk with an LLM to generate a summary
3. Synthesize the summaries into a final summary
4. Translate the summary to Chinese
"""

import json
import logging
import re
import time
from pathlib import Path
from typing import Dict, Optional, Any
import os
from enum import Enum

# TODO: add a new type for other types of articles
class ArticleType(Enum):
    research = 'r'
    news = 'n'

# for chunking the md content
from .content_chunker import ContentChunker

# for the prompts of the summarizing tasks
from ..config.prompt_templates.translator import TRANSLATION_PROMPT
from ..config.prompt_templates.research_summarizer import (
    RESEARCH_CHUNK_ANALYSIS_PROMPT,
    RESEARCH_SYNTHESIS_PROMPT)
from ..config.prompt_templates.news_summarizer import (
    NEWS_CHUNK_ANALYSIS_PROMPT,
    NEWS_SYNTHESIS_PROMPT)

from ..config.llms.llm_config import llm_config

# prompts
SUMMARIZER_PROMPTS = {
    ArticleType.research: {
        "chunk_analysis_prompt": RESEARCH_CHUNK_ANALYSIS_PROMPT,
        "synthesis_prompt": RESEARCH_SYNTHESIS_PROMPT,
    },
    ArticleType.news: {
        "chunk_analysis_prompt": NEWS_CHUNK_ANALYSIS_PROMPT,
        "synthesis_prompt": NEWS_SYNTHESIS_PROMPT,
    }
}

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Summarizer class for processing markdown content
class MDSummarizer:
    """
    Processes research papers by chunking them and using an LLM to generate 
    summaries.
    """
    
    def __init__ (self, llm_client, type: ArticleType):
        """
        Initialize the summarizer.
        
        Args:
            llm_client: Client for interacting with the LLM API
            output_dir: Directory to save summaries
        """
        # Dynamically calculate max_chunk_size based on model limits from the client
        model_context_window = llm_client.model_context_window
        max_output_tokens = llm_client.max_tokens

        # Reserve a conservative 10,000 tokens for prompt overhead 
        # (template + previous summary) to ensure the chunk content fits.
        prompt_overhead = 10000
        
        # Calculate the token budget for the main content chunk
        content_token_budget = (model_context_window - max_output_tokens - 
                                prompt_overhead)
        
        # Convert token budget to character count for the chunker
        # Using a ratio of 3.5 chars/token for English
        char_per_token_ratio = 3.5
        max_chars = int(content_token_budget * char_per_token_ratio)

        self.content_chunker = ContentChunker(max_chunk_size=max_chars)
        self.llm_client = llm_client
        self.save_type = {
            "chunk": "chunks",
            "prompt": "prompts",
            "response": "responses",
        }

        # set up the article type
        self.type = type

        # set up the logger
        self.logger = logging.getLogger(__name__)
        self.logger.info("Markdown Summarizer Initialized")
    

    def summarize_md (self, content_path: str) -> bool:
        """
        Process a research paper to generate a summary.
        
        Args:
            content_path: The path to the markdown content to summarize
            
        Returns:
            success: True if the summary is generated successfully, False otherwise
        """
        # initialize the success flag
        success = False

        # Initialize process times tracking
        process_times = {
            "total": 0,
            "chunking": 0,
            "chunk_analysis": 0,
            "synthesis": 0,
            "translation": 0
        }
        start_total = time.time()
        
        # read the content from the file
        suffix = Path(content_path).suffix.lower()
        with open(content_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert suffix == ".md" and content is not None
        
        # get title
        title = Path(content_path).stem

        # create the output directory for this input
        output_dir = (Path(content_path).parent.absolute() / 
                            "llm_summaries" / 
                            f"{title}_{self.llm_client.model_name}")
        output_dir.mkdir(parents=True, exist_ok=True)
        self.logger.debug (f"Summarizer output directory: {output_dir}")
        
        # Step 1: Split the paper into chunks
        start_chunking = time.time()
        chunk_result = self.content_chunker.process_content(content)
        chunks = [chunk['content'] for chunk in chunk_result['chunks']]
        process_times["chunking"] = time.time() - start_chunking
        
        # Save the chunks for inspection
        for i, chunk in enumerate(chunks):
            self._save_content("chunk", f"chunk_{i+1}", chunk, output_dir)
        self.logger.debug (f"Saved {len(chunks)} chunks to {output_dir}")
        
        # Step 2: Analyze each chunk
        start_chunk_analysis = time.time()
        chunk_analyses = []

        total_chunks = len(chunks)
        for i, chunk in enumerate(chunks):
            try:
                prompt = SUMMARIZER_PROMPTS[self.type]["chunk_analysis_prompt"].\
                format(
                    chunk_number=i+1,
                    total_chunks=total_chunks,
                    previous_chunksummary=chunk_analyses[i-1] if i > 0 else "",
                    content=chunk
                )
            except Exception as e:
                self.logger.error(f"Error formatting prompt for chunk {i+1}: {str(e)}")
                return success
            
            try:
                self.logger.info (f"Processing chunk {i+1}/{total_chunks}...")
                self._save_content("prompt", f"chunk_analysis_{i+1}", 
                                   prompt, output_dir)
                response = self._make_api_request(prompt, 
                                                  f"chunk_analysis_{i+1}")
                # Save the full response
                self._save_content("response", f"chunk_analysis_{i+1}", 
                                   response["text"], output_dir)
                
                # If there is only one chunk, skip the summary extraction
                if total_chunks == 1:
                    synthesis_response = response
                    break

                # for research papers, extract the summary from the response
                if self.type == ArticleType.research:
                    summary = self._extract_summary(response["text"])
                    if summary:
                        chunk_analyses.append(summary)
                    else:
                        self.logger.warning(
                            f"{title}: Could not extract summary "
                            f"from chunk {i+1}"
                        )
                        chunk_analyses.append(response["text"])
                # for news papers, add the response directlyto the chunk analyses
                elif self.type == ArticleType.news:
                    chunk_analyses.append(response["text"])

            except Exception as e:
                self.logger.error(f"Error analyzing chunk {i+1}: {str(e)}")
                return success
        
        process_times["chunk_analysis"] = time.time() - start_chunk_analysis
        
        # Step 3: Synthesize the analyses into a final summary
        start_synthesis = time.time()
        if total_chunks > 1:
            self.logger.info (f"Synthesizing {len(chunk_analyses)} chunks...")
            combined_analyses = "\n\n".join([f"Chunk {i+1} Analysis:\n{analysis}" 
                                             for i, analysis in 
                                             enumerate(chunk_analyses)])
            synthesis_prompt = SUMMARIZER_PROMPTS[self.type]["synthesis_prompt"]\
                                            .format(analyses=combined_analyses)
            self._save_content("prompt", "synthesis", synthesis_prompt, output_dir)       
            
            try:
                synthesis_response = self._make_api_request(synthesis_prompt, 
                                                            "synthesis")
                self._save_content("response", "synthesis", 
                                   synthesis_response["text"], output_dir)
                
            except Exception as e:
                self.logger.error(f"Error synthesizing summary: {str(e)}")
                return success
        
        process_times["synthesis"] = time.time() - start_synthesis
        
        # Step 4: Translate the synthesis to Chinese
        self.logger.info (f"Translating synthesis to Chinese...")
        start_translation = time.time()
        
        translation_prompt = TRANSLATION_PROMPT.format(
            content=synthesis_response["text"] if synthesis_response else "",
            title=title
        )
        
        try:
            self._save_content("prompt", "translation", translation_prompt, 
                           output_dir)
            translation_response = self._make_api_request(translation_prompt, 
                                                          "translation")
            self._save_content("response", "translation", 
                               translation_response["text"], output_dir)
            
        except Exception as e:
            self.logger.error(f"Error translating summary: {str(e)}")
            return success
        
        # mark the success
        success = True
        
        # save the translation time
        process_times["translation"] = time.time() - start_translation
        
        # Calculate total process time
        process_times["total"] = time.time() - start_total
        
        # Save process times report
        try:
            self._save_process_times_report(title, process_times, output_dir)
        except Exception as e:
            self.logger.warning (f"Unable to save process times report: {str(e)}")
        
        # Save token usage report
        try:
            self.llm_client.save_token_usage_report(title, output_dir)
        except Exception as e:
            self.logger.warning (f"Unable to save token usage report: {str(e)}")
        
        # Return the summary and metadata
        return success
    
    
    def _extract_summary(self, response: str) -> Optional[str]:
        """
        Extract the summary section from a chunk analysis response.
        
        Args:
            response: The LLM response
            
        Returns:
            The extracted summary or None if not found
        """
        # Try to extract the summary section using regex
        summary_match = re.search (r'(?:SUMMARY:|Summary:)(.*?)(?:$|(?:\n\n(?:[A-Z]+:|$)))', 
                                   response, re.DOTALL | re.IGNORECASE)
        
        if summary_match:
            summary = summary_match.group(1).strip()
            return summary
        
        return None
    
    def _save_content(self, type:str, content_name: str, content: str, 
                      paper_output_dir: Path) -> None:
        """
        Save a prompt to a file for inspection.
        
        Args:
            prompt_name: Name of the prompt
            prompt: The prompt content
            paper_name: Name of the paper
        """
        save_dir = paper_output_dir / self.save_type[type]
        try:
            os.makedirs(save_dir, exist_ok=True)
        except Exception as e:
            logging.error(f"Error creating directory: {str(e)}")
        
        try:
            with open(f"{save_dir}/{content_name}.md", 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            logging.error(f"Error saving content: {str(e)}")
    

    def _save_process_times_report(self, paper_name: str, 
                                   process_times: Dict[str, float], 
                                   paper_output_dir: Path) -> None:
        """
        Save a report of process times for the paper processing.
        
        Args:
            paper_name: Name of the paper
            process_times: Dictionary with process times for each step
        """
        # Create output directory for this paper
        token_dir = paper_output_dir / "process_times"
        token_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as JSON
        with open(token_dir / "process_times.json", 'w', encoding='utf-8') as f:
            json.dump(process_times, f, indent=2)
        
        # Also save a human-readable summary
        with open(token_dir / "process_times.txt", 'w', encoding='utf-8') as f:
            f.write (f"Process Times Report for {paper_name}\n")
            f.write (f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write ("Summary:\n")
            f.write (f"  Total Process Time: {process_times['total']:.2f} seconds ({process_times['total']/60:.2f} minutes)\n\n")
            f.write ("Detailed Times by Step:\n")
            f.write (f"  Chunking: {process_times['chunking']:.2f} seconds ({process_times['chunking']/process_times['total']*100:.1f}%)\n")
            f.write (f"  Chunk Analysis: {process_times['chunk_analysis']:.2f} seconds ({process_times['chunk_analysis']/process_times['total']*100:.1f}%)\n")
            f.write (f"  Synthesis: {process_times['synthesis']:.2f} seconds ({process_times['synthesis']/process_times['total']*100:.1f}%)\n")
            f.write (f"  Translation: {process_times['translation']:.2f} seconds ({process_times['translation']/process_times['total']*100:.1f}%)\n")

    def _make_api_request(self, prompt: str, request_name: str) -> Dict[str, Any]:
        """
        Make an API request to the LLM client.
        
        Args:
            prompt: The prompt to send
            request_name: Name of the request for tracking
            
        Returns:
            Dictionary with the response and metadata
        """
        try:
            return self.llm_client.generate_response(prompt, request_name)
        except ConnectionError as e:
            logging.error(f"Connection failed during {request_name}: {str(e)}")
            raise ConnectionError(f"Failed to connect to LLM service: {str(e)}") from e
        except ValueError as e:
            logging.error(f"Invalid input for {request_name}: {str(e)}")
            raise ValueError(f"Invalid input for {request_name}: {str(e)}") from e
        except Exception as e:
            logging.error(f"Unexpected error in {request_name}: {str(e)}")
            raise Exception(f"Error generating response for {request_name}: {str(e)}") from e

if __name__ == "__main__":
    from .llm_client import LLMClient
    from .md_summarizer import MDSummarizer

    llm_client = LLMClient(model_name="deepseek-v3")
    md_summarizer = MDSummarizer(llm_client, "research")

    md_path = "samples/test_results/2025-06-05_11-22-23/url_BMC_Mapping \
the viruses belonging to the order Bunyavirales in China.md"
    md_summarizer.summarize_md(md_path)