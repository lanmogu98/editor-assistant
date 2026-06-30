"""Compatibility shim for the extracted LLM client."""

from typing import TYPE_CHECKING
import sys

if TYPE_CHECKING:
    from llm_exec_core.client import LLMClient  # noqa: F401
else:
    import llm_exec_core.client as _client

    sys.modules[__name__] = _client
