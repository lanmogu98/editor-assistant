"""
Repository for database CRUD operations.
"""

import sqlite3
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

from .database import get_connection, init_database, get_database_path


@dataclass
class RunRecord:
    """Represents a run record."""
    id: int
    timestamp: str
    task: str
    model: str
    thinking_level: Optional[str]
    stream: bool
    status: str
    error_message: Optional[str]


@dataclass
class InputRecord:
    """Represents an input record."""
    id: int
    type: str
    source_path: str
    title: str
    content_hash: str
    created_at: str


class RunRepository:
    """Repository for managing run history in SQLite."""
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize repository.
        
        Args:
            db_path: Optional custom database path
        """
        self.db_path = db_path or get_database_path()
        self._ensure_initialized()
    
    def _ensure_initialized(self) -> None:
        """Ensure database is initialized."""
        if not self.db_path.exists():
            init_database(self.db_path)
    
    def _get_conn(self) -> sqlite3.Connection:
        """Get database connection."""
        return get_connection(self.db_path)
    
    # =========================================================================
    # Input Operations
    # =========================================================================
    
    def get_or_create_input(
        self,
        input_type: str,
        source_path: str,
        title: str,
        content: str
    ) -> int:
        """
        Get existing input by content hash or create new one.
        
        Args:
            input_type: Type of input (paper, news)
            source_path: Source file path or URL
            title: Document title
            content: Full content for hashing
        
        Returns:
            Input ID
        """
        content_hash = self._hash_content(content)
        
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Try to find existing
        cursor.execute(
            "SELECT id FROM inputs WHERE content_hash = ?",
            (content_hash,)
        )
        row = cursor.fetchone()
        
        if row:
            conn.close()
            return row[0]
        
        # Create new
        cursor.execute(
            """INSERT INTO inputs (type, source_path, title, content_hash)
               VALUES (?, ?, ?, ?)""",
            (input_type, source_path, title, content_hash)
        )
        input_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return input_id
    
    def _hash_content(self, content: str) -> str:
        """Generate MD5 hash of content."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    # =========================================================================
    # Run Operations
    # =========================================================================
    
    def create_run(
        self,
        task: str,
        model: str,
        input_ids: List[int],
        thinking_level: Optional[str] = None,
        stream: bool = True,
        currency: str = "$"
    ) -> int:
        """
        Create a new run record.
        
        Args:
            task: Task name (brief, outline, translate)
            model: Model name
            input_ids: List of input IDs
            thinking_level: Optional thinking level
            stream: Whether streaming was used
            currency: Pricing currency symbol
        
        Returns:
            Run ID
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Create run
        cursor.execute(
            """INSERT INTO runs (task, model, thinking_level, stream, currency, status)
               VALUES (?, ?, ?, ?, ?, 'pending')""",
            (task, model, thinking_level, 1 if stream else 0, currency)
        )
        run_id = cursor.lastrowid
        
        # Link inputs
        for input_id in input_ids:
            cursor.execute(
                "INSERT INTO run_inputs (run_id, input_id) VALUES (?, ?)",
                (run_id, input_id)
            )
        
        conn.commit()
        conn.close()
        
        return run_id
    
    def update_run_status(
        self,
        run_id: int,
        status: str,
        error_message: Optional[str] = None
    ) -> None:
        """
        Update run status.
        
        Args:
            run_id: Run ID
            status: New status (success, failed)
            error_message: Optional error message
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute(
            "UPDATE runs SET status = ?, error_message = ? WHERE id = ?",
            (status, error_message, run_id)
        )
        
        conn.commit()
        conn.close()
    
    # =========================================================================
    # Output Operations
    # =========================================================================
    
    def add_output(
        self,
        run_id: int,
        output_type: str,
        content: str,
        content_type: str = "text"
    ) -> int:
        """
        Add output to a run.
        
        Args:
            run_id: Run ID
            output_type: Type of output (main, bilingual, classification)
            content: Output content
            content_type: Content type (text, json)
        
        Returns:
            Output ID
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO outputs (run_id, output_type, content_type, content)
               VALUES (?, ?, ?, ?)""",
            (run_id, output_type, content_type, content)
        )
        output_id = cursor.lastrowid
        
        conn.commit()
        conn.close()
        
        return output_id
    
    # =========================================================================
    # Token Usage Operations
    # =========================================================================
    
    def add_token_usage(
        self,
        run_id: int,
        input_tokens: int,
        output_tokens: int,
        cost_input: float,
        cost_output: float,
        process_time: float
    ) -> None:
        """
        Add token usage for a run.
        
        Args:
            run_id: Run ID
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            cost_input: Input cost
            cost_output: Output cost
            process_time: Processing time in seconds
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute(
            """INSERT INTO token_usage 
               (run_id, input_tokens, output_tokens, cost_input, cost_output, process_time)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (run_id, input_tokens, output_tokens, cost_input, cost_output, process_time)
        )
        
        conn.commit()
        conn.close()
    
    # =========================================================================
    # Query Operations
    # =========================================================================
    
    def get_recent_runs(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get recent runs.
        
        Args:
            limit: Maximum number of runs to return
        
        Returns:
            List of run records with input titles
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                r.id,
                r.timestamp,
                r.task,
                r.model,
                r.status,
                r.currency,
                GROUP_CONCAT(i.title, ', ') as input_titles,
                t.input_tokens,
                t.output_tokens,
                COALESCE(t.cost_input, 0) + COALESCE(t.cost_output, 0) as total_cost
            FROM runs r
            LEFT JOIN run_inputs ri ON r.id = ri.run_id
            LEFT JOIN inputs i ON ri.input_id = i.id
            LEFT JOIN token_usage t ON r.id = t.run_id
            GROUP BY r.id
            ORDER BY r.id DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_run_details(self, run_id: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a run.
        
        Args:
            run_id: Run ID
        
        Returns:
            Run details including inputs and outputs
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Get run info
        cursor.execute("SELECT * FROM runs WHERE id = ?", (run_id,))
        run_row = cursor.fetchone()
        if not run_row:
            conn.close()
            return None
        
        run = dict(run_row)
        
        # Get inputs
        cursor.execute("""
            SELECT i.* FROM inputs i
            JOIN run_inputs ri ON i.id = ri.input_id
            WHERE ri.run_id = ?
        """, (run_id,))
        run["inputs"] = [dict(row) for row in cursor.fetchall()]
        
        # Get outputs
        cursor.execute(
            "SELECT * FROM outputs WHERE run_id = ?",
            (run_id,)
        )
        run["outputs"] = [dict(row) for row in cursor.fetchall()]
        
        # Get token usage
        cursor.execute(
            "SELECT * FROM token_usage WHERE run_id = ?",
            (run_id,)
        )
        usage_row = cursor.fetchone()
        run["token_usage"] = dict(usage_row) if usage_row else None
        
        conn.close()
        return run
    
    def get_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        Get usage statistics.
        
        Args:
            days: Number of days to include
        
        Returns:
            Statistics dictionary
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Total runs
        cursor.execute("""
            SELECT COUNT(*) FROM runs 
            WHERE timestamp > datetime('now', ?)
        """, (f'-{days} days',))
        total_runs = cursor.fetchone()[0]
        
        # By model
        cursor.execute("""
            SELECT 
                r.model,
                COUNT(*) as runs,
                SUM(COALESCE(t.cost_input, 0) + COALESCE(t.cost_output, 0)) as total_cost,
                SUM(COALESCE(t.input_tokens, 0) + COALESCE(t.output_tokens, 0)) as total_tokens
            FROM runs r
            LEFT JOIN token_usage t ON r.id = t.run_id
            WHERE r.timestamp > datetime('now', ?)
            GROUP BY r.model
            ORDER BY runs DESC
        """, (f'-{days} days',))
        by_model = [dict(row) for row in cursor.fetchall()]
        
        # By task
        cursor.execute("""
            SELECT 
                r.task,
                COUNT(*) as runs
            FROM runs r
            WHERE r.timestamp > datetime('now', ?)
            GROUP BY r.task
            ORDER BY runs DESC
        """, (f'-{days} days',))
        by_task = [dict(row) for row in cursor.fetchall()]
        
        # Success rate
        cursor.execute("""
            SELECT 
                status,
                COUNT(*) as count
            FROM runs
            WHERE timestamp > datetime('now', ?)
            GROUP BY status
        """, (f'-{days} days',))
        by_status = {row[0]: row[1] for row in cursor.fetchall()}
        
        conn.close()
        
        return {
            "period_days": days,
            "total_runs": total_runs,
            "by_model": by_model,
            "by_task": by_task,
            "by_status": by_status,
            "success_rate": by_status.get("success", 0) / total_runs if total_runs > 0 else 0
        }
    
    def search_by_title(self, title_pattern: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search runs by input title.
        
        Args:
            title_pattern: Title pattern to search (supports SQL LIKE)
            limit: Maximum results
        
        Returns:
            List of matching runs
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT
                r.id,
                r.timestamp,
                r.task,
                r.model,
                r.status,
                i.title
            FROM runs r
            JOIN run_inputs ri ON r.id = ri.run_id
            JOIN inputs i ON ri.input_id = i.id
            WHERE i.title LIKE ?
            ORDER BY r.timestamp DESC
            LIMIT ?
        """, (f'%{title_pattern}%', limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in rows]
    
    # =========================================================================
    # Resume Operations
    # =========================================================================
    
    def get_resumable_runs(self) -> List[Dict[str, Any]]:
        """
        Get runs that can be resumed (status='pending' or 'aborted').
        
        Returns:
            List of resumable runs with their input information,
            ordered by timestamp (oldest first for resume priority)
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Get resumable runs
        cursor.execute("""
            SELECT 
                r.id,
                r.timestamp,
                r.task,
                r.model,
                r.thinking_level,
                r.stream,
                r.currency,
                r.status
            FROM runs r
            WHERE r.status IN ('pending', 'aborted')
            ORDER BY r.id ASC
        """)
        
        runs = []
        for row in cursor.fetchall():
            run = dict(row)
            run_id = run["id"]
            
            # Get inputs for this run
            cursor.execute("""
                SELECT i.id, i.type, i.source_path, i.title, i.content_hash
                FROM inputs i
                JOIN run_inputs ri ON i.id = ri.input_id
                WHERE ri.run_id = ?
            """, (run_id,))
            
            run["inputs"] = [dict(inp) for inp in cursor.fetchall()]
            runs.append(run)
        
        conn.close()
        return runs
    
    # =========================================================================
    # Export Operations
    # =========================================================================
    
    def export_runs(
        self,
        output_path: Path,
        format: str = "json",
        limit: Optional[int] = None
    ) -> None:
        """
        Export run history to file.
        
        Args:
            output_path: Path to output file
            format: Export format ('json' or 'csv')
            limit: Optional limit on number of runs to export
        """
        conn = self._get_conn()
        cursor = conn.cursor()
        
        # Get all runs
        query = """
            SELECT 
                r.id,
                r.timestamp,
                r.task,
                r.model,
                r.thinking_level,
                r.stream,
                r.currency,
                r.status,
                r.error_message
            FROM runs r
            ORDER BY r.id DESC
        """
        if limit:
            query += f" LIMIT {limit}"
        
        cursor.execute(query)
        
        runs = []
        for row in cursor.fetchall():
            run = dict(row)
            run_id = run["id"]
            
            # Get inputs
            cursor.execute("""
                SELECT i.id, i.type, i.source_path, i.title
                FROM inputs i
                JOIN run_inputs ri ON i.id = ri.input_id
                WHERE ri.run_id = ?
            """, (run_id,))
            run["inputs"] = [dict(inp) for inp in cursor.fetchall()]
            
            # Get outputs
            cursor.execute("""
                SELECT output_type, content_type, content
                FROM outputs
                WHERE run_id = ?
            """, (run_id,))
            run["outputs"] = [dict(out) for out in cursor.fetchall()]
            
            # Get token usage
            cursor.execute("""
                SELECT input_tokens, output_tokens, cost_input, cost_output, process_time
                FROM token_usage
                WHERE run_id = ?
            """, (run_id,))
            usage_row = cursor.fetchone()
            run["token_usage"] = dict(usage_row) if usage_row else None
            
            runs.append(run)
        
        conn.close()
        
        # Write to file
        if format == "json":
            self._export_json(output_path, runs)
        elif format == "csv":
            self._export_csv(output_path, runs)
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_json(self, output_path: Path, runs: List[Dict[str, Any]]) -> None:
        """Export runs to JSON file."""
        import json
        
        data = {
            "exported_at": datetime.now().isoformat(),
            "total_runs": len(runs),
            "runs": runs
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _export_csv(self, output_path: Path, runs: List[Dict[str, Any]]) -> None:
        """Export runs to CSV file."""
        import csv
        
        fieldnames = [
            "id", "timestamp", "task", "model", "thinking_level", 
            "stream", "currency", "status", "error_message",
            "input_titles", "input_tokens", "output_tokens", 
            "cost_input", "cost_output", "total_cost"
        ]
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for run in runs:
                # Flatten input titles
                input_titles = ", ".join(
                    inp.get("title", "") for inp in run.get("inputs", [])
                )
                
                # Get token usage
                usage = run.get("token_usage") or {}
                
                row = {
                    "id": run.get("id"),
                    "timestamp": run.get("timestamp"),
                    "task": run.get("task"),
                    "model": run.get("model"),
                    "thinking_level": run.get("thinking_level"),
                    "stream": run.get("stream"),
                    "currency": run.get("currency"),
                    "status": run.get("status"),
                    "error_message": run.get("error_message"),
                    "input_titles": input_titles,
                    "input_tokens": usage.get("input_tokens"),
                    "output_tokens": usage.get("output_tokens"),
                    "cost_input": usage.get("cost_input"),
                    "cost_output": usage.get("cost_output"),
                    "total_cost": (usage.get("cost_input") or 0) + (usage.get("cost_output") or 0)
                }
                writer.writerow(row)

