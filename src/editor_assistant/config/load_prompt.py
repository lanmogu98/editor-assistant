"""
Simplified Prompt Template Loader

Utility for loading and rendering prompt templates from external files.
Uses Jinja2 for template rendering with support for variables and logic.
Supports user-customizable prompts in ~/.editor_assistant/prompts/
"""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# Prompt files
RESEARCH_OUTLINER_PROMPT_FILE = "research_outliner.txt"
NEWS_GENERATOR_PROMPT_FILE = "news_generator.txt"
TRANSLATOR_PROMPT_FILE = "translator.txt"

class PromptLoader:
    """Loads and renders prompt templates from user config or fallback to source."""
    
    def __init__(self):
        self.prompts_dir = Path(__file__).parent / "prompts"
        
        # Create Jinja2 environment
        self.env = None
        
        if self.prompts_dir.exists():
            self.env = Environment(
                loader=FileSystemLoader(str(self.prompts_dir)),
                trim_blocks=True,
                lstrip_blocks=True
            )
    
    def render(self, template_name: str, **kwargs) -> str:
        """Load and render a template with the provided variables."""
        # Try user template first, fallback to source template
        try:
            if self.env:
                template = self.env.get_template(template_name)
                return template.render(**kwargs)
        except:
            raise FileNotFoundError(f"Template '{template_name}' not found in prompt directories")

# Global loader instance
_loader = PromptLoader()

# Simplified convenience functions
def load_research_outliner_prompt(**kwargs) -> str:
    """Load research outliner prompt with fallback system."""
    return _loader.render(RESEARCH_OUTLINER_PROMPT_FILE, **kwargs)

def load_news_generator_prompt(**kwargs) -> str:
    """Load news generator prompt with fallback system."""
    return _loader.render(NEWS_GENERATOR_PROMPT_FILE, **kwargs)

def load_translation_prompt(**kwargs) -> str:
    """Load translation prompt with fallback system."""
    return _loader.render(TRANSLATOR_PROMPT_FILE, **kwargs)


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