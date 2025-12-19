from .md_processor import MDProcessor
from .data_models import MDArticle, InputType, Input, ProcessType
from .md_converter import MarkdownConverter
from .config.logging_config import setup_logging, progress, error, warning, user_message
import logging
import asyncio
from pathlib import Path
from typing import Union

class EditorAssistant:
    def __init__(self, model_name, debug_mode=False, thinking_level=None, stream=True):
        setup_logging(debug_mode)
        self.logger = logging.getLogger(__name__)
        self.md_processor = MDProcessor(model_name, thinking_level=thinking_level, stream=stream)
        self.md_converter = MarkdownConverter()
    
    # LLM processor for multiple files (Async)
    async def process_multiple(self, inputs: list[Input], process_type: Union[ProcessType, str], output_to_console=True, save_files=False):       
        # early return if no paths are provided
        if len(inputs) == 0:
            error("No input provided")
            return

        # Normalize task name (support both ProcessType enum and string)
        task_name = process_type.value if isinstance(process_type, ProcessType) else process_type

        # show clean progress message to user
        progress(f"Start to {task_name} with {self.md_processor.llm_client.model_name}")

        # initialize the md content list
        md_articles = []
        failed_inputs = []

        # Step 1: Pre-process inputs (Convert/Read) - Synchronous for now (Phase 2 optimization: async thread pool)
        # Note: We keep this sync for simplicity in this phase, or we can use to_thread.
        # Given conversion can be slow, let's just keep it simple sequential for conversion, parallel for LLM.
        # Why? Because LLM is the main bottleneck (30s+), conversion is usually seconds.
        for input in inputs:
            # if the path is a markdown file, read the content and create an MDArticle object
            md_article = None
            if input.path.endswith(".md"):
                try:
                    with open(input.path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    md_article = MDArticle(
                        type=input.type,
                        content=content,
                        title=Path(input.path).stem,
                        source_path=input.path,
                        output_path=input.path,
                    )
                    md_articles.append(md_article)
                except Exception as e:
                    failed_inputs.append((input.path, str(e)))
                continue
            
            # if the path is not a markdown file, convert it to markdown
            try:
                md_article = self.md_converter.convert_content(input.path, type=input.type)
                if md_article:
                    md_articles.append(md_article)
                else:
                    failed_inputs.append((input.path, "conversion returned None"))
            except Exception as e:
                failed_inputs.append((input.path, str(e)))
                continue

        if failed_inputs and not md_articles:
            error(f"All inputs failed to convert: {failed_inputs}")
            return
        if failed_inputs:
            for path, msg in failed_inputs:
                warning(f"Failed to convert {path}: {msg}")
            user_message(
                f"{len(failed_inputs)} input(s) failed conversion; continuing with remaining."
            )

        progress("Input formatted as markdown and ready to process.")
        
        # process the md files concurrently
        # Logic: We launch a task for each article.
        tasks = []
        for article in md_articles:
            # Wrap single article in list because process_mds expects list
            # We process them individually to maximize concurrency (1 input = 1 task)
            # unless the task inherently supports multi-input aggregation (like summary of multiple papers).
            # But the current architecture (MDProcessor.process_mds) takes a list of articles.
            # If the Task supports multi-input (e.g. compare 2 papers), we should pass them together?
            # Let's check Task.supports_multi_input.
            
            # Check task capability
            # We need to instantiate the task temporarily to check property? Or assume single-doc for now?
            # Existing logic was: process_mds takes list.
            # If we want to process N docs in parallel, we should spawn N tasks, each calling process_mds([doc]).
            # BUT, if the user intended to summarize 5 docs into 1 (Multi-input task), we should call process_mds(all_docs) once.
            
            # How to decide?
            # RFC didn't specify. Current behavior in main.py loop suggests 1-by-1.
            # So we assume default is 1-by-1 unless logic dictates otherwise.
            # Let's preserve 1-by-1 behavior but run them in parallel.
            tasks.append(
                self.md_processor.process_mds(
                    [article],
                    task_name,
                    output_to_console,
                    save_files=save_files,
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
