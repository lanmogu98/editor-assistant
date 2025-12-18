"""
Unit tests for the storage module.

Tests database initialization, CRUD operations, and query functions.
"""

import pytest
import os
import threading

from editor_assistant.storage.database import (
    init_database,
    get_connection,
    get_database_path,
    SCHEMA_VERSION,
)
from editor_assistant.storage.repository import RunRepository


class TestDatabaseInitialization:
    """Tests for database initialization and schema."""
    
    def test_init_creates_database(self, temp_dir):
        """Database file should be created on init."""
        db_path = temp_dir / "test.db"
        assert not db_path.exists()
        
        init_database(db_path)
        
        assert db_path.exists()
    
    def test_init_creates_all_tables(self, temp_dir):
        """All required tables should be created."""
        db_path = temp_dir / "test.db"
        init_database(db_path)
        
        conn = get_connection(db_path)
        cursor = conn.cursor()
        
        # Check all tables exist
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' ORDER BY name
        """)
        tables = {row[0] for row in cursor.fetchall()}
        
        expected_tables = {
            'schema_version',
            'inputs',
            'runs',
            'run_inputs',
            'outputs',
            'token_usage'
        }
        assert expected_tables.issubset(tables)
        
        conn.close()
    
    def test_schema_version_set(self, temp_dir):
        """Schema version should be set after init."""
        db_path = temp_dir / "test.db"
        init_database(db_path)
        
        conn = get_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT version FROM schema_version WHERE id = 1")
        version = cursor.fetchone()[0]
        conn.close()
        
        assert version == SCHEMA_VERSION
    
    def test_init_idempotent(self, temp_dir):
        """Multiple init calls should not fail."""
        db_path = temp_dir / "test.db"
        
        init_database(db_path)
        init_database(db_path)  # Should not raise
        
        # Data should still be intact
        conn = get_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM schema_version")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 1
    
    def test_foreign_keys_enabled(self, temp_dir):
        """Foreign key constraints should be enabled."""
        db_path = temp_dir / "test.db"
        init_database(db_path)
        
        conn = get_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys")
        fk_enabled = cursor.fetchone()[0]
        conn.close()
        
        assert fk_enabled == 1


class TestRunRepository:
    """Tests for RunRepository CRUD operations."""
    
    @pytest.fixture
    def repo(self, temp_dir):
        """Create a repository with a temp database."""
        db_path = temp_dir / "test.db"
        return RunRepository(db_path=db_path)
    
    # =========================================================================
    # Input Operations
    # =========================================================================
    
    def test_get_or_create_input_creates_new(self, repo):
        """Should create new input if not exists."""
        input_id = repo.get_or_create_input(
            input_type="paper",
            source_path="/path/to/paper.pdf",
            title="Test Paper",
            content="This is the content"
        )
        
        assert input_id > 0
    
    def test_get_or_create_input_returns_existing(self, repo):
        """Should return existing input if content hash matches."""
        content = "Same content for both calls"
        
        id1 = repo.get_or_create_input("paper", "/path1.pdf", "Title 1", content)
        id2 = repo.get_or_create_input("paper", "/path2.pdf", "Title 2", content)
        
        assert id1 == id2  # Same content = same ID
    
    def test_content_hash_deduplication(self, repo):
        """Different content should create different inputs."""
        id1 = repo.get_or_create_input("paper", "/p1.pdf", "T1", "Content A")
        id2 = repo.get_or_create_input("paper", "/p2.pdf", "T2", "Content B")
        
        assert id1 != id2
    
    def test_input_preserves_metadata(self, repo):
        """First call's metadata should be preserved."""
        content = "Shared content"
        
        repo.get_or_create_input("paper", "/first.pdf", "First Title", content)
        
        # Second call with different metadata
        input_id = repo.get_or_create_input("news", "/second.md", "Second Title", content)
        
        # Verify original metadata is preserved
        conn = repo._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT type, source_path, title FROM inputs WHERE id = ?", (input_id,))
        row = cursor.fetchone()
        conn.close()
        
        assert row[0] == "paper"  # Original type preserved
        assert row[1] == "/first.pdf"  # Original path preserved
        assert row[2] == "First Title"  # Original title preserved
    
    # =========================================================================
    # Run Operations
    # =========================================================================
    
    def test_create_run_basic(self, repo):
        """Should create a run with basic fields."""
        input_id = repo.get_or_create_input("paper", "/p.pdf", "Title", "Content")
        
        run_id = repo.create_run(
            task="brief",
            model="deepseek-v3.2",
            input_ids=[input_id]
        )
        
        assert run_id > 0
    
    def test_create_run_with_all_options(self, repo):
        """Should create run with all optional fields."""
        input_id = repo.get_or_create_input("paper", "/p.pdf", "Title", "Content")
        
        run_id = repo.create_run(
            task="outline",
            model="gemini-3-flash",
            input_ids=[input_id],
            thinking_level="high",
            stream=False,
            currency="¥"
        )
        
        # Verify all fields
        conn = repo._get_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT task, model, thinking_level, stream, currency, status 
            FROM runs WHERE id = ?
        """, (run_id,))
        row = cursor.fetchone()
        conn.close()
        
        assert row[0] == "outline"
        assert row[1] == "gemini-3-flash"
        assert row[2] == "high"
        assert row[3] == 0  # stream=False
        assert row[4] == "¥"
        assert row[5] == "pending"
    
    def test_create_run_links_multiple_inputs(self, repo):
        """Should link multiple inputs to one run."""
        id1 = repo.get_or_create_input("paper", "/p1.pdf", "Paper", "Paper content")
        id2 = repo.get_or_create_input("news", "/n1.md", "News", "News content")
        
        run_id = repo.create_run(
            task="brief",
            model="test-model",
            input_ids=[id1, id2]
        )
        
        # Verify both inputs linked
        conn = repo._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM run_inputs WHERE run_id = ?", (run_id,))
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 2
    
    def test_update_run_status_success(self, repo):
        """Should update run status to success."""
        input_id = repo.get_or_create_input("paper", "/p.pdf", "T", "C")
        run_id = repo.create_run("brief", "model", [input_id])
        
        repo.update_run_status(run_id, "success")
        
        details = repo.get_run_details(run_id)
        assert details["status"] == "success"
    
    def test_update_run_status_failed_with_error(self, repo):
        """Should update run status with error message."""
        input_id = repo.get_or_create_input("paper", "/p.pdf", "T", "C")
        run_id = repo.create_run("brief", "model", [input_id])
        
        repo.update_run_status(run_id, "failed", "API rate limit exceeded")
        
        details = repo.get_run_details(run_id)
        assert details["status"] == "failed"
        assert details["error_message"] == "API rate limit exceeded"
    
    # =========================================================================
    # Output Operations
    # =========================================================================
    
    def test_add_output_text(self, repo):
        """Should add text output."""
        input_id = repo.get_or_create_input("paper", "/p.pdf", "T", "C")
        run_id = repo.create_run("brief", "model", [input_id])
        
        output_id = repo.add_output(run_id, "main", "Generated summary text")
        
        assert output_id > 0
        
        details = repo.get_run_details(run_id)
        assert len(details["outputs"]) == 1
        assert details["outputs"][0]["content_type"] == "text"
    
    def test_add_output_json(self, repo):
        """Should add JSON output with correct content_type."""
        input_id = repo.get_or_create_input("paper", "/p.pdf", "T", "C")
        run_id = repo.create_run("classify", "model", [input_id])
        
        json_content = '{"keywords": ["ai", "ml"], "discipline": "computer science"}'
        output_id = repo.add_output(run_id, "classification", json_content, "json")
        
        details = repo.get_run_details(run_id)
        assert details["outputs"][0]["content_type"] == "json"
        assert details["outputs"][0]["content"] == json_content
    
    def test_add_multiple_outputs(self, repo):
        """Should support multiple outputs per run."""
        input_id = repo.get_or_create_input("paper", "/p.pdf", "T", "C")
        run_id = repo.create_run("translate", "model", [input_id])
        
        repo.add_output(run_id, "main", "Chinese translation")
        repo.add_output(run_id, "bilingual", "Side by side translation")
        
        details = repo.get_run_details(run_id)
        assert len(details["outputs"]) == 2
        
        output_types = {o["output_type"] for o in details["outputs"]}
        assert output_types == {"main", "bilingual"}
    
    # =========================================================================
    # Token Usage Operations
    # =========================================================================
    
    def test_add_token_usage(self, repo):
        """Should add token usage with all fields."""
        input_id = repo.get_or_create_input("paper", "/p.pdf", "T", "C")
        run_id = repo.create_run("brief", "model", [input_id])
        
        repo.add_token_usage(
            run_id=run_id,
            input_tokens=10000,
            output_tokens=500,
            cost_input=0.05,
            cost_output=0.01,
            process_time=15.5
        )
        
        details = repo.get_run_details(run_id)
        usage = details["token_usage"]
        
        assert usage["input_tokens"] == 10000
        assert usage["output_tokens"] == 500
        assert usage["cost_input"] == 0.05
        assert usage["cost_output"] == 0.01
        assert usage["process_time"] == 15.5
    
    # =========================================================================
    # Query Operations
    # =========================================================================
    
    def test_get_recent_runs_empty(self, repo):
        """Should return empty list when no runs."""
        runs = repo.get_recent_runs()
        assert runs == []
    
    def test_get_recent_runs_ordered(self, repo):
        """Should return runs in reverse ID order (proxy for chronological)."""
        input_id = repo.get_or_create_input("paper", "/p.pdf", "T", "C")
        
        run1 = repo.create_run("brief", "model1", [input_id])
        run2 = repo.create_run("outline", "model2", [input_id])
        run3 = repo.create_run("translate", "model3", [input_id])
        
        runs = repo.get_recent_runs(limit=10)
        
        # All three runs should be present
        assert len(runs) == 3
        
        # IDs should be in descending order (most recent = highest ID)
        run_ids = [r["id"] for r in runs]
        assert run_ids == sorted(run_ids, reverse=True)
    
    def test_get_recent_runs_includes_currency(self, repo):
        """Should include currency field."""
        input_id = repo.get_or_create_input("paper", "/p.pdf", "T", "C")
        repo.create_run("brief", "deepseek-v3.2", [input_id], currency="¥")
        
        runs = repo.get_recent_runs()
        assert runs[0]["currency"] == "¥"
    
    def test_get_run_details_not_found(self, repo):
        """Should return None for non-existent run."""
        details = repo.get_run_details(9999)
        assert details is None
    
    def test_get_stats_empty(self, repo):
        """Should return zero stats when no runs."""
        stats = repo.get_stats()
        
        assert stats["total_runs"] == 0
        assert stats["success_rate"] == 0
    
    def test_get_stats_with_data(self, repo):
        """Should return correct statistics."""
        input_id = repo.get_or_create_input("paper", "/p.pdf", "T", "C")
        
        # Create 3 runs, 2 success, 1 failed
        run1 = repo.create_run("brief", "model-a", [input_id])
        run2 = repo.create_run("outline", "model-a", [input_id])
        run3 = repo.create_run("brief", "model-b", [input_id])
        
        repo.update_run_status(run1, "success")
        repo.update_run_status(run2, "success")
        repo.update_run_status(run3, "failed")
        
        stats = repo.get_stats()
        
        assert stats["total_runs"] == 3
        assert stats["by_status"]["success"] == 2
        assert stats["by_status"]["failed"] == 1
    
    def test_search_by_title(self, repo):
        """Should find runs by input title pattern."""
        id1 = repo.get_or_create_input("paper", "/a.pdf", "Quantum Computing Paper", "C1")
        id2 = repo.get_or_create_input("paper", "/b.pdf", "Machine Learning Paper", "C2")
        
        repo.create_run("brief", "model", [id1])
        repo.create_run("brief", "model", [id2])
        
        results = repo.search_by_title("Quantum")
        
        assert len(results) == 1
        assert "Quantum" in results[0]["title"]


class TestManyToManyRelationship:
    """Tests for the many-to-many relationship between runs and inputs."""
    
    @pytest.fixture
    def repo(self, temp_dir):
        db_path = temp_dir / "test.db"
        return RunRepository(db_path=db_path)
    
    def test_same_input_multiple_runs(self, repo):
        """Same input should be usable in multiple runs."""
        # Same content = same input ID
        content = "This is the paper content"
        input_id = repo.get_or_create_input("paper", "/p.pdf", "My Paper", content)
        
        # Three different runs with same input
        run1 = repo.create_run("brief", "model-a", [input_id])
        run2 = repo.create_run("outline", "model-a", [input_id])
        run3 = repo.create_run("brief", "model-b", [input_id])
        
        # Verify all three runs exist
        runs = repo.get_recent_runs()
        assert len(runs) == 3
        
        # Verify only one input record
        conn = repo._get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM inputs")
        input_count = cursor.fetchone()[0]
        conn.close()
        
        assert input_count == 1
    
    def test_one_run_multiple_inputs(self, repo):
        """One run should be able to have multiple inputs."""
        id1 = repo.get_or_create_input("paper", "/paper.pdf", "Paper", "Paper content")
        id2 = repo.get_or_create_input("news", "/news.md", "News 1", "News content 1")
        id3 = repo.get_or_create_input("news", "/news2.md", "News 2", "News content 2")
        
        run_id = repo.create_run("brief", "model", [id1, id2, id3])
        
        details = repo.get_run_details(run_id)
        assert len(details["inputs"]) == 3
    
    def test_query_runs_by_input(self, repo):
        """Should be able to find all runs for a specific input."""
        content = "Unique paper content for tracking"
        input_id = repo.get_or_create_input("paper", "/p.pdf", "Tracked Paper", content)
        
        # Multiple runs
        repo.create_run("brief", "model1", [input_id])
        repo.create_run("outline", "model2", [input_id])
        
        # Query runs by searching title
        results = repo.search_by_title("Tracked Paper")
        assert len(results) == 2
    
    def test_cascade_delete_run(self, repo):
        """Deleting a run should cascade to run_inputs, outputs, and token_usage."""
        input_id = repo.get_or_create_input("paper", "/p.pdf", "T", "C")
        run_id = repo.create_run("brief", "model", [input_id])
        repo.add_output(run_id, "main", "Output content")
        repo.add_token_usage(run_id, 1000, 100, 0.01, 0.001, 5.0)
        
        # Delete the run
        conn = repo._get_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM runs WHERE id = ?", (run_id,))
        conn.commit()
        
        # Verify cascaded deletes
        cursor.execute("SELECT COUNT(*) FROM run_inputs WHERE run_id = ?", (run_id,))
        assert cursor.fetchone()[0] == 0
        
        cursor.execute("SELECT COUNT(*) FROM outputs WHERE run_id = ?", (run_id,))
        assert cursor.fetchone()[0] == 0
        
        cursor.execute("SELECT COUNT(*) FROM token_usage WHERE run_id = ?", (run_id,))
        assert cursor.fetchone()[0] == 0
        
        # But input should still exist
        cursor.execute("SELECT COUNT(*) FROM inputs WHERE id = ?", (input_id,))
        assert cursor.fetchone()[0] == 1
        
        conn.close()


class TestEdgeCases:
    """Tests for edge cases and potential issues."""
    
    @pytest.fixture
    def repo(self, temp_dir):
        db_path = temp_dir / "test.db"
        return RunRepository(db_path=db_path)
    
    def test_unicode_content(self, repo):
        """Should handle unicode content correctly."""
        content = "这是中文内容 🎉 with émojis and spëcial çharacters"
        input_id = repo.get_or_create_input("paper", "/中文.pdf", "中文标题", content)
        
        run_id = repo.create_run("brief", "model", [input_id])
        repo.add_output(run_id, "main", "生成的中文摘要 📝")
        
        details = repo.get_run_details(run_id)
        assert details["inputs"][0]["title"] == "中文标题"
        assert "中文摘要" in details["outputs"][0]["content"]
    
    def test_empty_content(self, repo):
        """Should handle empty content."""
        input_id = repo.get_or_create_input("paper", "/empty.pdf", "Empty", "")
        assert input_id > 0
    
    def test_very_long_content(self, repo):
        """Should handle very long content."""
        long_content = "x" * 1_000_000  # 1MB
        input_id = repo.get_or_create_input("paper", "/big.pdf", "Big Paper", long_content)
        
        # Should still hash correctly
        run_id = repo.create_run("brief", "model", [input_id])
        details = repo.get_run_details(run_id)
        assert details is not None
    
    def test_special_characters_in_path(self, repo):
        """Should handle special characters in file paths."""
        path = "/path/with spaces/and (parens)/file [1].pdf"
        input_id = repo.get_or_create_input("paper", path, "Title", "Content")
        
        details = repo.get_run_details(
            repo.create_run("brief", "model", [input_id])
        )
        assert details["inputs"][0]["source_path"] == path
    
    def test_null_thinking_level(self, repo):
        """Should handle null thinking_level."""
        input_id = repo.get_or_create_input("paper", "/p.pdf", "T", "C")
        run_id = repo.create_run("brief", "model", [input_id], thinking_level=None)
        
        details = repo.get_run_details(run_id)
        assert details["thinking_level"] is None
    
    def test_concurrent_reads(self, repo):
        """Should handle concurrent read operations."""
        input_id = repo.get_or_create_input("paper", "/p.pdf", "T", "C")
        run_id = repo.create_run("brief", "model", [input_id])
        repo.update_run_status(run_id, "success")
        
        results = []
        errors = []
        
        def read_runs():
            try:
                runs = repo.get_recent_runs()
                results.append(len(runs))
            except Exception as e:
                errors.append(str(e))
        
        threads = [threading.Thread(target=read_runs) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0
        assert all(r == 1 for r in results)
    
    def test_concurrent_writes_same_input(self, repo):
        """Concurrent writes with same content - some may fail due to SQLite locking."""
        content = "Shared content for concurrent test"
        results = []
        errors = []
        
        def create_input():
            try:
                input_id = repo.get_or_create_input("paper", "/p.pdf", "T", content)
                results.append(input_id)
            except Exception as e:
                errors.append(str(e))
        
        threads = [threading.Thread(target=create_input) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # At least one should succeed
        assert len(results) >= 1
        # All successful results should have the same ID (content hash dedup)
        assert len(set(results)) == 1
        
        # Note: SQLite has limited write concurrency, some failures are expected
        # In production, writes are sequential (one API call at a time)


class TestCurrencyHandling:
    """Tests for currency symbol handling."""
    
    @pytest.fixture
    def repo(self, temp_dir):
        db_path = temp_dir / "test.db"
        return RunRepository(db_path=db_path)
    
    def test_default_currency_usd(self, repo):
        """Default currency should be USD."""
        input_id = repo.get_or_create_input("paper", "/p.pdf", "T", "C")
        run_id = repo.create_run("brief", "model", [input_id])
        
        runs = repo.get_recent_runs()
        assert runs[0]["currency"] == "$"
    
    def test_custom_currency_cny(self, repo):
        """Should support CNY currency."""
        input_id = repo.get_or_create_input("paper", "/p.pdf", "T", "C")
        run_id = repo.create_run("brief", "deepseek-v3.2", [input_id], currency="¥")
        
        runs = repo.get_recent_runs()
        assert runs[0]["currency"] == "¥"
    
    def test_different_currencies_different_runs(self, repo):
        """Different runs can have different currencies."""
        input_id = repo.get_or_create_input("paper", "/p.pdf", "T", "C")
        
        run1 = repo.create_run("brief", "deepseek", [input_id], currency="¥")
        run2 = repo.create_run("brief", "gpt-4o", [input_id], currency="$")
        
        runs = repo.get_recent_runs()
        currencies = {r["currency"] for r in runs}
        assert currencies == {"¥", "$"}


class TestDatabasePathEnvironmentVariables:
    """Tests for database path environment variable priority."""
    
    def _clear_env_vars(self):
        """Clear all database-related environment variables."""
        for key in ["EDITOR_ASSISTANT_TEST_DB_DIR", "EDITOR_ASSISTANT_DB_DIR"]:
            if key in os.environ:
                del os.environ[key]
    
    def _save_env_vars(self):
        """Save current environment variables."""
        return {
            "EDITOR_ASSISTANT_TEST_DB_DIR": os.environ.get("EDITOR_ASSISTANT_TEST_DB_DIR"),
            "EDITOR_ASSISTANT_DB_DIR": os.environ.get("EDITOR_ASSISTANT_DB_DIR"),
        }
    
    def _restore_env_vars(self, saved):
        """Restore saved environment variables."""
        for key, value in saved.items():
            if value is not None:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]
    
    def test_default_path_when_no_env_vars(self):
        """Should use ~/.editor_assistant when no env vars set."""
        saved = self._save_env_vars()
        try:
            self._clear_env_vars()
            
            path = get_database_path()
            
            assert ".editor_assistant" in str(path)
            assert path.name == "runs.db"
        finally:
            self._restore_env_vars(saved)
    
    def test_test_env_var_takes_priority(self, temp_dir):
        """EDITOR_ASSISTANT_TEST_DB_DIR should take highest priority."""
        saved = self._save_env_vars()
        try:
            test_dir = temp_dir / "test_priority"
            os.environ["EDITOR_ASSISTANT_TEST_DB_DIR"] = str(test_dir)
            os.environ["EDITOR_ASSISTANT_DB_DIR"] = "/should/not/use/this"
            
            path = get_database_path()
            
            assert str(test_dir) in str(path)
            assert "/should/not/use/this" not in str(path)
        finally:
            self._restore_env_vars(saved)
    
    def test_prod_env_var_when_no_test_var(self, temp_dir):
        """EDITOR_ASSISTANT_DB_DIR used when TEST var not set."""
        saved = self._save_env_vars()
        try:
            self._clear_env_vars()
            prod_dir = temp_dir / "prod_override"
            os.environ["EDITOR_ASSISTANT_DB_DIR"] = str(prod_dir)
            
            path = get_database_path()
            
            assert str(prod_dir) in str(path)
        finally:
            self._restore_env_vars(saved)
    
    def test_empty_test_var_falls_through(self, temp_dir):
        """Empty TEST var should fall through to PROD var."""
        saved = self._save_env_vars()
        try:
            self._clear_env_vars()
            prod_dir = temp_dir / "prod_fallback"
            os.environ["EDITOR_ASSISTANT_TEST_DB_DIR"] = ""  # Empty string
            os.environ["EDITOR_ASSISTANT_DB_DIR"] = str(prod_dir)
            
            path = get_database_path()
            
            # Empty string is falsy, so should use PROD
            assert str(prod_dir) in str(path)
        finally:
            self._restore_env_vars(saved)
    
    def test_creates_directory_if_not_exists(self, temp_dir):
        """Should create database directory if it doesn't exist."""
        saved = self._save_env_vars()
        try:
            new_dir = temp_dir / "new" / "nested" / "directory"
            assert not new_dir.exists()
            
            os.environ["EDITOR_ASSISTANT_TEST_DB_DIR"] = str(new_dir)
            
            path = get_database_path()
            
            assert new_dir.exists()
            assert path == new_dir / "runs.db"
        finally:
            self._restore_env_vars(saved)
    
    def test_test_and_prod_are_independent(self, temp_dir):
        """Changing TEST var should not affect what PROD would use."""
        saved = self._save_env_vars()
        try:
            self._clear_env_vars()
            
            # First call with TEST var
            test_dir = temp_dir / "test_path"
            os.environ["EDITOR_ASSISTANT_TEST_DB_DIR"] = str(test_dir)
            path1 = get_database_path()
            
            # Remove TEST var, should fall back to default
            del os.environ["EDITOR_ASSISTANT_TEST_DB_DIR"]
            path2 = get_database_path()
            
            assert str(test_dir) in str(path1)
            assert str(test_dir) not in str(path2)
            assert ".editor_assistant" in str(path2)
        finally:
            self._restore_env_vars(saved)
    
    def test_path_with_spaces_and_special_chars(self, temp_dir):
        """Should handle paths with spaces and special characters."""
        saved = self._save_env_vars()
        try:
            special_dir = temp_dir / "path with spaces" / "and (parens)"
            os.environ["EDITOR_ASSISTANT_TEST_DB_DIR"] = str(special_dir)
            
            path = get_database_path()
            
            assert special_dir.exists()
            assert path == special_dir / "runs.db"
        finally:
            self._restore_env_vars(saved)


