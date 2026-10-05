"""Offline coverage for CLI service tiers and resumed runs."""

import csv
import json
from argparse import Namespace
from unittest.mock import patch

import httpx
import pytest

from editor_assistant.cli import cmd_resume, cmd_show_run, create_parser
from editor_assistant.storage.database import (
    SCHEMA,
    get_connection,
    get_schema_version,
)
from editor_assistant.storage.repository import RunRepository

pytestmark = pytest.mark.unit


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "command", ["brief", "outline", "translate", "process", "batch"]
)
@pytest.mark.parametrize("stream", [False, True])
@pytest.mark.parametrize("tier", [None, "fast"])
async def test_cli_service_tier_reaches_http_and_storage(
    command, stream, tier, tmp_path, monkeypatch
):
    monkeypatch.setenv("DOUBAO_API_KEY", "offline-test-key")
    monkeypatch.setattr("editor_assistant.cli.RICH_AVAILABLE", False)
    source = tmp_path / "paper.md"
    source.write_text("A research paper with meaningful content. " * 100)
    args = [command]
    if command in {"brief", "process"}:
        args.append(f"paper={source}")
    elif command == "batch":
        args.extend([str(tmp_path), "--task", "outline", "--ext", ".md"])
    else:
        args.append(str(source))
    if command == "process":
        args.extend(["--tasks", "brief,outline"])
    args.extend(["--model", "doubao-seed-2.0-pro"])
    if tier:
        args.extend(["--service-tier", tier])
    if not stream:
        args.append("--no-stream")

    payloads = []

    def respond(request):
        payload = json.loads(request.content)
        payloads.append(payload)
        usage = {"prompt_tokens": 10, "completion_tokens": 5}
        if payload["stream"]:
            chunk = {
                "choices": [{"delta": {"content": "Generated text"}}],
                "usage": usage,
            }
            return httpx.Response(
                200,
                text=f"data: {json.dumps(chunk)}\n\ndata: [DONE]\n\n",
                headers={"content-type": "text/event-stream"},
            )
        return httpx.Response(
            200,
            json={
                "choices": [{"message": {"content": "Generated text"}}],
                "usage": usage,
            },
        )

    repo = RunRepository()
    old_ids = {run["id"] for run in repo.get_recent_runs(limit=1000)}
    async with httpx.AsyncClient(
        transport=httpx.MockTransport(respond)
    ) as http_client:
        with patch(
            "llm_exec_core.client.httpx.AsyncClient", return_value=http_client
        ):
            parsed = create_parser().parse_args(args)
            await parsed.func(parsed)

    assert len(payloads) == (2 if command == "process" else 1)
    for payload in payloads:
        assert payload["stream"] is stream
        assert payload["model"] == "doubao-seed-2-0-pro-260215"
        if tier:
            assert payload["service_tier"] == tier
        else:
            assert "service_tier" not in payload
    new_runs = [
        repo.get_run_details(run["id"])
        for run in repo.get_recent_runs(limit=1000)
        if run["id"] not in old_ids
    ]
    assert len(new_runs) == len(payloads)
    assert all(run["service_tier"] == tier for run in new_runs)
    assert all(run["status"] == "success" for run in new_runs)


def test_cli_rejects_invalid_service_tier(capsys):
    with pytest.raises(SystemExit) as error:
        create_parser().parse_args(
            ["outline", "paper.md", "--service-tier", "invalid"]
        )
    assert error.value.code == 2
    assert "invalid choice" in capsys.readouterr().err


