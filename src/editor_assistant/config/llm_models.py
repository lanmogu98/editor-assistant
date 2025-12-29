"""
LLM Configuration Loader.

Single Source of Truth: llm_config.yml
All model and provider metadata is defined in the YAML file.
This module dynamically loads and exposes the configuration.
"""

import yaml
from pathlib import Path
from pydantic import BaseModel
from typing import Dict, Tuple, Optional, Any, List


# =============================================================================
# Pydantic Models for YAML Structure Validation
# =============================================================================

class Pricing(BaseModel):
    input: float
    output: float


class ModelDetails(BaseModel):
    id: str  # The actual model ID for the API call
    pricing: Pricing


class RateLimitSettings(BaseModel):
    """Per-provider rate limiting configuration."""
    min_interval_seconds: float = 0.5  # Minimum time between requests
    max_requests_per_minute: int = 60  # Max requests per minute (0 = unlimited)


class ProviderSettings(BaseModel):
    api_key_env_var: str
    api_base_url: str
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    context_window: Optional[int] = None
    pricing_currency: str
    models: Dict[str, ModelDetails]  # model_name -> details
    request_overrides: Optional[Dict[str, Any]] = None
    rate_limit: Optional[RateLimitSettings] = None


# =============================================================================
# Configuration Loader (Single Source of Truth)
# =============================================================================

def _get_config_path() -> Path:
    """Get path to llm_config.yml."""
    return Path(__file__).parent / "llm_config.yml"


def load_all_settings() -> Dict[str, ProviderSettings]:
    """
    Load all provider settings from llm_config.yml.
    
    Returns:
        Dict mapping provider_name -> ProviderSettings
    """
    config_path = _get_config_path()
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")

    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)
    
    # Skip keys starting with "_" (shared anchors like _shared_endpoints)
    return {
        provider_name: ProviderSettings(**provider_data) 
        for provider_name, provider_data in config_data.items() 
        if not provider_name.startswith("_")
    }


# =============================================================================
# Module-Level Caches (Loaded Once at Import)
# =============================================================================

# All provider settings: provider_name -> ProviderSettings
ALL_PROVIDER_SETTINGS: Dict[str, ProviderSettings] = load_all_settings()

# Flattened model lookup: model_name -> (ProviderSettings, ModelDetails)
ALL_MODEL_DETAILS: Dict[str, Tuple[ProviderSettings, ModelDetails]] = {
    model_name: (settings, model_details)
    for settings in ALL_PROVIDER_SETTINGS.values()
    for model_name, model_details in settings.models.items()
}

# List of all available model names (for CLI choices)
ALL_MODEL_NAMES: List[str] = list(ALL_MODEL_DETAILS.keys())

# List of all provider names
ALL_PROVIDER_NAMES: List[str] = list(ALL_PROVIDER_SETTINGS.keys())


# =============================================================================
# Public API
# =============================================================================

def get_supported_models() -> List[str]:
    """Return list of all supported model names."""
    return ALL_MODEL_NAMES


def get_model_details(model_name: str) -> Tuple[ProviderSettings, ModelDetails]:
    """
    Get provider settings and model details for a given model name.
    
    Args:
        model_name: The model name as defined in llm_config.yml
        
    Returns:
        Tuple of (ProviderSettings, ModelDetails)
        
    Raises:
        ValueError: If model_name is not found
    """
    if model_name not in ALL_MODEL_DETAILS:
        raise ValueError(
            f"Model '{model_name}' not found. "
            f"Available models: {', '.join(ALL_MODEL_NAMES)}"
        )
    return ALL_MODEL_DETAILS[model_name]


def get_provider_settings(provider_name: str) -> ProviderSettings:
    """
    Get settings for a provider.
    
    Args:
        provider_name: The provider name as defined in llm_config.yml
        
    Returns:
        ProviderSettings
        
    Raises:
        ValueError: If provider_name is not found
    """
    if provider_name not in ALL_PROVIDER_SETTINGS:
        raise ValueError(
            f"Provider '{provider_name}' not found. "
            f"Available providers: {', '.join(ALL_PROVIDER_NAMES)}"
        )
    return ALL_PROVIDER_SETTINGS[provider_name]
