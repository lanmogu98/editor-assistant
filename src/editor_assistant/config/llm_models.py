"""Compatibility shim for extracted LLM model configuration."""

from pathlib import Path
from typing import Any

from llm_exec_core.config import ModelDetails
from llm_exec_core.config import Pricing
from llm_exec_core.config import ProviderSettings
from llm_exec_core.config import RateLimitSettings
from llm_exec_core.config import get_model_details as _core_get_model_details
from llm_exec_core.config import get_provider_settings
from llm_exec_core.config import get_supported_models
from llm_exec_core.config import load_all_settings


def get_model_details(
    model_name: str,
    config_source: Path | dict[str, Any] | None = None,
) -> tuple[ProviderSettings, ModelDetails]:
    _, provider_settings, model_details = _core_get_model_details(
        model_name, config_source
    )
    return provider_settings, model_details
