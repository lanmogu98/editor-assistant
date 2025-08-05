# Python argparse and CLI Design Reference

## Table of Contents
1. [Python argparse Basics](#python-argparse-basics)
2. [CLI Architecture Design](#cli-architecture-design)  
3. [Our cli.py Structure](#our-clipy-structure)
4. [Argument Types Reference](#argument-types-reference)
5. [Best Practices](#best-practices)
6. [Common Patterns](#common-patterns)
7. [Troubleshooting](#troubleshooting)

## Python argparse Basics

### Simple Parser Foundation

```python
import argparse

# Create a parser object
parser = argparse.ArgumentParser(description="My program description")

# Add arguments
parser.add_argument("filename", help="File to process")  # Positional argument
parser.add_argument("--verbose", action="store_true", help="Enable verbose output")  # Optional flag

# Parse command line arguments
args = parser.parse_args()

# Use the arguments
print(f"Processing {args.filename}")
if args.verbose:
    print("Verbose mode enabled")
```

**Command line usage:**
```bash
python script.py myfile.txt --verbose
```

### Subcommands (Advanced)

```python
import argparse

# Main parser
parser = argparse.ArgumentParser(description="Git-like tool")

# Create subparsers
subparsers = parser.add_subparsers(dest="command", help="Available commands")

# Add 'add' subcommand
add_parser = subparsers.add_parser("add", help="Add files")
add_parser.add_argument("files", nargs="+", help="Files to add")

# Add 'commit' subcommand  
commit_parser = subparsers.add_parser("commit", help="Create commit")
commit_parser.add_argument("-m", "--message", required=True, help="Commit message")

# Parse arguments
args = parser.parse_args()

# Handle different commands
if args.command == "add":
    print(f"Adding files: {args.files}")
elif args.command == "commit":
    print(f"Committing with message: {args.message}")
```

**Command line usage:**
```bash
python script.py add file1.txt file2.txt
python script.py commit -m "Fix bug"
```

## CLI Architecture Design

### Design Principles

1. **Separation of Concerns**: CLI parsing ≠ Business logic
2. **Single Responsibility**: Each function has one clear purpose
3. **DRY (Don't Repeat Yourself)**: Common arguments defined once
4. **Extensibility**: Easy to add new commands
5. **Error Handling**: Graceful failures with proper exit codes

### Architecture Layers

```
┌─────────────────────────────────────┐
│          Command Line               │
│  editor-assistant news paper.pdf   │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│            CLI Layer                │
│  • Argument parsing                 │
│  • Input validation                 │
│  • Help generation                  │
│  • Error handling                   │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│        Command Handlers             │
│  • cmd_generate_news()              │
│  • cmd_generate_outline()           │
│  • cmd_convert_to_md()              │
└─────────────────┬───────────────────┘
                  │
┌─────────────────▼───────────────────┐
│        Business Logic               │
│  • EditorAssistant                  │
│  • MDProcessor                      │
│  • MarkdownConverter                │
└─────────────────────────────────────┘
```

## Our cli.py Structure

### 1. Import Section

```python
#!/usr/bin/env python3
"""
Command-line interface for Editor Assistant.
Provides a clean, consistent CLI with subcommands for different operations.
"""

import argparse        # Core argument parsing
import sys            # System functions (exit codes)
from pathlib import Path  # File path handling

# Import your business logic modules
from .main import EditorAssistant
from .md_processesor import ArticleType
from .llm_client import LLMClient
from .md_converter import MarkdownConverter
from .clean_html_to_md import clean_html_to_markdown
```

**Purpose**: Import all necessary tools. CLI module acts as a **coordinator** between command line and business logic.

### 2. Helper Function Pattern

```python
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
```

**Benefits**:
- **DRY principle**: Define common arguments once
- **Consistency**: All commands have same argument behavior
- **Maintainability**: Change behavior in one place

### 3. Command Handler Functions

```python
def cmd_generate_news(args):
    """Generate news articles from content."""
    assistant = EditorAssistant(args.model, debug_mode=args.debug)
    for path in args.content_paths:
        assistant.summarize_multiple([path], ArticleType.news)
```

**Pattern**: Each command gets its own handler function:
- **Input**: `args` object (parsed arguments)  
- **Job**: Translate CLI args → Business logic calls
- **Clean separation**: CLI concerns vs business logic

### 4. Main Parser Setup

```python
def create_parser():
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="editor-assistant",                                    # Program name
        description="AI-powered editor assistant for research and news generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,      # Keep formatting
        epilog="""
Examples:
  %(prog)s news "https://example.com/article"
  %(prog)s outline paper.pdf --model deepseek-r1-latest
  %(prog)s convert *.pdf --output-dir ./markdown/
  %(prog)s clean https://example.com/page.html -o clean.md
        """
    )
    
    # Global options (work with any subcommand)
    parser.add_argument(
        "--version",
        action="version", 
        version="%(prog)s 0.1.0"
    )
    
    # Create subcommand system
    subparsers = parser.add_subparsers(
        dest="command",           # Store chosen command in args.command
        help="Available commands",
        metavar="COMMAND"
    )
    
    return parser
```

**Key Parameters**:
- **`prog`**: Name shown in help messages
- **`formatter_class`**: How help text is formatted
- **`epilog`**: Examples shown at bottom of help
- **`dest="command"`**: Where to store the chosen subcommand

### 5. Subcommand Definition Pattern

```python
# Create a subcommand
news_parser = subparsers.add_parser(
    "news",                                                    # Command name
    help="Generate news articles from research content",       # Short help
    description="Convert research papers and articles into news format"  # Long help
)

# Add arguments specific to this subcommand
news_parser.add_argument(
    "content_paths",        # Argument name (becomes args.content_paths)
    nargs="+",             # Accept 1 or more values
    help="URLs, PDFs, or markdown files to convert to news"
)

# Add common arguments (--model, --debug)
add_common_arguments(news_parser)

# CRUCIAL: Connect subcommand to handler function
news_parser.set_defaults(func=cmd_generate_news)
```

**Steps for Each Subcommand**:
1. Create parser object with `subparsers.add_parser()`
2. Define specific arguments with `add_argument()`
3. Add common arguments with helper function
4. **Link to handler function** via `set_defaults(func=...)`

### 6. Main Entry Point

```python
def main():
    """Main CLI entry point."""
    # 1. Create the parser with all subcommands
    parser = create_parser()
    
    # 2. Parse command line arguments
    args = parser.parse_args()
    
    # 3. Handle edge case - no subcommand given
    if not args.command:
        parser.print_help()    # Show help message
        sys.exit(1)           # Exit with error code
    
    # 4. Execute the appropriate command handler
    try:
        args.func(args)       # Call the function assigned by set_defaults()
    except KeyboardInterrupt:
        print("\n✗ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        sys.exit(1)
```

**Key Magic**: `args.func(args)` 
- Each subcommand sets `func=cmd_generate_news` via `set_defaults()`
- So `args.func` contains the handler function reference
- We call it with the parsed arguments

## Argument Types Reference

### Positional Arguments
```python
parser.add_argument("filename")  # Required, no -- prefix
# Usage: command myfile.txt
# Access: args.filename
```

### Optional Arguments
```python
parser.add_argument("--model", default="gpt-4")  # Optional, with -- prefix
parser.add_argument("-m", "--model", default="gpt-4")  # Short and long form
# Usage: command --model deepseek OR command -m deepseek
# Access: args.model
```

### Boolean Flags
```python
parser.add_argument("--debug", action="store_true")  # True if present, False if not
parser.add_argument("--no-cache", action="store_false")  # False if present, True if not
# Usage: command --debug
# Access: args.debug (True/False)
```

### Multiple Values
```python
parser.add_argument("files", nargs="+")    # 1 or more values (required)
parser.add_argument("files", nargs="*")    # 0 or more values (optional)
parser.add_argument("files", nargs=2)      # Exactly 2 values
parser.add_argument("files", nargs="?")    # 0 or 1 value
# Usage: command file1.txt file2.txt file3.txt
# Access: args.files (list)
```

### Restricted Choices
```python
parser.add_argument("--model", choices=["gpt-4", "claude", "deepseek"])
parser.add_argument("--level", type=int, choices=range(1, 6))  # 1-5
# Only allows specified values
# Automatic validation and error messages
```

### Type Conversion
```python
parser.add_argument("--port", type=int, default=8080)
parser.add_argument("--config", type=Path)  # Convert to Path object
parser.add_argument("--timeout", type=float)
# Automatic type conversion and validation
```

### Required Optional Arguments
```python
parser.add_argument("--api-key", required=True)
# Optional syntax (--) but required to be present
```

## Command Flow Summary

```
Command Line: editor-assistant news paper.pdf --model deepseek --debug
                     ↓
1. create_parser() builds the argument structure
                     ↓  
2. parse_args() parses and creates args object:
   - args.command = "news"
   - args.content_paths = ["paper.pdf"]
   - args.model = "deepseek" 
   - args.debug = True
   - args.func = cmd_generate_news
                     ↓
3. main() calls args.func(args)
                     ↓
4. cmd_generate_news(args) gets called with parsed arguments
                     ↓
5. Handler creates EditorAssistant(args.model, debug_mode=args.debug)
                     ↓
6. Business logic executes: assistant.summarize_multiple([path], ArticleType.news)
```

## Best Practices

### 1. Clear Argument Names
```python
# Good
parser.add_argument("--output-file", help="Where to save results")
parser.add_argument("--max-tokens", type=int, help="Maximum tokens to generate")

# Avoid
parser.add_argument("--of")  # Unclear
parser.add_argument("--x", type=int)  # Cryptic
```

### 2. Helpful Documentation
```python
parser.add_argument(
    "--model",
    choices=["gpt-4", "claude", "deepseek"],
    default="gpt-4",
    help="LLM model to use for generation (default: %(default)s)"
)
# %(default)s automatically shows the default value
```

### 3. Sensible Defaults
```python
parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds")
parser.add_argument("--output-dir", default="./output", help="Output directory")
```

### 4. Input Validation
```python
def validate_file(filename):
    path = Path(filename)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"File {filename} does not exist")
    return path

parser.add_argument("input_file", type=validate_file, help="Input file to process")
```

### 5. Proper Exit Codes
```python
def main():
    try:
        args.func(args)
    except KeyboardInterrupt:
        sys.exit(130)  # Standard code for Ctrl+C
    except FileNotFoundError:
        print("Error: File not found")
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
```

## Common Patterns

### Mutually Exclusive Arguments
```python
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument("--file", help="Read from file")
group.add_argument("--url", help="Read from URL")
# User must choose exactly one
```

### Argument Groups (Visual Organization)
```python
input_group = parser.add_argument_group("Input Options")
input_group.add_argument("--file", help="Input file")
input_group.add_argument("--url", help="Input URL")

output_group = parser.add_argument_group("Output Options")  
output_group.add_argument("--output", help="Output file")
output_group.add_argument("--format", help="Output format")
```

### Configuration File Support
```python
parser.add_argument("--config", type=argparse.FileType('r'), 
                   help="Configuration file")

# In your handler:
if args.config:
    config = json.load(args.config)
    # Merge config with command line args
```

### Verbose Levels
```python
parser.add_argument("-v", "--verbose", action="count", default=0,
                   help="Increase verbosity (use -vv for more)")
# Usage: command -v (level 1), command -vv (level 2)
```

## Troubleshooting

### Common Issues

1. **`AttributeError: 'Namespace' object has no attribute 'func'`**
   - **Cause**: Forgot `set_defaults(func=handler)` for a subcommand
   - **Fix**: Add `subcommand_parser.set_defaults(func=your_handler)`

2. **Arguments not parsed correctly**
   - **Debug**: Add `print(args)` after `parse_args()` to see what was parsed
   - **Check**: Argument names, nargs values, type conversions

3. **Subcommand not recognized**
   - **Cause**: Subcommand not added to subparsers
   - **Fix**: Ensure `subparsers.add_parser("your-command")` is called

4. **Help text formatting issues**
   - **Fix**: Use `formatter_class=argparse.RawDescriptionHelpFormatter`
   - **Alternative**: Use `argparse.RawTextHelpFormatter` for complete control

### Debugging Tips

```python
# Add debug output
def main():
    parser = create_parser()
    args = parser.parse_args()
    
    # Debug: Print parsed arguments
    print(f"Debug: Parsed args: {args}")
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        print("Error: No function assigned to this command")
        parser.print_help()
```

### Testing CLI
```python
# Test your CLI programmatically
import sys
from io import StringIO

def test_cli():
    # Capture output
    old_stdout = sys.stdout
    sys.stdout = StringIO()
    
    # Test command
    sys.argv = ['editor-assistant', 'news', 'test.pdf']
    main()
    
    # Get output
    output = sys.stdout.getvalue()
    sys.stdout = old_stdout
    
    print(f"CLI output: {output}")
```

This reference covers all the key concepts needed to understand and extend the CLI system!