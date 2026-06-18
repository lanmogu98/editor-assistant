"""
Task Registry and Base Classes

Provides a pluggable task system for extending Editor Assistant with new task types.
"""

from .base import Task, TaskRegistry
from .brief import BriefTask
from .outline import OutlineTask
from .translate import TranslateTask

__all__ = [
    "Task",
    "TaskRegistry",
    "BriefTask",
    "OutlineTask", 
    "TranslateTask",
]

