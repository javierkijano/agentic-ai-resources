# -*- coding: utf-8 -*-
"""Predicates used by policies. Each returns (bool, bindings_dict).

Registered by name. Policies reference the name in their `trigger.predicate` field.
"""
from datetime import datetime
from typing import Callable, Dict, Tuple

from . import clock

OPEN_STATUSES = {"pending", "in_progress", "postponed"}


def _open_tasks(state):
    return [t for t in state.get("commitments", {}).get("tasks", [])
            if t.get("status") in OPEN_STATUSES]


def has_upcoming_appointment(state, config, now) -> Tuple[bool, dict]:
    window = config.get("automation", {}).get("upcoming_window_minutes", 60)
    best = None
    best_mins = None
    items = (state.get("commitments", {}).get("appointments", []) +
             state.get("commitments", {}).get("events", []))
    for item in items:
        starts = clock.parse_iso(item.get("starts_at"))
        if not starts:
            continue
        mins = (starts - now).total_seconds() / 60.0
        if 0 <= mins <= window:
            if best_mins is None or mins < best_mins:
                best, best_mins = item, mins
    if best is None:
        return False, {}
    return True, {"appointment": best, "minutes_until": int(round(best_mins))}


def has_due_reminder(state, config, now) -> Tuple[bool, dict]:
    reminders = state.get("support", {}).get("reminders", [])
    due = [r for r in reminders
           if r.get("status") == "scheduled"
           and (clock.parse_iso(r.get("due_at")) or now) <= now]
    if not due:
        return False, {}
    due.sort(key=lambda r: r.get("due_at", ""))
    r = due[0]
    linked_task = None
    if r.get("linked_type") == "task":
        for t in state.get("commitments", {}).get("tasks", []):
            if str(t.get("id")) == str(r.get("linked_id")):
                linked_task = t
                break
    return True, {"reminder": r, "linked_task": linked_task}


def has_overdue_task(state, config, now) -> Tuple[bool, dict]:
    out = []
    for t in _open_tasks(state):
        deadline = clock.parse_iso(t.get("deadline"))
        if deadline and deadline < now:
            out.append(t)
    if not out:
        return False, {}
    out.sort(key=lambda t: (t.get("priority", 9), t.get("deadline") or ""))
    return True, {"task": out[0]}


def has_postpone_escalation(state, config, now) -> Tuple[bool, dict]:
    threshold = config.get("automation", {}).get("postpone_escalation_threshold", 3)
    for t in _open_tasks(state):
        if int(t.get("postponed_count", 0)) >= threshold:
            return True, {"task": t, "count": t.get("postponed_count", 0)}
    return False, {}


def is_daily_review_time(state, config, now) -> Tuple[bool, dict]:
    target = config.get("automation", {}).get("daily_review_time", "09:30")
    try:
        hh, mm = target.split(":", 1)
        target_minutes = int(hh) * 60 + int(mm)
    except Exception:
        target_minutes = 9 * 60 + 30
    current_minutes = now.hour * 60 + now.minute
    if current_minutes < target_minutes:
        return False, {}
    last_date = state.get("history", {}).get("last_daily_review_date")
    if last_date == now.date().isoformat():
        return False, {}
    tasks = _open_tasks(state)
    top = sorted(tasks, key=lambda t: (t.get("priority", 9), t.get("deadline") or "9999"))[:3]
    return True, {"open_count": len(tasks), "top": top}


def has_pending_onboarding(state, config, now) -> Tuple[bool, dict]:
    loops = state.get("support", {}).get("open_loops", [])
    pending = [o for o in loops
               if str(o.get("id", "")).startswith("onboarding-")
               and o.get("status") == "open"]
    if not pending:
        return False, {}
    gap_hours = config.get("automation", {}).get("onboarding_nudge_gap_hours", 24)
    last = state.get("history", {}).get("last_onboarding_nudge_at")
    last_dt = clock.parse_iso(last) if last else None
    if last_dt is not None:
        gap_min = (now - last_dt).total_seconds() / 60.0
        if gap_min < gap_hours * 60:
            return False, {}
    return True, {"pending": pending}


REGISTRY: Dict[str, Callable] = {
    "has_upcoming_appointment": has_upcoming_appointment,
    "has_due_reminder": has_due_reminder,
    "has_overdue_task": has_overdue_task,
    "has_postpone_escalation": has_postpone_escalation,
    "is_daily_review_time": is_daily_review_time,
    "has_pending_onboarding": has_pending_onboarding,
}


def resolve(name: str):
    if name not in REGISTRY:
        raise KeyError(f"Unknown predicate: {name}")
    return REGISTRY[name]
