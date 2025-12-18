"""
Centralized constants for Editor Assistant.

This module contains all configurable constants used throughout the application.
Keeping them in one place makes tuning easier and documents assumptions.
"""

import logging

# =============================================================================
# TOKEN ESTIMATION
# =============================================================================

# Conservative character-to-token ratio for estimating token counts.
# Different LLMs have different tokenizers, so this is an approximation.
# Lower values are more conservative (assume more tokens per character).
CHAR_TOKEN_RATIO = 3.5

# Minimum token count for valid input content.
# Content below this threshold is likely malformed or empty.
MINIMAL_TOKEN_ACCEPTED = 100

# Token buffer reserved for prompt template overhead.
# This accounts for system prompts, formatting, and response structure.
PROMPT_OVERHEAD_TOKENS = 10000


# =============================================================================
# API RETRY CONFIGURATION
# =============================================================================

# Maximum number of retry attempts for API calls.
MAX_API_RETRIES = 3

# Initial delay (in seconds) before first retry.
# Subsequent retries use exponential backoff (delay * 2^attempt).
INITIAL_RETRY_DELAY_SECONDS = 1


# =============================================================================
# RATE LIMITING
# =============================================================================

# Minimum interval between API requests (in seconds).
# This prevents hitting per-second rate limits.
MIN_REQUEST_INTERVAL_SECONDS = 0.5

# Maximum requests per minute (per client instance).
# Set to 0 to disable per-minute limiting.
MAX_REQUESTS_PER_MINUTE = 60

# Enable rate limit warning messages.
RATE_LIMIT_WARNINGS_ENABLED = True


# =============================================================================
# RESPONSE CACHING
# =============================================================================

# Enable response caching for identical prompts.
# When enabled, identical prompts return cached responses without API calls.
RESPONSE_CACHE_ENABLED = False

# Maximum number of cached responses (LRU eviction when exceeded).
RESPONSE_CACHE_MAX_SIZE = 100

# Cache entry time-to-live in seconds (0 = no expiration).
RESPONSE_CACHE_TTL_SECONDS = 3600  # 1 hour


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
