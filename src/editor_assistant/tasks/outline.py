"""
Outline Task - Generate research paper outlines.
"""

from typing import List, Dict
from .base import Task, TaskRegistry
from ..data_models import MDArticle
from ..config.load_prompt import load_research_outliner_prompt


@TaskRegistry.register("outline")
class OutlineTask(Task):
    """Generate detailed research outline from a single paper."""
    
    name = "outline"
    description = "Generate structured research outline with Chinese translation"
    supports_multi_input = False
    
    def validate(self, articles: List[MDArticle]) -> tuple[bool, str]:
        if len(articles) != 1:
            return False, "Outline requires exactly one article"
        return True, ""
    
    def build_prompt(self, articles: List[MDArticle]) -> str:
        return load_research_outliner_prompt(content=articles[0].content)
    
    def post_process(self, response: str, articles: List[MDArticle]) -> Dict[str, str]:
        return {"main": response}

