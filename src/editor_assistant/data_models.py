# This file contains the data models for the project.

from pydantic import BaseModel
from typing import Optional
from enum import Enum
from pathlib import Path


# for the input source data
class InputType(str, Enum):
    """
    The type of source.
    """
    PAPER = "paper"
    NEWS = "news"

# class for the input source
class Input(BaseModel):
    """
    The type of input source.
    """
    type: InputType
    path: str

# for the process type
class ProcessType(str, Enum):
    """
    Type of process to perform on the markdown content.
    """
    OUTLINE = 'outline' # outline the research paper
    BRIEF = 'brief' # generate brief news from the input content
    TRANSLATE = 'translate' # translate the outline to Chinese

# for the converted markdown article, the output of the markdown converter
class MDArticle(BaseModel):
    """
    A structure for a converted markdown article.
    """
    type: InputType
    content: Optional[str] = None
    title: Optional[str] = None
    authors: Optional[str] = None
    converter: Optional[str] = None
    source_path: Optional[str] = None
    output_path: Optional[Path] = None

    class Config:
        arbitrary_types_allowed = True  # Allow Path type


class SaveType(str, Enum):
    """
    Type of content to save.
    """
    PROMPT = "prompt"
    RESPONSE = "response"
