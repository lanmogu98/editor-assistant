import yaml
from pathlib import Path
from pydantic import BaseModel
from enum import Enum
from typing import Dict, Tuple


# --- LLMModel and ServiceProvider enums as a single source of truth of model switch ---
class LLMModel(str, Enum):
    deepseek_r1 = "deepseek-r1"
    deepseek_r1_latest = "deepseek-r1-latest"
    deepseek_v3 = "deepseek-v3"
    deepseek_v3_latest = "deepseek-v3-latest"
    gemini_2_5_flash = "gemini-2.5-flash"
    gemini_2_5_pro = "gemini-2.5-pro"
    gemini_2_5_flash_lite = "gemini-2.5-flash-lite"

class ServiceProvider(str, Enum):
    deepseek = "deepseek"
    gemini = "gemini"

# --- Pydantic Models for the configing of YAML structure ---
class Pricing(BaseModel):
    input: float
    output: float

class ModelDetails(BaseModel):
    id: str  # The actual model ID for the API call
    pricing: Pricing

class ProviderSettings(BaseModel):
    api_key_env_var: str
    api_base_url: str
    temperature: float
    max_tokens: int
    context_window: int
    pricing_currency: str
    models: Dict[LLMModel, ModelDetails]


# --- Function to load the single config file ---
def load_all_settings() -> Dict[ServiceProvider, ProviderSettings]:
    """Loads all provider settings from the single llm_config.yml file."""
    config_path = Path(__file__).parent / "llm_config.yml"
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")

    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)
    
    # Pydantic validates the entire structure at once
    return {ServiceProvider(k): ProviderSettings(**v) 
            for k, v in config_data.items()}


# --- Programmatically build mappings from the single source of truth ---
ALL_PROVIDER_SETTINGS = load_all_settings()

# flattened map for easy access to any model's full details
ALL_MODEL_DETAILS: Dict[LLMModel, Tuple[ProviderSettings, ModelDetails]] = {
    model: (settings, model_details)
    for _, settings in ALL_PROVIDER_SETTINGS.items()
    for model, model_details in settings.models.items()
}