@pytest.mark.asyncio
@pytest.mark.parametrize("tier", [None, "fast"])
async def test_resume_restores_requested_service_tier(
    tier, tmp_path, monkeypatch
):
    monkeypatch.setenv("DOUBAO_API_KEY", "offline-test-key")
    repo = RunRepository(tmp_path / "runs.db")
    input_id = repo.get_or_create_input(
        "paper", "paper.md", "Paper", "Content"
    )
    run_id = repo.create_run(
        "outline", "doubao-seed-2.0-pro", [input_id], service_tier=tier
    )
    processors = []

    async def capture(assistant, *args, **kwargs):
        processors.append(assistant.md_processor)

    with (
        patch("editor_assistant.cli.RunRepository", return_value=repo),
        patch(
            "editor_assistant.main.EditorAssistant.process_multiple", capture
        ),
    ):
        await cmd_resume(
            Namespace(dry_run=False, debug=False, save_files=False)
        )
    assert len(processors) == 1
    assert processors[0].service_tier == tier
    assert repo.get_run_details(run_id)["status"] == "success"


def test_service_tier_is_visible_and_exported(tmp_path, capsys):
    repo = RunRepository(tmp_path / "runs.db")
    run_id = repo.create_run(
        "outline", "doubao-seed-2.0-pro", [], service_tier="fast"
    )
    with patch("editor_assistant.cli.RunRepository", return_value=repo):
        cmd_show_run(Namespace(run_id=run_id, output=False))
    assert "Requested tier: fast" in capsys.readouterr().out
    json_path = tmp_path / "runs.json"
    csv_path = tmp_path / "runs.csv"
    repo.export_runs(json_path)
    repo.export_runs(csv_path, format="csv")
    assert (
        json.loads(json_path.read_text())["runs"][0]["service_tier"] == "fast"
    )
    with csv_path.open() as handle:
        assert next(csv.DictReader(handle))["service_tier"] == "fast"


def test_existing_database_migrates_without_losing_runs(tmp_path):
    db_path = tmp_path / "legacy.db"
    conn = get_connection(db_path)
    conn.executescript(SCHEMA.replace("    service_tier TEXT,\n", ""))
    conn.execute("INSERT INTO schema_version VALUES (1, 1)")
    conn.execute(
        "INSERT INTO runs (task, model) VALUES ('brief', 'old-model')"
    )
    conn.commit()
    conn.close()

    repo = RunRepository(db_path)
    old_run = repo.get_run_details(1)
    assert old_run["model"] == "old-model"
    assert old_run["service_tier"] is None
    assert repo.get_resumable_runs()[0]["service_tier"] is None
    new_id = repo.create_run(
        "outline", "doubao-seed-2.0-pro", [], service_tier="fast"
    )
    assert (
        RunRepository(db_path).get_run_details(new_id)["service_tier"]
        == "fast"
    )
    conn = get_connection(db_path)
    assert get_schema_version(conn) == 2
    columns = [row[1] for row in conn.execute("PRAGMA table_info(runs)")]
    conn.close()
    assert columns.count("service_tier") == 1


def test_current_database_initialization_does_not_need_write_lock(
    tmp_path, monkeypatch
):
    from editor_assistant.storage import database

    db_path = tmp_path / "runs.db"
    run_id = RunRepository(db_path).create_run("outline", "test-model", [])
    writer = get_connection(db_path)
    writer.execute("BEGIN IMMEDIATE")
    original_connect = database.get_connection

    def connect(path=None):
        conn = original_connect(path)
        conn.execute("PRAGMA busy_timeout=0")
        return conn

    monkeypatch.setattr(database, "get_connection", connect)
    try:
        assert (
            RunRepository(db_path).get_run_details(run_id)["model"]
            == "test-model"
        )
    finally:
        writer.rollback()
        writer.close()


def test_current_database_initialization_supports_read_only_connection(
    tmp_path, monkeypatch
):
    import sqlite3
    from editor_assistant.storage import database

    db_path = tmp_path / "runs.db"
    RunRepository(db_path)
    conn = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    monkeypatch.setattr(database, "get_connection", lambda path=None: conn)
    database.init_database(db_path)
    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        conn.execute("SELECT 1")


