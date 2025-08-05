# Python Logging Module Basics

## Introduction

Python's `logging` module is like a newspaper publishing system. Understanding its core components will help you work with any logging system, including our custom one.

## Core Architecture

```text
Logger → Handler → Formatter → Output
  ↓         ↓          ↓         ↓
Writer   Editor   Layout    Newspaper
```

### The Four Main Components

1. **Logger**: Creates messages (like a writer)
2. **Handler**: Decides where messages go (like an editor)
3. **Formatter**: Decides how messages look (like layout designer)
4. **Record**: The complete message package (like an article)

## 1. Logger - The Message Creator

```python
import logging

# Create a logger
logger = logging.getLogger('my_app')

# Create messages at different levels
logger.debug('Detailed info for debugging')
logger.info('General information')  
logger.warning('Something unexpected happened')
logger.error('Something went wrong')
logger.critical('Very serious error')
```

### Logger Hierarchy

```python
# Loggers form a hierarchy like folders
logger1 = logging.getLogger('myapp')           # Parent
logger2 = logging.getLogger('myapp.database')  # Child
logger3 = logging.getLogger('myapp.network')   # Child

# Child loggers inherit from parents
```

### Log Levels (in order of severity)

| Level    | Numeric Value | When to Use |
|----------|---------------|-------------|
| DEBUG    | 10           | Detailed diagnostic info |
| INFO     | 20           | General information |
| WARNING  | 30           | Something unexpected |
| ERROR    | 40           | Serious problem |
| CRITICAL | 50           | Very serious error |

## 2. Handler - Where Messages Go

```python
import sys
import logging

# Console handler (prints to terminal)
console_handler = logging.StreamHandler(sys.stdout)

# File handler (saves to file)
file_handler = logging.FileHandler('app.log')

# Add handlers to logger
logger = logging.getLogger('my_app')
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Now messages go to BOTH console AND file
logger.info("This appears in both places")
```

### Common Handler Types

```python
# Console output
logging.StreamHandler()                    # stdout
logging.StreamHandler(sys.stderr)          # stderr

# File output
logging.FileHandler('app.log')             # Basic file
logging.RotatingFileHandler('app.log')     # Rotates when too big
logging.TimedRotatingFileHandler('app.log') # Rotates daily/weekly

# Network
logging.handlers.SMTPHandler()             # Email alerts
logging.handlers.HTTPHandler()             # Web services
```

## 3. Formatter - How Messages Look

```python
# Create a formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Apply to handler
handler.setFormatter(formatter)

# Output: "2025-07-30 15:30:45 - my_app - INFO - Hello world"
```

### Common Format Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `%(asctime)s` | Timestamp | `2025-07-30 15:30:45` |
| `%(name)s` | Logger name | `my_app` |
| `%(levelname)s` | Log level | `INFO` |
| `%(message)s` | The message | `Hello world` |
| `%(filename)s` | File name | `main.py` |
| `%(lineno)d` | Line number | `42` |
| `%(funcName)s` | Function name | `process_data` |

## 4. LogRecord - The Message Package

```python
# When you call logger.info("Hello"), Python creates:
record = logging.LogRecord(
    name='my_app',           # Logger name
    level=logging.INFO,      # 20
    pathname='/path/file.py', # Full file path
    lineno=42,              # Line number
    msg='Hello',            # Your message
    args=(),                # Message arguments
    exc_info=None,          # Exception info
    func='main',            # Function name
    created=1690735845.123  # Timestamp
)
```

### Accessing Record Data

```python
class MyFormatter(logging.Formatter):
    def format(self, record):
        # Access any record attribute
        timestamp = record.created
        level = record.levelname  
        message = record.getMessage()
        logger_name = record.name
        
        return f"[{level}] {message}"
```

## Complete Flow Example

```python
import logging
import sys

# 1. Create logger
logger = logging.getLogger('example')

# 2. Create handler
handler = logging.StreamHandler(sys.stdout)

# 3. Create formatter  
formatter = logging.Formatter('%(levelname)s: %(message)s')

# 4. Connect them
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# 5. Use it
logger.info("Hello world")
# Output: "INFO: Hello world"
```

## Advanced Concepts

### Custom Formatter Class

```python
class ColoredFormatter(logging.Formatter):
    """Add colors to log messages."""
    
    COLORS = {
        'ERROR': '\033[31m',    # Red
        'WARNING': '\033[33m',  # Yellow
        'INFO': '\033[32m',     # Green
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        # Get the original formatted message
        message = super().format(record)
        
        # Add color
        color = self.COLORS.get(record.levelname, '')
        reset = self.COLORS['RESET']
        
        return f"{color}{message}{reset}"

# Usage
formatter = ColoredFormatter('%(levelname)s: %(message)s')
handler.setFormatter(formatter)
```

### Inheritance Explained

```python
# logging.Formatter is the parent class
class ColoredFormatter(logging.Formatter):
    # We inherit all methods and override format()
    def format(self, record):
        # Our custom logic here
        return "Custom: " + record.getMessage()

# Python will use OUR format() method instead of the default
```

### Multiple Handlers with Different Formats

```python
logger = logging.getLogger('app')

# Console: Clean format for users
console_handler = logging.StreamHandler()
console_formatter = logging.Formatter('%(message)s')
console_handler.setFormatter(console_formatter)

# File: Detailed format for debugging
file_handler = logging.FileHandler('debug.log')
file_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
)
file_handler.setFormatter(file_formatter)

# Add both
logger.addHandler(console_handler) 
logger.addHandler(file_handler)

# One message, two different outputs!
logger.info("Processing complete")

# Console shows: "Processing complete"
# File gets: "2025-07-30 15:30:45 - app - INFO - main.py:25 - Processing complete"
```

### Filter by Level

```python
# Set minimum level for logger
logger.setLevel(logging.WARNING)  # Only WARNING and above

# Set different levels for different handlers
console_handler.setLevel(logging.INFO)    # Show INFO+ on console
file_handler.setLevel(logging.DEBUG)      # Show DEBUG+ in file
```

## Best Practices

### 1. Use Appropriate Levels

```python
logger.debug("Loop iteration %d", i)           # Detailed tracing
logger.info("Processing file %s", filename)    # User information  
logger.warning("Config file not found")        # Unexpected but ok
logger.error("Failed to save %s", filename)    # Definite problem
logger.critical("Database unavailable")        # System failure
```

### 2. Use Logger Hierarchy

```python
# Good structure
main_logger = logging.getLogger('myapp')
db_logger = logging.getLogger('myapp.database')  
net_logger = logging.getLogger('myapp.network')

# Configure once at root
main_logger.setLevel(logging.INFO)
# Children inherit the configuration
```

### 3. Lazy String Formatting

```python
# Good - only formats if message will be shown
logger.debug("Processing %s with %d items", filename, count)

# Bad - always creates string even if debug is off
logger.debug(f"Processing {filename} with {count} items")
```

## Common Patterns

### Basic Setup

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),           # Console
        logging.FileHandler('app.log')     # File
    ]
)

logger = logging.getLogger(__name__)
```

### Class-based Logging

```python
class MyClass:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def process(self):
        self.logger.info("Starting process")
        try:
            # ... work ...
            self.logger.info("Process complete")
        except Exception as e:
            self.logger.error("Process failed: %s", str(e))
```

This foundation will help you understand any logging system, including the custom one we built for this project!