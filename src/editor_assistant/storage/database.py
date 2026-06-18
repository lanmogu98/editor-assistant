"""
Database initialization and connection management.
"""

import sqlite3
from pathlib import Path
from typing import Optional
import os

# Default database location
DEFAULT_DB_DIR = Path.home() / ".editor_assistant"
DEFAULT_DB_NAME = "runs.db"

# Schema version for migrations
SCHEMA_VERSION = 1


def get_database_path() -> Path:
    """
    Get the database file path, creating directory if needed.
    
    Environment variables (checked in order):
    1. EDITOR_ASSISTANT_TEST_DB_DIR - For testing (highest priority)
    2. EDITOR_ASSISTANT_DB_DIR - For production override
    3. Default: ~/.editor_assistant/runs.db
    """
    # Test environment takes priority
    test_db_dir = os.getenv("EDITOR_ASSISTANT_TEST_DB_DIR")
    if test_db_dir:
        db_dir = Path(test_db_dir)
        db_dir.mkdir(parents=True, exist_ok=True)
        return db_dir / DEFAULT_DB_NAME
    
    # Production: explicit override or default
    db_dir = Path(os.getenv("EDITOR_ASSISTANT_DB_DIR", DEFAULT_DB_DIR))
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / DEFAULT_DB_NAME


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Get a database connection.
    
    Args:
        db_path: Optional custom database path. Uses default if not provided.
    
    Returns:
        SQLite connection with row factory enabled
    """
    if db_path is None:
        db_path = get_database_path()
    
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row  # Enable dict-like access
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
    return conn


def init_database(db_path: Optional[Path] = None) -> None:
    """
    Initialize the database with schema.
    
    Args:
        db_path: Optional custom database path
    """
    conn = get_connection(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.executescript(SCHEMA)
    
    # Set schema version
    cursor.execute(
        "INSERT OR REPLACE INTO schema_version (id, version) VALUES (1, ?)",
        (SCHEMA_VERSION,)
    )
    
    conn.commit()
    conn.close()


# Database schema
SCHEMA = """
-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_version (
    id INTEGER PRIMARY KEY,
    version INTEGER NOT NULL
);

-- Inputs table (independent, supports deduplication)
CREATE TABLE IF NOT EXISTS inputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    type TEXT NOT NULL,                     -- paper, news
    source_path TEXT,
    title TEXT,
    content_hash TEXT UNIQUE,               -- MD5 for deduplication
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Runs table
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    task TEXT NOT NULL,                     -- brief, outline, translate
    model TEXT NOT NULL,                    -- deepseek-v3.2, gemini-3-flash
    thinking_level TEXT,                    -- low, medium, high, null
    stream INTEGER DEFAULT 1,               -- 0 or 1
    currency TEXT DEFAULT '$',              -- pricing currency symbol
    status TEXT DEFAULT 'pending',          -- pending, success, failed
    error_message TEXT
);

-- Run-Input association (many-to-many)
CREATE TABLE IF NOT EXISTS run_inputs (
    run_id INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    input_id INTEGER NOT NULL REFERENCES inputs(id) ON DELETE CASCADE,
    PRIMARY KEY (run_id, input_id)
);

-- Outputs table
CREATE TABLE IF NOT EXISTS outputs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    output_type TEXT NOT NULL,              -- main, bilingual, classification
    content_type TEXT DEFAULT 'text',       -- text, json
    content TEXT
);

-- Token usage table
CREATE TABLE IF NOT EXISTS token_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    cost_input REAL DEFAULT 0,
    cost_output REAL DEFAULT 0,
    process_time REAL DEFAULT 0
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_runs_timestamp ON runs(timestamp);
CREATE INDEX IF NOT EXISTS idx_runs_model ON runs(model);
CREATE INDEX IF NOT EXISTS idx_runs_task ON runs(task);
CREATE INDEX IF NOT EXISTS idx_inputs_hash ON inputs(content_hash);
CREATE INDEX IF NOT EXISTS idx_outputs_run ON outputs(run_id);
"""


def get_schema_version(conn: sqlite3.Connection) -> int:
    """Get current schema version."""
    try:
        cursor = conn.execute("SELECT version FROM schema_version WHERE id = 1")
        row = cursor.fetchone()
        return row[0] if row else 0
    except sqlite3.OperationalError:
        return 0

