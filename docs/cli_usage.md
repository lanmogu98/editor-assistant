# CLI Usage Guide

## New Unified Command Structure

The CLI has been restructured to follow best practices with a single entry point and subcommands.

### Main Command: `editor-assistant`

```bash
editor-assistant --help
```

### Available Subcommands

#### 1. Generate News Articles
```bash
editor-assistant news "https://example.com/research-article"
editor-assistant news paper.pdf --model deepseek-r1-latest --debug
```

#### 2. Generate Research Outlines  
```bash
editor-assistant outline "https://arxiv.org/paper.pdf"
editor-assistant outline *.pdf --model deepseek-r1-latest
```

#### 3. Convert Files to Markdown
```bash
editor-assistant convert document.pdf
editor-assistant convert *.docx -o converted/
```

#### 4. Clean HTML to Markdown
```bash
editor-assistant clean "https://example.com/page.html" -o clean.md
editor-assistant clean page.html --stdout
```

### Global Options

- `--model`: Choose LLM model (default: deepseek-r1-latest)
- `--debug`: Enable detailed debug logging
- `--version`: Show version information

### Examples

```bash
# Generate news from a research paper
editor-assistant news "https://nature.com/article.pdf"

# Create research outline with debug mode
editor-assistant outline paper.pdf --debug

# Convert multiple files
editor-assistant convert *.pdf *.docx

# Clean web page and print to console
editor-assistant clean "https://example.com" --stdout
```

## Legacy Commands (Backward Compatibility)

The old command names still work:

```bash
generate_news "https://example.com/article"    # Same as: editor-assistant news
generate_outline paper.pdf                     # Same as: editor-assistant outline
any2md document.pdf                           # Same as: editor-assistant convert  
html2md page.html                             # Same as: editor-assistant clean
```

## Benefits of New Structure

### ✅ **Consistent Interface**
- Single entry point with subcommands
- Consistent argument patterns across all operations
- Clear help text and examples

### ✅ **Better Organization** 
- All CLI logic in one module (`cli.py`)
- Business logic separated from CLI concerns
- Easy to add new commands

### ✅ **Improved Discoverability**
- `editor-assistant --help` shows all available operations
- Each subcommand has detailed help
- Clear command hierarchy

### ✅ **Enhanced Maintainability**
- No code duplication in argument parsing
- Single place to add global options
- Consistent error handling

## Migration Guide

### Old Way → New Way

```bash
# Old individual commands
generate_news article.pdf
generate_outline paper.pdf  
any2md document.docx
html2md page.html

# New unified interface
editor-assistant news article.pdf
editor-assistant outline paper.pdf
editor-assistant convert document.docx  
editor-assistant clean page.html
```

### For Scripts/Automation

If you have scripts using the old commands, they'll continue to work. But for new scripts, prefer the unified interface:

```bash
#!/bin/bash
# Old style (still works)
generate_news "$1"

# New style (recommended)
editor-assistant news "$1" --debug
```

## Advanced Usage

### Batch Processing
```bash
# Process multiple research papers
editor-assistant outline paper1.pdf paper2.pdf paper3.pdf

# Convert all PDFs in directory
editor-assistant convert documents/*.pdf
```

### Pipeline Integration
```bash
# Use with other tools
find . -name "*.pdf" | xargs editor-assistant outline
curl -s "https://api.arxiv.org/paper.pdf" | editor-assistant news /dev/stdin
```

### Debug Mode
```bash
# Enable detailed logging for troubleshooting
editor-assistant news article.pdf --debug

# Check log files
ls logs/editor_assistant_*.log
```

This new structure provides a more professional, maintainable, and user-friendly CLI experience.