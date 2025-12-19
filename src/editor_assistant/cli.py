#!/usr/bin/env python3
"""
Command-line interface for Editor Assistant.

Provides a clean, consistent CLI with subcommands for different operations.
"""

import argparse
import sys
import asyncio
from pathlib import Path

# Optional rich import for better UI
try:
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from .main import EditorAssistant
from .data_models import ProcessType, Input, InputType
from .llm_client import LLMClient
from .md_converter import MarkdownConverter
from .clean_html_to_md import CleanHTML2Markdown
from .config.logging_config import progress
from .storage import RunRepository


DEFAULT_MODEL = "deepseek-v3.2"


def add_common_arguments(parser):
    """Add common arguments used across multiple commands."""
    parser.add_argument(
        "--model", 
        default=DEFAULT_MODEL,
        choices=LLMClient.get_supported_models(),
        help="Model to use for generation"
    )
    parser.add_argument(
        "--thinking",
        choices=["low", "medium", "high"],
        default=None,
        help="Thinking/reasoning level for models that support it (Gemini 3+). "
             "low=fast, medium=balanced, high=deep reasoning. Default: model decides."
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        dest="no_stream",
        help="Disable streaming output (default: streaming enabled)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode with detailed logging"
    )
    parser.add_argument(
        "--save-files",
        action="store_true",
        help="Persist generated files to disk (default: off; DB always updated)"
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

async def cmd_generate_brief(args):
    """Generate brief news from one or more sources (multi-source supported)."""
    stream = not getattr(args, 'no_stream', False)
    assistant = EditorAssistant(args.model, debug_mode=args.debug, thinking_level=args.thinking, stream=stream)

    # Parse key=value sources into Input objects
    inputs = [parse_source_spec(source) for source in args.sources]

    await assistant.process_multiple(inputs, ProcessType.BRIEF, save_files=args.save_files)


async def cmd_generate_outline(args):
    """Generate research outlines from a single paper."""
    stream = not getattr(args, 'no_stream', False)
    assistant = EditorAssistant(args.model, debug_mode=args.debug, thinking_level=args.thinking, stream=stream)
    # Create Input object for the paper
    input_obj = Input(type=InputType.PAPER, path=args.input_file)
    await assistant.process_multiple([input_obj], ProcessType.OUTLINE, save_files=args.save_files)

async def cmd_generate_translate(args):
    """Generate translation from a single paper."""
    stream = not getattr(args, 'no_stream', False)
    assistant = EditorAssistant(args.model, debug_mode=args.debug, thinking_level=args.thinking, stream=stream)
    # Create Input object for the paper
    input_obj = Input(type=InputType.PAPER, path=args.input_file)
    await assistant.process_multiple([input_obj], ProcessType.TRANSLATE, save_files=args.save_files)


async def cmd_process_multi_task(args):
    """Process input with multiple tasks (serial execution)."""
    stream = not getattr(args, 'no_stream', False)
    assistant = EditorAssistant(args.model, debug_mode=args.debug, thinking_level=args.thinking, stream=stream)
    
    # Parse sources into Input objects
    inputs = [parse_source_spec(source) for source in args.sources]
    
    # Parse tasks (comma-separated)
    task_names = [t.strip() for t in args.tasks.split(",")]
    
    # Execute each task serially (one task type after another)
    # But for each task type, process_multiple handles concurrent inputs!
    for task_name in task_names:
        progress(f"Executing task: {task_name}")
        await assistant.process_multiple(inputs, task_name, save_files=args.save_files)

async def cmd_batch_process(args):
    """Batch process files in a directory."""
    folder = Path(args.folder)
    if not folder.exists():
        print(f"Error: Folder '{folder}' does not exist")
        return

    # Support filtering by extension
    ext = args.ext if args.ext.startswith(".") else f".{args.ext}"
    pattern = f"*{ext}"
    files = sorted(folder.glob(pattern))
    
    if not files:
        print(f"No {ext} files found in '{folder}'")
        return

    print(f"Found {len(files)} {ext} files in '{folder}'")
    
    stream = not getattr(args, 'no_stream', False)
    assistant = EditorAssistant(args.model, debug_mode=args.debug, thinking_level=args.thinking, stream=stream)
    
    # Create Input objects for all files
    # Default to PAPER type for batch processing unless specified (future enhancement)
    inputs = [Input(type=InputType.PAPER, path=str(f)) for f in files]
    
    # Prepare callbacks for Rich UI if available and streaming enabled
    progress_callbacks = {}
    
    if RICH_AVAILABLE and stream:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("{task.fields[status]}"),
            TimeRemainingColumn(),
        ) as progress_ctx:
            
            # Create a task for each file (hidden initially to prevent clutter)
            rich_tasks = {}
            
            # Overall progress bar
            overall_task = progress_ctx.add_task(
                f"[bold green]Batch Processing ({len(inputs)} files)", 
                total=len(inputs),
                completed=0,
                status=""  # Initialize status field to avoid KeyError
            )
            
            for inp in inputs:
                filename = Path(inp.path).name
                task_id = progress_ctx.add_task(
                    f"[cyan]{filename}", 
                    total=None,
                    status="[dim]Pending...",
                    visible=False # Hide until active
                )
                rich_tasks[inp.path] = task_id
            
            # Helper to create a stream callback closure
            def make_callback(file_path):
                task_id = rich_tasks[file_path]
                
                # State to track if we've started receiving tokens
                started = False
                
                def callback(chunk: str):
                    nonlocal started
                    if not started:
                        # Make visible on first activity
                        progress_ctx.update(task_id, visible=True, status="[green]Generating...", total=100)
                        started = True
                    
                    # Show activity
                    progress_ctx.update(task_id, advance=len(chunk)/50)
                    
                return callback

            # Helper for done callback
            def on_done(file_path, success):
                task_id = rich_tasks.get(file_path)
                if task_id is not None:
                    # Mark complete in UI
                    progress_ctx.update(task_id, completed=100, visible=False)
                    
                    # Print permanent log line
                    filename = Path(file_path).name
                    if success:
                        progress_ctx.console.print(f"[green]✔ {filename} processed[/green]")
                    else:
                        progress_ctx.console.print(f"[red]✗ {filename} failed[/red]")
                    
                    # Update overall progress
                    progress_ctx.update(overall_task, advance=1)

            # Create callbacks for all inputs
            for inp in inputs:
                progress_callbacks[inp.path] = make_callback(inp.path)
            
            await assistant.process_multiple(
                inputs, 
                args.task, 
                output_to_console=False, 
                save_files=args.save_files or True, 
                progress_callbacks=progress_callbacks,
                done_callback=on_done
            )
            
            # Ensure overall is done (in case of weirdness)
            progress_ctx.update(overall_task, completed=len(inputs))
                
    else:
        # Fallback to standard behavior (concurrent text mixing or serial if desired)
        # Fallback to standard behavior (concurrent text mixing or serial if desired)
        # Or just run it. If streaming is on but Rich missing, it will be messy.
        # We assume Rich is installed.
        if not RICH_AVAILABLE and stream:
            print("Warning: 'rich' library not found. Streaming output will be interleaved.")
            
        await assistant.process_multiple(
            inputs, 
            args.task, 
            save_files=args.save_files or True # Force save for batch
        )

    # Print Batch Summary
    usage = assistant.md_processor.llm_client.get_token_usage()
    total_cost = usage["cost"]["total_cost"]
    total_tokens = usage["total_input_tokens"] + usage["total_output_tokens"]
    currency = assistant.md_processor.llm_client.pricing_currency
    processed_count = len(usage["requests"])
    
    if processed_count > 0:
        avg_cost = total_cost / processed_count
        avg_tokens = total_tokens / processed_count
    else:
        avg_cost = 0
        avg_tokens = 0

    if RICH_AVAILABLE:
        console = Console()
        table = Table(show_header=False, box=None)
        table.add_row("Total Files", str(len(inputs)))
        table.add_row("Successful API Calls", str(processed_count))
        table.add_row("Total Tokens", f"{total_tokens:,}")
        table.add_row("Total Cost", f"{currency}{total_cost:.4f}")
        table.add_row("Avg Tokens/Task", f"{avg_tokens:,.0f}")
        table.add_row("Avg Cost/Task", f"{currency}{avg_cost:.4f}")
        
        console.print()
        console.print(Panel(table, title="[bold green]Batch Processing Summary[/bold green]", expand=False))
    else:
        print("\nBatch Processing Summary")
        print(f"Total Files: {len(inputs)}")
        print(f"Successful Calls: {processed_count}")
        print(f"Total Tokens: {total_tokens:,}")
        print(f"Total Cost: {currency}{total_cost:.4f}")
        print(f"Avg Tokens/Task: {avg_tokens:,.0f}")
        print(f"Avg Cost/Task: {currency}{avg_cost:.4f}")


