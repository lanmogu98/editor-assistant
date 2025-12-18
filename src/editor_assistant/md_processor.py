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

import logging
import datetime
from pathlib import Path
from typing import Dict, Any, List
import os
from .config.logging_config import error, progress, warning, user_message
from .config.constants import (
    CHAR_TOKEN_RATIO,
    MINIMAL_TOKEN_ACCEPTED,
    PROMPT_OVERHEAD_TOKENS,
    DEBUG_LOGGING_LEVEL,
)

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
    available_tokens = (llm_client.context_window - PROMPT_OVERHEAD_TOKENS)
    
    if estimated_tokens > available_tokens:
        raise ContentTooLargeError(
            f"Content size ({estimated_tokens:.0f} tokens) exceeds "
            f"model capacity ({available_tokens:.0f} tokens) for {llm_client.model_name}. "
            f"Please use a smaller document or split manually."
        )


# Summarizer class for processing markdown content
class MDProcessor:
    """
    Processes documents using large language models to generate comprehensive summaries.
    Designed for 128k+ context window models that can handle entire documents in single requests.
    """
    
    def __init__ (self, model_name: str, thinking_level: str = None):
        """
        Initialize the summarizer.
        
        Args:
            model_name: Name of the LLM model to use
            thinking_level: Optional thinking/reasoning level override (low, medium, high, minimal)
        """
        self.llm_client = LLMClient(model_name, thinking_level=thinking_level)
        self.model_name = model_name
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(DEBUG_LOGGING_LEVEL)
    
    def process_mds (self, md_articles: List[MDArticle], type: ProcessType, output_to_console=True) -> bool:
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

        # Create base title for the output files
        title_base = md_articles[0].title if md_articles and md_articles[0].title else "untitled"
        if type == ProcessType.BRIEF and len(md_articles) > 1:
            title_base = f"{title_base}-multi"
        time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        title = f"{title_base}_{type.value}_{self.model_name}_{time}"

        # Create output directory for the output files
        output_dir = (Path(md_articles[0].output_path).parent / "llm_generations")
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

        # Make LLM request and save the output
        try:
            progress(f"Processing document with {len(prompt)} characters...")
            response = self._make_api_request(prompt, type.value)
        
        except Exception as e:
            error(f"Error making API request: {str(e)}")
            return False

        # Prepend metadata from articles
        metadata_lines = []

        try:
            for article in md_articles:
                art_title = article.title or "Untitled"
                art_source = article.source_path or "Unknown Source"
                metadata_lines.append(f"Title: {art_title}")
                metadata_lines.append(f"Source: {art_source}")
            metadata_prefix = "\n".join(metadata_lines) + "\n\n" if metadata_lines else ""
            formatted_response = metadata_prefix + response
            
            self._save_content(SaveType.RESPONSE, title, 
                               formatted_response, output_dir, output_to_console)
        except Exception as e:
            error(f"Error saving response: {str(e)}")
            return False
        
        # Create bilingual content if translation is requested
        if type == ProcessType.TRANSLATE:
            try:
                bilingual_content = self._create_bilingual_content(md_articles[0].content, response)
                if metadata_lines:
                    bilingual_content = "\n".join(metadata_lines) + "\n\n" + bilingual_content
                self._save_content(SaveType.RESPONSE, f"bilingual_{title}",
                                   bilingual_content, output_dir)
                progress(f"bilingual content generated and saved to {output_dir / f'bilingual_{title}.md'}")
            except Exception as e:
                error(f"Error processing bilingual content: {str(e)}")
                return False



        # Save token usage report
        try:
            self.llm_client.save_token_usage_report(title, output_dir)
        except Exception as e:
            warning (f"Unable to save token usage report: {str(e)}")
        
        return True
    
    def _create_bilingual_content(self, input: str, output: str) -> str:
        """Create a bilingual markdown file with alternating source/translation lines."""
        input_lines = input.strip().split("\n")
        output_lines = output.strip().split("\n")

        # Use list append + join for O(n) performance instead of string concatenation
        bilingual_lines = []
        for i in range(len(input_lines)):
            try:
                bilingual_lines.append(input_lines[i])
                bilingual_lines.append(output_lines[i])
            except IndexError:
                warning(f"Line count mismatch at line {i}: input has {len(input_lines)} lines, output has {len(output_lines)} lines")
                break

        return "\n".join(bilingual_lines) + "\n"


    # save content to a file
    def _save_content(self, type:SaveType, content_name: str, content: str, 
                      paper_output_dir: Path, console_print: bool = False) -> None:
        """
        Save a prompt to a file for inspection.
        
        Args:
            prompt_name: Name of the prompt
            prompt: The prompt content
            paper_name: Name of the paper
        """
        save_dir = paper_output_dir
        try:
            os.makedirs(save_dir, exist_ok=True)
        except OSError as e:
            error(f"Error creating directory: {str(e)}")
            raise

        try:
            with open(f"{save_dir}/{type.value}_{content_name}.md", 'w', encoding='utf-8') as f:
                f.write(content)
            if type == SaveType.RESPONSE and console_print:
                user_message(f"{content}")
        except IOError as e:
            error(f"Error saving content: {str(e)}")
            raise

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
            error(f"Connection failed during {request_name}: {str(e)}")
            raise ConnectionError(f"Failed to connect to LLM service: {str(e)}") from e
        except ValueError as e:
            error(f"Invalid input for {request_name}: {str(e)}")
            raise ValueError(f"Invalid input for {request_name}: {str(e)}") from e
        except Exception as e:
            error(f"Unexpected error in {request_name}: {str(e)}")
            raise RuntimeError(f"Error generating response for {request_name}: {str(e)}") from e

# CLI functionality moved to cli.py - this module now contains only core processing logic
