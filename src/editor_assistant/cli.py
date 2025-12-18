#!/usr/bin/env python3
"""
Command-line interface for Editor Assistant.

Provides a clean, consistent CLI with subcommands for different operations.
"""

import argparse
import sys
from pathlib import Path

from .main import EditorAssistant
from .data_models import ProcessType, Input, InputType
from .llm_client import LLMClient
from .md_converter import MarkdownConverter
from .clean_html_to_md import CleanHTML2Markdown


DEFAULT_MODEL = "glm-4.6-or"


def add_common_arguments(parser):
    """Add common arguments used across multiple commands."""
    parser.add_argument(
        "--model", 
        default=DEFAULT_MODEL,
        choices=LLMClient.get_supported_models(),
        help="Model to use for generation"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with detailed logging"
    )



def parse_source_spec(spec: str) -> Input:
    """Parse key=value format into Input object."""
    if "=" not in spec:
        raise argparse.ArgumentTypeError("Sources must be in format 'type=path' (e.g., paper=file.pdf, news=url.com)")

    type_str, path = spec.split("=", 1)
    type_str = type_str.strip().lower()

    if type_str not in ["paper", "news"]:
        raise argparse.ArgumentTypeError(f"Invalid source type '{type_str}'. Use 'paper' or 'news'")

    if not path.strip():
        raise argparse.ArgumentTypeError("Path cannot be empty in 'type=path' format")

    src_type = InputType.PAPER if type_str == "paper" else InputType.NEWS
    return Input(type=src_type, path=path.strip())

def cmd_generate_brief(args):
    """Generate brief news from one or more sources (multi-source supported)."""
    assistant = EditorAssistant(args.model, debug_mode=args.debug)

    # Parse key=value sources into Input objects
    inputs = [parse_source_spec(source) for source in args.sources]

    assistant.process_multiple(inputs, ProcessType.BRIEF)


def cmd_generate_outline(args):
    """Generate research outlines from a single paper."""
    assistant = EditorAssistant(args.model, debug_mode=args.debug)
    # Create Input object for the paper
    input_obj = Input(type=InputType.PAPER, path=args.input_file)
    assistant.process_multiple([input_obj], ProcessType.OUTLINE)

def cmd_generate_translate(args):
    """Generate translation from a single paper."""
    assistant = EditorAssistant(args.model, debug_mode=args.debug)
    # Create Input object for the paper
    input_obj = Input(type=InputType.PAPER, path=args.input_file)
    assistant.process_multiple([input_obj], ProcessType.TRANSLATE)

def cmd_convert_to_md(args):
    """Convert various formats to markdown."""
    from urllib.parse import urlparse
    converter = MarkdownConverter()
    
    for input_path in args.input_paths:
        try:
            # Determine output path
            if args.output:
                output_path = Path(args.output)
            elif input_path.startswith("http"):
                # For URLs, generate a sanitized filename in current directory
                parsed = urlparse(input_path)
                # Use path component, replace slashes, remove leading/trailing underscores
                filename = parsed.path.replace("/", "_").strip("_") or "output"
                output_path = Path(f"{filename}.md")
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
        converter = CleanHTML2Markdown()
        result = converter.convert(args.url_or_file)
        
        if result is None:
            print(f"✗ Failed to convert: {args.url_or_file}")
            sys.exit(1)
        
        if args.stdout:
            print(result.content)
        else:
            output_path = args.output
            if not output_path:
                # Generate output path from input
                from pathlib import Path
                if args.url_or_file.startswith("http"):
                    # Extract filename from URL
                    output_path = "clean_output.md"
                else:
                    input_file = Path(args.url_or_file)
                    output_path = str(input_file.parent / f"{input_file.stem}_clean.md")
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"# {result.title}\n\n")
                if result.authors:
                    f.write(f"**Authors:** {result.authors}\n\n")
                f.write(f"**Source:** {result.source_path}\n\n")
                f.write("---\n\n")
                f.write(result.content)
            print(f"✓ Cleaned HTML saved to: {output_path}")
            
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
  %(prog)s brief paper=https://arxiv.org/pdf/2508.08443
  %(prog)s brief paper=paper.pdf news=https://example.com/article \
                 --model deepseek-r1 --debug
  %(prog)s outline paper.pdf --model deepseek-r1
  %(prog)s translate paper.pdf --model deepseek-r1
  %(prog)s convert *.pdf -o ./markdown/
  %(prog)s clean https://example.com/page.html -o clean.md
"""
    )
    
    # Global options
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.3.0"
    )
    
    # Create subcommands
    subparsers = parser.add_subparsers(
        dest="command",
        help="Available commands",
        metavar="COMMAND"
    )
    
    # Brief (short news generation) command - multi-source supported
    brief_parser = subparsers.add_parser(
        "brief",
        help="Generate brief news from research content",
        description="Convert research papers and articles into short news format"
    )
    brief_parser.add_argument(
        "sources",
        nargs="+",
        help="Sources in format 'type=path' (e.g., paper=file.pdf news=url.com)"
    )
    add_common_arguments(brief_parser)
    brief_parser.set_defaults(func=cmd_generate_brief)
    
    # Research outline command
    outline_parser = subparsers.add_parser(
        "outline",
        help="Generate research outlines and summaries",
        description="Create detailed outlines and Chinese translations of research papers"
    )
    outline_parser.add_argument(
        "input_file",
        help="Path to research paper (PDF, DOCX, or markdown file)"
    )
    add_common_arguments(outline_parser)
    outline_parser.set_defaults(func=cmd_generate_outline)

    # Translate command
    translate_parser = subparsers.add_parser(
        "translate",
        help="Generate Chinese translation from a single paper",
        description="Create Chinese translations of research papers"
    )
    translate_parser.add_argument(
        "input_file",
        help="Path to research paper (PDF, DOCX, or markdown file)"
    )
    add_common_arguments(translate_parser)
    translate_parser.set_defaults(func=cmd_generate_translate)
    
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



if __name__ == "__main__":
    main()
