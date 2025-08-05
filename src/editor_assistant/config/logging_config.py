"""
Centralized logging configuration for editor_assistant.

Provides clean console output for users while maintaining detailed file logs for debugging.
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
import os

class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green  
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
        'RESET': '\033[0m'       # Reset
    }
    
    def format(self, record):
        if hasattr(record, '_raw_message'):
            return record._raw_message
        
        color = self.COLORS.get(record.levelname, '')
        reset = self.COLORS['RESET']
        
        if record.levelname in ['ERROR', 'CRITICAL']:
            return f"{color}✗ {record.getMessage()}{reset}"
        elif record.levelname == 'WARNING':
            return f"{color}⚠ {record.getMessage()}{reset}"
        elif record.levelname == 'INFO':
            return f"{color}• {record.getMessage()}{reset}"
        else:
            return f"{color}{record.getMessage()}{reset}"

def setup_logging(debug_mode: bool = False):
    """
    Set up centralized logging configuration.
    
    Args:
        debug_mode: Enable debug logging to file. If None, checks EDITOR_ASSISTANT_DEBUG env var.
    """
    
    # Determine debug mode
    if debug_mode == False:
        debug_mode = os.getenv('EDITOR_ASSISTANT_DEBUG', '').lower() in ('1', 'true', 'yes')

    # Clear any existing handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    
    # Console handler - clean output for users
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(ColoredFormatter())
    
    # Configure root logger
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.INFO)
    
    # File handler for debugging (optional)
    if debug_mode:
        logs_dir = Path.cwd() / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = logs_dir / f"editor_assistant_{timestamp}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        )
        
        root_logger.addHandler(file_handler)
        root_logger.setLevel(logging.DEBUG)
        
        # Notify user about debug logging
        record = logging.LogRecord(
            name='setup', level=logging.INFO, pathname='', lineno=0,
            msg='', args=(), exc_info=None
        )
        record._raw_message = f"Debug logging enabled: {log_file}"
        console_handler.handle(record)

def user_message(message: str):
    """Log a clean message for users without level indicators."""
    logger = logging.getLogger('user')
    record = logging.LogRecord(
        name='user', level=logging.INFO, pathname='', lineno=0,
        msg='', args=(), exc_info=None
    )
    record._raw_message = message
    logger.handle(record)

def progress(message: str):
    """Log a progress message with clean formatting."""
    logger = logging.getLogger('progress')
    logger.info(message)

def error(message: str):
    """Log an error message."""
    logger = logging.getLogger('error')
    logger.error(message)

def warning(message: str):
    """Log a warning message."""
    logger = logging.getLogger('warning')
    logger.warning(message)