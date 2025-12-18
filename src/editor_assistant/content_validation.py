"""
Two-stage content validation system.

This implements a clean, practical validation approach:
1. First check: Is this a blocked publisher? → Hard stop
2. Second check: Is content too short? → Warning with preview

This design is user-friendly - blocks known bad sources but lets users
decide on borderline content.
"""

from typing import Optional, Tuple
from .config.constants import MIN_CHARS_WARNING_THRESHOLD
from .config.logging_config import warning, error


# Known blocked publishers/sources that don't allow scraping or have paywalls
BLOCKED_PUBLISHERS = [
    "nytimes.com",
    "wsj.com",
    "ft.com",
    "bloomberg.com",
    "economist.com",
    "washingtonpost.com",
]


class ContentValidationError(Exception):
    """Base exception for content validation errors."""
    pass


class BlockedPublisherError(ContentValidationError):
    """Raised when content is from a blocked publisher."""
    pass


class ContentTooShortWarning(ContentValidationError):
    """Raised when content is suspiciously short."""
    pass


def is_blocked_publisher(url: str) -> bool:
    """
    Check if a URL is from a known blocked publisher.

    Args:
        url: The URL to check

    Returns:
        True if the URL is from a blocked publisher
    """
    url_lower = url.lower()
    return any(publisher in url_lower for publisher in BLOCKED_PUBLISHERS)


def validate_content_source(url: str) -> None:
    """
    Validate that a content source is allowed.

    Args:
        url: The URL to validate

    Raises:
        BlockedPublisherError: If the URL is from a blocked publisher
    """
    if is_blocked_publisher(url):
        raise BlockedPublisherError(
            f"Content from this publisher is blocked: {url}. "
            "This site may have paywalls or restrict scraping."
        )


def validate_content_length(
    content: str,
    source: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Check if content length is acceptable.

    Args:
        content: The content to validate
        source: Optional source identifier for the warning message

    Returns:
        Tuple of (is_valid, warning_message)
        - is_valid: True if content passes validation
        - warning_message: Warning message if content is short, None otherwise
    """
    if not content:
        return False, "Content is empty"

    char_count = len(content)

    if char_count < MIN_CHARS_WARNING_THRESHOLD:
        source_info = f" from {source}" if source else ""
        warning_msg = (
            f"Content{source_info} is short ({char_count} chars, "
            f"threshold: {MIN_CHARS_WARNING_THRESHOLD}). "
            "This may indicate incomplete extraction."
        )
        return True, warning_msg  # Still valid, but with warning

    return True, None


def validate_content(
    content: str,
    source_url: Optional[str] = None,
    check_publisher: bool = True,
    check_length: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Perform full content validation.

    Args:
        content: The content to validate
        source_url: Optional URL of the content source
        check_publisher: Whether to check for blocked publishers
        check_length: Whether to check content length

    Returns:
        Tuple of (is_valid, message)

    Raises:
        BlockedPublisherError: If source is from a blocked publisher
    """
    # Stage 1: Check blocked publishers (hard stop)
    if check_publisher and source_url:
        validate_content_source(source_url)

    # Stage 2: Check content length (warning only)
    if check_length:
        is_valid, warning_msg = validate_content_length(content, source_url)
        if warning_msg:
            warning(warning_msg)
        return is_valid, warning_msg

    return True, None


def get_blocked_publishers() -> list:
    """Return the list of blocked publishers."""
    return BLOCKED_PUBLISHERS.copy()


def add_blocked_publisher(domain: str) -> None:
    """
    Add a publisher to the blocked list.

    Args:
        domain: The domain to block (e.g., "example.com")
    """
    domain_lower = domain.lower()
    if domain_lower not in BLOCKED_PUBLISHERS:
        BLOCKED_PUBLISHERS.append(domain_lower)


def remove_blocked_publisher(domain: str) -> bool:
    """
    Remove a publisher from the blocked list.

    Args:
        domain: The domain to unblock

    Returns:
        True if the domain was removed, False if it wasn't in the list
    """
    domain_lower = domain.lower()
    if domain_lower in BLOCKED_PUBLISHERS:
        BLOCKED_PUBLISHERS.remove(domain_lower)
        return True
    return False
