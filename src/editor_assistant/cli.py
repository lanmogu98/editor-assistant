#!/usr/bin/env python3
"""
Command-line interface for Editor Assistant.

Provides a clean, consistent CLI with subcommands for different operations.
"""

import argparse
import sys
from pathlib import Path

from .main import EditorAssistant
from .md_processesor import ArticleType
from .llm_client import LLMClient
from .md_converter import MarkdownConverter
from .clean_html_to_md import CleanHTML2Markdown
from .config.user_config import user_config


def add_common_arguments(parser):
    """Add common arguments used across multiple commands."""
    parser.add_argument(
        "--model", 
        default="deepseek-r1-latest",
        choices=LLMClient.get_supported_models(),
        help="Model to use for generation"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with detailed logging"
    )


def cmd_generate_news(args):
    """Generate news articles from content."""
    assistant = EditorAssistant(args.model, debug_mode=args.debug)
    for path in args.content_paths:
        assistant.summarize_multiple([path], ArticleType.news)


def cmd_generate_outline(args):
    """Generate research outlines from content."""
    assistant = EditorAssistant(args.model, debug_mode=args.debug)
    for path in args.content_paths:
        assistant.summarize_multiple([path], ArticleType.research)


def cmd_convert_to_md(args):
    """Convert various formats to markdown."""
    converter = MarkdownConverter()
    
    for input_path in args.input_paths:
        try:
            # Determine output path
            if args.output:
                output_path = Path(args.output)
            else:
                input_file = Path(input_path)
                output_path = input_file.parent / f"{input_file.stem}.md"
            
            # Convert based on file type
            result = converter.convert_content(input_path)
            if result:
                # Save converted content
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {result.title}\n\n")
                    if result.authors:
                        f.write(f"**Authors:** {result.authors}\n\n")
                    f.write(f"**Source:** {result.source_path}\n\n")
                    f.write("---\n\n")
                    f.write(result.markdown_content)
                
                print(f"✓ Converted: {input_path} → {output_path}")
            else:
                print(f"✗ Failed to convert: {input_path}")
                
        except Exception as e:
            print(f"✗ Error converting {input_path}: {str(e)}")


def cmd_clean_html(args):
    """Clean HTML and convert to markdown."""
    try:
        result = CleanHTML2Markdown(
            args.url_or_file,
            args.output,
            save_file=not args.stdout
        )
        
        if args.stdout:
            print(result)
        else:
            print(f"✓ Cleaned HTML saved to: {args.output}")
            
    except Exception as e:
        print(f"✗ Error cleaning HTML: {str(e)}")
        sys.exit(1)


def cmd_config(args):
    """Manage user configuration."""
    if args.action == "show":
        user_config.show_config_location()
    elif args.action == "init":
        user_config._initialize_user_config()
    elif args.action == "models":
        models = user_config.list_available_models()
        print("🤖 Available Models:")
        for model_name, info in models.items():
            print(f"  • {model_name} ({info['provider']})")
            if info.get('pricing'):
                pricing = info['pricing']
                print(f"    Pricing: ¥{pricing.get('input', 0)}/1K input, ¥{pricing.get('output', 0)}/1K output")
    elif args.action == "add-model":
        if not all([args.provider, args.model_name, args.model_id]):
            print("✗ Error: --provider, --model-name, and --model-id are required for add-model")
            sys.exit(1)
        
        model_config = {
            'id': args.model_id,
            'pricing': {
                'input': args.input_price or 0.0,
                'output': args.output_price or 0.0
            }
        }
        
        user_config.add_custom_model(
            args.provider, 
            args.model_name, 
            args.max_tokens or 16000,
            args.context_window or 128000,
            model_config
        )


