#!/usr/bin/env python3
"""
Document Processor (Async Refactor).

Processes markdown content using large language models.
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
from typing import Dict, Any, List, Optional, Union, Callable, Tuple
import os

from llm_exec_core.usage import format_usage_report

from .config.logging_config import error, progress, warning, user_message
from .config.constants import (
    PROMPT_OVERHEAD_TOKENS,
    DEBUG_LOGGING_LEVEL,
    OUTPUT_TOKEN_RESERVE,
)

# for LLM processing
from .llm_client import LLMClient, LLMResult

# for data models
from .data_models import (
    MDArticle,
    OutputArtifact,
    ProcessType,
    SaveType,
    TaskExecutionResult,
)

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
    if llm_client.context_window is None:
        raise ContentTooLargeError(
            "Model context window is not configured for "
            f"{llm_client.model_name}."
        )

    estimated_tokens = estimate_tokens(content)
    context_window = llm_client.context_window

    # Reserve space for prompt overhead and model output
    output_reserve = llm_client.max_tokens or OUTPUT_TOKEN_RESERVE
    # Avoid over-reserving relative to context
    output_reserve = min(output_reserve, context_window // 2)

    available_tokens = context_window - PROMPT_OVERHEAD_TOKENS - output_reserve

    if available_tokens <= 0:
        raise ContentTooLargeError(
            "Model capacity too small after reserves for "
            f"{llm_client.model_name}."
        )

    if estimated_tokens > available_tokens:
        raise ContentTooLargeError(
            f"Content size ({estimated_tokens:.0f} tokens) exceeds "
            f"model capacity ({available_tokens:.0f} tokens) "
            f"for {llm_client.model_name} "
            f"(reserved {output_reserve} for output, "
            f"{PROMPT_OVERHEAD_TOKENS} for prompt). "
            f"Please use a smaller document or split manually."
        )


class MDProcessor:
    """
    Processes documents using large language models (Async).
    """

    def __init__(
        self,
        model_name: str,
        thinking_level: Optional[str] = None,
        stream: bool = True,
        max_concurrent: int = 5,
    ) -> None:
        """
        Initialize the processor.

        Args:
            model_name: Name of the LLM model to use
            thinking_level: Optional thinking/reasoning level override
            stream: Whether to use streaming output
            max_concurrent: Maximum number of concurrent requests
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

    async def execute_task(
        self,
        md_articles: List[MDArticle],
        task_type: Union[ProcessType, str],
        output_to_console: bool = True,
        save_files: bool = False,
        stream_callback: Optional[Callable[[str], None]] = None,
    ) -> TaskExecutionResult:
        """Execute a task and return its successful typed result.

        Validation, provider, and post-processing exceptions propagate to
        typed callers.
        """
        result = await self._execute_task(
            md_articles,
            task_type,
            output_to_console=output_to_console,
            save_files=save_files,
            stream_callback=stream_callback,
            use_legacy_client=False,
        )
        if result is None:
            raise RuntimeError("Typed task execution produced no result.")
        return result

    async def process_mds(
        self,
        md_articles: List[MDArticle],
        task_type: Union[ProcessType, str],
        output_to_console: bool = True,
        save_files: bool = False,
        stream_callback: Optional[Callable[[str], None]] = None,
    ) -> tuple[bool, int]:
        """Compatibility wrapper returning the legacy success tuple."""
        run_id = -1

        def remember_run_id(value: int) -> None:
            nonlocal run_id
            run_id = value

        try:
            await self._execute_task(
                md_articles,
                task_type,
                output_to_console=output_to_console,
                save_files=save_files,
                stream_callback=stream_callback,
                use_legacy_client=True,
                on_run_created=remember_run_id,
            )
        except asyncio.CancelledError:
            raise
        except Exception:
            return False, run_id

        return True, run_id

    async def _execute_task(
        self,
        md_articles: List[MDArticle],
        task_type: Union[ProcessType, str],
        output_to_console: bool,
        save_files: bool,
        stream_callback: Optional[Callable[[str], None]],
        *,
        use_legacy_client: bool,
        on_run_created: Optional[Callable[[int], None]] = None,
    ) -> Optional[TaskExecutionResult]:
        """
        Process documents using the pluggable task system (Async).

        Args:
            stream_callback: Optional callback for streaming chunks.
                If None and output_to_console is True, chunks print to stdout.
        """
        run_id = -1

        # Resolve task type to string
        task_name = (
            task_type.value
            if isinstance(task_type, ProcessType)
            else task_type
        )

        # Get the task class from registry
        task_cls = TaskRegistry.get(task_name)
        if task_cls is None:
            available_tasks = TaskRegistry.list_tasks()
            message = (
                f"Unknown task type: {task_name}. Available: {available_tasks}"
            )
            error(message)
            raise ValueError(message)

        # Instantiate task
        task: Task = task_cls()

        # Validate inputs (task-level)
        is_valid, err_msg = task.validate(md_articles)
        if not is_valid:
            message = f"Validation failed for {task_name}: {err_msg}"
            error(message)
            raise ValueError(message)

        # Content validation per article
        for md_article in md_articles:
            try:
                source_url = (
                    md_article.source_path
                    if md_article.source_path
                    and str(md_article.source_path).startswith("http")
                    else None
                )
                is_content_valid, warn_msg = validate_content(
                    md_article.content or "", source_url=source_url
                )
                if warn_msg:
                    warning(warn_msg)
                if not is_content_valid:
                    message = (
                        "Content invalid for "
                        f"{md_article.title or 'Untitled'}: {warn_msg}"
                    )
                    error(message)
                    raise ValueError(message)
            except BlockedPublisherError as e:
                error(f"Blocked publisher: {e}")
                raise

        # Context budget check
        for md_article in md_articles:
            try:
                check_context_budget(md_article.content or "", self.llm_client)
            except ContentTooLargeError as e:
                error(f"Content too large: {md_article.title}: {str(e)}")
                raise

        # Create run record in database (Async via thread pool)
        # Offload synchronous DB write to prevent blocking the event loop
        try:
            run_id = await asyncio.to_thread(
                self._create_run_record, md_articles, task_name
            )
        except Exception as e:
            self.logger.warning(f"Async DB creation failed, falling back: {e}")
            run_id = self._create_run_record(md_articles, task_name)
        if on_run_created is not None:
            on_run_created(run_id)

        # Create base title
        title_base = (
            md_articles[0].title
            if md_articles and md_articles[0].title
            else "untitled"
        )
        if task.supports_multi_input and len(md_articles) > 1:
            title_base = f"{title_base}-multi"
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        title = (
            f"{title_base}{task.get_output_suffix()}_"
            f"{self.model_name}_{timestamp}"
        )

        output_dir = None
        if save_files:
            base_output = (
                Path(md_articles[0].output_path)
                if md_articles[0].output_path
                else Path.cwd()
            )
            # If base_output is a file, use its parent directory.
            if base_output.is_file():
                base_output = base_output.parent

            output_dir = base_output / "llm_summaries" / self.model_name
            output_dir.mkdir(parents=True, exist_ok=True)

        # Build prompt using task
        try:
            prompt = task.build_prompt(md_articles)
        except Exception as e:
            error(f"Failed to build prompt: {e}")
            raise

        # Check prompt size
        try:
            check_context_budget(prompt, self.llm_client)
        except ContentTooLargeError as e:
            error(f"Prompt too large: {str(e)}")
            raise

        # Make LLM request (Async with Semaphore)
        llm_result: Optional[LLMResult] = None
        try:
            progress(f"Processing document with {len(prompt)} characters...")
            async with self._semaphore:
                final_callback = stream_callback
                app_prints_stream = (
                    self.stream
                    and output_to_console
                    and final_callback is None
                )

                if app_prints_stream:

                    def print_stream_chunk(content: str) -> None:
                        print(content, end="", flush=True)

                    final_callback = print_stream_chunk
                elif final_callback is None and not output_to_console:

                    def suppress_output(_: str) -> None:
                        return None

                    final_callback = suppress_output

                if use_legacy_client:
                    response, usage_stats = await self._make_api_request(
                        prompt,
                        task_name,
                        stream=self.stream,
                        stream_callback=final_callback,
                    )
                else:
                    llm_result = await self._make_typed_api_request(
                        prompt,
                        task_name,
                        stream=self.stream,
                        stream_callback=final_callback,
                    )
                    response, usage_stats = llm_result.to_legacy_tuple()
                if app_prints_stream:
                    print(flush=True)
        except asyncio.CancelledError:
            warning(f"Run {run_id} cancelled during API request")
            await asyncio.to_thread(
                self._update_run_status, run_id, "aborted", "Cancelled by user"
            )
            raise
        except Exception as e:
            error(f"Error making API request: {str(e)}")
            await asyncio.to_thread(
                self._update_run_status, run_id, "failed", str(e)
            )
            raise

        # Build metadata prefix
        metadata_lines = []
        for article in md_articles:
            metadata_lines.append(f"Title: {article.title or 'Untitled'}")
            metadata_lines.append(
                f"Source: {article.source_path or 'Unknown Source'}"
            )
        metadata_prefix = (
            "\n".join(metadata_lines) + "\n\n" if metadata_lines else ""
        )

        # Post-process response using task
        try:
            outputs = task.post_process(response, md_articles)
        except Exception as e:
            error(f"Post-processing failed: {e}")
            await asyncio.to_thread(
                self._update_run_status, run_id, "failed", str(e)
            )
            raise

        # Save all outputs
        should_print = output_to_console and not self.stream
        try:
            for output_name, content in outputs.items():
                formatted_content = metadata_prefix + content

                # Save to file (optional)
                if save_files and output_dir:
                    if output_name == "main":
                        self._save_content(
                            SaveType.RESPONSE,
                            title,
                            formatted_content,
                            output_dir,
                            should_print,
                        )
                    else:
                        self._save_content(
                            SaveType.RESPONSE,
                            f"{output_name}_{title}",
                            formatted_content,
                            output_dir,
                            False,
                        )
                        output_path = output_dir / f"{output_name}_{title}.md"
                        progress(
                            f"{output_name} output saved to {output_path}"
                        )

                # Save to database (Async via thread pool)
                await asyncio.to_thread(
                    self._save_output_to_db, run_id, output_name, content
                )

        except asyncio.CancelledError:
            warning(f"Run {run_id} cancelled during saving")
            await asyncio.to_thread(
                self._update_run_status, run_id, "aborted", "Cancelled by user"
            )
            raise
        except Exception as e:
            error(f"Error saving response: {str(e)}")
            await asyncio.to_thread(
                self._update_run_status, run_id, "failed", str(e)
            )
            raise

        # Save token usage (Async via thread pool)
        try:
            if save_files and output_dir:
                await asyncio.to_thread(
                    self._save_token_usage_report, title, output_dir
                )
            await asyncio.to_thread(
                self._save_token_usage_to_db, run_id, usage_stats
            )
        except Exception as e:
            warning(f"Unable to save token usage report: {str(e)}")

        # Mark run as successful (Async via thread pool)
        await asyncio.to_thread(self._update_run_status, run_id, "success")

        if llm_result is None:
            return None

        artifacts = {
            output_name: OutputArtifact(
                value=content,
                content_type="text/plain",
                serialized_text=content,
            )
            for output_name, content in outputs.items()
        }
        return TaskExecutionResult(
            task_name=task_name,
            run_id=run_id,
            outputs=artifacts,
            llm_result=llm_result,
        )

    # save content to a file
    def _save_content(
        self,
        type: SaveType,
        content_name: str,
        content: str,
        paper_output_dir: Path,
        console_print: bool = False,
    ) -> None:
        """Save content to a file."""
        save_dir = paper_output_dir
        try:
            os.makedirs(save_dir, exist_ok=True)
        except OSError as e:
            error(f"Error creating directory: {str(e)}")
            raise

        try:
            with open(
                f"{save_dir}/{type.value}_{content_name}.md",
                "w",
                encoding="utf-8",
            ) as f:
                f.write(content)
            if type == SaveType.RESPONSE and console_print:
                user_message(f"{content}")
        except IOError as e:
            error(f"Error saving content: {str(e)}")
            raise

    async def _make_typed_api_request(
        self,
        prompt: str,
        request_name: str,
        stream: bool = False,
        stream_callback: Optional[Callable[[str], None]] = None,
    ) -> LLMResult:
        """Make an API request and preserve the core typed result."""
        return await self.llm_client.generate(
            prompt,
            request_name,
            stream=stream,
            stream_callback=stream_callback,
        )

    async def _make_api_request(
        self,
        prompt: str,
        request_name: str,
        stream: bool = False,
        stream_callback: Optional[Callable[[str], None]] = None,
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Make an API request to the LLM client (Async).
        """
        try:
            # Important: close connections if we stop reusing the client.
            # RFC Plan: Use __aenter__ in LLMClient.
            # Here, self.llm_client persists for MDProcessor lifetime.
            # generate_response handles auto-client creation.
            return await self.llm_client.generate_response(
                prompt,
                request_name,
                stream=stream,
                stream_callback=stream_callback,
            )
        except ConnectionError as e:
            error(f"Connection failed during {request_name}: {str(e)}")
            raise ConnectionError(
                f"Failed to connect to LLM service: {str(e)}"
            ) from e
        except ValueError as e:
            error(f"Invalid input for {request_name}: {str(e)}")
            raise ValueError(
                f"Invalid input for {request_name}: {str(e)}"
            ) from e
        except Exception as e:
            error(f"Unexpected error in {request_name}: {str(e)}")
            raise RuntimeError(
                f"Error generating response for {request_name}: {str(e)}"
            ) from e

    # =========================================================================
    # Database Helper Methods (Synchronous - Called in Thread Pool)
    # =========================================================================

    def _create_run_record(
        self, md_articles: List[MDArticle], task_name: str
    ) -> int:
        try:
            input_ids = []
            for article in md_articles:
                input_id = self.repository.get_or_create_input(
                    input_type=article.type.value,
                    source_path=article.source_path or "",
                    title=article.title or "Untitled",
                    content=article.content or "",
                )
                input_ids.append(input_id)

            run_id = self.repository.create_run(
                task=task_name,
                model=self.model_name,
                input_ids=input_ids,
                thinking_level=self.thinking_level,
                stream=self.stream,
                currency=self.llm_client.pricing_currency,
            )
            return run_id
        except Exception as e:
            self.logger.warning(f"Failed to create run record: {e}")
            return -1

    def _update_run_status(
        self, run_id: int, status: str, error_message: Optional[str] = None
    ) -> None:
        if run_id < 0:
            return
        try:
            self.repository.update_run_status(run_id, status, error_message)
        except Exception as e:
            self.logger.warning(f"Failed to update run status: {e}")

    def _save_output_to_db(
        self, run_id: int, output_type: str, content: str
    ) -> None:
        if run_id < 0:
            return
        try:
            content_type = (
                "json" if content.strip().startswith(("{", "[")) else "text"
            )
            self.repository.add_output(
                run_id, output_type, content, content_type
            )
        except Exception as e:
            self.logger.warning(f"Failed to save output to database: {e}")

    def _save_token_usage_to_db(
        self, run_id: int, usage: Optional[Dict[str, Any]] = None
    ) -> None:
        if run_id < 0:
            return
        try:
            if usage is None:
                usage = self.llm_client.get_token_usage()

            self.repository.add_token_usage(
                run_id=run_id,
                input_tokens=usage.get("total_input_tokens", 0),
                output_tokens=usage.get("total_output_tokens", 0),
                cost_input=usage.get("cost", {}).get("input_cost", 0),
                cost_output=usage.get("cost", {}).get("output_cost", 0),
                process_time=usage.get("process_times", {}).get(
                    "total_time", 0
                ),
            )
        except Exception as e:
            self.logger.warning(f"Failed to save token usage to database: {e}")

    def _save_token_usage_report(
        self, project_name: str, output_dir: Path
    ) -> None:
        report = format_usage_report(
            project_name=project_name,
            model=self.llm_client.model,
            model_name=self.llm_client.model_name,
            pricing_currency=self.llm_client.pricing_currency,
            token_usage=self.llm_client.get_token_usage(),
            timestamp=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / f"token_usage_{project_name}.txt"
        report_path.write_text(report, encoding="utf-8")
