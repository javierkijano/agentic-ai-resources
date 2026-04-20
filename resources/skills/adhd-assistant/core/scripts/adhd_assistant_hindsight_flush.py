#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Skill-local hindsight flush launcher.

The real flush logic lives inside the skill and cron jobs call this module directly from the skill tree."""

from __future__ import annotations

import asyncio
import fcntl
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

DEFAULT_CLOUD_URL = "https://api.hindsight.vectorize.io"
DEFAULT_LOCAL_URL = "http://localhost:8888"

HERMES_HOME = Path(os.environ.get("HERMES_HOME", str(Path.home() / ".hermes")))
RUNTIME_DIR = HERMES_HOME / "adhd_assistant"
QUEUE_PATH = RUNTIME_DIR / "hindsight_queue.jsonl"
LOG_PATH = RUNTIME_DIR / "logs" / "hindsight_flush.jsonl"

RetainEntry = Callable[[dict[str, Any], str], Any]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def read_queue_lines(queue_path: Path) -> list[str]:
    if not queue_path.exists():
        return []
    return [line for line in queue_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def append_log(log_path: Path, summary: dict[str, Any]) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(summary)
    payload.setdefault("at", utc_now_iso())
    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False) + "\n")


def build_document_id(entry: dict[str, Any], raw_line: str) -> str:
    seed = "\u241f".join(
        [
            str(entry.get("at", "")),
            str(entry.get("context", "")),
            str(entry.get("content", "")),
            raw_line,
        ]
    )
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return f"adhd-assistant-hindsight-flush:{digest}"


def parse_timestamp(value: Any) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def _lock_file(handle) -> None:
    fcntl.flock(handle.fileno(), fcntl.LOCK_EX)


def _unlock_file(handle) -> None:
    fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def append_queue_line(queue_path: Path, raw_line: str) -> None:
    queue_path.parent.mkdir(parents=True, exist_ok=True)
    with queue_path.open("a+", encoding="utf-8") as handle:
        _lock_file(handle)
        try:
            handle.seek(0, os.SEEK_END)
            handle.write(raw_line + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        finally:
            _unlock_file(handle)


def load_hindsight_config(hermes_home: Path = HERMES_HOME) -> dict[str, Any]:
    config_path = hermes_home / "hindsight" / "config.json"
    raw: dict[str, Any] = {}
    if config_path.exists():
        raw = json.loads(config_path.read_text(encoding="utf-8"))

    mode = raw.get("mode") or os.environ.get("HINDSIGHT_MODE", "cloud")
    banks = raw.get("banks") or {}
    hermes_bank = banks.get("hermes") or {}

    config = {
        "mode": mode,
        "bank_id": raw.get("bank_id") or hermes_bank.get("bankId") or os.environ.get("HINDSIGHT_BANK_ID", "hermes"),
        "api_key": raw.get("apiKey") or raw.get("api_key") or os.environ.get("HINDSIGHT_API_KEY", ""),
        "api_url": raw.get("api_url") or raw.get("apiUrl") or os.environ.get(
            "HINDSIGHT_API_URL",
            DEFAULT_LOCAL_URL if mode == "local_external" else DEFAULT_CLOUD_URL,
        ),
        "profile": raw.get("profile") or os.environ.get("HINDSIGHT_PROFILE", "hermes"),
        "llm_provider": raw.get("llm_provider") or os.environ.get("HINDSIGHT_LLM_PROVIDER", ""),
        "llm_api_key": raw.get("llmApiKey") or raw.get("llm_api_key") or os.environ.get("HINDSIGHT_LLM_API_KEY", ""),
        "llm_model": raw.get("llm_model") or os.environ.get("HINDSIGHT_LLM_MODEL", ""),
        "llm_base_url": raw.get("llm_base_url") or os.environ.get("HINDSIGHT_LLM_BASE_URL", ""),
    }
    return config


def make_client(config: dict[str, Any]):
    mode = config.get("mode") or "cloud"
    if mode == "local_embedded":
        from hindsight import HindsightEmbedded

        HindsightEmbedded.__del__ = lambda self: None
        llm_provider = config.get("llm_provider") or "openai"
        if llm_provider in {"openai_compatible", "openrouter"}:
            llm_provider = "openai"
        return HindsightEmbedded(
            profile=config.get("profile") or "hermes",
            llm_provider=llm_provider,
            llm_api_key=config.get("llm_api_key") or "",
            llm_model=config.get("llm_model") or "",
            llm_base_url=config.get("llm_base_url") or None,
            ui=False,
        )

    from hindsight_client import Hindsight

    kwargs: dict[str, Any] = {
        "base_url": config.get("api_url") or DEFAULT_CLOUD_URL,
        "timeout": 30.0,
    }
    api_key = config.get("api_key") or ""
    if api_key:
        kwargs["api_key"] = api_key
    return Hindsight(**kwargs)


def make_retain_entry(client: Any, bank_id: str) -> RetainEntry:
    def retain_entry(entry: dict[str, Any], raw_line: str) -> Any:
        kwargs: dict[str, Any] = {
            "bank_id": bank_id,
            "content": entry.get("content", ""),
            "document_id": build_document_id(entry, raw_line),
        }
        context = entry.get("context")
        if context:
            kwargs["context"] = context
        timestamp = parse_timestamp(entry.get("at"))
        if timestamp is not None:
            kwargs["timestamp"] = timestamp
        tags = entry.get("tags")
        if tags:
            kwargs["tags"] = [str(tag) for tag in tags]
        metadata = entry.get("metadata")
        if isinstance(metadata, dict) and metadata:
            kwargs["metadata"] = {str(key): str(value) for key, value in metadata.items()}

        sync_retain = getattr(client, "retain", None)
        if sync_retain is not None:
            return sync_retain(**kwargs)

        async_retain = getattr(client, "aretain", None)
        if async_retain is not None:
            return asyncio.run(async_retain(**kwargs))
        raise AttributeError("client does not expose retain or aretain")

    return retain_entry


def close_client(client: Any) -> None:
    async_close = getattr(client, "aclose", None)
    if async_close is not None:
        asyncio.run(async_close())
        return

    close = getattr(client, "close", None)
    if close is not None:
        close()


def flush_queue(
    queue_path: Path = QUEUE_PATH,
    log_path: Path = LOG_PATH,
    retain_entry: RetainEntry | None = None,
    retain_entry_factory: Callable[[], RetainEntry] | None = None,
) -> dict[str, Any]:
    queue_path.parent.mkdir(parents=True, exist_ok=True)

    with queue_path.open("a+", encoding="utf-8") as handle:
        _lock_file(handle)
        try:
            handle.seek(0)
            raw_lines = [line.rstrip("\n") for line in handle if line.strip()]

            if not raw_lines:
                summary = {
                    "at": utc_now_iso(),
                    "status": "ok",
                    "reason": "empty_queue",
                    "processed": 0,
                    "remaining": 0,
                }
                append_log(log_path, summary)
                return summary

            if retain_entry is None:
                if retain_entry_factory is None:
                    raise RuntimeError("retain_entry is required when the queue is not empty")
                retain_entry = retain_entry_factory()

            processed = 0
            remaining_lines: list[str] = []
            reason = ""

            for index, raw_line in enumerate(raw_lines):
                try:
                    entry = json.loads(raw_line)
                except json.JSONDecodeError as exc:
                    reason = f"invalid_json line={index + 1}: {exc.msg}"
                    remaining_lines = raw_lines[index:]
                    break

                try:
                    retain_entry(entry, raw_line)
                except Exception as exc:
                    reason = str(exc)
                    remaining_lines = raw_lines[index:]
                    break

                processed += 1

            if reason:
                status = "partial" if processed > 0 else "error"
            else:
                status = "ok"

            handle.seek(0)
            handle.truncate()
            for line in remaining_lines:
                handle.write(line + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        finally:
            _unlock_file(handle)

    summary = {
        "at": utc_now_iso(),
        "status": status,
        "processed": processed,
        "remaining": len(remaining_lines),
    }
    if reason:
        summary["reason"] = reason

    append_log(log_path, summary)
    return summary


def main() -> int:
    client_holder: dict[str, Any] = {}

    def build_runtime_retain_entry() -> RetainEntry:
        config = load_hindsight_config(HERMES_HOME)
        client = make_client(config)
        client_holder["client"] = client
        return make_retain_entry(client, config.get("bank_id") or "hermes")

    try:
        summary = flush_queue(
            queue_path=QUEUE_PATH,
            log_path=LOG_PATH,
            retain_entry_factory=build_runtime_retain_entry,
        )
        print(json.dumps(summary, ensure_ascii=False))
        return 0 if summary.get("status") == "ok" else 1
    except Exception as exc:
        summary = {
            "at": utc_now_iso(),
            "status": "error",
            "processed": 0,
            "remaining": len(read_queue_lines(QUEUE_PATH)),
            "reason": str(exc),
        }
        append_log(LOG_PATH, summary)
        print(json.dumps(summary, ensure_ascii=False))
        return 1
    finally:
        client = client_holder.get("client")
        if client is not None:
            try:
                close_client(client)
            except Exception:
                pass


if __name__ == "__main__":
    raise SystemExit(main())