def create_parser():
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="editor-assistant",
        description="AI-powered editor assistant for research and news generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s news "https://example.com/article"
  %(prog)s outline paper.pdf --model deepseek-r1-latest
  %(prog)s convert *.pdf -o ./markdown/
  %(prog)s clean https://example.com/page.html -o clean.md
  %(prog)s config show
  %(prog)s config add-model --provider openai --model-name gpt-4-custom --model-id gpt-4
        """
    )
    
    # Global options
    parser.add_argument(
        "--version",
        action="version", 
        version="%(prog)s 0.1.0"
    )
    
    # Create subcommands
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        metavar="COMMAND"
    )
    
    # News generation command
    news_parser = subparsers.add_parser(
        "news",
        help="Generate news articles from research content",
        description="Convert research papers and articles into news format"
    )
    news_parser.add_argument(
        "content_paths",
        nargs="+",
        help="URLs, PDFs, or markdown files to convert to news"
    )
    add_common_arguments(news_parser)
    news_parser.set_defaults(func=cmd_generate_news)
    
    # Research outline command  
    outline_parser = subparsers.add_parser(
        "outline", 
        help="Generate research outlines and summaries",
        description="Create detailed outlines and Chinese translations of research papers"
    )
    outline_parser.add_argument(
        "content_paths",
        nargs="+", 
        help="URLs, PDFs, or markdown files to outline"
    )
    add_common_arguments(outline_parser)
    outline_parser.set_defaults(func=cmd_generate_outline)
    
    # Format conversion command
    convert_parser = subparsers.add_parser(
        "convert",
        help="Convert files to markdown format", 
        description="Convert PDFs, HTML, DOCX, and other formats to markdown"
    )
    convert_parser.add_argument(
        "input_paths",
        nargs="+",
        help="Files to convert to markdown"
    )
    convert_parser.add_argument(
        "-o", "--output",
        help="Output file path (default: same name with .md extension)"
    )
    convert_parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    convert_parser.set_defaults(func=cmd_convert_to_md)
    
    # HTML cleaning command
    clean_parser = subparsers.add_parser(
        "clean",
        help="Clean HTML and convert to markdown",
        description="Extract main content from HTML pages and convert to clean markdown"
    )
    clean_parser.add_argument(
        "url_or_file",
        help="URL or HTML file to clean"
    )
    clean_parser.add_argument(
        "-o", "--output",
        help="Output markdown file"
    )
    clean_parser.add_argument(
        "--stdout",
        action="store_true", 
        help="Print result to stdout instead of saving to file"
    )
    clean_parser.set_defaults(func=cmd_clean_html)
    
    # Configuration management command
    config_parser = subparsers.add_parser(
        "config",
        help="Manage user configuration and models",
        description="Configure prompts, models, and other user settings"
    )
    config_parser.add_argument(
        "action",
        choices=["show", "init", "models", "add-model"],
        help="Configuration action to perform"
    )
    
    # Arguments for add-model action
    config_parser.add_argument(
        "--provider",
        help="Provider name (e.g., 'openai', 'anthropic', 'custom')"
    )
    config_parser.add_argument(
        "--model-name", 
        help="Model name as you want to reference it"
    )
    config_parser.add_argument(
        "--model-id",
        help="Actual model ID/name used by the API"
    )
    config_parser.add_argument(
        "--input-price",
        type=float,
        help="Input token price per 1K tokens in CNY"
    )
    config_parser.add_argument(
        "--output-price", 
        type=float,
        help="Output token price per 1K tokens in CNY"
    )
    config_parser.add_argument(
        "--max-tokens",
        type=int,
        help="Maximum tokens per request (default: 16000)"
    )
    config_parser.add_argument(
        "--context-window",
        type=int, 
        help="Model context window size (default: 128000)"
    )
    config_parser.set_defaults(func=cmd_config)
    
    return parser


def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Show help if no command specified
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Execute the appropriate command
    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\n✗ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        sys.exit(1)


# Legacy entry points for backward compatibility
def generate_news():
    """Legacy entry point for generate_news command."""
    # Convert old-style args to new CLI format
    import sys
    sys.argv = ['editor-assistant', 'news'] + sys.argv[1:]
    main()


def generate_outline():
    """Legacy entry point for generate_outline command."""
    # Convert old-style args to new CLI format
    import sys
    sys.argv = ['editor-assistant', 'outline'] + sys.argv[1:]
    main()


if __name__ == "__main__":
    main()