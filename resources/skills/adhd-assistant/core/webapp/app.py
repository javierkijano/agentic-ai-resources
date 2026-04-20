# -*- coding: utf-8 -*-
"""FastAPI web app for ADHD Assistant.

Run (from skill dir):
  python3 -m webapp.app

Then open:
  http://127.0.0.1:8765
"""

from __future__ import annotations

import inspect
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from webapp.services.runtime_monitor import (
    OPEN_STATUSES,
    RuntimeMonitor,
    RuntimePaths,
    _coerce_for_compare,
    _normalize_status,
    _parse_iso,
)


APP_DIR = Path(__file__).resolve().parent
SKILL_DIR = APP_DIR.parent

BUCKET_CHOICES = [
    {"key": "proxima-hora", "label": "Próxima hora"},
    {"key": "proximas-4h", "label": "Próximas 4 horas"},
    {"key": "hoy", "label": "Hoy"},
    {"key": "manana", "label": "Mañana"},
    {"key": "pasado-manana", "label": "Pasado mañana"},
    {"key": "esta-semana", "label": "Esta semana"},
    {"key": "este-mes", "label": "Este mes"},
    {"key": "sin-definir", "label": "Sin definir"},
]
BUCKET_LABELS = {choice["key"]: choice["label"] for choice in BUCKET_CHOICES}
BUCKET_ORDER = {choice["key"]: idx for idx, choice in enumerate(BUCKET_CHOICES)}
BUCKET_ALIASES = {
    "proxima-hora": "proxima-hora",
    "próxima-hora": "proxima-hora",
    "next-hour": "proxima-hora",
    "proximas-4h": "proximas-4h",
    "proximas-4-horas": "proximas-4h",
    "próximas-4h": "proximas-4h",
    "próximas-4-horas": "proximas-4h",
    "today": "hoy",
    "tomorrow": "manana",
    "manana": "manana",
    "mañana": "manana",
    "pasado-manana": "pasado-manana",
    "pasado-mañana": "pasado-manana",
    "this-week": "esta-semana",
    "esta-semana": "esta-semana",
    "this-month": "este-mes",
    "este-mes": "este-mes",
    "sin-definir": "sin-definir",
    "undefined": "sin-definir",
}


def normalize_root_path(value: str | None) -> str:
    root = (value or "").strip()
    if not root or root == "/":
        return ""
    if not root.startswith("/"):
        root = f"/{root}"
    return root.rstrip("/")


APP_BASE_PATH = normalize_root_path(
    os.environ.get("ADHD_WEBAPP_ROOT_PATH") or os.environ.get("WEBAPP_ROOT_PATH", "")
)

paths = RuntimePaths.from_environment(SKILL_DIR)
monitor = RuntimeMonitor(paths)

templates = Jinja2Templates(directory=str(APP_DIR / "templates"))

app = FastAPI(
    title="ADHD Assistant Webapp",
    description="Operational task app + runtime monitor for ADHD Assistant",
    version="0.2.0",
)
app.mount("/static", StaticFiles(directory=str(APP_DIR / "static")), name="static")
if APP_BASE_PATH:
    app.mount(f"{APP_BASE_PATH}/static", StaticFiles(directory=str(APP_DIR / 'static')), name="static-prefixed")


def request_base_path(request: Request) -> str:
    return normalize_root_path(request.scope.get("root_path") or APP_BASE_PATH)


def render_template(request: Request, template_name: str, context: dict):
    params = inspect.signature(templates.TemplateResponse).parameters
    if "request" in params:
        return templates.TemplateResponse(
            request=request,
            name=template_name,
            context=context,
        )
    return templates.TemplateResponse(
        template_name,
        {
            "request": request,
            **context,
        },
    )


def normalize_bucket_key(value: Any) -> str | None:
    raw = str(value or "").strip().lower().replace("_", "-")
    return BUCKET_ALIASES.get(raw, raw if raw in BUCKET_LABELS else None)


def slugify_hashtag(value: Any) -> str | None:
    text = str(value or "").strip().lower()
    if not text:
        return None
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"[^a-z0-9áéíóúñü\-]", "", text)
    text = text.strip("-")
    if not text:
        return None
    return f"#{text}"


def task_hashtags(task: Dict[str, Any]) -> List[str]:
    hashtags: List[str] = []
    tags = task.get("tags") if isinstance(task.get("tags"), list) else []
    for tag in tags:
        normalized = slugify_hashtag(str(tag).lstrip("#"))
        if normalized and normalized not in hashtags:
            hashtags.append(normalized)
    project_tag = slugify_hashtag(task.get("project"))
    if project_tag and project_tag not in hashtags:
        hashtags.append(project_tag)
    if not hashtags:
        title_words = re.findall(r"[A-Za-zÁÉÍÓÚáéíóúñÑ]{4,}", str(task.get("title") or ""))
        for word in title_words[:2]:
            normalized = slugify_hashtag(word)
            if normalized and normalized not in hashtags:
                hashtags.append(normalized)
    return hashtags[:5]


