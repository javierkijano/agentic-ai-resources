# -*- coding: utf-8 -*-
"""Web monitor service tests.

Run:
  cd /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/adhd-assistant
  python3 -m tests.test_webapp_monitoring
"""

import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from fastapi.testclient import TestClient  # noqa: E402

import webapp.app as webapp_app_module  # noqa: E402
from webapp.services.runtime_monitor import RuntimeMonitor, RuntimePaths  # noqa: E402


def _assert(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print(f"  ok  {msg}")


def _seed_runtime(tmp_dir: str) -> RuntimePaths:
    hermes_home = Path(tmp_dir) / ".hermes"
    runtime_dir = hermes_home / "adhd_assistant"
    logs_dir = runtime_dir / "logs"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    logs_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone(timedelta(hours=2)))

    state = {
        "commitments": {
            "tasks": [
                {
                    "id": "t1",
                    "title": "Pagar impuesto",
                    "status": "pending",
                    "deadline": (now - timedelta(hours=1)).isoformat(),
                    "priority": 1,
                    "project": "legal",
                },
                {
                    "id": "t2",
                    "title": "Enviar correo",
                    "status": "in_progress",
                    "deadline": (now + timedelta(hours=5)).isoformat(),
                    "priority": 2,
                    "project": "trabajo",
                },
                {
                    "id": "t3",
                    "title": "Planificar semana",
                    "status": "pending",
                    "priority": 3,
                    "project": "personal",
                },
            ],
            "appointments": [
                {
                    "id": "a1",
                    "title": "Reunión",
                    "starts_at": (now + timedelta(minutes=20)).isoformat(),
                }
            ],
            "events": [],
            "routines": [],
            "checklists": [],
        },
        "support": {
            "reminders": [
                {
                    "id": "r1",
                    "message": "Llamar proveedor",
                    "status": "scheduled",
                    "due_at": (now - timedelta(minutes=10)).isoformat(),
                }
            ],
            "open_loops": ["loop-1"],
            "recommendations": ["rec-1", "rec-2"],
        },
        "history": {
            "last_tick_at": now.isoformat(),
            "recent_events": [
                {
                    "at": now.isoformat(),
                    "kind": "test",
                    "summary": "fixture",
                }
            ],
        },
        "meta": {"active_schema_version": "2.0.0"},
    }

    config = {
        "profile": {"timezone": "Europe/Madrid"},
        "preferences": {"primary_mode": "operator", "coaching_level": "contextual"},
        "delivery": {"default_channel": "telegram"},
    }

    queue_lines = [
        {"context": "adhd-assistant:event", "content": "event-1"},
        {"context": "adhd-assistant:event", "content": "event-2"},
    ]

    log_entry = {
        "status": "ok",
        "sent": True,
        "reason": "due_reminder",
        "at": now.isoformat(),
    }

    state_path = runtime_dir / "state.json"
    config_path = runtime_dir / "config.yaml"
    queue_path = runtime_dir / "hindsight_queue.jsonl"
    log_path = logs_dir / "tick-20260418.jsonl"

    state_path.write_text(json.dumps(state, ensure_ascii=False), encoding="utf-8")
    config_path.write_text(yaml.safe_dump(config, allow_unicode=True), encoding="utf-8")
    queue_path.write_text(
        "\n".join(json.dumps(x, ensure_ascii=False) for x in queue_lines) + "\n",
        encoding="utf-8",
    )
    log_path.write_text(json.dumps(log_entry, ensure_ascii=False) + "\n", encoding="utf-8")

    return RuntimePaths(
        skill_dir=SKILL_DIR,
        hermes_home=hermes_home,
        runtime_dir=runtime_dir,
        state_path=state_path,
        config_path=config_path,
        hindsight_queue_path=queue_path,
        logs_dir=logs_dir,
        legacy_tasks_path=hermes_home / "tasks" / "tasks.json",
    )


def test_summary_counts_and_latest_log():
    print("test_summary_counts_and_latest_log")
    with tempfile.TemporaryDirectory() as tmp:
        paths = _seed_runtime(tmp)
        monitor = RuntimeMonitor(paths)

        summary = monitor.build_summary()
        _assert(summary["counts"]["tasks"]["total"] == 3, "task total detected")
        _assert(summary["counts"]["tasks"]["overdue"] == 1, "overdue task counted")
        _assert(summary["counts"]["appointments"]["upcoming_1h"] == 1, "upcoming appointment in 1h")
        _assert(summary["counts"]["reminders"]["due_now_or_past"] == 1, "due reminder counted")
        _assert(summary["counts"]["hindsight_queue_pending"] == 2, "queue depth counted")
        _assert(summary["latest"]["last_log"]["reason"] == "due_reminder", "latest log surfaced")


