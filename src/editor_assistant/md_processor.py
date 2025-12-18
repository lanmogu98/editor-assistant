#!/usr/bin/env python3
"""
Document Processor

Processes markdown content using large language models with 128k+ context windows.
Uses a pluggable task system for extensibility.

Workflow:
1. Validate content size against model context window
2. Load and validate the appropriate task
3. Build prompt and make LLM request
4. Post-process and save outputs
"""

import logging
import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import os
from .config.logging_config import error, progress, warning, user_message
from .config.constants import (
    CHAR_TOKEN_RATIO,
    PROMPT_OVERHEAD_TOKENS,
    DEBUG_LOGGING_LEVEL,
)

# for LLM processing
from .llm_client import LLMClient

# for data models
from .data_models import MDArticle, ProcessType, SaveType

# for the pluggable task system
from .tasks import TaskRegistry, Task

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
    
    def __init__(self, model_name: str, thinking_level: str = None, stream: bool = True):
        """
        Initialize the processor.
        
        Args:
            model_name: Name of the LLM model to use
            thinking_level: Optional thinking/reasoning level override (low, medium, high, minimal)
            stream: Whether to use streaming output (default: True)
        """
        self.llm_client = LLMClient(model_name, thinking_level=thinking_level)
        self.model_name = model_name
        self.stream = stream
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(DEBUG_LOGGING_LEVEL)
    
    def process_mds(self, md_articles: List[MDArticle], 
                     task_type: Union[ProcessType, str], 
                     output_to_console: bool = True) -> bool:
        """
        Process documents using the pluggable task system.
        
        Args:
            md_articles: The list of MDArticle objects to process
            task_type: Task type (ProcessType enum or string name)
            output_to_console: Whether to print output to console (ignored if streaming)
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Resolve task type to string
        task_name = task_type.value if isinstance(task_type, ProcessType) else task_type
        
        # Get the task class from registry
        task_cls = TaskRegistry.get(task_name)
        if task_cls is None:
            error(f"Unknown task type: {task_name}. Available: {TaskRegistry.list_tasks()}")
            return False
        
        # Instantiate task
        task: Task = task_cls()
        
        # Validate inputs
        is_valid, err_msg = task.validate(md_articles)
        if not is_valid:
            error(f"Validation failed for {task_name}: {err_msg}")
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
        if task.supports_multi_input and len(md_articles) > 1:
            title_base = f"{title_base}-multi"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        title = f"{title_base}{task.get_output_suffix()}_{self.model_name}_{timestamp}"

        # Create output directory
        output_dir = (Path(md_articles[0].output_path).parent / "llm_generations")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build prompt using task
        try:
            prompt = task.build_prompt(md_articles)
        except Exception as e:
            error(f"Failed to build prompt: {e}")
            return False
          
        # Check prompt size
        try:
            check_content_size(prompt, self.llm_client)
        except ContentTooLargeError as e:
            error(f"Prompt too large: {str(e)}")
            return False

        # Make LLM request
        try:
            progress(f"Processing document with {len(prompt)} characters...")
            response = self._make_api_request(prompt, task_name, stream=self.stream)
        except Exception as e:
            error(f"Error making API request: {str(e)}")
            return False

        # Build metadata prefix
        metadata_lines = []
        for article in md_articles:
            metadata_lines.append(f"Title: {article.title or 'Untitled'}")
            metadata_lines.append(f"Source: {article.source_path or 'Unknown Source'}")
        metadata_prefix = "\n".join(metadata_lines) + "\n\n" if metadata_lines else ""

        # Post-process response using task
        try:
            outputs = task.post_process(response, md_articles)
        except Exception as e:
            error(f"Post-processing failed: {e}")
            return False

        # Save all outputs
        # Note: if streaming, content was already printed in real-time
        should_print = output_to_console and not self.stream
        try:
            for output_name, content in outputs.items():
                formatted_content = metadata_prefix + content
                
                if output_name == "main":
                    self._save_content(SaveType.RESPONSE, title, 
                                       formatted_content, output_dir, should_print)
                else:
                    # Additional outputs (e.g., bilingual)
                    self._save_content(SaveType.RESPONSE, f"{output_name}_{title}",
                                       formatted_content, output_dir, False)
                    progress(f"{output_name} output saved to {output_dir / f'{output_name}_{title}.md'}")
        except Exception as e:
            error(f"Error saving response: {str(e)}")
            return False

        # Save token usage report
        try:
            self.llm_client.save_token_usage_report(title, output_dir)
        except Exception as e:
            warning(f"Unable to save token usage report: {str(e)}")
        
        return True


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

    def _make_api_request(self, prompt: str, request_name: str, stream: bool = False) -> str:
        """
        Make an API request to the LLM client.
        
        Args:
            prompt: The prompt to send
            request_name: Name of the request for tracking
            stream: Whether to use streaming output
            
        Returns:
            The response text
        """
        try:
            return self.llm_client.generate_response(prompt, request_name, stream=stream)
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
