from .md_summarizer import MDSummarizer, ArticleType
from .md_converter import MarkdownConverter
from .llm_client import LLMClient
from ..config.llms.llm_config import llm_config
import logging
import time
from pathlib import Path

supported_models = llm_config["MODELS"].keys()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class EditorAssistant:
    def __init__(self, model_name, type:ArticleType):
        self.type = type
        self.llm_client = LLMClient(model_name)
        self.md_converter = MarkdownConverter()
        self.md_summarizer = MDSummarizer(self.llm_client, self.type) 
        # create and configure the logger
        self.logger = logging.getLogger(__name__)
        self.logger.info("Editor Assistant Initialized")
    
    def summarize_multiple (self, paths:list[str]):
        
        # early return if no paths are provided
        if len(paths) == 0:
            self.logger.error ("No paths provided")
            return
        
        # start the timer
        time_start = time.time()

        # print the summary of the job
        self.logger.info(
            f"Summarizing {len(paths)} {str(self.type.name)} article(s) "
            f"using {self.llm_client.model_name}"
        )
        
        # initialize metadata
        metadata = {
            "type": str(self.type.name),
            "item_count": len(paths),
            "markdown_conversion": {"success": 0, "failed": len(paths)},
            "summarization": {"success": 0, "failed": len(paths)},
            "process_time": {"total": 0, "markdown_conversion": 0, "summarization": 0}
        }

        # initialize the md content list
        md_paths_list = []

        # TODO: add multi-thread support for the job, for conversion and 
        # llm summerization all takes time, especially for summerizations.
        for path in paths:
            md_content, md_metadata = self.md_converter.convert_content(path)
            
            if md_content is not None:
                # save the md content to a file
                file_name = md_metadata["title"] + ".md"
                md_path = Path (path).parent / "md" / file_name
                Path(md_path).parent.mkdir(parents=True, exist_ok=True)
                self.logger.debug (f"Saving md content to {md_path}")
                with open(md_path, "w") as f:
                    f.write(md_content)
                # mark one success
                md_paths_list.append(md_path)
                metadata["markdown_conversion"]["success"] += 1
                metadata["markdown_conversion"]["failed"] -= 1
            else:
                self.logger.warning (f"failed to convert {path}: {str(e)} to md")
                md_paths_list.append(None)


        if metadata["markdown_conversion"]["success"] == 0:
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
                success = self.md_summarizer.summarize_md (md_path)
                if success:
                    metadata["summarization"]["success"] += 1
                    metadata["summarization"]["failed"] -= 1
                else:
                    self.logger.warning (f"failed to summarize {md_path}")
            except Exception as e:
                self.logger.warning (f"failed to summarize {md_path}: {str(e)}")

        if metadata["summarization"]["success"] == 0:
            self.logger.error ("No markdown files summarized successfully")
            return

        # print the metadata after summarization
        self.logger.debug(
            f"Successfully summarized "
            f"{metadata['summarization']['success']} "
            f"markdown files out of {metadata['item_count']}"
        )
        
        time_summarization_ended = time.time()
        time_summarization = time_summarization_ended - time_md_conversion_ended
        metadata["process_time"]["summarization"] = f"{time_summarization:.2f} seconds"

        time_total = time_summarization_ended - time_start
        metadata["process_time"]["total"] = f"{time_total:.2f} seconds"

        # print the total time
        self.logger.debug (f"Total time taken: {metadata['process_time']['total']}")

        self.logger.info (f"Metadata: {metadata}")
         
        return 

def summarize_news (paths:list[str], model_name="deepseek-r3-latest"):
    summerizer = EditorAssistant(model_name, ArticleType.news)
    summerizer.summarize_multiple(paths)

def summarize_research (paths:list[str], model_name="deepseek-r3-latest"):
    summerizer = EditorAssistant(model_name, ArticleType.research)
    summerizer.summarize_multiple(paths)

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser(description="LLM Editor Assistant")
    parser.add_argument("--type", 
                        type = ArticleType,
                        default = ArticleType.research, 
                        choices = list(ArticleType), 
                        help = "Type of content to summarize")
    parser.add_argument("content_paths", 
                        nargs= '+', 
                        help= "Path(s) to the research paper markdown file(s)")
    parser.add_argument("--model", 
                        default = "deepseek-v3-latest", 
                        choices = supported_models, 
                        help = "Model to use for generation")
    args = parser.parse_args()
    
    if args.type == ArticleType.research:
        summarize_research(args.content_paths, args.model)
    elif args.type == ArticleType.news:
        summarize_news(args.content_paths, args.model)
    else:
        parser.error("Invalid article type, please input 'r' for research or 'n' for news")