"""Offline coverage for optional application history storage."""

import json
import sqlite3
import asyncio
from unittest.mock import patch

import httpx
import pytest
import pytest_asyncio

from editor_assistant.cli import create_parser
from editor_assistant.data_models import Input, InputType, MDArticle
from editor_assistant.main import EditorAssistant
from editor_assistant.md_processor import MDProcessor
from editor_assistant.storage import database
from editor_assistant.storage.repository import RunRepository

pytestmark = pytest.mark.unit


@pytest.fixture
def offline_history(tmp_path, monkeypatch):
    monkeypatch.setenv("DOUBAO_API_KEY", "offline-test-key")
    monkeypatch.setenv("EDITOR_ASSISTANT_TEST_DB_DIR", str(tmp_path / "db"))
    monkeypatch.setattr("editor_assistant.cli.RICH_AVAILABLE", False)
    source = tmp_path / "paper.md"
    source.write_text("A research paper with meaningful content. " * 100)
    return source


@pytest_asyncio.fixture
async def offline_http():
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

    async with httpx.AsyncClient(
        transport=httpx.MockTransport(respond)
    ) as client:
        with patch(
            "llm_exec_core.client.httpx.AsyncClient", return_value=client
        ):
            yield payloads


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "command", ["brief", "outline", "translate", "process", "batch"]
)
@pytest.mark.parametrize("stream", [False, True])
@pytest.mark.parametrize("save_files", [False, True])
@pytest.mark.parametrize("save_history", [False, True])
async def test_cli_history_and_files_are_independent(
    command,
    stream,
    save_files,
    save_history,
    offline_history,
    offline_http,
    capsys,
):
    source = offline_history
    argv = [command]
    if command in {"brief", "process"}:
        argv.append(f"paper={source}")
    elif command == "batch":
        argv.extend([str(source.parent), "--task", "outline", "--ext", ".md"])
    else:
        argv.append(str(source))
    if command == "process":
        argv.extend(["--tasks", "brief,outline"])
    argv.extend(["--model", "doubao-seed-2.0-pro"])
    if not stream:
        argv.append("--no-stream")
    if save_files:
        argv.append("--save-files")
    if save_history:
        argv.append("--save-history")
    args = create_parser().parse_args(argv)
    if save_history:
        await args.func(args)
    else:
        with patch(
            "editor_assistant.md_processor.RunRepository",
            side_effect=AssertionError("Default processing opened SQLite"),
        ):
            await args.func(args)

    assert len(offline_http) == (2 if command == "process" else 1)
    assert all(payload["stream"] is stream for payload in offline_http)
    assert "Generated text" in capsys.readouterr().out
    outputs = source.parent / "llm_summaries"
    assert outputs.exists() is save_files
    if save_files:
        assert any(
            "Generated text" in p.read_text() for p in outputs.rglob("*.md")
        )
        assert list(outputs.rglob("token_usage_*.txt"))
    db_dir = source.parent / "db"
    assert db_dir.exists() is save_history
    if save_history:
        repo = RunRepository(db_dir / "runs.db")
        runs = repo.get_recent_runs()
        assert len(runs) == len(offline_http)
        for run in runs:
            details = repo.get_run_details(run["id"])
            assert details["status"] == "success"
            assert details["inputs"][0]["source_path"] == str(source)
            assert "Generated text" in details["outputs"][0]["content"]
            assert details["token_usage"]["input_tokens"] == 10
            assert details["token_usage"]["output_tokens"] == 5


@pytest.mark.asyncio
async def test_python_api_defaults_do_not_open_storage(
    offline_history, offline_http
):
    source = offline_history
    with patch(
        "editor_assistant.md_processor.RunRepository",
        side_effect=AssertionError("Default API opened SQLite"),
    ):
        processor = MDProcessor("doubao-seed-2.0-pro", stream=False)
        article = MDArticle(
            type=InputType.PAPER,
            content=source.read_text(),
            title="paper",
            source_path=str(source),
            output_path=source,
        )
        assert await processor.process_mds([article], "outline", False) == (
            True,
            -1,
        )
        assistant = EditorAssistant("doubao-seed-2.0-pro", stream=False)
        await assistant.process_multiple(
            [Input(type=InputType.PAPER, path=str(source))], "outline"
        )
        assert processor.repository is None
        assert assistant.md_processor.repository is None
        assert (
            processor.llm_client.get_token_usage()["total_input_tokens"] == 10
        )
    assert len(offline_http) == 2
    assert not (source.parent / "db").exists()


