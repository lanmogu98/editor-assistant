from ._summarizer import Summarizer
from ._llm_client import LLMClient
import argparse
import sys
import traceback

def summarize_multiple(paths, type:str, model_name="deepseek-r1"):
    """
    Summarize multiple research papers using the ResearchPaperSummarizer.

    Args:
        paper_paths: List of paths to research paper markdown files
        model_name: Name of the model to use
    """
    # Initialize the paper summarizer once for all papers
    summarizer = Summarizer(LLMClient(model_name), type)
    
    for paper_path in paths:
        print(f"\nProcessing paper: {paper_path}")
        try:
            summarize_one(paper_path, type, model_name, summarizer)
        except Exception as e:
            print(f"Error processing paper {paper_path}: {str(e)}")
            traceback.print_exc()
            # Continue with next paper instead of exiting
            continue

def summarize_one(paper_path, type:str, model_name="deepseek-r1", summarizer=None):
    """
    Summarize a single research paper using the ResearchPaperSummarizer.

    Args:
        paper_path: Path to the research paper markdown file
        model_name: Name of the model to use
        summarizer: Optional existing ResearchSummarizer instance
    """
    # Initialize the paper summarizer if not provided
    if summarizer is None:
        summarizer = Summarizer(LLMClient(model_name), type)
    
    # Process the paper
    try:
        result = summarizer.process_content(paper_path)
        
        # Print summary information
        print("\n" + "="*50)
        print(f"Paper: {result['metadata']['paper_name']}")
        print(f"Model: {summarizer.llm_client.model_name} ({summarizer.llm_client.model})")
        print(f"Number of chunks: {result['metadata']['chunks']}")
        # Print token usage
        token_usage = result['metadata']['token_usage']
        print("\nToken Usage:")
        print(f"  Total input tokens: {token_usage['total_input_tokens']}")
        print(f"  Total output tokens: {token_usage['total_output_tokens']}")
        print(f"  Total tokens: {token_usage['total_input_tokens'] + token_usage['total_output_tokens']}")
        
        # Print cost information
        print("\nCost Information:")
        print(f"  Input cost: ¥{token_usage['cost']['input_cost']:.6f}")
        print(f"  Output cost: ¥{token_usage['cost']['output_cost']:.6f}")
        print(f"  Total cost: ¥{token_usage['cost']['total_cost']:.6f}")
        
        # Print process times
        process_times = result['metadata']['process_times']
        print("\nProcess Times:")
        print(f"  Chunking: {process_times['chunking']:.2f} seconds ({process_times['chunking']/process_times['total']*100:.1f}%)")
        print(f"  Chunk Analysis: {process_times['chunk_analysis']:.2f} seconds ({process_times['chunk_analysis']/process_times['total']*100:.1f}%)")
        print(f"  Synthesis: {process_times['synthesis']:.2f} seconds ({process_times['synthesis']/process_times['total']*100:.1f}%)")
        print(f"  Translation: {process_times['translation']:.2f} seconds ({process_times['translation']/process_times['total']*100:.1f}%)")
        print(f"  Total: {process_times['total']:.2f} seconds ({process_times['total']/60:.2f} minutes)")
        
        print("\nSummaries saved to:")
        print(f"  {result['metadata']['paper_output_dir']}")
        print("="*50)
        
    except Exception as e:
        print(f"Error processing paper: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

    return


def summarize_research():
    """Main function to run the paper summarizer."""
    parser = argparse.ArgumentParser(description="Summarize research papers")
    parser.add_argument("content_paths", nargs='+', help="Path(s) to the research paper markdown file(s)")
    parser.add_argument("--model", default="deepseek-v3", choices=["deepseek-r1", "deepseek-v3"], help="Model to use for generation")
    args = parser.parse_args()
    
    summarize_multiple(args.content_paths, "research", args.model)

def summarize_news():
    """Main function to run the paper summarizer."""
    parser = argparse.ArgumentParser(description="Summarize research papers")
    parser.add_argument("content_paths", nargs='+', help="Path(s) to the research paper markdown file(s)")
    parser.add_argument("--model", default="deepseek-v3-latest", choices=["deepseek-r1", "deepseek-v3", "deepseek-v3-latest"], help="Model to use for generation")
    args = parser.parse_args()

    summarize_multiple(args.content_paths, "news", args.model)
    

if __name__ == "__main__":
    pass