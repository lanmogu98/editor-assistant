"""
User configuration management for Editor Assistant.

Handles user-editable configuration files outside the source code to prevent
accidental modifications to the system files.
"""

try:
    from .logging_config import user_message
except ImportError:
    # Fallback for when logging_config is not available
    def user_message(msg):
        print(msg)
import shutil
import yaml
from pathlib import Path
from typing import Dict, Any


class UserConfigManager:
    """Manages user configuration files in a dedicated directory."""
    
    def __init__(self):
        # User config directory in home folder
        self.user_config_dir = Path.home() / ".editor_assistant"
        self.user_prompts_dir = self.user_config_dir / "user_prompts"
        self.user_llm_config_file = self.user_config_dir / "user_llm_config.yml"
        
        # Source config directory (read-only templates)
        self.source_config_dir = Path(__file__).parent
        self.source_prompts_dir = self.source_config_dir / "prompts"
        self.source_llm_config_file = self.source_config_dir / "llm_config.yml"
        
        # Initialize user config if needed
        self._initialize_user_config()
    
    def _initialize_user_config(self):
        """Initialize user configuration directory with default files."""
        if not self.user_config_dir.exists():
            user_message(f"🔧 Creating user configuration directory: {self.user_config_dir}")
            self.user_config_dir.mkdir(parents=True, exist_ok=True)
            self.user_prompts_dir.mkdir(exist_ok=True)
            
            # Copy default prompts to user directory
            if self.source_prompts_dir.exists():
                for prompt_file in self.source_prompts_dir.glob("*.txt"):
                    user_prompt_file = self.user_prompts_dir / prompt_file.name
                    if not user_prompt_file.exists():
                        shutil.copy2(prompt_file, user_prompt_file)
                        user_message(f"📝 Copied prompt template: {prompt_file.name}")
            
            # Copy default config to user directory
            if self.source_llm_config_file.exists():
                if not self.user_llm_config_file.exists():
                    shutil.copy2(self.source_llm_config_file, self.user_llm_config_file)
                    user_message(f"⚙️ Copied configuration template: user_llm_config.yml")
            
            user_message(f"✅ User configuration initialized at: {self.user_config_dir}")
            user_message(f"📝 Edit prompts in: {self.user_prompts_dir}")
            user_message(f"⚙️ Edit model config in: {self.user_llm_config_file}")
    
    def get_prompt_path(self, prompt_name: str) -> Path:
        """Get path to user's prompt file, falling back to source if not found."""
        user_prompt = self.user_prompts_dir / f"{prompt_name}.txt"
        source_prompt = self.source_prompts_dir / f"{prompt_name}.txt"
        
        if user_prompt.exists():
            return user_prompt
        elif source_prompt.exists():
            return source_prompt
        else:
            raise FileNotFoundError(f"Prompt template '{prompt_name}' not found")
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Load user configuration, falling back to source config."""
        llm_config_file = self.user_llm_config_file if self.user_llm_config_file.exists() else self.source_llm_config_file
        
        with open(llm_config_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def list_available_models(self) -> Dict[str, Any]:
        """List all available models from user configuration."""
        config = self.get_llm_config()
        models = {}
        
        for provider_name, provider_config in config.items():
            if isinstance(provider_config, dict) and 'models' in provider_config:
                for model_name, model_config in provider_config['models'].items():
                    models[model_name] = {
                        'provider': provider_name,
                        'id': model_config.get('id', model_name),
                        'pricing': model_config.get('pricing', {}),
                        'context_window': provider_config.get('context_window', None),
                        'max_tokens': provider_config.get('max_tokens', None)
                    }
        
        return models
    
    def add_custom_model(self, provider: str, model_name: str, max_tokens: int, 
                         context_window: int, model_config: Dict[str, Any]):
        """Add a custom model to user configuration."""
        config = self.get_llm_config()
        
        if provider not in config:
            config[provider] = {
                'api_key_env_var': f"{provider.upper()}_API_KEY",
                'temperature': 0.5,
                'max_tokens': max_tokens,
                'context_window': context_window,
                'models': {}
            }
        
        if 'models' not in config[provider]:
            config[provider]['models'] = {}
        
        config[provider]['models'][model_name] = model_config
        
        # Save to user config file
        with open(self.user_llm_config_file, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)
        
        user_message(f"✅ Added custom model '{model_name}' to provider '{provider}':")
        user_message(f"  • Max tokens: {max_tokens}")
        user_message(f"  • Context window: {context_window}")
        user_message(f"  • Pricing: {model_config.get('pricing', {})}")
    
    def show_config_location(self):
        """Show user where their configuration files are located."""
        user_message("\n📂 Editor Assistant Configuration:")
        user_message(f"  📁 Config Directory: {self.user_config_dir}")
        user_message(f"  ⚙️  Model Config: {self.user_llm_config_file}")
        user_message(f"  📝 Prompts Directory: {self.user_prompts_dir}")
        
        if self.user_prompts_dir.exists():
            user_message(f"  📝 Available Prompts:")
            for prompt_file in self.user_prompts_dir.glob("*.txt"):
                user_message(f"     • {prompt_file.name}")
        
        user_message(f"\n💡 Tips:")
        user_message(f"  • Edit prompts to customize AI behavior")
        user_message(f"  • Add models to config.yml to try different LLMs")
        user_message(f"  • Changes take effect immediately")


# Global instance
user_config = UserConfigManager()