"""Real translate CLI experiment with environment-only credentials."""

import argparse
import asyncio
import contextlib
import csv
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import sqlite3
import statistics
import subprocess
import time
from datetime import datetime, timezone
from unittest.mock import patch

import httpx

ROOT = Path(__file__).resolve().parent
RUNTIME = ROOT / "runtime"
SOURCE_URL = (
    "https://www.nobelprize.org/prizes/medicine/2025/popular-information/"
)
MODEL = "doubao-seed-2.1-lite"


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def digest(value):
    if isinstance(value, dict):
        value = json.dumps(value, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(value).hexdigest()


def head(path):
    return subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
    ).strip()


def prepare():
    from editor_assistant.clean_html_to_md import CleanHTML2Markdown
    from editor_assistant.config.llm_models import get_model_details

    RUNTIME.mkdir(parents=True, exist_ok=True)
    response = httpx.get(SOURCE_URL, follow_redirects=True, timeout=60)
    response.raise_for_status()
    html_path = RUNTIME / "source.html"
    html_path.write_text(response.text)
    article = CleanHTML2Markdown().convert(str(html_path))
    if article is None or not article.content:
        raise RuntimeError("Package HTML extraction failed")
    content = article.content
    required = ("FOXP3", "Key publications", "CD25", "Brunkow", "Sakaguchi")
    if not all(term in content for term in required):
        raise RuntimeError("Extracted article does not contain all anchors")
    source_path = RUNTIME / "nobel-medicine-2025.md"
    source_path.write_text(content)
    provider, model = get_model_details(MODEL)
    import llm_exec_core

    manifest = {
        "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_url": SOURCE_URL,
        "http_status": response.status_code,
        "html_bytes": len(response.content),
        "html_sha256": digest(response.content),
        "extractor": article.converter,
        "article_title": article.title,
        "input_chars": len(content),
        "input_lines": len(content.splitlines()),
        "input_words": len(re.findall(r"\b[\w’'-]+\b", content)),
        "input_sha256": digest(source_path.read_bytes()),
        "input_file": "runtime/nobel-medicine-2025.md",
        "source_heading_count": sum(
            line.startswith("#") for line in content.splitlines()
        ),
        "model_alias": MODEL,
        "model_id": model.id,
        "endpoint": provider.api_base_url,
        "temperature": (
            model.temperature
            if model.temperature is not None
            else provider.temperature
        ),
        "max_tokens": (
            model.max_tokens
            if model.max_tokens is not None
            else provider.max_tokens
        ),
        "thinking_cli": "low",
        "stream": True,
        "schedule": ["default", "fast", "fast", "default", "default", "fast"],
        "python": platform.python_version(),
        "platform": platform.platform(),
        "app_head": head(ROOT.parents[1]),
        "core_head": head(Path(llm_exec_core.__file__).resolve().parents[2]),
        "core_version": llm_exec_core.__version__,
        "credential": (
            "DOUBAO_API_KEY from inherited environment; "
            "value never recorded"
        ),
    }
    write_json(ROOT / "manifest.json", manifest)
    print(
        json.dumps(
            {
                k: manifest[k]
                for k in (
                    "http_status",
                    "input_chars",
                    "input_words",
                    "model_id",
                    "core_head",
                )
            },
            ensure_ascii=False,
        )
    )


