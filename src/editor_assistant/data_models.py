# This file contains the data models for the project.

from pydantic import BaseModel
from typing import Optional

# for the converted markdown article
class MDArticle(BaseModel):
    """
    A structure for a converted markdown article.
    """
    markdown_content: str
    title: str
    authors: Optional[str] = None
    converter: str
    source_path: str


