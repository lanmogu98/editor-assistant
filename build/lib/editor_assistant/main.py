from .md_summarizer import MDSummarizer, ArticleType
from .md_converter import MarkdownConverter
from .llm_client import LLMClient
import logging
import time
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class EditorAssistant:
    def __init__(self, model_name):
        self.md_summarizer = MDSummarizer(model_name)
        self.md_converter = MarkdownConverter() 
        # create and configure the logger
        self.logger = logging.getLogger(__name__)
        self.logger.info("Editor Assistant Initialized")
    
    def summarize_multiple (self, paths:list[str], type:ArticleType):
        
        # early return if no paths are provided
        if len(paths) == 0:
            self.logger.error ("No paths provided")
            return
                      
        # start the timer
        time_start = time.time()

        # print the summary of the job
        self.logger.info(
            f"Summarizing {len(paths)} {str(type)} article(s) "
            f"using {self.md_summarizer.llm_client.model_name}"
        )
        
        # initialize metadata
        metadata = {
            "type": str(type),
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
            md_article = self.md_converter.convert_content(path)
            
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
                success = self.md_summarizer.summarize_md (md_path, type)
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

# entry point for the news summarizer
def summarize_news ():
    from argparse import ArgumentParser
    parser = ArgumentParser(description="LLM Editor Assistant")
    parser.add_argument("content_paths", 
                        nargs= '+', 
                        help= "Path(s) to the research paper markdown file(s)")
    parser.add_argument("--model", 
                        default = "deepseek-r1-latest", 
                        choices = LLMClient.get_supported_models(), 
                        help = "Model to use for generation")
    args = parser.parse_args()

    editor_assistant = EditorAssistant(args.model)
    for path in args.content_paths:
        editor_assistant.summarize_multiple([path], ArticleType.news)

# entry point for the research summarizer
def summarize_research ():
    from argparse import ArgumentParser
    parser = ArgumentParser(description="LLM Editor Assistant")
    parser.add_argument("content_paths", 
                        nargs= '+', 
                        help= "Path(s) to the research paper markdown file(s)")
    parser.add_argument("--model", 
                        default = "deepseek-r1-latest", 
                        choices = LLMClient.get_supported_models(), 
                        help = "Model to use for generation")
    args = parser.parse_args()

    editor_assistant = EditorAssistant(args.model)
    for path in args.content_paths:
        editor_assistant.summarize_multiple([path], ArticleType.research)

def main():
    from argparse import ArgumentParser

    parser = ArgumentParser(description="LLM Editor Assistant")
    parser.add_argument("content_paths", 
                        nargs= '+', 
                        help= "Path(s) to the research paper markdown file(s)")
    parser.add_argument("--model", 
                        default = "deepseek-r1-latest", 
                        choices = LLMClient.get_supported_models(), 
                        help = "Model to use for generation")
    args = parser.parse_args()

    editor_assistant = EditorAssistant(args.model)
    if args.type == ArticleType.research:
        editor_assistant.summarize_research(args.content_paths)
    elif args.type == ArticleType.news:
        editor_assistant.summarize_news(args.content_paths)
    else:
        parser.error("Invalid article type, please input 'r' for research or 'n' for news")

if __name__ == "__main__":
    main()