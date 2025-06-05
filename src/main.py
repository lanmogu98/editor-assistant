from .md_summarizer import MDSummarizer
from .md_converter import MarkdownConverter
from .llm_client import LLMClient
from ..config.llms.llm_config import llm_config
import argparse
import sys
import traceback
import logging
from enum import Enum
import time

supported_models = llm_config["MODELS"].keys()

class ArticleType(Enum):
    research = 'r'
    news = 'n'

class EditorAssistant:
    def __init__(self):
        self.llm_client = LLMClient()
        self.md_converter = MarkdownConverter()
        self.md_summarizer = MDSummarizer(self.llm_client, type)
        self.logger = logging.getLogger(__name__)
        self.logger.info("="*50)
        self.logger.info(f"{time.strftime('%Y-%m-%d %H:%M:%S')}: Editor Assistant Initialized")
    
    def summarize_multiple(self, type:ArticleType, paths:list[str], 
                           model_name="deepseek-r3"):
        self.logger.info(f"Summarizing {len(paths)} {type} articles using {model_name}")
        
        time_start = time.time()
        metadata = {
            "type": type,
            "item_count": len(paths),
            "markdown_conversion": {
                "success": 0,
                "failed": len(paths),
            },
            "summarization": {
                "success": 0,
                "failed": len(paths),
            },
            "process_time": {
                "total": 0,
                "markdown_conversion": 0,
                "summarization": 0,
            }
        }
         
        md_content = []
        # 
        for path in paths:
            try:
                md_content.append(self.md_converter.convert_content(path))
            except Exception as e:
                logging.warning (f"failed to convert {path}: {str(e)} to md")
                # Continue with next paper instead of exiting
                continue

        
        # Process the paper
        try:
            md_content, _ = self.md_converter.convert_content(input_path)
            result = self.summarizer.summarize_content(md_content)
            
            # Print summary information
            print("\n" + "="*50)
            print(f"Paper: {result['metadata']['title']}")
            print(f"Model: {self.summarizer.llm_client.model_name} ({self.summarizer.llm_client.model})")
            print(f"Number of chunks: {result['metadata']['chunks']}")
            # Print token usage
            token_usage = result['metadata']['token_usage']
            print("\nToken Usage:")
            print(f"  Total input tokens: {token_usage['total_input_tokens']}")
            print(f"  Total output tokens: {token_usage['total_output_tokens']}")
            print(f"  Total tokens: {token_usage['total_input_tokens'] + 
                                     token_usage['total_output_tokens']}")
            
            # Print cost information
            print("\nCost Information:")
            print(f"  Input cost: ¥{token_usage['cost']['input_cost']:.6f}")
            print(f"  Output cost: ¥{token_usage['cost']['output_cost']:.6f}")
            print(f"  Total cost: ¥{token_usage['cost']['total_cost']:.6f}")
            
            # Print process times
            process_times = result['metadata']['process_times']
            print("\nProcess Times:")
            print(f"  Chunking: {process_times['chunking']:.2f} seconds \
                  ({process_times['chunking']/process_times['total']*100:.1f}%)")
            print(f"  Chunk Analysis: {process_times['chunk_analysis']:.2f} seconds \
                  ({process_times['chunk_analysis']/process_times['total']*100:.1f}%)")
            print(f"  Synthesis: {process_times['synthesis']:.2f} seconds \
                  ({process_times['synthesis']/process_times['total']*100:.1f}%)")
            print(f"  Translation: {process_times['translation']:.2f} seconds\
                   ({process_times['translation']/process_times['total']*100:.1f}%)")
            print(f"  Total: {process_times['total']:.2f} seconds \
                  {process_times['total']/60:.2f} minutes)")
            
            print("\nSummaries saved to:")
            print(f"  {result['metadata']['paper_output_dir']}")
            print("="*50)
            
        except Exception as e:
            print(f"Error processing paper: {str(e)}")
            traceback.print_exc()
            sys.exit(1)

        return


if __name__ == "__main__":
  summerizer = SummarizeAssistant()

  def summarize_research (self):
        """Main function to run the paper summarizer."""
        parser = argparse.ArgumentParser(description="Summarize research papers")
        parser.add_argument("--type", 
                            default = "research", 
                            choices = ["research", "news"], 
                            help = "Type of content to summarize")
        parser.add_argument("content_paths", 
                            nargs= '+', 
                            help= "Path(s) to the research paper markdown file(s)")
        parser.add_argument("--model", 
                            default = "deepseek-v3", 
                            choices = supported_models, 
                            help = "Model to use for generation")
        args = parser.parse_args()
        
        self.summarize_multiple(args.content_paths, "research", args.model)
