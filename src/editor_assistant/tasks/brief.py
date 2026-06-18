"""
Brief Task - Generate short news from research papers.
"""

from typing import List, Dict
from .base import Task, TaskRegistry
from ..data_models import MDArticle
from ..config.load_prompt import load_news_generator_prompt


@TaskRegistry.register("brief")
class BriefTask(Task):
    """Generate brief news articles from one or more research sources."""
    
    name = "brief"
    description = "Generate brief news from research papers and articles"
    supports_multi_input = True
    
    def validate(self, articles: List[MDArticle]) -> tuple[bool, str]:
        if not articles:
            return False, "At least one article is required"
        return True, ""
    
    def build_prompt(self, articles: List[MDArticle]) -> str:
        return load_news_generator_prompt(articles=articles)
    
    def post_process(self, response: str, articles: List[MDArticle]) -> Dict[str, str]:
        # Brief task only produces the main output
        return {"main": response}

