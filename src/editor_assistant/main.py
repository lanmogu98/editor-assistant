from .md_processor import MDProcessor
from .data_models import MDArticle, InputType, Input, ProcessType
from .md_converter import MarkdownConverter
from .config.logging_config import setup_logging, progress, error, warning, user_message
import logging
import asyncio
from pathlib import Path
from typing import Union, Optional, Tuple, Dict, Callable

class EditorAssistant:
    def __init__(self, model_name, debug_mode=False, thinking_level=None, stream=True):
        setup_logging(debug_mode)
        self.logger = logging.getLogger(__name__)
        self.md_processor = MDProcessor(model_name, thinking_level=thinking_level, stream=stream)
        self.md_converter = MarkdownConverter()
    
    async def _process_input_to_article(self, input: Input) -> Tuple[Optional[MDArticle], Optional[str]]:
        """Helper to convert/read input to MDArticle (Async via thread pool)."""
        try:
            if input.path.endswith(".md"):
                # File I/O in thread
                def read_md():
                    with open(input.path, 'r', encoding='utf-8') as f:
                        return f.read()
                
                content = await asyncio.to_thread(read_md)
                return MDArticle(
                    type=input.type,
                    content=content,
                    title=Path(input.path).stem,
                    source_path=input.path,
                    output_path=input.path,
                ), None
            else:
                # Conversion in thread (CPU/IO bound)
                md_article = await asyncio.to_thread(
                    self.md_converter.convert_content, input.path, type=input.type
                )
                if md_article:
                    return md_article, None
                else:
                    return None, "conversion returned None"
        except Exception as e:
            return None, str(e)

    # LLM processor for multiple files (Async)
    async def process_multiple(self, inputs: list[Input], process_type: Union[ProcessType, str], 
                             output_to_console=True, save_files=False,
                             progress_callbacks: Dict[str, Callable[[str], None]] = None):       
        # early return if no paths are provided
        if len(inputs) == 0:
            error("No input provided")
            return

        # Normalize task name (support both ProcessType enum and string)
        task_name = process_type.value if isinstance(process_type, ProcessType) else process_type

        # show clean progress message to user
        progress(f"Start to {task_name} with {self.md_processor.llm_client.model_name}")

        # Step 1: Pre-process inputs (Convert/Read) - Parallel
        progress(f"Converting/Reading {len(inputs)} inputs in parallel...")
        
        conversion_tasks = [self._process_input_to_article(inp) for inp in inputs]
        conversion_results = await asyncio.gather(*conversion_tasks)

        md_articles = []
        failed_inputs = []

        for i, (article, err_msg) in enumerate(conversion_results):
            if article:
                md_articles.append(article)
            else:
                failed_inputs.append((inputs[i].path, err_msg))

        if failed_inputs and not md_articles:
            error(f"All inputs failed to convert: {failed_inputs}")
            return
        if failed_inputs:
            for path, msg in failed_inputs:
                warning(f"Failed to convert {path}: {msg}")
            user_message(
                f"{len(failed_inputs)} input(s) failed conversion; continuing with remaining."
            )

        progress("Inputs ready. Starting parallel processing...")
        
        # process the md files concurrently
        # Logic: We launch a task for each article.
        tasks = []
        for article in md_articles:
            # Find callback for this file if available
            callback = None
            if progress_callbacks:
                # Key is the source path (absolute or relative as passed in input)
                # We expect strict string matching
                callback = progress_callbacks.get(str(article.source_path))

            tasks.append(
                self.md_processor.process_mds(
                    [article],
                    task_name,
                    output_to_console,
                    save_files=save_files,
                    stream_callback=callback
                )
            )

        try:
            # Run all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check results
            for i, result in enumerate(results):
                article_title = md_articles[i].title
                if isinstance(result, Exception):
                    self.logger.warning(f"Failed to process {article_title}: {result}")
                else:
                    success, _ = result
                    if not success:
                        self.logger.warning(f"Failed to process {article_title} (Task returned failure)")
                        
        except Exception as e:
            self.logger.warning(f"Critical error during concurrent processing: {str(e)}")
            return
         
        return 
