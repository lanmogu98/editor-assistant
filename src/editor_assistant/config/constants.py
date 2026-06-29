"""
Centralized constants for Editor Assistant.

This module contains all configurable constants used throughout the app.
Keeping them in one place makes tuning easier and documents assumptions.
"""

import logging

from llm_exec_core.constants import API_REQUEST_TIMEOUT_SECONDS
from llm_exec_core.constants import CHAR_TOKEN_RATIO
from llm_exec_core.constants import CHAR_TOKEN_RATIO_EN
from llm_exec_core.constants import CHAR_TOKEN_RATIO_ZH
from llm_exec_core.constants import INITIAL_RETRY_DELAY_SECONDS
from llm_exec_core.constants import MAX_API_RETRIES
from llm_exec_core.constants import MAX_REQUESTS_PER_MINUTE
from llm_exec_core.constants import MIN_REQUEST_INTERVAL_SECONDS
from llm_exec_core.constants import RATE_LIMIT_WARNINGS_ENABLED
from llm_exec_core.constants import RESPONSE_CACHE_ENABLED
from llm_exec_core.constants import RESPONSE_CACHE_MAX_SIZE
from llm_exec_core.constants import RESPONSE_CACHE_TTL_SECONDS

# =============================================================================
# TOKEN ESTIMATION
# =============================================================================

# Minimum token count for valid input content.
# Content below this threshold is likely malformed or empty.
MINIMAL_TOKEN_ACCEPTED = 100

# Token buffer reserved for prompt template overhead.
# This accounts for system prompts, formatting, and response structure.
PROMPT_OVERHEAD_TOKENS = 10000

# Default token reserve for model output when context budgeting.
OUTPUT_TOKEN_RESERVE = 2000


# =============================================================================
# API RETRY CONFIGURATION
# =============================================================================

# =============================================================================
# CONTENT VALIDATION
# =============================================================================

# Character count threshold below which a warning is shown.
# Documents smaller than this may be incomplete or malformed.
MIN_CHARS_WARNING_THRESHOLD = 1000


# =============================================================================
# LOGGING
# =============================================================================

# Default logging level for modules.
# Set to DEBUG for development, INFO for production.
DEFAULT_LOGGING_LEVEL = logging.INFO

# Logging level for detailed debugging (when --debug flag is used).
DEBUG_LOGGING_LEVEL = logging.DEBUG


# =============================================================================
# HTTP CONFIGURATION
# =============================================================================

# Default User-Agent header for HTTP requests.
# Mimics a real browser to avoid being blocked by websites.
DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

# Timeout for HTTP HEAD requests (URL content-type detection).
URL_HEAD_TIMEOUT_SECONDS = 10