# Synchronous commands (CPU bound or simple IO)
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


# =========================================================================
# History and Stats Commands (Synchronous)
# =========================================================================

def cmd_history(args):
    """Show run history."""
    repo = RunRepository()
    
    if args.search:
        runs = repo.search_by_title(args.search, limit=args.limit)
        print(f"\n📋 Runs matching '{args.search}':\n")
    else:
        runs = repo.get_recent_runs(limit=args.limit)
        print(f"\n📋 Recent {len(runs)} runs:\n")
    
    if not runs:
        print("  No runs found.")
        return
    
    # Print header
    print(f"{'ID':>5} │ {'Time':^19} │ {'Task':<10} │ {'Model':<18} │ {'Status':<8} │ {'Cost':>8} │ Input")
    print("─" * 100)
    
    for run in runs:
        run_id = run.get('id', 0)
        timestamp = run.get('timestamp', '')[:19] if run.get('timestamp') else ''
        task = run.get('task', '')[:10]
        model = run.get('model', '')[:18]
        status = run.get('status', '')[:8]
        cost = run.get('total_cost', 0) or 0
        currency = run.get('currency', '$') or '$'
        titles = run.get('input_titles', '') or 'Unknown'
        titles = titles[:30] + '...' if len(titles) > 30 else titles
        
        status_icon = "✓" if status == "success" else "✗" if status == "failed" else "○"
        print(f"{run_id:>5} │ {timestamp} │ {task:<10} │ {model:<18} │ {status_icon} {status:<6} │ {currency}{cost:>6.4f} │ {titles}")
    
    print()


