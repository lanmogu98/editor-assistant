"""
Simplified Prompt Template Loader

Utility for loading and rendering prompt templates from external files.
Uses Jinja2 for template rendering with support for variables and logic.
Supports user-customizable prompts in ~/.editor_assistant/prompts/
"""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from .user_config import user_config

class PromptLoader:
    """Loads and renders prompt templates from user config or fallback to source."""
    
    def __init__(self):
        # Use user config manager to get prompt directory
        self.user_prompts_dir = user_config.user_prompts_dir
        self.source_prompts_dir = Path(__file__).parent / "prompts"
        
        # Create Jinja2 environments for both directories
        self.user_env = None
        self.source_env = None
        
        if self.user_prompts_dir.exists():
            self.user_env = Environment(
                loader=FileSystemLoader(str(self.user_prompts_dir)),
                trim_blocks=True,
                lstrip_blocks=True
            )
        
        if self.source_prompts_dir.exists():
            self.source_env = Environment(
                loader=FileSystemLoader(str(self.source_prompts_dir)),
                trim_blocks=True,
                lstrip_blocks=True
            )
    
    def render(self, template_name: str, **kwargs) -> str:
        """Load and render a template with the provided variables."""
        # Try user template first, fallback to source template
        try:
            if self.user_env:
                template = self.user_env.get_template(template_name)
                return template.render(**kwargs)
        except:
            pass
        
        if self.source_env:
            template = self.source_env.get_template(template_name)
            return template.render(**kwargs)
        
        raise FileNotFoundError(f"Template '{template_name}' not found in user or source directories")

# Global loader instance
_loader = PromptLoader()

# Simplified convenience functions
def load_research_outliner_prompt(**kwargs) -> str:
    """Load research outliner prompt with fallback system."""
    return _loader.render("research_outliner.txt", **kwargs)

def load_news_generator_prompt(**kwargs) -> str:
    """Load news generator prompt with fallback system."""
    return _loader.render("news_generator.txt", **kwargs)

def load_translation_prompt(**kwargs) -> str:
    """Load translation prompt with fallback system."""
    return _loader.render("translator.txt", **kwargs)


if __name__ == "__main__":
    # Test rendering a template
    try:
        rendered = load_translation_prompt(
            content="Research content here",
            title="Research title here"
        )
        print(f"Test render successful. Length: {len(rendered)} characters")
    except Exception as e:
        print(f"Test render failed: {e}") 