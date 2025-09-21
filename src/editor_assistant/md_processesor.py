#!/usr/bin/env python3
"""
Document Summarizer

Processes markdown content using large language models with 128k+ context windows
to generate comprehensive summaries in a single request.

Workflow:
1. Validate content size against model context window
2. Analyze the entire document with an LLM to generate a comprehensive summary
3. Translate the summary to Chinese
"""

import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, List
import os
from .config.logging_config import error, progress, warning, user_message

# for LLM processing
from .llm_client import LLMClient

# for data models
from .data_models import MDArticle, ProcessType, SaveType

# for the prompts of the summarizing tasks
from .config.load_prompt import (
    load_research_outliner_prompt,
    load_news_generator_prompt,
    load_translation_prompt
)

# Conservative char/token ratio used throughout the application
CHAR_TOKEN_RATIO = 3.5

# Minimal token count for a sound input whatsoever
MINIMAL_TOKEN_ACCESPTED = 100

class ContentTooLargeError(Exception):
    """Raised when content exceeds model context window capacity."""
    pass

class ContentTooSmallError(Exception):
    """Raised when content is suspiciously small for llm processing."""
    pass

def check_content_size(content: str, llm_client: LLMClient) -> None:
    """
    Check if content size exceeds model context window capacity.
    
    Args:
        content: The content to check
        llm_client: LLM client with model configuration
        
    Raises:
        ContentTooLargeError: If content is too large for the model
    """
    # Estimate token count 
    estimated_tokens = len(content) / CHAR_TOKEN_RATIO
    
    # Calculate available tokens (context - output - prompt overhead)
    prompt_overhead = 10000  # Conservative estimate for prompt
    available_tokens = (llm_client.context_window - prompt_overhead)
    
    if estimated_tokens > available_tokens:
        raise ContentTooLargeError(
            f"Content size ({estimated_tokens:.0f} tokens) exceeds "
            f"model capacity ({available_tokens:.0f} tokens) for {llm_client.model_name}. "
            f"Please use a smaller document or split manually."
        )
    
    if estimated_tokens < MINIMAL_TOKEN_ACCESPTED:
        raise ContentTooSmallError(
            f"Content size ({estimated_tokens:.0f} tokens) is suspiciously small, " 
            f"Please make consult the raw input is properly converted or formatted."
        )