def infer_bucket(task: Dict[str, Any], now_dt: datetime) -> tuple[str, str]:
    explicit = normalize_bucket_key(task.get("schedule_bucket"))
    if explicit:
        return explicit, BUCKET_LABELS[explicit]

    raw_when = task.get("deadline") or task.get("due_at")
    when = _coerce_for_compare(_parse_iso(raw_when), now_dt)
    if when is None:
        return "sin-definir", BUCKET_LABELS["sin-definir"]

    if when <= now_dt:
        return "hoy", BUCKET_LABELS["hoy"]

    delta_seconds = (when - now_dt).total_seconds()
    if delta_seconds <= 3600:
        return "proxima-hora", BUCKET_LABELS["proxima-hora"]
    if delta_seconds <= 4 * 3600:
        return "proximas-4h", BUCKET_LABELS["proximas-4h"]

    if when.date() == now_dt.date():
        return "hoy", BUCKET_LABELS["hoy"]
    if (when.date() - now_dt.date()).days == 1:
        return "manana", BUCKET_LABELS["manana"]
    if (when.date() - now_dt.date()).days == 2:
        return "pasado-manana", BUCKET_LABELS["pasado-manana"]
    if when.isocalendar()[:2] == now_dt.isocalendar()[:2]:
        return "esta-semana", BUCKET_LABELS["esta-semana"]
    if when.year == now_dt.year and when.month == now_dt.month:
        return "este-mes", BUCKET_LABELS["este-mes"]
    return "este-mes", BUCKET_LABELS["este-mes"]


def short_title(value: Any, limit: int = 52) -> str:
    text = str(value or "(sin título)").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "…"


def format_deadline(dt: datetime | None) -> str | None:
    if dt is None:
        return None
    return dt.strftime("%d/%m %H:%M") if dt.strftime("%H:%M") != "00:00" else dt.strftime("%d/%m")


def task_card_payload(task: Dict[str, Any], now_dt: datetime) -> Dict[str, Any]:
    status = _normalize_status(task.get("status"))
    raw_when = task.get("deadline") or task.get("due_at")
    when = _coerce_for_compare(_parse_iso(raw_when), now_dt)
    bucket_key, bucket_label = infer_bucket(task, now_dt)
    hashtags = task_hashtags(task)
    description = str(task.get("description") or task.get("notes") or "").strip()
    priority = task.get("priority") if isinstance(task.get("priority"), int) else None
    is_overdue = when is not None and when <= now_dt

    return {
        "id": str(task.get("id") or ""),
        "title": str(task.get("title") or "(sin título)"),
        "short_title": short_title(task.get("title")),
        "description": description,
        "status": status,
        "priority": priority,
        "project": task.get("project"),
        "hashtags": hashtags,
        "bucket_key": bucket_key,
        "bucket_label": bucket_label,
        "bucket_choices": BUCKET_CHOICES,
        "deadline_label": format_deadline(when),
        "is_overdue": bool(is_overdue),
        "details_id": f"task-details-{task.get('id')}",
        "sort_deadline": when.isoformat() if when is not None else "9999-12-31T23:59:59+00:00",
    }