def cmd_stats(args):
    """Show usage statistics."""
    repo = RunRepository()
    stats = repo.get_stats(days=args.days)
    
    print(f"\n📊 Usage Statistics (last {stats['period_days']} days)\n")
    print(f"Total Runs: {stats['total_runs']}")
    print(f"Success Rate: {stats['success_rate']:.1%}")
    
    # By status
    print(f"\n📈 By Status:")
    for status, count in stats.get('by_status', {}).items():
        icon = "✓" if status == "success" else "✗" if status == "failed" else "○"
        print(f"  {icon} {status}: {count}")
    
    # By model
    print(f"\n🤖 By Model:")
    if stats.get('by_model'):
        for item in stats['by_model']:
            model = item.get('model', 'Unknown')
            runs = item.get('runs', 0)
            cost = item.get('total_cost', 0) or 0
            tokens = item.get('total_tokens', 0) or 0
            print(f"  {model}: {runs} runs, {tokens:,} tokens, ${cost:.4f}")
    else:
        print("  No data")
    
    # By task
    print(f"\n📝 By Task:")
    if stats.get('by_task'):
        for item in stats['by_task']:
            task = item.get('task', 'Unknown')
            runs = item.get('runs', 0)
            print(f"  {task}: {runs} runs")
    else:
        print("  No data")
    
    print()


def cmd_show_run(args):
    """Show details of a specific run."""
    repo = RunRepository()
    run = repo.get_run_details(args.run_id)
    
    if not run:
        print(f"✗ Run #{args.run_id} not found")
        sys.exit(1)
    
    print(f"\n📄 Run #{run['id']} Details\n")
    print(f"  Timestamp: {run.get('timestamp', 'Unknown')}")
    print(f"  Task:      {run.get('task', 'Unknown')}")
    print(f"  Model:     {run.get('model', 'Unknown')}")
    print(f"  Status:    {run.get('status', 'Unknown')}")
    if run.get('thinking_level'):
        print(f"  Thinking:  {run.get('thinking_level')}")
    print(f"  Stream:    {'Yes' if run.get('stream') else 'No'}")
    if run.get('error_message'):
        print(f"  Error:     {run.get('error_message')}")
    
    # Inputs
    print(f"\n📥 Inputs ({len(run.get('inputs', []))}):")
    for inp in run.get('inputs', []):
        print(f"  • [{inp.get('type', '')}] {inp.get('title', 'Untitled')}")
        print(f"    Source: {inp.get('source_path', 'Unknown')}")
    
    # Token usage
    usage = run.get('token_usage')
    currency = run.get('currency', '$') or '$'
    if usage:
        print(f"\n💰 Token Usage:")
        print(f"  Input:  {usage.get('input_tokens', 0):,} tokens ({currency}{usage.get('cost_input', 0):.4f})")
        print(f"  Output: {usage.get('output_tokens', 0):,} tokens ({currency}{usage.get('cost_output', 0):.4f})")
        total_cost = (usage.get('cost_input', 0) or 0) + (usage.get('cost_output', 0) or 0)
        print(f"  Total:  {currency}{total_cost:.4f}")
        print(f"  Time:   {usage.get('process_time', 0):.1f}s")
    
    # Outputs
    outputs = run.get('outputs', [])
    print(f"\n📤 Outputs ({len(outputs)}):")
    for out in outputs:
        out_type = out.get('output_type', 'unknown')
        content_type = out.get('content_type', 'text')
        content = out.get('content', '')
        preview = content[:200] + '...' if len(content) > 200 else content
        preview = preview.replace('\n', ' ')
        
        print(f"  • {out_type} ({content_type})")
        if args.output:
            print(f"\n{content}\n")
        else:
            print(f"    Preview: {preview}")
    
    print()


