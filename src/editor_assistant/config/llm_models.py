"""Compatibility shim for extracted LLM model configuration."""

from pathlib import Path
from typing import Any

from llm_exec_core import config as _core_config
from llm_exec_core.config import get_model_details as _core_get_model_details

from .constants import LLM_CONFIG_PATH

ModelDetails = _core_config.ModelDetails
Pricing = _core_config.Pricing
ProviderSettings = _core_config.ProviderSettings
RateLimitSettings = _core_config.RateLimitSettings


def _resolve_config_source(
    config_source: Path | dict[str, Any] | None,
) -> Path | dict[str, Any]:
    if config_source is None:
        return LLM_CONFIG_PATH
    return config_source


def load_all_settings(
    config_source: Path | dict[str, Any] | None = None,
) -> dict[str, ProviderSettings]:
    return _core_config.load_all_settings(
        _resolve_config_source(config_source)
    )


def get_supported_models(
    config_source: Path | dict[str, Any] | None = None,
) -> list[str]:
    return _core_config.get_supported_models(
        _resolve_config_source(config_source)
    )


def get_provider_settings(
    provider_name: str,
    config_source: Path | dict[str, Any] | None = None,
) -> ProviderSettings:
    return _core_config.get_provider_settings(
        provider_name, _resolve_config_source(config_source)
    )


def get_model_details(
    model_name: str,
    config_source: Path | dict[str, Any] | None = None,
) -> tuple[ProviderSettings, ModelDetails]:
    _, provider_settings, model_details = _core_get_model_details(
        model_name, _resolve_config_source(config_source)
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
