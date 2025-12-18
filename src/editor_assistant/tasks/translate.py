"""
Translate Task - Generate Chinese translation with bilingual output.
"""

from typing import List, Dict
from .base import Task, TaskRegistry
from ..data_models import MDArticle
from ..config.load_prompt import load_translation_prompt
from ..config.logging_config import warning


@TaskRegistry.register("translate")
class TranslateTask(Task):
    """Generate Chinese translation with optional bilingual side-by-side output."""
    
    name = "translate"
    description = "Translate content to Chinese with bilingual output"
    supports_multi_input = False
    
    def validate(self, articles: List[MDArticle]) -> tuple[bool, str]:
        if len(articles) != 1:
            return False, "Translate requires exactly one article"
        return True, ""
    
    def build_prompt(self, articles: List[MDArticle]) -> str:
        return load_translation_prompt(content=articles[0].content)
    
    def post_process(self, response: str, articles: List[MDArticle]) -> Dict[str, str]:
        """Generate both Chinese-only and bilingual versions."""
        outputs = {"main": response}
        
        # Create bilingual content
        try:
            bilingual = self._create_bilingual_content(
                articles[0].content, 
                response
            )
            outputs["bilingual"] = bilingual
        except Exception as e:
            warning(f"Could not create bilingual output: {e}")
        
        return outputs
    
    def _create_bilingual_content(self, source: str, translated: str) -> str:
        """Create bilingual markdown with alternating source/translation lines."""
        source_lines = source.strip().split("\n")
        trans_lines = translated.strip().split("\n")
        
        bilingual_lines = []
        for i in range(len(source_lines)):
            bilingual_lines.append(source_lines[i])
            if i < len(trans_lines):
                bilingual_lines.append(trans_lines[i])
            else:
                warning(f"Line count mismatch at line {i}: source has {len(source_lines)}, translation has {len(trans_lines)}")
                break
        
        return "\n".join(bilingual_lines) + "\n"

