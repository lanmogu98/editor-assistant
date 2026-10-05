"""Reconcile real HTTP traces, CLI outputs and public metrics offline."""

import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
RUNTIME = ROOT / "runtime"
source = (RUNTIME / "nobel-medicine-2025.md").read_text()
checks = []
evidence = []
for path in sorted(ROOT.glob("0[1-6]-*.json")):
    run = json.loads(path.read_text())
    metric = run["attempts"][0]
    folder = RUNTIME / run["label"]
    request = json.loads((folder / "request-1.json").read_text())
    request_without_tier = {
        key: value for key, value in request.items() if key != "service_tier"
    }
    payload_hash = hashlib.sha256(
        json.dumps(
            request_without_tier, sort_keys=True, ensure_ascii=False
        ).encode()
    ).hexdigest()
    assert payload_hash == metric["request_sha256_without_tier"]
    assert source in request["messages"][-1]["content"]
    content = []
    tiers = set()
    first_content = None
    first_token = None
    last_content = None
    last_usage = None
    done_at = None
    snapshots = []
    for line in (folder / "stream-1.jsonl").read_text().splitlines():
        recorded = json.loads(line)
        raw = recorded["line"]
        if not raw.startswith("data:"):
            continue
        raw = raw[5:].strip()
        if raw == "[DONE]":
            done_at = recorded["elapsed_s"]
            continue
        event = json.loads(raw)
        tier = event.get("service_tier")
        if tier:
            tiers.add(tier)
        if event.get("usage"):
            last_usage = event["usage"]
        if not snapshots or event.get("usage"):
            snapshots.append(
                {
                    "elapsed_s": recorded["elapsed_s"],
                    **{
                        key: event[key]
                        for key in (
                            "id",
                            "model",
                            "object",
                            "service_tier",
                            "service_status",
                            "usage",
                        )
                        if key in event
                    },
                    "finish_reasons": [
                        choice["finish_reason"]
                        for choice in event.get("choices", [])
                        if choice.get("finish_reason")
                    ],
                }
            )
        for choice in event.get("choices", []):
            delta = choice.get("delta", {})
            text = delta.get("content") or ""
            reasoning = delta.get("reasoning_content") or ""
            if (text or reasoning) and first_token is None:
                first_token = recorded["elapsed_s"]
            if text:
                content.append(text)
                if first_content is None:
                    first_content = recorded["elapsed_s"]
                last_content = recorded["elapsed_s"]
    assert sorted(tiers) == sorted(metric["response_tiers"])
    assert first_content == metric["first_content_s"]
    assert first_token == metric["first_token_s"]
    assert last_content == metric["last_content_s"]
    assert done_at == metric["api_end_s"]
    assert last_usage == metric["usage"]
    translation = "".join(content)
    assert translation == (folder / "main.md").read_text()
    quality = {
        "label": run["label"],
        "translation_lines": len(translation.splitlines()),
        "source_lines": len(source.splitlines()),
        "translation_nonblank_lines": sum(
            bool(line.strip()) for line in translation.splitlines()
        ),
        "source_nonblank_lines": sum(
            bool(line.strip()) for line in source.splitlines()
        ),
        "translation_headings": sum(
            line.startswith("#") for line in translation.splitlines()
        ),
        "source_headings": sum(
            line.startswith("#") for line in source.splitlines()
        ),
        "chinese_chars": len(re.findall(r"[\u4e00-\u9fff]", translation)),
        "technical_anchors": {
            term: term in translation
            for term in ("FOXP3", "CD4", "CD25", "IPEX")
        },
        "translation_sha256": hashlib.sha256(translation.encode()).hexdigest(),
        "trace_sha256": hashlib.sha256(
            (folder / "stream-1.jsonl").read_bytes()
        ).hexdigest(),
        "reconciled": True,
    }
    checks.append(quality)
    evidence.append({"label": run["label"], "events": snapshots})
assert len(checks) == 6
for name, value in (
    ("quality.json", checks),
    ("response-evidence.json", evidence),
):
    (ROOT / name).write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    )
print(
    json.dumps({"runs_reconciled": len(checks), "quality": checks}, indent=2)
)