def create_parser():
    """Create the main argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="editor-assistant",
        description="AI-powered editor assistant for research and news generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate content
  %(prog)s brief paper=https://arxiv.org/pdf/2508.08443
  %(prog)s outline paper.pdf --model deepseek-r1
  %(prog)s translate paper.pdf --model gemini-2.5-flash --thinking high
  %(prog)s process paper.pdf --tasks brief,outline --no-stream
  
  # Batch processing
  %(prog)s batch ./samples/ --ext .pdf --task brief
  %(prog)s batch ./papers/ --ext .html --task translate --model deepseek-v3.2
  
  # Convert and clean
  %(prog)s convert *.pdf -o ./markdown/
  %(prog)s clean https://example.com/page.html -o clean.md
  
  # View history and stats
  %(prog)s history -n 20
  %(prog)s history --search "quantum"
  %(prog)s stats -d 30
  %(prog)s show 1 --output
"""
    )
    
    # Global options
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.4.0"
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
    
    # Multi-task process command
    process_parser = subparsers.add_parser(
        "process",
        help="Process input with multiple tasks",
        description="Execute multiple tasks on the same input (serial execution)"
    )
    process_parser.add_argument(
        "sources",
        nargs="+",
        help="Sources in format 'type=path' (e.g., paper=file.pdf news=url.com)"
    )
    process_parser.add_argument(
        "--tasks",
        required=True,
        help="Comma-separated list of tasks to execute (e.g., 'brief,outline')"
    )
    add_common_arguments(process_parser)
    process_parser.set_defaults(func=cmd_process_multi_task)
    
    # Batch process command
    batch_parser = subparsers.add_parser(
        "batch",
        help="Batch process files in a directory",
        description="Process multiple files concurrently using a single task"
    )
    batch_parser.add_argument(
        "folder",
        help="Path to folder containing files"
    )
    batch_parser.add_argument(
        "--task",
        required=True,
        choices=["brief", "outline", "translate"],
        help="Task to run on each file"
    )
    batch_parser.add_argument(
        "--ext",
        default=".pdf",
        help="File extension to filter by (default: .pdf)"
    )
    add_common_arguments(batch_parser)
    batch_parser.set_defaults(func=cmd_batch_process)
    
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
    
    # =========================================================================
    # History and Stats Commands
    # =========================================================================
    
    # History command
    history_parser = subparsers.add_parser(
        "history",
        help="View run history",
        description="List recent runs from the database"
    )
    history_parser.add_argument(
        "-n", "--limit",
        type=int,
        default=20,
        help="Number of runs to show (default: 20)"
    )
    history_parser.add_argument(
        "--search",
        help="Search by input title"
    )
    history_parser.set_defaults(func=cmd_history)
    
    # Stats command
    stats_parser = subparsers.add_parser(
        "stats",
        help="View usage statistics",
        description="Show usage statistics and costs"
    )
    stats_parser.add_argument(
        "-d", "--days",
        type=int,
        default=7,
        help="Number of days to include (default: 7)"
    )
    stats_parser.set_defaults(func=cmd_stats)
    
    # Show command
    show_parser = subparsers.add_parser(
        "show",
        help="Show details of a specific run",
        description="Display detailed information about a run"
    )
    show_parser.add_argument(
        "run_id",
        type=int,
        help="Run ID to show"
    )
    show_parser.add_argument(
        "--output",
        action="store_true",
        help="Include full output content"
    )
    show_parser.set_defaults(func=cmd_show_run)
    
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
        if asyncio.iscoroutinefunction(args.func):
            asyncio.run(args.func(args))
        else:
            args.func(args)
    except KeyboardInterrupt:
        print("\n✗ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        # Raise debugging info if needed, or exit cleanly
        sys.exit(1)



if __name__ == "__main__":
    main()
