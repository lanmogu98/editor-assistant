# This file contains the data models for the project.

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Literal, Mapping, Optional, TypeAlias

from llm_exec_core import LLMResult
from pydantic import BaseModel, ConfigDict

JSONValue: TypeAlias = (
    None
    | bool
    | int
    | float
    | str
    | list["JSONValue"]
    | dict[str, "JSONValue"]
)


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

    OUTLINE = "outline"  # outline the research paper
    BRIEF = "brief"  # generate brief news from the input content
    TRANSLATE = "translate"  # translate the outline to Chinese


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

    model_config = ConfigDict(arbitrary_types_allowed=True)  # Allow Path type


@dataclass(slots=True)
class OutputArtifact:
    """A typed task output and its stable serialized representation."""

    value: str | JSONValue
    content_type: Literal["text/plain", "application/json"]
    serialized_text: str


@dataclass(slots=True)
class TaskExecutionResult:
    """Successful task execution with Editor and core result metadata."""

    task_name: str
    run_id: int
    outputs: Mapping[str, OutputArtifact]
    llm_result: LLMResult


class SaveType(str, Enum):
    """
    Type of content to save.
    """

    PROMPT = "prompt"
    RESPONSE = "response"