def test_future_schema_version_is_not_overwritten(tmp_path):
    from editor_assistant.storage.database import init_database

    db_path = tmp_path / "runs.db"
    RunRepository(db_path)
    conn = get_connection(db_path)
    conn.execute("UPDATE schema_version SET version=99")
    conn.commit()
    conn.close()
    with pytest.raises(ValueError, match="newer"):
        init_database(db_path)
    conn = get_connection(db_path)
    assert get_schema_version(conn) == 99
    conn.close()


def test_migration_rechecks_version_after_acquiring_lock(
    tmp_path, monkeypatch
):
    from editor_assistant.storage import database

    db_path = tmp_path / "runs.db"
    RunRepository(db_path)
    statements = []
    conn = get_connection(db_path)
    conn.set_trace_callback(statements.append)
    monkeypatch.setattr(database, "get_connection", lambda path=None: conn)
    with patch.object(
        database, "get_schema_version", side_effect=[1, 2]
    ) as version:
        database.init_database(db_path)
    assert version.call_count == 2
    assert "BEGIN IMMEDIATE" in statements
    assert not any(
        sql.lstrip().startswith(("CREATE", "ALTER", "INSERT"))
        for sql in statements
    )


def test_failed_migration_rolls_back_and_closes_connection(
    tmp_path, monkeypatch
):
    import sqlite3
    from editor_assistant.storage import database

    db_path = tmp_path / "legacy.db"
    conn = get_connection(db_path)
    conn.executescript(SCHEMA.replace("    service_tier TEXT,\n", ""))
    conn.execute("INSERT INTO schema_version VALUES (1, 1)")
    conn.commit()

    def deny_version_write(action, table, *args):
        if action == sqlite3.SQLITE_INSERT and table == "schema_version":
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK

    conn.set_authorizer(deny_version_write)
    monkeypatch.setattr(database, "get_connection", lambda path=None: conn)
    with pytest.raises(sqlite3.DatabaseError, match="authorized"):
        database.init_database(db_path)
    with pytest.raises(sqlite3.ProgrammingError, match="closed"):
        conn.execute("SELECT 1")
    check = get_connection(db_path)
    assert get_schema_version(check) == 1
    assert "service_tier" not in {
        row[1] for row in check.execute("PRAGMA table_info(runs)")
    }
    check.close()


@pytest.mark.parametrize(
    "model",
    ["glm-5.2-or", "doubao-seed-2.1-pro", "doubao-seed-1.6", "qwen3.6-flash"],
)
def test_processor_rejects_unreviewed_fast_support_before_initializing_clients(
    model,
):
    from editor_assistant.md_processor import MDProcessor

    with (
        patch("editor_assistant.md_processor.LLMClient") as client,
        patch("editor_assistant.md_processor.RunRepository") as repository,
    ):
        with pytest.raises(
            ValueError, match="no documented support.*service_tier.*fast"
        ):
            MDProcessor(model, service_tier="fast")
    client.assert_not_called()
    repository.assert_not_called()


def test_fast_support_matches_reviewed_model_catalog():
    from editor_assistant.config.llm_models import load_all_settings

    supported = {
        name
        for provider in load_all_settings().values()
        for name, model in provider.models.items()
        if model.capabilities is not None
        and "fast" in (model.capabilities.service_tiers or [])
    }
    assert supported == {
        "doubao-seed-2.1-lite",
        "doubao-seed-2.0-pro",
        "doubao-seed-2.0-lite",
        "doubao-seed-2.0-mini",
    }


def test_cli_rejects_unsupported_fast_before_reading_input(
    monkeypatch, capsys
):
    from editor_assistant.cli import main

    monkeypatch.delenv("DOUBAO_API_KEY", raising=False)
    monkeypatch.setattr(
        "sys.argv",
        [
            "editor-assistant",
            "outline",
            "missing.md",
            "--model",
            "doubao-seed-2.1-pro",
            "--service-tier",
            "fast",
        ],
    )
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 1
    assert "no documented support" in capsys.readouterr().out
