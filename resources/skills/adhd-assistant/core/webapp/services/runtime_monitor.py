# -*- coding: utf-8 -*-
"""Monitoring services for ADHD Assistant webapp (read-only).

Design goals:
- Read-only by default (no state mutation).
- Runtime-path aware (HERMES_HOME override friendly).
- Extensible: new metrics/endpoints can reuse this service layer.
"""

from __future__ import annotations

import json
import os
import sys
from collections import Counter, deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

import yaml

# Ensure skill modules (engine/, actions/) are importable.
SKILL_DIR = Path(__file__).resolve().parents[2]
if str(SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(SKILL_DIR))

from engine import clock, loader, state_store  # noqa: E402


OPEN_STATUSES = {"pending", "in_progress", "postponed"}
SENSITIVE_KEY_PARTS = (
    "token",
    "secret",
    "password",
    "api_key",
    "apikey",
    "auth",
    "cookie",
    "private_key",
)


@dataclass(frozen=True)
class RuntimePaths:
    skill_dir: Path
    hermes_home: Path
    runtime_dir: Path
    state_path: Path
    config_path: Path
    hindsight_queue_path: Path
    logs_dir: Path
    legacy_tasks_path: Path

    @classmethod
    def from_environment(cls, skill_dir: Path) -> "RuntimePaths":
        hermes_home = Path(
            os.environ.get("HERMES_HOME", str(Path.home() / ".hermes"))
        ).expanduser()
        runtime_dir = hermes_home / "adhd_assistant"
        return cls(
            skill_dir=skill_dir.resolve(),
            hermes_home=hermes_home,
            runtime_dir=runtime_dir,
            state_path=runtime_dir / "state.json",
            config_path=runtime_dir / "config.yaml",
            hindsight_queue_path=runtime_dir / "hindsight_queue.jsonl",
            logs_dir=runtime_dir / "logs",
            legacy_tasks_path=hermes_home / "tasks" / "tasks.json",
        )


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_iso(value: Any):
    if value is None:
        return None
    return clock.parse_iso(str(value))


def _coerce_for_compare(dt, ref):
    if dt is None or ref is None:
        return dt
    if dt.tzinfo is None and ref.tzinfo is not None:
        return dt.replace(tzinfo=ref.tzinfo)
    if dt.tzinfo is not None and ref.tzinfo is None:
        return dt.replace(tzinfo=None)
    return dt


def _safe_read_json(path: Path) -> Tuple[Any, str | None]:
    if not path.exists():
        return None, f"missing:{path}"
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f), None
    except Exception as exc:
        return None, f"json_error:{exc}"


def _safe_read_yaml(path: Path) -> Tuple[Any, str | None]:
    if not path.exists():
        return None, f"missing:{path}"
    try:
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f) or {}, None
    except Exception as exc:
        return None, f"yaml_error:{exc}"


