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
from typing import Dict, Any
import os
from enum import Enum

class ArticleType(str,Enum):
    research = 'r'
    news = 'n'

class ContentTooLargeError(Exception):
    """Raised when content exceeds model context window capacity."""
    pass

def check_content_size(content: str, llm_client) -> None:
    """
    Check if content size exceeds model context window capacity.
    
    Args:
        content: The content to check
        llm_client: LLM client with model configuration
        
    Raises:
        ContentTooLargeError: If content is too large for the model
    """
    # Estimate token count (conservative 3.5 chars/token ratio)
    estimated_tokens = len(content) / 3.5
    
    # Calculate available tokens (context - output - prompt overhead)
    prompt_overhead = 10000  # Conservative estimate for prompt
    available_tokens = (llm_client.context_window - 
                       llm_client.max_tokens - 
                       prompt_overhead)
    
    if estimated_tokens > available_tokens:
        raise ContentTooLargeError(
            f"Content size ({estimated_tokens:.0f} tokens) exceeds "
            f"model capacity ({available_tokens:.0f} tokens) for {llm_client.model_name}. "
            f"Please use a smaller document or split manually."
        )

# for LLM processing
from .llm_client import LLMClient

# for the prompts of the summarizing tasks
from .config.load_prompt import (
    load_research_outliner_prompt,
    load_news_generator_prompt,
    load_translation_prompt
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
        self.save_type = {
            "prompt": "prompts",
            "response": "responses",
        }

        # set up the logger
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        self.logger.debug("Markdown Summarizer Initialized")
    

    def process_md (self, content_path: str, type: ArticleType) -> bool:
        """
        Process a document to generate a summary using single-context processing.
        
        Args:
            content_path: The path to the markdown content to summarize
            type: Type of article (research or news)
            
        Returns:
            success: True if the summary is generated successfully, False otherwise
        """
        success = False

        # Initialize process times tracking
        process_times = {
            "total": 0,
            "analysis": 0,
            "translation": 0
        }
        start_total = time.time()
        
        # Read the content from the file
        suffix = Path(content_path).suffix.lower()
        with open(content_path, 'r', encoding='utf-8') as f:
            content = f.read()
        assert suffix == ".md" and content is not None
        
        # Check content size before processing
        try:
            check_content_size(content, self.llm_client)
        except ContentTooLargeError as e:
            self.logger.error(f"Content too large: {str(e)}")
            return False
        
        # Get title
        title = Path(content_path).stem

        # Create the output directory for this input
        output_dir = (Path(content_path).parent.absolute() / 
                            "llm_summaries" / 
                            f"{title}_{self.llm_client.model_name}") / type.value
        output_dir.mkdir(parents=True, exist_ok=True)
        self.logger.debug(f"Summarizer output directory: {output_dir}")
        
        # Step 1: Analyze the entire document in single context
        start_analysis = time.time()
        try:
            self.logger.info(f"Processing document with {len(content)} characters...")
            
            # Generate analysis prompt for single document
            prompt = ""
            match type:
                case ArticleType.research:
                    prompt = load_research_outliner_prompt(
                        content=content
                    )
                case ArticleType.news:
                    prompt = load_news_generator_prompt(
                        content=content
                    )
                case _:
                    raise ValueError(f"Invalid article type: {type}")
            
            self._save_content("prompt", "analysis", prompt, output_dir)
            response = self._make_api_request(prompt, "analysis")
            self._save_content("response", "analysis", response, output_dir)
            
        except Exception as e:
            self.logger.error(f"Error analyzing document: {str(e)}")
            return success
        
        process_times["analysis"] = time.time() - start_analysis
        
        # Step 2: For outliner, translate the synthesis to Chinese
        if type == ArticleType.research:
            self.logger.info (f"Translating outlining to Chinese...")
            start_translation = time.time()
        
            translation_prompt = load_translation_prompt(
                content=response if response else "",
                title=title
            )
            
            try:
                self._save_content("prompt", "translation", translation_prompt, 
                            output_dir)
                translation_response = self._make_api_request(translation_prompt, 
                                                            "translation")
                self._save_content("response", "translation", 
                                translation_response, output_dir)
                
            except Exception as e:
                self.logger.error(f"Error translating summary: {str(e)}")
                return success
        
            # mark the success
            success = True
            
            # save the translation time
            process_times["translation"] = time.time() - start_translation
            
            # Calculate total process time
            process_times["total"] = time.time() - start_total
        else:
            success = True
            # Calculate total process time for news articles too
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
        
        # Show output location for successful processing
        if success:
            from .config.logging_config import progress, user_message
            if type == ArticleType.news:
                news_file = output_dir / "responses" / "analysis.md"
                if news_file.exists():
                    progress(f"News article generated: \n")
                    user_message(f"{response} \n")
                    progress(f"News article saved: {news_file}")
            else:  # research
                outline_file = output_dir / "responses" / "analysis.md"
                translation_file = output_dir / "responses" / "translation.md"
                if outline_file.exists():
                    progress(f"Research outline saved: {outline_file}")
                if translation_file.exists():
                    translation_preview = translation_response[:400] + "..."
                    progress(f"Chinese translation preview:  \n ")
                    user_message(f"{translation_preview} \n")
                    progress(f"Chinese translation saved: {translation_file}")
        
        return success
    
    
    
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
            # Calculate percentages safely to avoid division by zero
            analysis_pct = (process_times['analysis']/process_times['total']*100) if process_times['total'] > 0 else 0
            translation_pct = (process_times['translation']/process_times['total']*100) if process_times['total'] > 0 else 0
            f.write (f"  Analysis: {process_times['analysis']:.2f} seconds ({analysis_pct:.1f}%)\n")
            f.write (f"  Translation: {process_times['translation']:.2f} seconds ({translation_pct:.1f}%)\n")

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