def sort_task_cards(cards: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return sorted(
        cards,
        key=lambda card: (
            0 if card.get("is_overdue") else 1,
            BUCKET_ORDER.get(card.get("bucket_key"), 99),
            card.get("priority") if card.get("priority") is not None else 99,
            card.get("sort_deadline") or "9999-12-31T23:59:59+00:00",
            card.get("title") or "",
        ),
    )


def build_today_view() -> Dict[str, Any]:
    summary = monitor.build_summary()
    state_payload = monitor.read_state()
    state = state_payload["state"]
    now_dt = datetime.fromisoformat(summary["now"])

    cards: List[Dict[str, Any]] = []
    tasks = (state.get("commitments", {}) or {}).get("tasks", []) or []
    for task in tasks:
        if not isinstance(task, dict):
            continue
        status = _normalize_status(task.get("status"))
        if status not in OPEN_STATUSES:
            continue
        cards.append(task_card_payload(task, now_dt))

    cards = sort_task_cards(cards)
    focus_task = cards[0] if cards else None
    overdue = [card for card in cards if card.get("is_overdue")]
    today_cards = [
        card
        for card in cards
        if not card.get("is_overdue") and card.get("bucket_key") in {"proxima-hora", "proximas-4h", "hoy"}
    ]
    later_cards = [
        card
        for card in cards
        if card.get("bucket_key") in {"manana", "pasado-manana", "esta-semana", "este-mes"}
    ]
    unscheduled = [card for card in cards if card.get("bucket_key") == "sin-definir"]

    sections = [
        {
            "id": "today",
            "title": "Qué toca hoy",
            "description": "Tareas con más probabilidad de moverse hoy sin abrir una lista infinita.",
            "tasks": today_cards,
        },
        {
            "id": "later",
            "title": "Más adelante",
            "description": "Compromisos ya apuntados, pero fuera del radar inmediato.",
            "tasks": later_cards,
        },
        {
            "id": "unscheduled",
            "title": "Sin definir",
            "description": "Pendientes abiertos que aún necesitan una ventana realista.",
            "tasks": unscheduled,
        },
    ]

    return {
        "generated_at": summary["generated_at"],
        "timezone": summary["timezone"],
        "now": summary["now"],
        "focus_task": focus_task,
        "rescue_tasks": overdue,
        "sections": sections,
        "counts": {
            "open": len(cards),
            "overdue": len(overdue),
            "today": len(today_cards),
            "unscheduled": len(unscheduled),
        },
    }


@app.get("/")
def today_view(request: Request):
    today = build_today_view()
    context = {
        "today": today,
        "active_page": "today",
        "app_base_path": request_base_path(request),
    }
    return render_template(request, "today.html", context)


@app.get("/monitor")
def dashboard(request: Request):
    summary = monitor.build_summary()
    context = {
        "summary": summary,
        "runtime_dir": str(paths.runtime_dir),
        "skill_dir": str(paths.skill_dir),
        "active_page": "monitor",
        "app_base_path": request_base_path(request),
    }
    return render_template(request, "index.html", context)


@app.get("/monitor/calendar")
@app.get("/calendar")
def calendar_view(request: Request, days: int = Query(default=14, ge=1, le=31)):
    calendar = monitor.build_calendar_mockup(days=days)
    context = {
        "calendar": calendar,
        "runtime_dir": str(paths.runtime_dir),
        "skill_dir": str(paths.skill_dir),
        "active_page": "calendar",
        "app_base_path": request_base_path(request),
    }
    return render_template(request, "calendar.html", context)


@app.get("/api/health")
def api_health():
    summary = monitor.build_summary()
    state_exists = bool((summary.get("paths") or {}).get("state")) and paths.state_path.exists()
    config_exists = bool((summary.get("paths") or {}).get("config")) and paths.config_path.exists()
    latest_log = (summary.get("latest") or {}).get("last_log") or {}

    status = "ok"
    if not state_exists:
        status = "degraded"
    if latest_log.get("status") == "error":
        status = "error"

    return {
        "status": status,
        "state_exists": state_exists,
        "config_exists": config_exists,
        "last_log_status": latest_log.get("status"),
        "generated_at": summary.get("generated_at"),
    }


@app.get("/api/summary")
def api_summary():
    return monitor.build_summary()


@app.get("/api/catalog")
def api_catalog():
    return monitor.build_catalog()


@app.get("/api/files")
def api_files():
    return monitor.build_files_status()


@app.get("/api/logs")
def api_logs(limit: int = Query(default=50, ge=1, le=500)):
    return monitor.read_logs(limit=limit)


@app.get("/api/hindsight-queue")
def api_hindsight_queue(limit: int = Query(default=50, ge=1, le=500)):
    return monitor.read_hindsight_queue(limit=limit)


@app.get("/api/state")
def api_state():
    return monitor.read_state()


@app.get("/api/config")
def api_config():
    return monitor.read_config_bundle()


@app.get("/api/calendar-mockup")
def api_calendar_mockup(days: int = Query(default=14, ge=1, le=31)):
    return monitor.build_calendar_mockup(days=days)


@app.get("/api/dashboard")
def api_dashboard(
    logs_limit: int = Query(default=30, ge=1, le=300),
    queue_limit: int = Query(default=30, ge=1, le=300),
    include_state: bool = Query(default=False),
    include_config: bool = Query(default=False),
):
    return monitor.build_dashboard_payload(
        include_state=include_state,
        include_config=include_config,
        logs_limit=logs_limit,
        queue_limit=queue_limit,
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "error": str(exc),
        },
    )


if APP_BASE_PATH:
    app.add_api_route(f"{APP_BASE_PATH}/", today_view, methods=["GET"], include_in_schema=False)
    app.add_api_route(f"{APP_BASE_PATH}/monitor", dashboard, methods=["GET"], include_in_schema=False)
    app.add_api_route(
        f"{APP_BASE_PATH}/monitor/calendar",
        calendar_view,
        methods=["GET"],
        include_in_schema=False,
    )


if __name__ == "__main__":
    import uvicorn

    host = os.environ.get("ADHD_WEBAPP_HOST", "127.0.0.1")
    port = int(os.environ.get("ADHD_WEBAPP_PORT", "8765"))
    reload = os.environ.get("ADHD_WEBAPP_RELOAD", "0") in {"1", "true", "True"}

    uvicorn.run(app, host=host, port=port, reload=reload)