def run_one(label, tier):
    from editor_assistant import cli

    if not os.environ.get("DOUBAO_API_KEY"):
        raise RuntimeError(
            "Set DOUBAO_API_KEY in the environment before running"
        )
    folder = RUNTIME / label
    folder.mkdir(parents=True, exist_ok=False)
    os.environ["EDITOR_ASSISTANT_TEST_DB_DIR"] = str(folder)
    arguments = [
        "editor-assistant",
        "translate",
        str(RUNTIME / "nobel-medicine-2025.md"),
        "--model",
        MODEL,
        "--thinking",
        "low",
    ]
    if tier == "fast":
        arguments += ["--service-tier", "fast"]
    original_client = httpx.AsyncClient
    attempts = []
    opened_clients = []

    async def on_request(request):
        payload = json.loads(request.content)
        normalized = {k: v for k, v in payload.items() if k != "service_tier"}
        metric = {
            "number": len(attempts) + 1,
            "started_at_utc": datetime.now(timezone.utc).isoformat(),
            "request_tier": payload.get("service_tier"),
            "request_model": payload.get("model"),
            "request_sha256_without_tier": digest(normalized),
            "request_controls": {
                k: v for k, v in payload.items() if k != "messages"
            },
            "prompt_chars": sum(
                len(m.get("content", "")) for m in payload.get("messages", [])
            ),
            "response_tiers": [],
            "finish_reasons": [],
            "service_status": [],
            "content_chars": 0,
            "reasoning_chars": 0,
            "sse_event_count": 0,
            "done_received": False,
            "first_event_s": None,
            "first_token_s": None,
            "first_content_s": None,
            "first_reasoning_s": None,
            "last_content_s": None,
        }
        attempts.append(metric)
        request.extensions["experiment_start"] = time.perf_counter()
        request.extensions["experiment_metric"] = metric
        write_json(folder / f"request-{metric['number']}.json", payload)

    async def on_response(response):
        metric = response.request.extensions["experiment_metric"]
        start = response.request.extensions["experiment_start"]
        metric["status_code"] = response.status_code
        metric["headers_s"] = time.perf_counter() - start
        metric["http_version"] = response.http_version
        metric["response_request_id"] = response.headers.get("x-request-id")
        if response.status_code != 200:
            raw = await response.aread()
            (folder / f"error-{metric['number']}.txt").write_bytes(raw)
            metric["api_end_s"] = time.perf_counter() - start
            return
        original_lines = response.aiter_lines

        async def record_lines():
            with (folder / f"stream-{metric['number']}.jsonl").open(
                "w"
            ) as trace:
                async for line in original_lines():
                    elapsed = time.perf_counter() - start
                    trace.write(
                        json.dumps(
                            {"elapsed_s": elapsed, "line": line},
                            ensure_ascii=False,
                        )
                        + "\n"
                    )
                    if line.startswith("data:"):
                        data = line[5:].strip()
                        if data == "[DONE]":
                            metric["done_received"] = True
                            metric["api_end_s"] = elapsed
                        else:
                            event = json.loads(data)
                            metric["sse_event_count"] += 1
                            if metric["first_event_s"] is None:
                                metric["first_event_s"] = elapsed
                            for key, field in (
                                ("service_tier", "response_tiers"),
                                ("service_status", "service_status"),
                            ):
                                value = event.get(key)
                                if (
                                    value is not None
                                    and value not in metric[field]
                                ):
                                    metric[field].append(value)
                            for key in ("id", "model"):
                                if key in event:
                                    metric["response_" + key] = event[key]
                            if event.get("usage") is not None:
                                metric["usage"] = event["usage"]
                            for choice in event.get("choices", []):
                                delta = choice.get("delta", {})
                                content = delta.get("content") or ""
                                reasoning = (
                                    delta.get("reasoning_content") or ""
                                )
                                if content or reasoning:
                                    if metric["first_token_s"] is None:
                                        metric["first_token_s"] = elapsed
                                if content:
                                    if metric["first_content_s"] is None:
                                        metric["first_content_s"] = elapsed
                                    metric["last_content_s"] = elapsed
                                    metric["content_chars"] += len(content)
                                if reasoning:
                                    if metric["first_reasoning_s"] is None:
                                        metric["first_reasoning_s"] = elapsed
                                    metric["reasoning_chars"] += len(reasoning)
                                finish = choice.get("finish_reason")
                                if (
                                    finish
                                    and finish not in metric["finish_reasons"]
                                ):
                                    metric["finish_reasons"].append(finish)
                    yield line

        response.aiter_lines = record_lines

    class RecordingClient(original_client):
        def __init__(self, *args, **kwargs):
            hooks = kwargs.setdefault("event_hooks", {})
            hooks.setdefault("request", []).append(on_request)
            hooks.setdefault("response", []).append(on_response)
            super().__init__(*args, **kwargs)
            opened_clients.append(self)

    async def invoke():
        try:
            parsed = cli.create_parser().parse_args(arguments[1:])
            await parsed.func(parsed)
        finally:
            for client in opened_clients:
                await client.aclose()

    started = time.perf_counter()
    error_type = None
    with (folder / "cli-output.txt").open("w") as output:
        with (
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(output),
        ):
            try:
                with patch("httpx.AsyncClient", RecordingClient):
                    asyncio.run(invoke())
            except Exception as exc:
                error_type = type(exc).__name__
    total = time.perf_counter() - started
    db_run = None
    outputs = []
    db_path = folder / "runs.db"
    if db_path.is_file():
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        try:
            row = conn.execute(
                "SELECT id, status, service_tier FROM runs "
                "ORDER BY id DESC LIMIT 1"
            ).fetchone()
            db_run = dict(row) if row else None
            if row:
                for result in conn.execute(
                    "SELECT output_type, content FROM outputs WHERE run_id=?",
                    (row["id"],),
                ):
                    text = result["content"]
                    path = folder / (result["output_type"] + ".md")
                    path.write_text(text)
                    outputs.append(
                        {
                            "type": result["output_type"],
                            "chars": len(text),
                            "lines": len(text.splitlines()),
                            "sha256": digest(text.encode()),
                            "file": str(path.relative_to(ROOT)),
                            "chinese_chars": len(
                                re.findall(r"[\u4e00-\u9fff]", text)
                            ),
                            "headings": sum(
                                line.startswith("#")
                                for line in text.splitlines()
                            ),
                        }
                    )
        finally:
            conn.close()
    result = {
        "label": label,
        "mode": tier,
        "argv": [
            "editor-assistant",
            "translate",
            "runtime/nobel-medicine-2025.md",
            *arguments[3:],
        ],
        "handler_elapsed_s": total,
        "error_type": error_type,
        "db_run": db_run,
        "outputs": outputs,
        "attempts": attempts,
    }
    write_json(ROOT / (label + ".json"), result)
    summary = {
        "label": label,
        "db_status": db_run.get("status") if db_run else None,
        "attempts": len(attempts),
        "actual_tiers": (
            attempts[-1].get("response_tiers") if attempts else None
        ),
        "api_s": attempts[-1].get("api_end_s") if attempts else None,
        "first_content_s": (
            attempts[-1].get("first_content_s") if attempts else None
        ),
    }
    print(json.dumps(summary, ensure_ascii=False), flush=True)
    if not db_run or db_run["status"] != "success" or error_type:
        raise SystemExit(1)