@pytest.mark.asyncio
async def test_processor_opt_in_returns_persisted_id(
    offline_history, offline_http
):
    processor = MDProcessor(
        "doubao-seed-2.0-pro", stream=False, save_history=True
    )
    article = MDArticle(
        type=InputType.PAPER,
        content=offline_history.read_text(),
        title="paper",
        source_path=str(offline_history),
    )
    success, run_id = await processor.process_mds([article], "outline", False)
    assert success is True
    assert run_id > 0
    assert processor.repository.get_run_details(run_id)["status"] == "success"


@pytest.mark.asyncio
@pytest.mark.parametrize("save_history", [False, True])
async def test_batch_streaming_result_or_rich_progress(
    save_history, offline_history, offline_http, monkeypatch, capsys
):
    monkeypatch.setattr("editor_assistant.cli.RICH_AVAILABLE", True)
    argv = [
        "batch",
        str(offline_history.parent),
        "--ext",
        ".md",
        "--task",
        "outline",
        "--model",
        "doubao-seed-2.0-pro",
    ]
    if save_history:
        argv.append("--save-history")
    args = create_parser().parse_args(argv)
    await args.func(args)
    if not save_history:
        assert "Generated text" in capsys.readouterr().out
    assert len(offline_http) == 1
    assert offline_http[0]["stream"] is True
    assert (offline_history.parent / "db").exists() is save_history
    if save_history:
        assert RunRepository().get_recent_runs()[0]["status"] == "success"


@pytest.mark.asyncio
@pytest.mark.parametrize("save_history", [False, True])
@pytest.mark.parametrize("cancelled", [False, True])
async def test_failed_or_cancelled_processing_respects_history(
    save_history, cancelled, offline_history
):
    processor = MDProcessor(
        "doubao-seed-2.0-pro", stream=False, save_history=save_history
    )
    article = MDArticle(
        type=InputType.PAPER,
        content=offline_history.read_text(),
        title="paper",
        source_path=str(offline_history),
    )
    failure = (
        asyncio.CancelledError()
        if cancelled
        else ConnectionError("offline failure")
    )
    with patch.object(
        processor.llm_client, "generate_response", side_effect=failure
    ):
        if cancelled:
            with pytest.raises(asyncio.CancelledError):
                await processor.process_mds([article], "outline", False)
        else:
            success, run_id = await processor.process_mds(
                [article], "outline", False
            )
            assert success is False
            assert (run_id > 0) is save_history
    assert (offline_history.parent / "db").exists() is save_history
    if save_history:
        run = RunRepository().get_recent_runs()[0]
        assert run["status"] == ("aborted" if cancelled else "failed")


@pytest.mark.asyncio
async def test_default_processing_preserves_existing_database(
    offline_history, offline_http
):
    repo = RunRepository()
    run_id = repo.create_run("outline", "old-model", [])
    before = repo.db_path.read_bytes()
    assistant = EditorAssistant("doubao-seed-2.0-pro", stream=False)
    await assistant.process_multiple(
        [Input(type=InputType.PAPER, path=str(offline_history))], "outline"
    )
    assert repo.db_path.read_bytes() == before
    assert [run["id"] for run in repo.get_recent_runs()] == [run_id]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "command", ["history", "stats", "show", "resume", "export"]
)
@pytest.mark.parametrize("directory_exists", [False, True])
async def test_missing_history_commands_do_not_create_database(
    command, directory_exists, offline_history, capsys
):
    db_dir = offline_history.parent / "db"
    if directory_exists:
        db_dir.mkdir()
    argv = [command]
    if command == "show":
        argv.append("1")
    if command == "export":
        argv.append(str(offline_history.parent / "history.json"))
    args = create_parser().parse_args(argv)
    with patch(
        "editor_assistant.cli.RunRepository",
        side_effect=AssertionError("Missing database opened a repository"),
    ):
        if command == "resume":
            await args.func(args)
        else:
            args.func(args)
    output = capsys.readouterr().out
    assert "--save-history" in output
    assert "runs.db" in output
    assert db_dir.exists() is directory_exists
    assert not (db_dir / "runs.db").exists()
    assert not (offline_history.parent / "history.json").exists()


