"""
Base Task class and TaskRegistry for pluggable task system.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Type, Optional
from ..data_models import MDArticle


class TaskRegistry:
    """
    Registry for task types. Tasks register themselves using the @register decorator.
    
    Usage:
        @TaskRegistry.register("my-task")
        class MyTask(Task):
            ...
    """
    _tasks: Dict[str, Type["Task"]] = {}
    
    @classmethod
    def register(cls, name: str):
        """Decorator to register a task class."""
        def decorator(task_cls: Type["Task"]):
            cls._tasks[name] = task_cls
            return task_cls
        return decorator
    
    @classmethod
    def get(cls, name: str) -> Optional[Type["Task"]]:
        """Get a task class by name."""
        return cls._tasks.get(name)
    
    @classmethod
    def list_tasks(cls) -> List[str]:
        """List all registered task names."""
        return list(cls._tasks.keys())
    
    @classmethod
    def get_all(cls) -> Dict[str, Type["Task"]]:
        """Get all registered tasks."""
        return cls._tasks.copy()


class Task(ABC):
    """
    Abstract base class for all tasks.
    
    Subclasses must implement:
        - validate(): Check if inputs are valid for this task
        - build_prompt(): Generate the LLM prompt
    
    Optionally override:
        - post_process(): Transform the LLM response
        - get_output_suffix(): Custom output file suffix
    """
    
    # Task metadata (override in subclasses)
    name: str = "base"
    description: str = "Base task"
    supports_multi_input: bool = False
    
    @abstractmethod
    def validate(self, articles: List[MDArticle]) -> tuple[bool, str]:
        """
        Validate input articles for this task.
        
        Args:
            articles: List of MDArticle objects
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass
    
    @abstractmethod
    def build_prompt(self, articles: List[MDArticle]) -> str:
        """
        Build the LLM prompt for this task.
        
        Args:
            articles: List of MDArticle objects
            
        Returns:
            The prompt string
        """
        pass
    
    def post_process(self, response: str, articles: List[MDArticle]) -> Dict[str, str]:
        """
        Post-process the LLM response.
        
        Override this method to generate additional outputs (e.g., bilingual version).
        
        Args:
            response: The raw LLM response
            articles: The input articles
            
        Returns:
            Dict mapping output_name -> content
            Default returns {"main": response}
        """
        return {"main": response}
    
    def get_output_suffix(self) -> str:
        """
        Get the output file suffix for this task.
        
        Returns:
            Suffix string (e.g., "_brief", "_outline")
        """
        return f"_{self.name}"

