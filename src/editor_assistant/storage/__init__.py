"""
Storage module for SQLite-based run history tracking.

This module provides:
- Database initialization and connection management
- CRUD operations for runs, inputs, outputs, and token usage
- Query interface for history and statistics
"""

from .database import get_database_path, init_database, get_connection
from .repository import RunRepository

__all__ = [
    "get_database_path",
    "init_database", 
    "get_connection",
    "RunRepository",
]