def _file_status(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {
            "path": str(path),
            "exists": False,
            "size_bytes": 0,
            "modified_at": None,
        }
    stat = path.stat()
    return {
        "path": str(path),
        "exists": True,
        "size_bytes": stat.st_size,
        "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
    }


def _count_nonempty_lines(path: Path) -> int:
    if not path.exists():
        return 0
    count = 0
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    count += 1
    except Exception:
        return 0
    return count


def _redact_sensitive(value: Any, key_hint: str = "") -> Any:
    key_l = (key_hint or "").lower()
    should_redact = any(part in key_l for part in SENSITIVE_KEY_PARTS)

    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            out[k] = _redact_sensitive(v, str(k))
        return out

    if isinstance(value, list):
        return [_redact_sensitive(v, key_hint) for v in value]

    if should_redact and value not in (None, "", False):
        return "***REDACTED***"

    return value


def _normalize_status(raw: Any) -> str:
    s = str(raw or "pending").strip().lower()
    aliases = {
        "todo": "pending",
        "open": "pending",
        "inprogress": "in_progress",
        "in-progress": "in_progress",
        "wip": "in_progress",
        "postpone": "postponed",
        "completed": "done",
        "complete": "done",
        "closed": "done",
        "canceled": "cancelled",
    }
    return aliases.get(s, s)


class RuntimeMonitor:
    """Read-only monitor for ADHD Assistant runtime + skill catalog."""

    def __init__(self, paths: RuntimePaths):
        self.paths = paths

    def read_state(self) -> Dict[str, Any]:
        raw, error = _safe_read_json(self.paths.state_path)
        state = raw if isinstance(raw, dict) else {}
        state = state_store.ensure_skeleton(state)
        return {
            "ok": error is None,
            "error": error,
            "path": str(self.paths.state_path),
            "state": state,
        }

    def read_config_bundle(self) -> Dict[str, Any]:
        user_cfg, user_error = _safe_read_yaml(self.paths.config_path)
        user_cfg = user_cfg if isinstance(user_cfg, dict) else {}

        effective_error = None
        try:
            effective_cfg, mode_info = loader.build_effective_config(
                str(self.paths.config_path) if self.paths.config_path.exists() else None
            )
        except Exception as exc:
            effective_error = f"effective_config_error:{exc}"
            effective_cfg = loader.load_defaults()
            mode_info = {
                "name": (effective_cfg.get("preferences", {}) or {}).get(
                    "primary_mode", "operator"
                ),
                "policy_filters": {},
            }

        return {
            "ok": user_error is None and effective_error is None,
            "errors": [e for e in [user_error, effective_error] if e],
            "path": str(self.paths.config_path),
            "user_config": _redact_sensitive(user_cfg),
            "effective_config": _redact_sensitive(effective_cfg),
            "mode_info": mode_info,
        }

    def _logs_files(self) -> List[Path]:
        if not self.paths.logs_dir.exists():
            return []
        return sorted(
            self.paths.logs_dir.glob("tick-*.jsonl"),
            key=lambda p: p.stat().st_mtime,
        )

    def read_logs(self, limit: int = 100) -> Dict[str, Any]:
        limit = max(1, min(int(limit), 1000))
        files = self._logs_files()
        acc: deque = deque(maxlen=limit)

        for file_path in files:
            try:
                with file_path.open("r", encoding="utf-8") as f:
                    for idx, line in enumerate(f, start=1):
                        line = line.strip()
                        if not line:
                            continue
                        try:
                            payload = json.loads(line)
                            if not isinstance(payload, dict):
                                payload = {"raw": payload}
                        except Exception:
                            payload = {"raw": line}
                        payload["_source_file"] = file_path.name
                        payload["_source_line"] = idx
                        acc.append(payload)
            except Exception as exc:
                acc.append(
                    {
                        "status": "error",
                        "error": f"log_read_error:{exc}",
                        "_source_file": file_path.name,
                    }
                )

        return {
            "ok": True,
            "files": [str(p) for p in files],
            "count": len(acc),
            "entries": list(reversed(list(acc))),  # newest first
        }

    def read_hindsight_queue(self, limit: int = 100) -> Dict[str, Any]:
        limit = max(1, min(int(limit), 1000))
        path = self.paths.hindsight_queue_path
        if not path.exists():
            return {
                "ok": True,
                "path": str(path),
                "count": 0,
                "entries": [],
                "missing": True,
            }

        acc: deque = deque(maxlen=limit)
        total = 0
        with path.open("r", encoding="utf-8") as f:
            for idx, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                total += 1
                try:
                    payload = json.loads(line)
                    if not isinstance(payload, dict):
                        payload = {"raw": payload}
                except Exception:
                    payload = {"raw": line}
                payload["_line"] = idx
                acc.append(payload)

        return {
            "ok": True,
            "path": str(path),
            "count": total,
            "returned": len(acc),
            "entries": list(reversed(list(acc))),  # newest first
            "missing": False,
        }

    def build_catalog(self) -> Dict[str, Any]:
        cfg_bundle = self.read_config_bundle()
        mode_info = cfg_bundle.get("mode_info", {})

        all_policies = loader.load_policies()
        active_policies = loader.filter_policies_by_mode(all_policies, mode_info)

        mode_files = sorted(
            p.stem for p in (self.paths.skill_dir / "config" / "modes").glob("*.yaml")
        )
        coaching_files = sorted(
            p.stem
            for p in (self.paths.skill_dir / "config" / "coaching").glob("*.yaml")
        )

        return {
            "generated_at": _now_iso(),
            "mode": mode_info,
            "available_modes": mode_files,
            "available_coaching_themes": coaching_files,
            "channels": ["telegram", "stdout"],
            "all_policies": [
                {
                    "id": p.get("id"),
                    "priority": p.get("priority"),
                    "enabled": p.get("enabled", True),
                    "urgency": p.get("urgency", "normal"),
                    "trigger": ((p.get("trigger") or {}).get("predicate")),
                    "file": p.get("_file"),
                }
                for p in all_policies
            ],
            "active_policy_ids": [p.get("id") for p in active_policies],
        }

    def build_files_status(self) -> Dict[str, Any]:
        log_files = self._logs_files()
        return {
            "generated_at": _now_iso(),
            "skill_dir": str(self.paths.skill_dir),
            "hermes_home": str(self.paths.hermes_home),
            "runtime_dir": str(self.paths.runtime_dir),
            "state": _file_status(self.paths.state_path),
            "config": _file_status(self.paths.config_path),
            "hindsight_queue": _file_status(self.paths.hindsight_queue_path),
            "logs_dir": {
                **_file_status(self.paths.logs_dir),
                "log_files_count": len(log_files),
                "log_files": [str(p) for p in log_files],
            },
            "legacy_tasks": _file_status(self.paths.legacy_tasks_path),
        }

    def _tasks_metrics(self, state: dict, now_dt: datetime) -> Dict[str, Any]:
        tasks = (state.get("commitments", {}) or {}).get("tasks", []) or []
        if not isinstance(tasks, list):
            tasks = []

        status_counter = Counter()
        overdue = 0
        due_24h = 0

        for task in tasks:
            if not isinstance(task, dict):
                continue
            status = _normalize_status(task.get("status"))
            status_counter[status] += 1
            deadline = _parse_iso(task.get("deadline") or task.get("due_at"))
            deadline = _coerce_for_compare(deadline, now_dt)
            if deadline is None:
                continue
            if status in OPEN_STATUSES and deadline <= now_dt:
                overdue += 1
            elif status in OPEN_STATUSES and (deadline - now_dt).total_seconds() <= 24 * 3600:
                due_24h += 1

        return {
            "total": len([t for t in tasks if isinstance(t, dict)]),
            "by_status": dict(status_counter),
            "overdue": overdue,
            "due_next_24h": due_24h,
        }

    def _appointments_metrics(self, state: dict, now_dt: datetime) -> Dict[str, Any]:
        appointments = (state.get("commitments", {}) or {}).get("appointments", []) or []
        if not isinstance(appointments, list):
            appointments = []

        upcoming_24h = 0
        upcoming_1h = 0
        overdue = 0

        for appt in appointments:
            if not isinstance(appt, dict):
                continue
            starts_at = _parse_iso(appt.get("starts_at"))
            starts_at = _coerce_for_compare(starts_at, now_dt)
            if starts_at is None:
                continue
            delta = (starts_at - now_dt).total_seconds()
            if delta < 0:
                overdue += 1
            elif delta <= 3600:
                upcoming_1h += 1
                upcoming_24h += 1
            elif delta <= 24 * 3600:
                upcoming_24h += 1

        return {
            "total": len([a for a in appointments if isinstance(a, dict)]),
            "upcoming_1h": upcoming_1h,
            "upcoming_24h": upcoming_24h,
            "past_start_time": overdue,
        }

    def _reminders_metrics(self, state: dict, now_dt: datetime) -> Dict[str, Any]:
        reminders = (state.get("support", {}) or {}).get("reminders", []) or []
        if not isinstance(reminders, list):
            reminders = []

        status_counter = Counter()
        due_now = 0

        for reminder in reminders:
            if not isinstance(reminder, dict):
                continue
            status = _normalize_status(reminder.get("status") or "scheduled")
            status_counter[status] += 1
            due_at = _parse_iso(reminder.get("due_at"))
            due_at = _coerce_for_compare(due_at, now_dt)
            if due_at is not None and status in {"scheduled", "pending"} and due_at <= now_dt:
                due_now += 1

        return {
            "total": len([r for r in reminders if isinstance(r, dict)]),
            "by_status": dict(status_counter),
            "due_now_or_past": due_now,
        }

    def _format_calendar_time(self, raw_value: Any, dt: datetime | None) -> str | None:
        if dt is None or raw_value in (None, ""):
            return None
        raw_text = str(raw_value)
        if "T" not in raw_text and " " not in raw_text:
            return None
        return dt.strftime("%H:%M")

    def _calendar_item(
        self,
        *,
        kind: str,
        title: Any,
        item_id: Any,
        status: Any,
        dt: datetime | None,
        raw_when: Any = None,
        priority: Any = None,
        project: Any = None,
        subtitle: Any = None,
    ) -> Dict[str, Any]:
        kind_labels = {
            "task": "tarea",
            "appointment": "cita",
            "reminder": "recordatorio",
        }
        return {
            "id": str(item_id or ""),
            "kind": kind,
            "kind_label": kind_labels.get(kind, kind),
            "title": str(title or "(sin título)"),
            "status": _normalize_status(status),
            "priority": priority if isinstance(priority, int) else None,
            "project": project,
            "subtitle": subtitle,
            "time": self._format_calendar_time(raw_when, dt),
            "date": dt.date().isoformat() if dt is not None else None,
        }

    def build_calendar_mockup(self, days: int = 14) -> Dict[str, Any]:
        days = max(1, min(int(days), 31))

        state_payload = self.read_state()
        state = state_payload["state"]

        cfg_bundle = self.read_config_bundle()
        cfg_effective = cfg_bundle.get("effective_config", {}) or {}
        tz_name = (cfg_effective.get("profile", {}) or {}).get(
            "timezone", "Europe/Madrid"
        )
        now_dt = clock.now(tz_name)
        start_date = now_dt.date()

        weekdays = ["lun", "mar", "mié", "jue", "vie", "sáb", "dom"]
        months = [
            "ene",
            "feb",
            "mar",
            "abr",
            "may",
            "jun",
            "jul",
            "ago",
            "sep",
            "oct",
            "nov",
            "dic",
        ]

        days_payload: List[Dict[str, Any]] = []
        day_lookup: Dict[str, Dict[str, Any]] = {}
        for offset in range(days):
            day_date = start_date.fromordinal(start_date.toordinal() + offset)
            weekday_idx = day_date.weekday()
            payload = {
                "date": day_date.isoformat(),
                "weekday_label": weekdays[weekday_idx],
                "day_label": f"{day_date.day} {months[day_date.month - 1]}",
                "is_today": offset == 0,
                "items": [],
            }
            days_payload.append(payload)
            day_lookup[payload["date"]] = payload

        unscheduled: List[Dict[str, Any]] = []

        tasks = (state.get("commitments", {}) or {}).get("tasks", []) or []
        for task in tasks:
            if not isinstance(task, dict):
                continue
            status = _normalize_status(task.get("status"))
            if status not in OPEN_STATUSES:
                continue
            raw_when = task.get("deadline") or task.get("due_at")
            when = _coerce_for_compare(_parse_iso(raw_when), now_dt)
            item = self._calendar_item(
                kind="task",
                title=task.get("title"),
                item_id=task.get("id"),
                status=status,
                dt=when,
                raw_when=raw_when,
                priority=task.get("priority"),
                project=task.get("project"),
                subtitle=task.get("description") or task.get("notes"),
            )
            if when is None:
                unscheduled.append(item)
                continue
            bucket = day_lookup.get(when.date().isoformat())
            if bucket is not None:
                bucket["items"].append(item)

        appointments = (state.get("commitments", {}) or {}).get("appointments", []) or []
        for appointment in appointments:
            if not isinstance(appointment, dict):
                continue
            raw_when = appointment.get("starts_at")
            when = _coerce_for_compare(_parse_iso(raw_when), now_dt)
            if when is None:
                continue
            bucket = day_lookup.get(when.date().isoformat())
            if bucket is None:
                continue
            bucket["items"].append(
                self._calendar_item(
                    kind="appointment",
                    title=appointment.get("title"),
                    item_id=appointment.get("id"),
                    status=appointment.get("status") or "scheduled",
                    dt=when,
                    raw_when=raw_when,
                    project=appointment.get("project"),
                    subtitle=appointment.get("location") or appointment.get("notes"),
                )
            )

        reminders = (state.get("support", {}) or {}).get("reminders", []) or []
        for reminder in reminders:
            if not isinstance(reminder, dict):
                continue
            status = _normalize_status(reminder.get("status") or "scheduled")
            if status not in {"scheduled", "pending"}:
                continue
            raw_when = reminder.get("due_at")
            when = _coerce_for_compare(_parse_iso(raw_when), now_dt)
            if when is None:
                continue
            bucket = day_lookup.get(when.date().isoformat())
            if bucket is None:
                continue
            bucket["items"].append(
                self._calendar_item(
                    kind="reminder",
                    title=reminder.get("message") or reminder.get("title"),
                    item_id=reminder.get("id"),
                    status=status,
                    dt=when,
                    raw_when=raw_when,
                    subtitle=reminder.get("linked_id"),
                )
            )

        for day in days_payload:
            day["items"].sort(
                key=lambda item: (
                    item.get("time") or "99:99",
                    item.get("kind") or "z",
                    item.get("title") or "",
                )
            )

        unscheduled.sort(
            key=lambda item: (
                item.get("priority") if item.get("priority") is not None else 99,
                item.get("title") or "",
            )
        )

        scheduled_items = sum(len(day["items"]) for day in days_payload)

        return {
            "generated_at": _now_iso(),
            "timezone": tz_name,
            "range_start": days_payload[0]["date"],
            "range_end": days_payload[-1]["date"],
            "days_count": days,
            "days": days_payload,
            "scheduled_items": scheduled_items,
            "unscheduled": unscheduled,
            "unscheduled_count": len(unscheduled),
            "source_counts": {
                "tasks": len([t for t in tasks if isinstance(t, dict)]),
                "appointments": len([a for a in appointments if isinstance(a, dict)]),
                "reminders": len([r for r in reminders if isinstance(r, dict)]),
            },
            "note": "Mockup local basado en state.json; Google Calendar vendrá después usando esta misma vista.",
        }

    def build_summary(self) -> Dict[str, Any]:
        state_payload = self.read_state()
        state = state_payload["state"]

        cfg_bundle = self.read_config_bundle()
        cfg_effective = cfg_bundle.get("effective_config", {}) or {}

        tz_name = (cfg_effective.get("profile", {}) or {}).get(
            "timezone", "Europe/Madrid"
        )
        now_dt = clock.now(tz_name)

        logs_payload = self.read_logs(limit=50)
        logs = logs_payload.get("entries", [])
        last_log = logs[0] if logs else None

        queue_depth = _count_nonempty_lines(self.paths.hindsight_queue_path)

        history = (state.get("history", {}) or {})
        support = (state.get("support", {}) or {})

        warnings: List[str] = []
        if not self.paths.state_path.exists():
            warnings.append("state.json no existe todavía")
        if not self.paths.config_path.exists():
            warnings.append("config.yaml no existe todavía (se usarán defaults)")
        if queue_depth > 200:
            warnings.append("hindsight_queue.jsonl supera 200 entradas pendientes")

        return {
            "generated_at": _now_iso(),
            "timezone": tz_name,
            "now": now_dt.isoformat(),
            "mode": {
                "primary_mode": (cfg_effective.get("preferences", {}) or {}).get(
                    "primary_mode"
                ),
                "coaching_level": (cfg_effective.get("preferences", {}) or {}).get(
                    "coaching_level"
                ),
                "delivery_channel": (cfg_effective.get("delivery", {}) or {}).get(
                    "default_channel"
                ),
            },
            "counts": {
                "tasks": self._tasks_metrics(state, now_dt),
                "appointments": self._appointments_metrics(state, now_dt),
                "reminders": self._reminders_metrics(state, now_dt),
                "open_loops": len(support.get("open_loops", []) or []),
                "recommendations": len(support.get("recommendations", []) or []),
                "hindsight_queue_pending": queue_depth,
            },
            "latest": {
                "last_tick_at": history.get("last_tick_at"),
                "last_sync_at": history.get("last_sync_at"),
                "last_daily_review_date": history.get("last_daily_review_date"),
                "recent_events_count": len(history.get("recent_events", []) or []),
                "last_log": last_log,
            },
            "warnings": warnings,
            "paths": {
                "state": str(self.paths.state_path),
                "config": str(self.paths.config_path),
                "hindsight_queue": str(self.paths.hindsight_queue_path),
                "logs_dir": str(self.paths.logs_dir),
            },
        }

    def build_dashboard_payload(
        self,
        include_state: bool = False,
        include_config: bool = False,
        logs_limit: int = 30,
        queue_limit: int = 30,
    ) -> Dict[str, Any]:
        payload = {
            "summary": self.build_summary(),
            "catalog": self.build_catalog(),
            "files": self.build_files_status(),
            "logs": self.read_logs(limit=logs_limit),
            "hindsight_queue": self.read_hindsight_queue(limit=queue_limit),
        }
        if include_state:
            payload["state"] = self.read_state()
        if include_config:
            payload["config"] = self.read_config_bundle()
        return payload
