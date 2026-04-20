# -*- coding: utf-8 -*-
"""Hindsight queue flush tests.

Run:
  cd /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/adhd-assistant
  python3 -m tests.test_hindsight_flush
"""

import json
import os
import sys
import tempfile
import threading
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from scripts import adhd_assistant_hindsight_flush as flush_module  # noqa: E402


def _assert(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print(f"  ok  {msg}")


def _read_lines(path: Path):
    if not path.exists():
        return []
    return path.read_text(encoding="utf-8").splitlines()


def test_empty_queue_returns_ok_and_logs_summary():
    print("test_empty_queue_returns_ok_and_logs_summary")
    with tempfile.TemporaryDirectory() as tmp:
        runtime_dir = Path(tmp) / "runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        queue_path = runtime_dir / "hindsight_queue.jsonl"
        log_path = runtime_dir / "logs" / "hindsight_flush.jsonl"

        result = flush_module.flush_queue(
            queue_path=queue_path,
            log_path=log_path,
            retain_entry=lambda entry, raw_line: None,
        )

        _assert(result["status"] == "ok", "empty queue returns ok")
        _assert(result["processed"] == 0, "empty queue processed count is zero")
        _assert(result["remaining"] == 0, "empty queue remaining count is zero")
        _assert(log_path.exists(), "flush log created")


def test_flush_stops_on_first_failure_and_preserves_remaining_lines():
    print("test_flush_stops_on_first_failure_and_preserves_remaining_lines")
    with tempfile.TemporaryDirectory() as tmp:
        runtime_dir = Path(tmp) / "runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        queue_path = runtime_dir / "hindsight_queue.jsonl"
        log_path = runtime_dir / "logs" / "hindsight_flush.jsonl"

        entries = [
            {"context": "ctx", "content": "ok-1", "at": "2026-04-19T14:00:00+02:00"},
            {"context": "ctx", "content": "boom", "at": "2026-04-19T14:01:00+02:00"},
            {"context": "ctx", "content": "ok-3", "at": "2026-04-19T14:02:00+02:00"},
        ]
        raw_lines = [json.dumps(item, ensure_ascii=False) for item in entries]
        queue_path.write_text("\n".join(raw_lines) + "\n", encoding="utf-8")

        seen = []

        def fake_retain(entry, raw_line):
            seen.append(entry["content"])
            if entry["content"] == "boom":
                raise RuntimeError("retain exploded")

        result = flush_module.flush_queue(
            queue_path=queue_path,
            log_path=log_path,
            retain_entry=fake_retain,
        )

        _assert(result["status"] == "partial", "partial returned after mid-queue failure")
        _assert(result["processed"] == 1, "only successful entries are counted as processed")
        _assert(result["remaining"] == 2, "failed entry and tail stay in queue")
        _assert(seen == ["ok-1", "boom"], "processing stops at first failure")
        _assert(_read_lines(queue_path) == raw_lines[1:], "queue keeps failed line plus remaining tail")


def test_invalid_json_line_is_preserved_in_queue():
    print("test_invalid_json_line_is_preserved_in_queue")
    with tempfile.TemporaryDirectory() as tmp:
        runtime_dir = Path(tmp) / "runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        queue_path = runtime_dir / "hindsight_queue.jsonl"
        log_path = runtime_dir / "logs" / "hindsight_flush.jsonl"

        raw_lines = [
            "{not valid json}",
            json.dumps({"context": "ctx", "content": "ok-2"}, ensure_ascii=False),
        ]
        queue_path.write_text("\n".join(raw_lines) + "\n", encoding="utf-8")

        result = flush_module.flush_queue(
            queue_path=queue_path,
            log_path=log_path,
            retain_entry=lambda entry, raw_line: None,
        )

        _assert(result["status"] == "error", "invalid json returns error when nothing processed")
        _assert(result["processed"] == 0, "invalid json prevents processing")
        _assert(result["remaining"] == 2, "invalid json line and remaining tail are preserved")
        _assert(_read_lines(queue_path) == raw_lines, "queue remains unchanged when first line is invalid")


def test_document_id_is_deterministic_for_same_entry():
    print("test_document_id_is_deterministic_for_same_entry")
    entry = {"context": "ctx", "content": "same", "at": "2026-04-19T14:00:00+02:00"}
    raw_line = json.dumps(entry, ensure_ascii=False)

    doc_a = flush_module.build_document_id(entry, raw_line)
    doc_b = flush_module.build_document_id(entry, raw_line)

    _assert(doc_a == doc_b, "document id is deterministic")
    _assert(doc_a.startswith("adhd-assistant-hindsight-flush:"), "document id has stable prefix")


def test_sync_retain_is_preferred_when_client_exposes_both_sync_and_async_methods():
    print("test_sync_retain_is_preferred_when_client_exposes_both_sync_and_async_methods")

    class FakeClient:
        def __init__(self):
            self.calls = []

        def retain(self, **kwargs):
            self.calls.append(("retain", kwargs))
            return {"ok": True}

        async def aretain(self, **kwargs):
            self.calls.append(("aretain", kwargs))
            return {"ok": True}

    client = FakeClient()
    retain_entry = flush_module.make_retain_entry(client, "hermes")
    entry = {"context": "ctx", "content": "sync-first"}
    raw_line = json.dumps(entry, ensure_ascii=False)

    retain_entry(entry, raw_line)

    _assert(client.calls[0][0] == "retain", "sync retain is preferred over async retain")


def test_retain_entry_factory_is_built_only_after_locked_queue_read():
    print("test_retain_entry_factory_is_built_only_after_locked_queue_read")
    with tempfile.TemporaryDirectory() as tmp:
        runtime_dir = Path(tmp) / "runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        queue_path = runtime_dir / "hindsight_queue.jsonl"
        log_path = runtime_dir / "logs" / "hindsight_flush.jsonl"
        raw_line = json.dumps({"context": "ctx", "content": "factory-entry"}, ensure_ascii=False)
        queue_path.write_text(raw_line + "\n", encoding="utf-8")

        built = []

        def build_retain_entry():
            built.append("built")
            return lambda entry, raw: None

        result = flush_module.flush_queue(
            queue_path=queue_path,
            log_path=log_path,
            retain_entry_factory=build_retain_entry,
        )

        _assert(result["status"] == "ok", "factory-created retain entry flushes queue")
        _assert(built == ["built"], "retain entry factory is invoked exactly once")


def test_locked_append_survives_while_flush_is_running():
    print("test_locked_append_survives_while_flush_is_running")
    with tempfile.TemporaryDirectory() as tmp:
        runtime_dir = Path(tmp) / "runtime"
        runtime_dir.mkdir(parents=True, exist_ok=True)
        queue_path = runtime_dir / "hindsight_queue.jsonl"
        log_path = runtime_dir / "logs" / "hindsight_flush.jsonl"

        initial_entries = [
            {"context": "ctx", "content": "ok-1"},
            {"context": "ctx", "content": "boom"},
        ]
        initial_lines = [json.dumps(item, ensure_ascii=False) for item in initial_entries]
        queue_path.write_text("\n".join(initial_lines) + "\n", encoding="utf-8")

        appended_line = json.dumps({"context": "ctx", "content": "late-entry"}, ensure_ascii=False)

        def append_late():
            time.sleep(0.1)
            flush_module.append_queue_line(queue_path, appended_line)

        def fake_retain(entry, raw_line):
            if entry["content"] == "ok-1":
                time.sleep(0.3)
            if entry["content"] == "boom":
                raise RuntimeError("retain exploded")

        worker = threading.Thread(target=append_late)
        worker.start()
        result = flush_module.flush_queue(
            queue_path=queue_path,
            log_path=log_path,
            retain_entry=fake_retain,
        )
        worker.join(timeout=2)

        _assert(result["status"] == "partial", "flush still reports partial on retained failure")
        _assert(worker.is_alive() is False, "append worker finishes")
        _assert(
            _read_lines(queue_path) == [initial_lines[1], appended_line],
            "late append survives flush and remains after the failed line",
        )


if __name__ == "__main__":
    tests = [
        test_empty_queue_returns_ok_and_logs_summary,
        test_flush_stops_on_first_failure_and_preserves_remaining_lines,
        test_invalid_json_line_is_preserved_in_queue,
        test_document_id_is_deterministic_for_same_entry,
        test_sync_retain_is_preferred_when_client_exposes_both_sync_and_async_methods,
        test_retain_entry_factory_is_built_only_after_locked_queue_read,
        test_locked_append_survives_while_flush_is_running,
    ]
    failures = 0
    for test in tests:
        try:
            test()
        except AssertionError as exc:
            failures += 1
            print(f"  FAIL {test.__name__}: {exc}")
        except Exception as exc:
            failures += 1
            print(f"  ERROR {test.__name__}: {exc!r}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    sys.exit(1 if failures else 0)