# Summarizer class for processing markdown content
class MDProcessor:
    """
    Processes documents using large language models to generate comprehensive summaries.
    Designed for 128k+ context window models that can handle entire documents in single requests.
    """
    
    def __init__ (self, model_name: str):
        """
        Initialize the summarizer.
        
        Args:
            model_name: Name of the LLM model to use
        """
        self.llm_client = LLMClient(model_name)
    
    def process_mds (self, md_articles: List[MDArticle], type: ProcessType) -> bool:
        """
        Process a document to generate a summary using single-context processing.
        
        Args:
            md_articles: The list of MDArticle objects to summarize
            type: Type of process (outline, news, translate)
            
        Returns:
            bool: True if successful, False otherwise
        """
        
        # Enforce single-article for outline/translate; allow multi-source for brief
        if type == ProcessType.OUTLINE and len(md_articles) != 1:
            error("Outline requires exactly one article (type=paper)")
            return False
        if type == ProcessType.TRANSLATE and len(md_articles) != 1:
            error("Translate requires exactly one article")
            return False

        # Check content size before processing
        for md_article in md_articles:
            try:
                check_content_size(md_article.content, self.llm_client)
            except ContentTooLargeError as e:
                error(f"Content too large: {md_article.title}: {str(e)}")
                return False
            except ContentTooSmallError as e:
                warning(f"Content too small: {md_article.title}: {str(e)}")
                user_message(f"Input markdown: \n{md_article.content}")
                return False

        # Create output dir and save it to the result
        title = md_articles[0].title if md_articles and md_articles[0].title else "untitled"
        if type == ProcessType.BRIEF and len(md_articles) > 1:
            title = f"{title}-multi"
        output_dir = (Path(md_articles[0].output_path).parent / 
                    "llm_summaries" / title / self.llm_client.model_name)
        output_dir.mkdir(parents=True, exist_ok=True)

    
        # Generate the prompt
        prompt = None
        try:
            match type:
                case ProcessType.OUTLINE:
                    prompt = load_research_outliner_prompt(
                        content=md_articles[0].content # only one article for outline
                        )
                case ProcessType.BRIEF:
                    # Pass MDArticle list directly; template handles type casting
                    prompt = load_news_generator_prompt(articles=md_articles)
                case ProcessType.TRANSLATE:
                    prompt = load_translation_prompt(
                        content=md_articles[0].content
                    )
        except Exception as e:
            error(f"Fails to load prompt: str{e}")  
            return False
          
        # Check prompt size
        try:
            check_content_size(prompt, self.llm_client)
        except ContentTooLargeError as e:
            error(f"Content too large: {str(e)}")
            return False
        self._save_content(SaveType.PROMPT, f"{title}_{type.value}", prompt, output_dir)

        # Make LLM request
        try:
            progress(f"Processing document with {len(prompt)} characters...")
            response = self._make_api_request(prompt, type.value)
            
            # Prepend metadata from articles
            metadata_lines = []
            for article in md_articles:
                art_title = article.title or "Untitled"
                art_source = article.source_path or "Unknown Source"
                metadata_lines.append(f"Title: {art_title}")
                metadata_lines.append(f"Source: {art_source}")
            metadata_prefix = "\n".join(metadata_lines) + "\n\n" if metadata_lines else ""
            formatted_response = metadata_prefix + response
            
            self._save_content(SaveType.RESPONSE, f"{title}_{type.value}", formatted_response, output_dir)
        except Exception as e:
            error(f"Error processing document: {str(e)}")
            return False

        # Save token usage report
        try:
            self.llm_client.save_token_usage_report(title, output_dir)
        except Exception as e:
            warning (f"Unable to save token usage report: {str(e)}")
        
        return True
    
    
    
    def _save_content(self, type:SaveType, content_name: str, content: str, 
                      paper_output_dir: Path) -> None:
        """
        Save a prompt to a file for inspection.
        
        Args:
            prompt_name: Name of the prompt
            prompt: The prompt content
            paper_name: Name of the paper
        """
        save_dir = paper_output_dir / type.value
        try:
            os.makedirs(save_dir, exist_ok=True)
        except Exception as e:
            logging.error(f"Error creating directory: {str(e)}")
        
        try:
            with open(f"{save_dir}/{content_name}.md", 'w', encoding='utf-8') as f:
                f.write(content)
            if type == SaveType.RESPONSE:
                user_message(f"{content}")
                progress(f"Saved: {save_dir}/{content_name}.md")
        except Exception as e:
            logging.error(f"Error saving content: {str(e)}")
    

    # def _save_process_times_report(self, paper_name: str, 
    #                                process_times: Dict[str, float], 
    #                                paper_output_dir: Path) -> None:
    #     """
    #     Save a report of process times for the paper processing.
        
    #     Args:
    #         paper_name: Name of the paper
    #         process_times: Dictionary with process times for each step
    #     """
    #     # Create output directory for this paper
    #     token_dir = paper_output_dir / "process_times"
    #     token_dir.mkdir(parents=True, exist_ok=True)
        
    #     # Save as JSON
    #     with open(token_dir / "process_times.json", 'w', encoding='utf-8') as f:
    #         json.dump(process_times, f, indent=2)
        
    #     # Also save a human-readable summary
    #     with open(token_dir / "process_times.txt", 'w', encoding='utf-8') as f:
    #         f.write (f"Process Times Report for {paper_name}\n")
    #         f.write (f"Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    #         f.write ("Summary:\n")
    #         f.write (f"  Total Process Time: {process_times['total']:.2f} seconds ({process_times['total']/60:.2f} minutes)\n\n")
    #         f.write ("Detailed Times by Step:\n")
    #         # Calculate percentages safely to avoid division by zero
    #         analysis_pct = (process_times['analysis']/process_times['total']*100) if process_times['total'] > 0 else 0
    #         translation_pct = (process_times['translation']/process_times['total']*100) if process_times['total'] > 0 else 0
    #         f.write (f"  Analysis: {process_times['analysis']:.2f} seconds ({analysis_pct:.1f}%)\n")
    #         f.write (f"  Translation: {process_times['translation']:.2f} seconds ({translation_pct:.1f}%)\n")

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

# CLI functionality moved to cli.py - this module now contains only core processing logic