def test_catalog_and_files_status():
    print("test_catalog_and_files_status")
    with tempfile.TemporaryDirectory() as tmp:
        paths = _seed_runtime(tmp)
        monitor = RuntimeMonitor(paths)

        catalog = monitor.build_catalog()
        active_ids = set(catalog.get("active_policy_ids", []))
        _assert("due_reminder" in active_ids, "policy catalog includes due_reminder")
        _assert("operator" in set(catalog.get("available_modes", [])), "mode catalog includes operator")

        files = monitor.build_files_status()
        _assert(files["state"]["exists"] is True, "state file exists")
        _assert(files["config"]["exists"] is True, "config file exists")
        _assert(files["hindsight_queue"]["exists"] is True, "queue file exists")
        _assert(files["logs_dir"]["log_files_count"] == 1, "one log file detected")


def test_queue_and_logs_readers():
    print("test_queue_and_logs_readers")
    with tempfile.TemporaryDirectory() as tmp:
        paths = _seed_runtime(tmp)
        monitor = RuntimeMonitor(paths)

        logs = monitor.read_logs(limit=10)
        _assert(logs["count"] == 1, "read_logs returns one entry")
        _assert(logs["entries"][0]["status"] == "ok", "read_logs status preserved")

        queue = monitor.read_hindsight_queue(limit=10)
        _assert(queue["count"] == 2, "queue count returned")
        _assert(queue["entries"][0]["content"] == "event-2", "queue newest-first ordering")


def test_calendar_mockup_groups_scheduled_and_unscheduled_items():
    print("test_calendar_mockup_groups_scheduled_and_unscheduled_items")
    with tempfile.TemporaryDirectory() as tmp:
        paths = _seed_runtime(tmp)
        monitor = RuntimeMonitor(paths)

        payload = monitor.build_calendar_mockup(days=7)
        _assert(payload["days_count"] == 7, "calendar mockup returns requested days")
        _assert(len(payload["days"]) == 7, "calendar mockup exposes day entries")
        _assert(any(item["id"] == "t1" for item in payload["days"][0]["items"]), "scheduled task rendered in current day")
        _assert(any(item["id"] == "a1" for item in payload["days"][0]["items"]), "appointment rendered in calendar day")
        _assert(any(item["id"] == "t3" for item in payload["unscheduled"]), "unscheduled task separated into backlog")


def test_dashboard_html_route_works_across_starlette_versions():
    print("test_dashboard_html_route_works_across_starlette_versions")
    with tempfile.TemporaryDirectory() as tmp:
        paths = _seed_runtime(tmp)
        monitor = RuntimeMonitor(paths)

        webapp_app_module.paths = paths
        webapp_app_module.monitor = monitor

        with TestClient(webapp_app_module.app) as client:
            response = client.get("/monitor")
            _assert(response.status_code == 200, "monitor route returns 200")
            _assert("ADHD Assistant" in response.text, "monitor HTML rendered")


def test_dashboard_html_uses_root_path_for_assets_and_navigation():
    print("test_dashboard_html_uses_root_path_for_assets_and_navigation")
    with tempfile.TemporaryDirectory() as tmp:
        paths = _seed_runtime(tmp)
        monitor = RuntimeMonitor(paths)

        webapp_app_module.paths = paths
        webapp_app_module.monitor = monitor

        with TestClient(webapp_app_module.app, root_path="/adhd-assistant") as client:
            response = client.get("/monitor")
            _assert(response.status_code == 200, "monitor route returns 200 with root_path")
            _assert("/adhd-assistant/static/styles.css" in response.text, "monitor CSS URL is prefixed")
            _assert("/adhd-assistant/static/dashboard.js" in response.text, "monitor JS URL is prefixed")
            _assert("/adhd-assistant/monitor/calendar" in response.text, "calendar nav link is prefixed")


def test_calendar_routes_render_and_serve_json():
    print("test_calendar_routes_render_and_serve_json")
    with tempfile.TemporaryDirectory() as tmp:
        paths = _seed_runtime(tmp)
        monitor = RuntimeMonitor(paths)

        webapp_app_module.paths = paths
        webapp_app_module.monitor = monitor

        with TestClient(webapp_app_module.app) as client:
            html_response = client.get("/monitor/calendar")
            _assert(html_response.status_code == 200, "monitor calendar route returns 200")
            _assert("Calendario" in html_response.text, "calendar HTML rendered")

            legacy_response = client.get("/calendar")
            _assert(legacy_response.status_code == 200, "legacy calendar alias still returns 200")

            json_response = client.get("/api/calendar-mockup?days=7")
            _assert(json_response.status_code == 200, "calendar api returns 200")
            payload = json_response.json()
            _assert(payload["days_count"] == 7, "calendar api respects days parameter")
            _assert(any(item["id"] == "t3" for item in payload["unscheduled"]), "calendar api exposes unscheduled tasks")


if __name__ == "__main__":
    tests = [
        test_summary_counts_and_latest_log,
        test_catalog_and_files_status,
        test_queue_and_logs_readers,
        test_calendar_mockup_groups_scheduled_and_unscheduled_items,
        test_dashboard_html_route_works_across_starlette_versions,
        test_dashboard_html_uses_root_path_for_assets_and_navigation,
        test_calendar_routes_render_and_serve_json,
    ]
    failures = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failures += 1
            print(f"  FAIL {t.__name__}: {e}")
        except Exception as e:
            failures += 1
            print(f"  ERROR {t.__name__}: {e!r}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    sys.exit(1 if failures else 0)
