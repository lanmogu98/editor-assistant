"""
Centralized constants for Editor Assistant.

This module contains all configurable constants used throughout the app.
Keeping them in one place makes tuning easier and documents assumptions.
"""

import logging
from pathlib import Path

from llm_exec_core import constants as _core_constants

LLM_CONFIG_PATH = Path(__file__).with_name("llm_config.yml")

API_REQUEST_TIMEOUT_SECONDS = _core_constants.API_REQUEST_TIMEOUT_SECONDS
CHAR_TOKEN_RATIO = _core_constants.CHAR_TOKEN_RATIO
CHAR_TOKEN_RATIO_EN = _core_constants.CHAR_TOKEN_RATIO_EN
CHAR_TOKEN_RATIO_ZH = _core_constants.CHAR_TOKEN_RATIO_ZH
INITIAL_RETRY_DELAY_SECONDS = _core_constants.INITIAL_RETRY_DELAY_SECONDS
MAX_API_RETRIES = _core_constants.MAX_API_RETRIES
MAX_REQUESTS_PER_MINUTE = _core_constants.MAX_REQUESTS_PER_MINUTE
MIN_REQUEST_INTERVAL_SECONDS = _core_constants.MIN_REQUEST_INTERVAL_SECONDS
RATE_LIMIT_WARNINGS_ENABLED = _core_constants.RATE_LIMIT_WARNINGS_ENABLED
RESPONSE_CACHE_ENABLED = _core_constants.RESPONSE_CACHE_ENABLED
RESPONSE_CACHE_MAX_SIZE = _core_constants.RESPONSE_CACHE_MAX_SIZE
RESPONSE_CACHE_TTL_SECONDS = _core_constants.RESPONSE_CACHE_TTL_SECONDS

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

__all__ = [
    "LLM_CONFIG_PATH",
    "API_REQUEST_TIMEOUT_SECONDS",
    "CHAR_TOKEN_RATIO",
    "CHAR_TOKEN_RATIO_EN",
    "CHAR_TOKEN_RATIO_ZH",
    "INITIAL_RETRY_DELAY_SECONDS",
    "MAX_API_RETRIES",
    "MAX_REQUESTS_PER_MINUTE",
    "MIN_REQUEST_INTERVAL_SECONDS",
    "RATE_LIMIT_WARNINGS_ENABLED",
    "RESPONSE_CACHE_ENABLED",
    "RESPONSE_CACHE_MAX_SIZE",
    "RESPONSE_CACHE_TTL_SECONDS",
    "MINIMAL_TOKEN_ACCEPTED",
    "PROMPT_OVERHEAD_TOKENS",
    "OUTPUT_TOKEN_RESERVE",
    "MIN_CHARS_WARNING_THRESHOLD",
    "DEFAULT_LOGGING_LEVEL",
    "DEBUG_LOGGING_LEVEL",
    "DEFAULT_USER_AGENT",
    "URL_HEAD_TIMEOUT_SECONDS",
]