@pytest.mark.asyncio
async def test_history_commands_query_existing_database(
    offline_history, capsys
):
    repo = RunRepository()
    source = offline_history
    input_id = repo.get_or_create_input(
        "paper", str(source), "paper", source.read_text()
    )
    run_id = repo.create_run("outline", "mock-model", [input_id])
    repo.add_output(run_id, "main", "Existing output")
    repo.add_token_usage(
        run_id,
        input_tokens=10,
        output_tokens=5,
        cost_input=0,
        cost_output=0,
        process_time=0.1,
    )
    for argv, expected in [
        (["history"], "mock-model"),
        (["history", "--search", "paper"], "paper"),
        (["stats"], "Total Runs: 1"),
        (["show", str(run_id), "--output"], "Existing output"),
        (["resume", "--dry-run"], "No runs were executed"),
    ]:
        args = create_parser().parse_args(argv)
        if args.command == "resume":
            await args.func(args)
        else:
            args.func(args)
        assert expected in capsys.readouterr().out
    for suffix in ["json", "csv"]:
        path = source.parent / f"history.{suffix}"
        args = create_parser().parse_args(["export", str(path)])
        args.func(args)
        assert "mock-model" in path.read_text()
        if suffix == "json":
            assert "Existing output" in path.read_text()
    assert repo.get_run_details(run_id)["status"] == "pending"


@pytest.mark.asyncio
async def test_resume_persists_new_outputs_and_usage(
    offline_history, offline_http
):
    repo = RunRepository()
    source = offline_history
    input_id = repo.get_or_create_input(
        "paper", str(source), "paper", source.read_text()
    )
    original = repo.create_run("outline", "doubao-seed-2.0-pro", [input_id])
    repo.update_run_status(original, "aborted")
    args = create_parser().parse_args(["resume"])
    await args.func(args)
    runs = repo.get_recent_runs()
    assert len(runs) == 2
    assert all(run["status"] == "success" for run in runs)
    new = next(run for run in runs if run["id"] != original)
    details = repo.get_run_details(new["id"])
    assert "Generated text" in details["outputs"][0]["content"]
    assert details["token_usage"]["input_tokens"] == 10


def test_existing_only_repository_never_creates_missing_database(tmp_path):
    path = tmp_path / "missing" / "runs.db"
    with pytest.raises(FileNotFoundError):
        RunRepository(path, create=False)
    assert not path.parent.exists()


def test_current_schema_repository_performs_no_writes(tmp_path, monkeypatch):
    path = tmp_path / "runs.db"
    repo = RunRepository(path)
    original = repo.create_run("outline", "mock", [])
    statements = []
    get_connection = database.get_connection

    def traced_connection(*args, **kwargs):
        conn = get_connection(*args, **kwargs)
        conn.set_trace_callback(statements.append)
        return conn

    monkeypatch.setattr(database, "get_connection", traced_connection)
    RunRepository(path, create=False)
    assert not any(
        sql.lstrip()
        .upper()
        .startswith(("BEGIN", "INSERT", "UPDATE", "CREATE", "ALTER"))
        for sql in statements
    )
    assert RunRepository(path).get_run_details(original)["task"] == "outline"


def test_existing_only_repository_does_not_recreate_deleted_database(tmp_path):
    path = tmp_path / "runs.db"
    RunRepository(path)
    repo = RunRepository(path, create=False)
    path.unlink()
    with pytest.raises(sqlite3.OperationalError):
        repo.get_recent_runs()
    assert not path.exists()
