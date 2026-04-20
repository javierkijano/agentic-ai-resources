# -*- coding: utf-8 -*-
"""Task-app UI tests for ADHD Assistant webapp.

Run:
  cd /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/adhd-assistant
  python3 -m pytest tests/test_webapp_task_app.py -q
"""

import importlib
import os
import tempfile

from fastapi.testclient import TestClient

import webapp.app as webapp_app_module
from tests.test_webapp_monitoring import _seed_runtime
from webapp.services.runtime_monitor import RuntimeMonitor


def test_root_route_renders_today_shell_and_monitor_moves_to_monitor():
    with tempfile.TemporaryDirectory() as tmp:
        paths = _seed_runtime(tmp)
        monitor = RuntimeMonitor(paths)

        webapp_app_module.paths = paths
        webapp_app_module.monitor = monitor

        with TestClient(webapp_app_module.app) as client:
            today_response = client.get("/")
            assert today_response.status_code == 200
            assert "ADHD Assistant · Hoy" in today_response.text
            assert "Qué toca hoy" in today_response.text
            assert "/monitor" in today_response.text

            monitor_response = client.get("/monitor")
            assert monitor_response.status_code == 200
            assert "ADHD Assistant · Monitor" in monitor_response.text

            calendar_response = client.get("/monitor/calendar")
            assert calendar_response.status_code == 200
            assert "ADHD Assistant · Calendario" in calendar_response.text


def test_today_shell_renders_collapsible_cards_and_bucket_menu_with_root_path():
    with tempfile.TemporaryDirectory() as tmp:
        paths = _seed_runtime(tmp)
        monitor = RuntimeMonitor(paths)

        webapp_app_module.paths = paths
        webapp_app_module.monitor = monitor

        with TestClient(webapp_app_module.app, root_path="/adhd-assistant") as client:
            response = client.get("/")
            assert response.status_code == 200
            assert "/adhd-assistant/static/styles.css" in response.text
            assert "/adhd-assistant/static/today.js" in response.text
            assert "/adhd-assistant/monitor" in response.text
            assert "task-card" in response.text
            assert "details" in response.text
            assert "Cuándo lo haré" in response.text
            assert "Próxima hora" in response.text
            assert "Próximas 4 horas" in response.text
            assert "Sin definir" in response.text
            assert "#legal" in response.text


def test_prefixed_alias_routes_and_assets_work_for_direct_local_access():
    previous_root_path = os.environ.get("ADHD_WEBAPP_ROOT_PATH")
    os.environ["ADHD_WEBAPP_ROOT_PATH"] = "/adhd-assistant"
    reloaded_app_module = importlib.reload(webapp_app_module)
    try:
        with tempfile.TemporaryDirectory() as tmp:
            paths = _seed_runtime(tmp)
            monitor = RuntimeMonitor(paths)

            reloaded_app_module.paths = paths
            reloaded_app_module.monitor = monitor

            with TestClient(reloaded_app_module.app) as client:
                assert client.get("/adhd-assistant/").status_code == 200
                assert client.get("/adhd-assistant/monitor").status_code == 200
                assert client.get("/adhd-assistant/monitor/calendar").status_code == 200
                assert client.get("/adhd-assistant/static/styles.css").status_code == 200
                assert client.get("/adhd-assistant/static/today.js").status_code == 200
    finally:
        if previous_root_path is None:
            os.environ.pop("ADHD_WEBAPP_ROOT_PATH", None)
        else:
            os.environ["ADHD_WEBAPP_ROOT_PATH"] = previous_root_path
        importlib.reload(webapp_app_module)
