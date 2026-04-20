# -*- coding: utf-8 -*-
"""Reconciliation helpers for ADHD Assistant.

Purpose:
- Keep local operational state (`state.json`) in sync with legacy local task store
  (`~/.hermes/tasks/tasks.json`) during migration period.
- Produce deterministic discrepancy summaries (added/updated/conflicts/missing).

Design constraints:
- Non-destructive by default.
- Conflict-aware (do not overwrite done/cancelled local tasks with open legacy tasks).
- Idempotent across repeated runs.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Tuple

from . import clock


OPEN_STATUSES = {"pending", "in_progress", "postponed"}
FINAL_STATUSES = {"done", "cancelled"}


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
    return aliases.get(s, s if s in OPEN_STATUSES | FINAL_STATUSES else "pending")


def _as_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except Exception:
        return default


def _expand(path: str) -> str:
    return os.path.expanduser(os.path.expandvars(path))


def should_run_sync(state: dict, config: dict, now) -> Tuple[bool, str]:
    sync_cfg = (config or {}).get("sync", {}) or {}
    if not bool(sync_cfg.get("enabled", True)):
        return False, "sync_disabled"

    cadence_hours = _as_int(sync_cfg.get("cadence_hours", 6), 6)
    if cadence_hours <= 0:
        cadence_hours = 6

    last_sync = (state.get("history", {}) or {}).get("last_sync_at")
    if not last_sync:
        return True, "first_sync"

    last_dt = clock.parse_iso(last_sync)
    if last_dt is None:
        return True, "invalid_last_sync"

    elapsed = (now - last_dt).total_seconds()
    if elapsed >= cadence_hours * 3600:
        return True, "cadence_elapsed"
    return False, "cadence_not_elapsed"


def _load_legacy_tasks(path: str) -> Tuple[List[dict], str | None]:
    p = _expand(path)
    if not os.path.exists(p):
        return [], None
    try:
        with open(p, "r", encoding="utf-8") as f:
            payload = json.load(f)
        tasks = payload.get("tasks", []) if isinstance(payload, dict) else []
        out = [t for t in tasks if isinstance(t, dict)]
        return out, None
    except Exception as e:
        return [], f"legacy_read_error:{e}"


def _legacy_to_state_task(legacy: dict, now_iso: str, source_path: str) -> dict:
    lid = str(legacy.get("id"))
    status = _normalize_status(legacy.get("status"))
    task = {
        "id": f"legacy-{lid}",
        "legacy_task_id": legacy.get("id"),
        "title": legacy.get("title") or f"Task {lid}",
        "description": legacy.get("description", ""),
        "status": status,
        "priority": _as_int(legacy.get("priority", 3), 3),
        "energy": legacy.get("energy"),
        "created_at": legacy.get("created") or legacy.get("created_at"),
        "deadline": legacy.get("deadline"),
        "postponed_count": _as_int(legacy.get("postponed_count", 0), 0),
        "postpone_history": legacy.get("postpone_history") if isinstance(legacy.get("postpone_history"), list) else [],
        "project": legacy.get("project"),
        "tags": legacy.get("tags") if isinstance(legacy.get("tags"), list) else [],
        "notes": legacy.get("notes", ""),
        "source": {
            "type": "legacy_tasks_json",
            "path": source_path,
            "id": legacy.get("id"),
            "synced_at": now_iso,
        },
        "updated_at": now_iso,
    }
    return task


def _reminder_id(legacy_task_id: Any, idx: int) -> str:
    return f"legacy-task-{legacy_task_id}-r{idx}"


def _sync_legacy_reminders(state: dict, legacy_tasks: List[dict], now_iso: str, summary: dict) -> None:
    support = state.setdefault("support", {})
    reminders = support.setdefault("reminders", [])
    if not isinstance(reminders, list):
        reminders = []
        support["reminders"] = reminders

    idx_by_id = {}
    for r in reminders:
        if isinstance(r, dict) and r.get("id") is not None:
            idx_by_id[str(r.get("id"))] = r

    # map task legacy id -> state task id
    task_id_by_legacy = {}
    for t in state.get("commitments", {}).get("tasks", []):
        if not isinstance(t, dict):
            continue
        lid = t.get("legacy_task_id")
        if lid is None:
            continue
        task_id_by_legacy[str(lid)] = t.get("id")

    added = 0
    updated = 0

    for lt in legacy_tasks:
        lid = lt.get("id")
        if lid is None:
            continue
        reminder_list = lt.get("reminders")
        if not isinstance(reminder_list, list):
            continue

        state_task_id = task_id_by_legacy.get(str(lid), f"legacy-{lid}")
        title = lt.get("title") or f"Task {lid}"

        for i, due in enumerate(reminder_list):
            rid = _reminder_id(lid, i)
            desired = {
                "id": rid,
                "message": f"Recordatorio: {title}",
                "due_at": due,
                "status": "scheduled",
                "linked_type": "task",
                "linked_id": state_task_id,
                "source": "legacy_tasks_json",
                "updated_at": now_iso,
            }

            existing = idx_by_id.get(rid)
            if existing is None:
                reminders.append(desired)
                idx_by_id[rid] = desired
                added += 1
                continue

            # Do not clobber reminders already sent/cancelled
            if existing.get("status") not in {"scheduled", None, ""}:
                continue

            changed = False
            for k, v in desired.items():
                if existing.get(k) != v:
                    existing[k] = v
                    changed = True
            if changed:
                updated += 1

    summary["reminders_added"] = added
    summary["reminders_updated"] = updated


def reconcile_local_tasks_json(state: dict, config: dict, now) -> dict:
    """Reconcile legacy ~/.hermes/tasks/tasks.json into state.commitments.tasks.

    Returns a structured summary suitable for logs/reports.
    """
    now_iso = now.isoformat()
    sync_cfg = (config or {}).get("sync", {}) or {}
    sources = sync_cfg.get("sources", {}) or {}

    enabled = bool(sources.get("local_tasks_json", True))
    source_path = _expand(sources.get("local_tasks_path", "~/.hermes/tasks/tasks.json"))

    summary = {
        "source": "local_tasks_json",
        "source_path": source_path,
        "enabled": enabled,
        "ran": False,
        "added": [],
        "updated": [],
        "conflicts": [],
        "missing_in_source": [],
        "reminders_added": 0,
        "reminders_updated": 0,
        "error": None,
    }

    if not enabled:
        summary["reason"] = "source_disabled"
        return summary

    legacy_tasks, err = _load_legacy_tasks(source_path)
    if err:
        summary["error"] = err
        summary["reason"] = "read_error"
        return summary

    commitments = state.setdefault("commitments", {})
    state_tasks = commitments.setdefault("tasks", [])
    if not isinstance(state_tasks, list):
        state_tasks = []
        commitments["tasks"] = state_tasks

    by_legacy = {}
    by_id = {}
    for t in state_tasks:
        if not isinstance(t, dict):
            continue
        if t.get("legacy_task_id") is not None:
            by_legacy[str(t.get("legacy_task_id"))] = t
        if t.get("id") is not None:
            by_id[str(t.get("id"))] = t

    legacy_seen = set()

    for lt in legacy_tasks:
        lid = lt.get("id")
        if lid is None:
            continue
        lid_s = str(lid)
        legacy_seen.add(lid_s)

        desired = _legacy_to_state_task(lt, now_iso, source_path)
        existing = by_legacy.get(lid_s) or by_id.get(desired["id"])

        if existing is None:
            state_tasks.append(desired)
            by_legacy[lid_s] = desired
            by_id[desired["id"]] = desired
            summary["added"].append(desired["id"])
            continue

        existing_status = _normalize_status(existing.get("status"))
        desired_status = _normalize_status(desired.get("status"))

        # Conflict rule: keep locally closed tasks closed unless source is also closed.
        if existing_status in FINAL_STATUSES and desired_status in OPEN_STATUSES:
            summary["conflicts"].append({
                "id": existing.get("id"),
                "legacy_task_id": lid,
                "reason": f"local_{existing_status}_vs_source_{desired_status}",
            })
            continue

        changed = False
        preserved_id = existing.get("id") or desired["id"]
        for k, v in desired.items():
            if k == "id":
                continue
            if existing.get(k) != v:
                existing[k] = v
                changed = True
        if existing.get("id") != preserved_id:
            existing["id"] = preserved_id
            changed = True
        if changed:
            summary["updated"].append(existing.get("id"))

    for t in state_tasks:
        if not isinstance(t, dict):
            continue
        lid = t.get("legacy_task_id")
        if lid is None:
            continue
        if str(lid) not in legacy_seen:
            summary["missing_in_source"].append(t.get("id"))

    _sync_legacy_reminders(state, legacy_tasks, now_iso, summary)

    summary["ran"] = True
    summary["legacy_count"] = len(legacy_tasks)
    summary["state_count"] = len([t for t in state_tasks if isinstance(t, dict)])
    summary["added_count"] = len(summary["added"])
    summary["updated_count"] = len(summary["updated"])
    summary["conflicts_count"] = len(summary["conflicts"])
    summary["missing_in_source_count"] = len(summary["missing_in_source"])
    return summary