def analyze():
    rows = []
    fingerprints = set()
    for path in sorted(ROOT.glob("0[1-6]-*.json")):
        result = json.loads(path.read_text())
        assert result["db_run"]["status"] == "success"
        assert (
            len(result["attempts"]) == 1
        ), "Retries cannot be compared as single attempts"
        attempt = result["attempts"][0]
        assert attempt["status_code"] == 200 and attempt["done_received"]
        assert attempt["finish_reasons"] == ["stop"]
        expected = "fast" if result["mode"] == "fast" else None
        assert attempt["request_tier"] == expected
        assert result["db_run"]["service_tier"] == expected
        assert attempt["request_model"] == "doubao-seed-2-1-lite-260915"
        assert attempt["response_model"] == attempt["request_model"]
        fingerprints.add(attempt["request_sha256_without_tier"])
        usage = attempt.get("usage", {})
        reasoning_tokens = usage.get("completion_tokens_details", {}).get(
            "reasoning_tokens", 0
        )
        completion_tokens = usage.get("completion_tokens", 0)
        end = attempt["api_end_s"]
        visible_time = attempt["last_content_s"] - attempt["first_content_s"]
        first_token = attempt["first_token_s"]
        row = {
            "label": result["label"],
            "mode": result["mode"],
            "actual_tiers": ",".join(attempt["response_tiers"]),
            "headers_s": attempt["headers_s"],
            "first_token_s": first_token,
            "first_content_s": attempt["first_content_s"],
            "api_s": end,
            "handler_s": result["handler_elapsed_s"],
            "prompt_tokens": usage.get("prompt_tokens"),
            "cached_tokens": usage.get("prompt_tokens_details", {}).get(
                "cached_tokens", 0
            ),
            "completion_tokens": completion_tokens,
            "reasoning_tokens": reasoning_tokens,
            "visible_tokens": completion_tokens - reasoning_tokens,
            "content_chars": attempt["content_chars"],
            "decode_tokens_s": completion_tokens / (end - first_token),
            "visible_chars_s": attempt["content_chars"] / visible_time,
            "request_id": attempt.get("response_id"),
        }
        rows.append(row)
    assert len(rows) == 6, "Expected three complete paired comparisons"
    assert (
        len(fingerprints) == 1
    ), "Only service_tier may differ between payloads"
    summary = {
        "runs": len(rows),
        "same_payload_except_tier": True,
        "metrics": {},
    }
    for field in (
        "first_token_s",
        "first_content_s",
        "api_s",
        "handler_s",
        "decode_tokens_s",
        "visible_chars_s",
        "completion_tokens",
        "reasoning_tokens",
    ):
        grouped = {
            mode: [row[field] for row in rows if row["mode"] == mode]
            for mode in ("default", "fast")
        }
        summary["metrics"][field] = {
            mode: {
                "median": statistics.median(values),
                "min": min(values),
                "max": max(values),
                "mean": statistics.mean(values),
            }
            for mode, values in grouped.items()
        }
    summary["fast_actual_tiers"] = [
        row["actual_tiers"] for row in rows if row["mode"] == "fast"
    ]
    write_json(ROOT / "summary.json", summary)
    with (ROOT / "metrics.csv").open("w") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=list(rows[0]), lineterminator="\n"
        )
        writer.writeheader()
        writer.writerows(rows)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["prepare", "run", "analyze"])
    parser.add_argument("--label")
    parser.add_argument("--tier", choices=["default", "fast"])
    args = parser.parse_args()
    if args.command == "prepare":
        prepare()
    elif args.command == "run":
        if args.label is None or args.tier is None:
            parser.error("run requires --label and --tier")
        run_one(args.label, args.tier)
    else:
        analyze()
