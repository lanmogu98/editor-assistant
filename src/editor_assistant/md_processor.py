#!/usr/bin/env python3
"""
Document Processor (Async Refactor).

Processes markdown content using large language models with 128k+ context windows.
Uses a pluggable task system for extensibility.

Workflow:
1. Validate content size against model context window
2. Load and validate the appropriate task
3. Build prompt and make LLM request (Async)
4. Post-process and save outputs
"""

import logging
import datetime
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Callable
import os
from .config.logging_config import error, progress, warning, user_message
from .config.constants import (
    PROMPT_OVERHEAD_TOKENS,
    DEBUG_LOGGING_LEVEL,
    OUTPUT_TOKEN_RESERVE,
)

# for LLM processing
from .llm_client import LLMClient

# for data models
from .data_models import MDArticle, ProcessType, SaveType

# for the pluggable task system
from .tasks import TaskRegistry, Task

# for storage
from .storage import RunRepository
# for content validation
from .content_validation import validate_content, BlockedPublisherError
# for token estimation
from .utils import estimate_tokens

class ContentTooLargeError(Exception):
    """Raised when content exceeds model context window capacity."""
    pass

class ContentTooSmallError(Exception):
    """Raised when content is suspiciously small for llm processing."""
    pass

def check_context_budget(content: str, llm_client: LLMClient) -> None:
    """
    Context-budget guardrail.
    """
    estimated_tokens = estimate_tokens(content)

    # Reserve space for prompt overhead and model output
    output_reserve = llm_client.max_tokens or OUTPUT_TOKEN_RESERVE
    # Avoid over-reserving relative to context
    output_reserve = min(output_reserve, llm_client.context_window // 2)

    available_tokens = llm_client.context_window - PROMPT_OVERHEAD_TOKENS - output_reserve

    if available_tokens <= 0:
        raise ContentTooLargeError(
            f"Model capacity too small after reserves for {llm_client.model_name}."
        )

    if estimated_tokens > available_tokens:
        raise ContentTooLargeError(
            f"Content size ({estimated_tokens:.0f} tokens) exceeds "
            f"model capacity ({available_tokens:.0f} tokens) for {llm_client.model_name} "
            f"(reserved {output_reserve} for output, {PROMPT_OVERHEAD_TOKENS} for prompt). "
            f"Please use a smaller document or split manually."
        )


class MDProcessor:
    """
    Processes documents using large language models (Async).
    """
    
    def __init__(self, model_name: str, thinking_level: str = None, stream: bool = True, max_concurrent: int = 5):
        """
        Initialize the processor.
        
        Args:
            model_name: Name of the LLM model to use
            thinking_level: Optional thinking/reasoning level override
            stream: Whether to use streaming output
            max_concurrent: Maximum number of concurrent requests (semaphore size)
        """
        self.llm_client = LLMClient(model_name, thinking_level=thinking_level)
        self.model_name = model_name
        self.thinking_level = thinking_level
        self.stream = stream
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(DEBUG_LOGGING_LEVEL)
        
        # Initialize storage repository
        self.repository = RunRepository()
        
        # Concurrency control
        self._semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_mds(self, md_articles: List[MDArticle],
                     task_type: Union[ProcessType, str],
                     output_to_console: bool = True,
                     save_files: bool = False,
                     stream_callback: Optional[Callable[[str], None]] = None) -> tuple[bool, int]:
        """
        Process documents using the pluggable task system (Async).
        
        Args:
            stream_callback: Optional callback function to receive streaming chunks.
                           If None and output_to_console is True, chunks are printed to stdout.
        """
        run_id = -1

        # Resolve task type to string
        task_name = task_type.value if isinstance(task_type, ProcessType) else task_type
        
        # Get the task class from registry
        task_cls = TaskRegistry.get(task_name)
        if task_cls is None:
            error(f"Unknown task type: {task_name}. Available: {TaskRegistry.list_tasks()}")
            return False, run_id
        
        # Instantiate task
        task: Task = task_cls()
        
        # Validate inputs (task-level)
        is_valid, err_msg = task.validate(md_articles)
        if not is_valid:
            error(f"Validation failed for {task_name}: {err_msg}")
            return False, run_id

        # Content validation per article
        for md_article in md_articles:
            try:
                source_url = md_article.source_path if md_article.source_path and str(md_article.source_path).startswith("http") else None
                is_content_valid, warn_msg = validate_content(
                    md_article.content or "",
                    source_url=source_url
                )
                if warn_msg:
                    warning(warn_msg)
                if not is_content_valid:
                    error(f"Content invalid for {md_article.title or 'Untitled'}: {warn_msg}")
                    return False, run_id
            except BlockedPublisherError as e:
                error(f"Blocked publisher: {e}")
                return False, run_id

        # Context budget check
        for md_article in md_articles:
            try:
                check_context_budget(md_article.content or "", self.llm_client)
            except ContentTooLargeError as e:
                error(f"Content too large: {md_article.title}: {str(e)}")
                return False, run_id

        # Create run record in database (Async via thread pool)
        # Offload synchronous DB write to prevent blocking the event loop
        try:
            run_id = await asyncio.to_thread(self._create_run_record, md_articles, task_name)
        except Exception as e:
            self.logger.warning(f"Async DB creation failed, falling back: {e}")
            run_id = self._create_run_record(md_articles, task_name)

        # Create base title
        title_base = md_articles[0].title if md_articles and md_articles[0].title else "untitled"
        if task.supports_multi_input and len(md_articles) > 1:
            title_base = f"{title_base}-multi"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        title = f"{title_base}{task.get_output_suffix()}_{self.model_name}_{timestamp}"

        output_dir = None
        if save_files:
            base_output = Path(md_articles[0].output_path) if md_articles[0].output_path else Path.cwd()
            # If base_output is a file (e.g. input file path), use its parent directory
            if base_output.is_file():
                base_output = base_output.parent
                
            output_dir = base_output / "llm_summaries" / self.model_name
            output_dir.mkdir(parents=True, exist_ok=True)

        # Build prompt using task
        try:
            prompt = task.build_prompt(md_articles)
        except Exception as e:
            error(f"Failed to build prompt: {e}")
            return False, run_id
          
        # Check prompt size
        try:
            check_context_budget(prompt, self.llm_client)
        except ContentTooLargeError as e:
            error(f"Prompt too large: {str(e)}")
            return False, run_id

        # Make LLM request (Async with Semaphore)
        try:
            progress(f"Processing document with {len(prompt)} characters...")
            async with self._semaphore:
                # If output_to_console is False and no callback provided, suppress output
                final_callback = stream_callback
                if final_callback is None and not output_to_console:
                    final_callback = lambda x: None
                
                response = await self._make_api_request(prompt, task_name, stream=self.stream, stream_callback=final_callback)
        except Exception as e:
            error(f"Error making API request: {str(e)}")
            await asyncio.to_thread(self._update_run_status, run_id, "failed", str(e))
            return False, run_id

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
            await asyncio.to_thread(self._update_run_status, run_id, "failed", str(e))
            return False, run_id

        # Save all outputs
        should_print = output_to_console and not self.stream
        try:
            for output_name, content in outputs.items():
                formatted_content = metadata_prefix + content
                
                # Save to file (optional)
                if save_files and output_dir:
                    if output_name == "main":
                        self._save_content(SaveType.RESPONSE, title, 
                                           formatted_content, output_dir, should_print)
                    else:
                        self._save_content(SaveType.RESPONSE, f"{output_name}_{title}",
                                           formatted_content, output_dir, False)
                        progress(f"{output_name} output saved to {output_dir / f'{output_name}_{title}.md'}")
                
                # Save to database (Async via thread pool)
                await asyncio.to_thread(self._save_output_to_db, run_id, output_name, content)
                
        except Exception as e:
            error(f"Error saving response: {str(e)}")
            await asyncio.to_thread(self._update_run_status, run_id, "failed", str(e))
            return False, run_id

        # Save token usage (Async via thread pool)
        try:
            if save_files and output_dir:
                self.llm_client.save_token_usage_report(title, output_dir)
            await asyncio.to_thread(self._save_token_usage_to_db, run_id)
        except Exception as e:
            warning(f"Unable to save token usage report: {str(e)}")
        
        # Mark run as successful (Async via thread pool)
        await asyncio.to_thread(self._update_run_status, run_id, "success")
        
        return True, run_id


    # save content to a file
    def _save_content(self, type:SaveType, content_name: str, content: str, 
                      paper_output_dir: Path, console_print: bool = False) -> None:
        """Save content to a file."""
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

    async def _make_api_request(self, prompt: str, request_name: str, stream: bool = False, stream_callback: Optional[Callable[[str], None]] = None) -> str:
        """
        Make an API request to the LLM client (Async).
        """
        try:
            # Important: Use context manager to ensure connection is closed if we're not reusing it?
            # RFC Plan: Use __aenter__ in LLMClient.
            # But here we have self.llm_client which is persistent for MDProcessor lifetime.
            # We can just call generate_response, as we implemented auto-client creation inside it.
            return await self.llm_client.generate_response(prompt, request_name, stream=stream, stream_callback=stream_callback)
        except ConnectionError as e:
            error(f"Connection failed during {request_name}: {str(e)}")
            raise ConnectionError(f"Failed to connect to LLM service: {str(e)}") from e
        except ValueError as e:
            error(f"Invalid input for {request_name}: {str(e)}")
            raise ValueError(f"Invalid input for {request_name}: {str(e)}") from e
        except Exception as e:
            error(f"Unexpected error in {request_name}: {str(e)}")
            raise RuntimeError(f"Error generating response for {request_name}: {str(e)}") from e

    # =========================================================================
    # Database Helper Methods (Synchronous - Called in Thread Pool)
    # =========================================================================
    
    def _create_run_record(self, md_articles: List[MDArticle], task_name: str) -> int:
        try:
            input_ids = []
            for article in md_articles:
                input_id = self.repository.get_or_create_input(
                    input_type=article.type.value,
                    source_path=article.source_path or "",
                    title=article.title or "Untitled",
                    content=article.content or ""
                )
                input_ids.append(input_id)
            
            run_id = self.repository.create_run(
                task=task_name,
                model=self.model_name,
                input_ids=input_ids,
                thinking_level=self.thinking_level,
                stream=self.stream,
                currency=self.llm_client.pricing_currency
            )
            return run_id
        except Exception as e:
            self.logger.warning(f"Failed to create run record: {e}")
            return -1
    
    def _update_run_status(self, run_id: int, status: str, error_message: str = None) -> None:
        if run_id < 0: return
        try:
            self.repository.update_run_status(run_id, status, error_message)
        except Exception as e:
            self.logger.warning(f"Failed to update run status: {e}")
    
    def _save_output_to_db(self, run_id: int, output_type: str, content: str) -> None:
        if run_id < 0: return
        try:
            content_type = "json" if content.strip().startswith(("{", "[")) else "text"
            self.repository.add_output(run_id, output_type, content, content_type)
        except Exception as e:
            self.logger.warning(f"Failed to save output to database: {e}")
    
    def _save_token_usage_to_db(self, run_id: int) -> None:
        if run_id < 0: return
        try:
            usage = self.llm_client.get_token_usage()
            self.repository.add_token_usage(
                run_id=run_id,
                input_tokens=usage.get("total_input_tokens", 0),
                output_tokens=usage.get("total_output_tokens", 0),
                cost_input=usage.get("cost", {}).get("input_cost", 0),
                cost_output=usage.get("cost", {}).get("output_cost", 0),
                process_time=usage.get("process_times", {}).get("total_time", 0)
            )
        except Exception as e:
            self.logger.warning(f"Failed to save token usage to database: {e}")
