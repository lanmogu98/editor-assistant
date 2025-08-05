# Editor Assistant Logging System Manual

## Overview

This project uses a centralized logging system that provides clean console output for users while maintaining detailed file logs for debugging. The system is designed to be simple to use but powerful when troubleshooting is needed.

## Key Features

- **Clean Console Output**: Beautiful colored messages with symbols
- **Optional Debug Mode**: Detailed file logging when needed
- **Centralized Configuration**: All logging setup in one place
- **Multiple Output Types**: Console and file logging simultaneously

## Architecture

The logging system consists of three main components:

### 1. ColoredFormatter Class
- **Location**: `src/editor_assistant/config/logging_config.py`
- **Purpose**: Creates beautiful console output with colors and symbols
- **Symbols Used**:
  - ✗ for errors (red)
  - ⚠ for warnings (yellow) 
  - • for info messages (green)
  - Raw messages (no symbols for clean output)

### 2. setup_logging() Function
- **Purpose**: Initializes the entire logging system
- **Two Modes**:
  - **Normal Mode** (default): Clean console output only
  - **Debug Mode**: Console + detailed file logging

### 3. Helper Functions
- `progress(message)`: Shows progress with • symbol
- `error(message)`: Shows errors with ✗ symbol
- `warning(message)`: Shows warnings with ⚠ symbol
- `user_message(message)`: Clean output without symbols

## Usage Guide

### Basic Usage

```python
from .config.logging_config import setup_logging, progress, error, warning, user_message

# Initialize logging (usually in __init__)
setup_logging()

# Use throughout your code
progress("Processing files...")        # • Processing files...
error("Something went wrong")          # ✗ Something went wrong  
warning("Be careful")                  # ⚠ Be careful
user_message("Clean output")           # Clean output
```

### Debug Mode

Enable debug mode in **3 ways**:

#### Method 1: In Code
```python
setup_logging(debug_mode=True)
```

#### Method 2: Environment Variable
```bash
export EDITOR_ASSISTANT_DEBUG=1
# or
export EDITOR_ASSISTANT_DEBUG=true
# or  
export EDITOR_ASSISTANT_DEBUG=yes
```

#### Method 3: Class Constructor
```python
EditorAssistant(model_name, debug_mode=True)
```

### What Debug Mode Does

**When ON**:
- Creates `logs/` folder in project root
- Saves detailed logs to timestamped files like `editor_assistant_20250730_152710.log`
- Shows all DEBUG level messages
- Console shows: "Debug logging enabled: /path/to/logfile.log"

**When OFF**:
- Only shows INFO level and above
- No files created
- Cleaner, faster experience

## File Structure

```
project_root/
├── src/editor_assistant/config/logging_config.py  # Main logging code
├── logs/                                          # Created when debug=True
│   ├── editor_assistant_20250730_152710.log     # Timestamped log files
│   └── editor_assistant_20250730_153245.log
└── docs/logging_system_manual.md                 # This file
```

## Customization Guide

### Adding New Message Types

```python
def success(message: str):
    """Log a success message with checkmark."""
    logger = logging.getLogger('success')
    logger.info(message)
```

### Changing Colors

Modify the `COLORS` dictionary in `ColoredFormatter`:

```python
COLORS = {
    'DEBUG': '\033[36m',     # Cyan
    'INFO': '\033[34m',      # Blue (changed from green)
    'WARNING': '\033[33m',   # Yellow
    'ERROR': '\033[31m',     # Red
    'CRITICAL': '\033[35m',  # Magenta
    'RESET': '\033[0m'       # Reset
}
```

### Adding New Symbols

Modify the `format()` method in `ColoredFormatter`:

```python
def format(self, record):
    # ... existing code ...
    elif record.levelname == 'INFO':
        return f"{color}→ {record.getMessage()}{reset}"  # Changed from •
```

### Custom Log Levels

```python
def critical(message: str):
    """Log a critical message."""
    logger = logging.getLogger('critical')
    logger.critical(message)

def debug(message: str):
    """Log a debug message (only shows in debug mode)."""
    logger = logging.getLogger('debug')
    logger.debug(message)
```

## Integration Examples

### In Main Classes

```python
class EditorAssistant:
    def __init__(self, model_name, debug_mode=False):
        setup_logging(debug_mode)  # Initialize first
        self.logger = logging.getLogger(__name__)
        progress(f"Initialized with {model_name}")
```

### In Processing Functions

```python
def process_document(self, path):
    progress(f"Processing {path}")
    try:
        # ... processing logic ...
        progress("Processing complete")
    except Exception as e:
        error(f"Failed to process {path}: {str(e)}")
        return False
```

## Troubleshooting

### Common Issues

1. **No colored output**: Check if terminal supports ANSI colors
2. **Debug files not created**: Ensure write permissions in project directory
3. **Too much output**: Disable debug mode for cleaner experience

### Debug Mode Benefits

- **Full context**: See all internal operations
- **Timestamps**: Know exactly when things happened  
- **File persistence**: Logs survive program crashes
- **Multiple sessions**: Each run gets its own timestamped file

## Migration from Old System

If you have old logging code:

```python
# Old way
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Message")

# New way
from .config.logging_config import setup_logging, progress
setup_logging()
progress("Message")
```

The new system provides cleaner output and better user experience while maintaining all debugging capabilities when needed.