#!/usr/bin/env python3
"""
Command-line interface for Editor Assistant.

Provides a clean, consistent CLI with subcommands for different operations.
"""

import argparse
import sys
from pathlib import Path

from .main import EditorAssistant
from .data_models import ProcessType, Input, SourceType
from .llm_client import LLMClient
from .md_converter import MarkdownConverter
from .clean_html_to_md import CleanHTML2Markdown

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

def make_article_parser(allowed_types: set[str] | None = None):
    """Return a parse-time validator for TYPE:PATH to an Input object."""
    def _parser(spec: str) -> Input:
        if ":" not in spec:
            raise argparse.ArgumentTypeError("Each --article must be in the format 'type:path'")
        type_str, path = spec.split(":", 1)
        type_str = type_str.strip().lower()
        try:
            src_type = SourceType(type_str)
        except ValueError:
            raise argparse.ArgumentTypeError("Invalid source type. Use 'paper' or 'news'.")
        if allowed_types and type_str not in allowed_types:
            allowed_msg = ", ".join(sorted(allowed_types))
            raise argparse.ArgumentTypeError(f"Unsupported type '{type_str}'. Allowed: {allowed_msg}")
        if not path.strip():
            raise argparse.ArgumentTypeError("Path portion in TYPE:PATH cannot be empty")
        return Input(type=src_type, path=path)
    return _parser


def cmd_generate_brief(args):
    """Generate brief news from one or more sources (multi-source supported)."""
    assistant = EditorAssistant(args.model, debug_mode=args.debug)
    assistant.process_multiple(args.article, ProcessType.BRIEF)


def cmd_generate_outline(args):
    """Generate research outlines from a single paper (requires explicit type)."""
    assistant = EditorAssistant(args.model, debug_mode=args.debug)
    if len(args.article) != 1:
        raise ValueError("outline requires exactly one --article of type 'paper'")
    assistant.process_multiple([args.article[0]], ProcessType.OUTLINE)


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
                    f.write(result.content)
                
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

def create_parser():
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="editor-assistant",
        description="AI-powered editor assistant for research and news generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s brief --article paper:https://arxiv.org/pdf/2508.08443
  %(prog)s brief --article paper:paper.pdf --article news:https://example.com/article \
                 --model deepseek-r1-latest --debug
  %(prog)s outline --article paper:paper.pdf --model deepseek-r1-latest
  %(prog)s convert *.pdf -o ./markdown/
  %(prog)s clean https://example.com/page.html -o clean.md
"""
    )
    
    # Global options
    parser.add_argument(
        "--version",
        action="version", 
        version="%(prog)s 0.2.0"
    )
    
    # Create subcommands
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        metavar="COMMAND"
    )
    
    # Brief (short news generation) command - multi-source supported
    news_parser = subparsers.add_parser(
        "brief",
        help="Generate brief news from research content",
        description="Convert research papers and articles into short news format"
    )
    news_parser.add_argument(
        "--article",
        action="append",
        required=True,
        type=make_article_parser({"paper", "news"}),
        metavar="TYPE:PATH",
        help="Add a source as TYPE:PATH (TYPE in {paper,news}); repeatable"
    )
    add_common_arguments(news_parser)
    news_parser.set_defaults(func=cmd_generate_brief)
    
    # Research outline command  
    outline_parser = subparsers.add_parser(
        "outline", 
        help="Generate research outlines and summaries",
        description="Create detailed outlines and Chinese translations of research papers"
    )
    outline_parser.add_argument(
        "--article",
        action="append",
        required=True,
        type=make_article_parser({"paper"}),
        metavar="TYPE:PATH",
        help="Add a paper source as TYPE:PATH (TYPE must be 'paper')"
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
    sys.argv = ['editor-assistant', 'brief'] + sys.argv[1:]
    main()


def generate_outline():
    """Legacy entry point for generate_outline command."""
    # Convert old-style args to new CLI format
    import sys
    sys.argv = ['editor-assistant', 'outline'] + sys.argv[1:]
    main()


if __name__ == "__main__":
    main()