class TestProductionDatabaseIsolation:
    """
    CRITICAL: Tests to ensure testing never pollutes production database.
    
    These tests verify that:
    1. Test writes go to test database, not production
    2. Production database is never touched during tests
    3. Test and production databases are completely separate files
    """
    
    def _save_and_clear_env_vars(self):
        """Save and clear environment variables."""
        saved = {
            "EDITOR_ASSISTANT_TEST_DB_DIR": os.environ.get("EDITOR_ASSISTANT_TEST_DB_DIR"),
            "EDITOR_ASSISTANT_DB_DIR": os.environ.get("EDITOR_ASSISTANT_DB_DIR"),
        }
        for key in saved:
            if key in os.environ:
                del os.environ[key]
        return saved
    
    def _restore_env_vars(self, saved):
        """Restore saved environment variables."""
        for key, value in saved.items():
            if value is not None:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]
    
    def test_test_database_is_different_file_from_production(self, temp_dir):
        """Test and production databases should be completely separate files."""
        saved = self._save_and_clear_env_vars()
        try:
            test_dir = temp_dir / "test_db"
            prod_dir = temp_dir / "prod_db"
            
            # Set up test environment
            os.environ["EDITOR_ASSISTANT_TEST_DB_DIR"] = str(test_dir)
            test_path = get_database_path()
            
            # Switch to production environment
            del os.environ["EDITOR_ASSISTANT_TEST_DB_DIR"]
            os.environ["EDITOR_ASSISTANT_DB_DIR"] = str(prod_dir)
            prod_path = get_database_path()
            
            # They must be completely different files
            assert test_path != prod_path
            assert str(test_dir) in str(test_path)
            assert str(prod_dir) in str(prod_path)
            assert str(test_dir) not in str(prod_path)
            assert str(prod_dir) not in str(test_path)
        finally:
            self._restore_env_vars(saved)
    
    def test_writes_to_test_db_do_not_appear_in_prod_db(self, temp_dir):
        """Data written to test database must not appear in production database."""
        saved = self._save_and_clear_env_vars()
        try:
            test_dir = temp_dir / "test_isolated"
            prod_dir = temp_dir / "prod_isolated"
            
            # Write to test database
            os.environ["EDITOR_ASSISTANT_TEST_DB_DIR"] = str(test_dir)
            test_repo = RunRepository()
            input_id = test_repo.get_or_create_input(
                "paper", "/test.pdf", "TEST ONLY TITLE", "test content"
            )
            test_repo.create_run("brief", "test-model", [input_id])
            
            # Verify data exists in test database
            test_runs = test_repo.get_recent_runs()
            assert len(test_runs) == 1
            assert test_runs[0]["input_titles"] == "TEST ONLY TITLE"
            
            # Switch to production database
            del os.environ["EDITOR_ASSISTANT_TEST_DB_DIR"]
            os.environ["EDITOR_ASSISTANT_DB_DIR"] = str(prod_dir)
            prod_repo = RunRepository()
            
            # Production database should be empty
            prod_runs = prod_repo.get_recent_runs()
            assert len(prod_runs) == 0
            
            # Search should not find the test data
            search_results = prod_repo.search_by_title("TEST ONLY")
            assert len(search_results) == 0
        finally:
            self._restore_env_vars(saved)
    
    def test_production_data_not_visible_in_test_environment(self, temp_dir):
        """Data in production database should not be visible in test environment."""
        saved = self._save_and_clear_env_vars()
        try:
            test_dir = temp_dir / "test_env"
            prod_dir = temp_dir / "prod_env"
            
            # First, write to production database
            os.environ["EDITOR_ASSISTANT_DB_DIR"] = str(prod_dir)
            prod_repo = RunRepository()
            input_id = prod_repo.get_or_create_input(
                "paper", "/prod.pdf", "PRODUCTION DATA", "prod content"
            )
            prod_repo.create_run("outline", "prod-model", [input_id])
            
            # Verify production has data
            assert len(prod_repo.get_recent_runs()) == 1
            
            # Now switch to test environment
            os.environ["EDITOR_ASSISTANT_TEST_DB_DIR"] = str(test_dir)
            test_repo = RunRepository()
            
            # Test environment should NOT see production data
            test_runs = test_repo.get_recent_runs()
            assert len(test_runs) == 0
            
            search_results = test_repo.search_by_title("PRODUCTION")
            assert len(search_results) == 0
        finally:
            self._restore_env_vars(saved)
    
    def test_conftest_isolation_fixture_works(self, isolate_database_from_production):
        """The conftest fixture should properly isolate the database."""
        # isolate_database_from_production is the session fixture from conftest.py
        # It should have set EDITOR_ASSISTANT_TEST_DB_DIR
        
        assert "EDITOR_ASSISTANT_TEST_DB_DIR" in os.environ
        test_db_dir = os.environ["EDITOR_ASSISTANT_TEST_DB_DIR"]
        
        # The path should be in a temp directory, not ~/.editor_assistant
        db_path = get_database_path()
        assert ".editor_assistant" not in str(db_path)
        assert test_db_dir in str(db_path)
    
    def test_repository_uses_isolated_database_during_tests(self, isolate_database_from_production):
        """RunRepository should use the isolated test database during tests."""
        # Create a repository (should use the isolated database)
        repo = RunRepository()
        
        # Write some data
        input_id = repo.get_or_create_input(
            "paper", "/isolation_test.pdf", "ISOLATION TEST", "content"
        )
        run_id = repo.create_run("translate", "isolation-model", [input_id])
        
        # The database file should be in the temp directory
        db_path = repo.db_path
        assert ".editor_assistant" not in str(db_path)
        
        # The data should be there
        runs = repo.get_recent_runs()
        assert any("ISOLATION TEST" in (r.get("input_titles") or "") for r in runs)
    
    def test_concurrent_test_and_production_processes(self, temp_dir):
        """
        Simulate: test is running while someone triggers production.
        
        Scenario:
        - Process A (pytest): has EDITOR_ASSISTANT_TEST_DB_DIR set
        - Process B (production): no test env var, uses default/PROD path
        
        They should write to completely different databases.
        """
        saved = {
            "EDITOR_ASSISTANT_TEST_DB_DIR": os.environ.get("EDITOR_ASSISTANT_TEST_DB_DIR"),
            "EDITOR_ASSISTANT_DB_DIR": os.environ.get("EDITOR_ASSISTANT_DB_DIR"),
        }
        try:
            test_dir = temp_dir / "concurrent_test"
            prod_dir = temp_dir / "concurrent_prod"
            
            # === Simulate Test Process ===
            os.environ["EDITOR_ASSISTANT_TEST_DB_DIR"] = str(test_dir)
            if "EDITOR_ASSISTANT_DB_DIR" in os.environ:
                del os.environ["EDITOR_ASSISTANT_DB_DIR"]
            
            test_repo = RunRepository()
            test_input_id = test_repo.get_or_create_input(
                "paper", "/test.pdf", "FROM_TEST_PROCESS", "test"
            )
            test_repo.create_run("brief", "test-model", [test_input_id])
            test_path = test_repo.db_path
            
            # === Simulate Production Process (different env) ===
            # Production process would NOT have TEST_DB_DIR set
            del os.environ["EDITOR_ASSISTANT_TEST_DB_DIR"]
            os.environ["EDITOR_ASSISTANT_DB_DIR"] = str(prod_dir)
            
            prod_repo = RunRepository()
            prod_input_id = prod_repo.get_or_create_input(
                "paper", "/prod.pdf", "FROM_PROD_PROCESS", "prod"
            )
            prod_repo.create_run("outline", "prod-model", [prod_input_id])
            prod_path = prod_repo.db_path
            
            # === Verify Complete Isolation ===
            # Different database files
            assert test_path != prod_path
            assert str(test_dir) in str(test_path)
            assert str(prod_dir) in str(prod_path)
            
            # Test data only in test db
            os.environ["EDITOR_ASSISTANT_TEST_DB_DIR"] = str(test_dir)
            if "EDITOR_ASSISTANT_DB_DIR" in os.environ:
                del os.environ["EDITOR_ASSISTANT_DB_DIR"]
            test_repo2 = RunRepository()
            test_runs = test_repo2.get_recent_runs()
            assert len(test_runs) == 1
            assert "FROM_TEST_PROCESS" in test_runs[0].get("input_titles", "")
            assert "FROM_PROD_PROCESS" not in test_runs[0].get("input_titles", "")
            
            # Prod data only in prod db
            del os.environ["EDITOR_ASSISTANT_TEST_DB_DIR"]
            os.environ["EDITOR_ASSISTANT_DB_DIR"] = str(prod_dir)
            prod_repo2 = RunRepository()
            prod_runs = prod_repo2.get_recent_runs()
            assert len(prod_runs) == 1
            assert "FROM_PROD_PROCESS" in prod_runs[0].get("input_titles", "")
            assert "FROM_TEST_PROCESS" not in prod_runs[0].get("input_titles", "")
            
        finally:
            # Restore
            for key, value in saved.items():
                if value is not None:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]
    
    def test_production_unaffected_by_test_env_var_in_different_process(self, temp_dir):
        """
        Real scenario: pytest sets TEST_DB_DIR, but production CLI in another
        terminal does NOT see this env var (different process).
        
        This test verifies the logic that production code without TEST_DB_DIR
        will use the production path.
        """
        saved = {
            "EDITOR_ASSISTANT_TEST_DB_DIR": os.environ.get("EDITOR_ASSISTANT_TEST_DB_DIR"),
            "EDITOR_ASSISTANT_DB_DIR": os.environ.get("EDITOR_ASSISTANT_DB_DIR"),
        }
        try:
            # === Scenario: Production process (no TEST_DB_DIR) ===
            # Clear both env vars to simulate fresh production process
            for key in ["EDITOR_ASSISTANT_TEST_DB_DIR", "EDITOR_ASSISTANT_DB_DIR"]:
                if key in os.environ:
                    del os.environ[key]
            
            prod_path = get_database_path()
            
            # Production should use default ~/.editor_assistant path
            assert ".editor_assistant" in str(prod_path)
            assert "test" not in str(prod_path).lower()
            
        finally:
            for key, value in saved.items():
                if value is not None:
                    os.environ[key] = value
                elif key in os.environ:
                    del os.environ[key]

