"""Compatibility shim for extracted LLM model configuration."""

from pathlib import Path
from typing import Any

from llm_exec_core import config as _core_config
from llm_exec_core.config import get_model_details as _core_get_model_details

ModelDetails = _core_config.ModelDetails
Pricing = _core_config.Pricing
ProviderSettings = _core_config.ProviderSettings
RateLimitSettings = _core_config.RateLimitSettings
get_provider_settings = _core_config.get_provider_settings
get_supported_models = _core_config.get_supported_models
load_all_settings = _core_config.load_all_settings


def get_model_details(
    model_name: str,
    config_source: Path | dict[str, Any] | None = None,
) -> tuple[ProviderSettings, ModelDetails]:
    _, provider_settings, model_details = _core_get_model_details(
        model_name, config_source
    )
    return provider_settings, model_details


__all__ = [
    "ModelDetails",
    "Pricing",
    "ProviderSettings",
    "RateLimitSettings",
    "get_model_details",
    "get_provider_settings",
    "get_supported_models",
    "load_all_settings",
]
