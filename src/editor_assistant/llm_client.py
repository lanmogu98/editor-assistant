"""Compatibility wrapper for the extracted LLM client."""

from pathlib import Path
from typing import Any

import httpx  # noqa: F401

from llm_exec_core import (
    ExecutionMetadata,
    LLMResult,
    StructuredOutputValidationError,
    TokenUsage,
)
from llm_exec_core.client import LLMClient as _CoreLLMClient
from llm_exec_core.client import ResponseCache

from .config.llm_models import _resolve_config_source, get_supported_models


class LLMClient(_CoreLLMClient):
    """Core client defaulting to Editor Assistant's packaged catalog."""

    @staticmethod
    def get_supported_models(
        config_source: Path | dict[str, Any] | None = None,
    ) -> list[str]:
        return get_supported_models(config_source)

    def __init__(
        self,
        model_name: str,
        thinking_level: str | None = None,
        config_source: Path | dict[str, Any] | None = None,
    ) -> None:
        super().__init__(
            model_name,
            thinking_level=thinking_level,
            config_source=_resolve_config_source(config_source),
        )


__all__ = [
    "ExecutionMetadata",
    "LLMClient",
    "LLMResult",
    "ResponseCache",
    "StructuredOutputValidationError",
    "TokenUsage",
]
