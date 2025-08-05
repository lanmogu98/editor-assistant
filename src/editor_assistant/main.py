from .md_processesor import MDProcessor, ArticleType
from .md_converter import MarkdownConverter
from .config.logging_config import setup_logging, progress, error
import logging
import time
from pathlib import Path

class EditorAssistant:
    def __init__(self, model_name, debug_mode=False):
        setup_logging(debug_mode)
        self.logger = logging.getLogger(__name__)
        self.md_processor = MDProcessor(model_name)
        self.md_converter = MarkdownConverter()
        self.logger.debug("Editor Assistant Initialized")
    
    def summarize_multiple (self, paths:list[str], type:ArticleType):
        
        # early return if no paths are provided
        if len(paths) == 0:
            error("No paths provided")
            return
                      
        # start the timer
        time_start = time.time()

        # show clean progress message to user
        progress(f"Processing {len(paths)} {str(type).lower()} article(s) with {self.md_processor.llm_client.model_name}")
        
        # detailed debug info
        self.logger.debug(
            f"Summarizing {len(paths)} {str(type)} article(s) "
            f"using {self.md_processor.llm_client.model_name}"
        )
        
        # initialize metadata
        metadata = {
            "type": str(type),
            "item_count": len(paths),
            "markdown_conversion": {"skipped": 0, "success": 0, "failed": len(paths)},
            "process_md": {"success": 0, "failed": len(paths)},
            "process_time": {"total": 0, "markdown_conversion": 0, "summarization": 0}
        }

        # initialize the md content list
        md_paths_list = []

        # TODO: add multi-thread support for the job, for conversion and 
        # llm summerization all takes time, especially for summerizations.
        for path in paths:
            if path.endswith(".md"):
                md_paths_list.append(path)
                metadata["markdown_conversion"]["skipped"] += 1
                metadata["markdown_conversion"]["failed"] -= 1
                continue
            try:
                md_article = self.md_converter.convert_content(path)
            except Exception as e:
                self.logger.warning (f"failed to convert {path}: {str(e)} to md")
                continue
            
            if md_article is not None:
                # save the md content to a file
                file_name = md_article.title + ".md"
                md_path = Path (path).parent / "md" / file_name
                Path(md_path).parent.mkdir(parents=True, exist_ok=True)
                self.logger.debug (f"Saving md content to {md_path}")
                with open(md_path, "w") as f:
                    f.write(f"url: {md_article.source_path}\n")
                    f.write(f"title: {md_article.title}\n")
                    f.write(f"authors: {md_article.authors}\n")
                    f.write(md_article.markdown_content)
                # mark one success
                md_paths_list.append(md_path)
                metadata["markdown_conversion"]["success"] += 1
                metadata["markdown_conversion"]["failed"] -= 1
            else:
                self.logger.warning (f"failed to convert {path}: {str(e)} to md")
                md_paths_list.append(None)


        if metadata["markdown_conversion"]["failed"] == len(paths):
            self.logger.error ("No markdown files converted successfully")
            return

        # print the metadata after conversion
        self.logger.debug(
            f"Successfully converted "
            f"{metadata['markdown_conversion']['success']} "
            f"markdown files out of {metadata['item_count']}"
        )
        
        time_md_conversion_ended = time.time()
        time_md_conversion = time_md_conversion_ended - time_start
        metadata["process_time"]["markdown_conversion"] = f"{time_md_conversion:.2f} seconds"

        # summarize the md files
        for md_path in md_paths_list:
            if md_path is None:
                continue
            try:
                success = self.md_processor.process_md (md_path, type)
                if success:
                    metadata["process_md"]["success"] += 1
                    metadata["process_md"]["failed"] -= 1
                else:
                    self.logger.warning (f"failed to summarize {md_path}")
            except Exception as e:
                self.logger.warning (f"failed to summarize {md_path}: {str(e)}")

        if metadata["process_md"]["success"] == 0:
            self.logger.error ("No markdown files summarized successfully")
            return

        # print the metadata after summarization
        self.logger.debug(
            f"Successfully summarized "
            f"{metadata['process_md']['success']} "
            f"markdown files out of {metadata['item_count']}"
        )
        
        time_summarization_ended = time.time()
        time_summarization = time_summarization_ended - time_md_conversion_ended
        metadata["process_time"]["process_md"] = f"{time_summarization:.2f} seconds"

        time_total = time_summarization_ended - time_start
        metadata["process_time"]["total"] = f"{time_total:.2f} seconds"

        # print the total time
        self.logger.debug (f"Total time taken: {metadata['process_time']['total']}")

        self.logger.debug (f"Metadata: {metadata}")
         
        return 
