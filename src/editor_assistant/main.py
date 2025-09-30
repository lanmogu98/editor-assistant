from .md_processesor import MDProcessor
from .data_models import MDArticle, InputType, Input, ProcessType
from .md_converter import MarkdownConverter
from .config.logging_config import setup_logging, progress, error
import logging
from pathlib import Path

class EditorAssistant:
    def __init__(self, model_name, debug_mode=False):
        setup_logging(debug_mode)
        self.logger = logging.getLogger(__name__)
        self.md_processor = MDProcessor(model_name)
        self.md_converter = MarkdownConverter()
    
    # LLM processor for multiple files
    def process_multiple (self, inputs:list[Input], process_type:ProcessType, output_to_console=True):       
        # early return if no paths are provided
        if len(inputs) == 0:
            error("No input provided")
            return

        # show clean progress message to user
        progress(f"Start to {process_type.value} with {self.md_processor.llm_client.model_name}")

        # initialize the md content list
        md_articles = []

        for input in inputs:
            # if the path is a markdown file, read the content and create an MDArticle object
            md_article = None
            if input.path.endswith(".md"):
                with open(input.path, 'r', encoding='utf-8') as f:
                    content = f.read()
                md_article = MDArticle(type=input.type,  
                                    content=content, 
                                    title=Path(input.path).stem, 
                                    source_path=input.path,
                                    output_path=input.path)
                md_articles.append(md_article)
                continue
            
            # if the path is not a markdown file, convert it to markdown
            try:
                md_article = self.md_converter.convert_content(input.path, type=input.type)
                md_articles.append(md_article)
            except Exception as e:
                error (f"failed to convert {input.path}: {str(e)} to md")
                return 

        progress("Input formatted as markdown and ready to process.")
        # process the md files
        try:
            success = self.md_processor.process_mds (md_articles, process_type, output_to_console)
            if not success:
                self.logger.warning (f"failed to process {md_articles[0].title}")
        except Exception as e:
            self.logger.warning (f"failed to process {md_articles[0].title}: {str(e)}")
         
        return 

# TODO: add process interface for a single input (for task translate & online),
# which requires no type specification.