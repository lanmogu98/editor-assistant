"""
Unit tests for content validation utilities.
"""

import pytest

from editor_assistant.content_validation import (
    is_blocked_publisher,
    validate_content,
    validate_content_length,
    BlockedPublisherError,
    add_blocked_publisher,
    remove_blocked_publisher,
    get_blocked_publishers,
)


@pytest.mark.unit
def test_is_blocked_publisher_detects_known_domain():
    assert is_blocked_publisher("https://www.nytimes.com/") is True
    assert is_blocked_publisher("https://example.com/") is False


@pytest.mark.unit
def test_validate_content_blocks_known_publisher():
    with pytest.raises(BlockedPublisherError):
        validate_content("content", source_url="https://www.nytimes.com/article")


@pytest.mark.unit
def test_validate_content_length_warning_for_short_text():
    is_valid, warning_msg = validate_content_length("short text", source=None)
    assert is_valid is True
    assert warning_msg is not None
    assert "short" in warning_msg.lower()


@pytest.mark.unit
def test_validate_content_length_handles_empty():
    is_valid, warning_msg = validate_content_length("", source="https://example.com")
    assert is_valid is False
    assert "empty" in warning_msg.lower()


@pytest.mark.unit
def test_add_and_remove_blocked_publisher_round_trip():
    domain = "example-blocked.com"
    try:
        add_blocked_publisher(domain)
        assert domain in get_blocked_publishers()
    finally:
        removed = remove_blocked_publisher(domain)
        assert removed is True
        assert domain not in get_blocked_publishers()
"""
Unit tests for content validation utilities.
"""

import pytest

from editor_assistant.content_validation import (
    is_blocked_publisher,
    validate_content,
    validate_content_length,
    BlockedPublisherError,
    add_blocked_publisher,
    remove_blocked_publisher,
    get_blocked_publishers,
)


@pytest.mark.unit
def test_is_blocked_publisher_detects_known_domain():
    assert is_blocked_publisher("https://www.nytimes.com/") is True
    assert is_blocked_publisher("https://example.com/") is False


@pytest.mark.unit
def test_validate_content_blocks_known_publisher():
    with pytest.raises(BlockedPublisherError):
        validate_content("content", source_url="https://www.nytimes.com/article")


@pytest.mark.unit
def test_validate_content_length_warning_for_short_text():
    is_valid, warning_msg = validate_content_length("short text", source=None)
    assert is_valid is True
    assert warning_msg is not None
    assert "short" in warning_msg.lower()


@pytest.mark.unit
def test_validate_content_length_handles_empty():
    is_valid, warning_msg = validate_content_length("", source="https://example.com")
    assert is_valid is False
    assert "empty" in warning_msg.lower()


@pytest.mark.unit
def test_add_and_remove_blocked_publisher_round_trip():
    domain = "example-blocked.com"
    try:
        add_blocked_publisher(domain)
        assert domain in get_blocked_publishers()
    finally:
        removed = remove_blocked_publisher(domain)
        assert removed is True
        assert domain not in get_blocked_publishers()

