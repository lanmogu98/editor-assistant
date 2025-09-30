import yaml
from pathlib import Path
from pydantic import BaseModel
from enum import Enum
from typing import Dict, Tuple, Optional, Any


# --- LLMModel and ServiceProvider enums as a single source of truth of model switch ---
class LLMModel(str, Enum):
    # deepseek
    deepseek_v3_1 = "deepseek-v3.1"
    deepseek_r1 = "deepseek-r1"
    deepseek_v3 = "deepseek-v3"
    deepseek_v3_2 = "deepseek-v3.2"
    # gemini
    gemini_2_5_flash = "gemini-2.5-flash"
    gemini_2_5_pro = "gemini-2.5-pro"
    kimi_k2 = "kimi-k2"
    # qwen
    qwen_plus = "qwen-plus"
    qwen3_max_preview = "qwen3-max-preview"
    qwen3_max = "qwen3-max"
    # zhipu
    glm_4_5 = "glm-4.5"
    glm_4_6 = "glm-4.6"
    glm_4_5_openrouter = "glm-4.5-or"
    # doubao
    doubao_seed_1_6 = "doubao-seed-1.6"
    # openai
    gpt_5_openrouter = "gpt-5-or"
    gpt_4o_openrouter = "gpt-4o-or"
    gpt_4_1_openrouter = "gpt-4.1-or"
    # anthropic
    claude_sonnet_4_openrouter = "claude-sonnet-4-or"


class ServiceProvider(str, Enum):
    # volcengine
    kimi_volcengine = "kimi-volcengine" 
    deepseek_volcengine = "deepseek-volcengine" 
    doubao = "doubao"
    # google cloud
    gemini = "gemini"
    # alibaba 
    qwen = "qwen"
    # zhipu 
    zhipu = "zhipu"
    # openrouter
    zhipu_openrouter = "zhipu-openrouter"
    openai_openrouter = "openai-openrouter"
    anthropic_openrouter = "anthropic-openrouter"
    # deepseek
    deepseek = "deepseek"

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
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    context_window: Optional[int] = None
    pricing_currency: str
    models: Dict[LLMModel, ModelDetails]
    # provider specific overrides
    request_overrides: Optional[Dict[str, Any]] = None


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
            for k, v in config_data.items() if not k.startswith("_")
            }


# --- Programmatically build mappings from the single source of truth ---
ALL_PROVIDER_SETTINGS = load_all_settings()

# flattened map for easy access to any model's full details
ALL_MODEL_DETAILS: Dict[LLMModel, Tuple[ProviderSettings, ModelDetails]] = {
    model: (settings, model_details)
    for _, settings in ALL_PROVIDER_SETTINGS.items()
    for model, model_details in settings.models.items()
}
