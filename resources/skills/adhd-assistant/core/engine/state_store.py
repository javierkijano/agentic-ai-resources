# -*- coding: utf-8 -*-
"""Atomic load/save for state.json."""
import json
import os
import tempfile


def load(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save(path: str, state: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    dir_ = os.path.dirname(path)
    fd, tmp = tempfile.mkstemp(prefix=".state-", suffix=".json", dir=dir_)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    except Exception:
        try:
            os.remove(tmp)
        except OSError:
            pass
        raise


def ensure_skeleton(state: dict) -> dict:
    """Guarantee required top-level sections exist. Non-destructive."""
    defaults = {
        "commitments": {"tasks": [], "appointments": [], "events": [], "routines": [], "checklists": []},
        "support": {"reminders": [], "notes": [], "ideas": [], "open_loops": [], "recommendations": []},
        "self_observation": {"mood_log": [], "energy_log": [], "focus_log": [], "sleep_log": [], "stress_flags": [], "perceived_overload": 0},
        "execution": {"current_front": None, "secondary_front": None, "active_intervention": None, "next_actions": [], "active_focus_block": None, "progress_checkpoints": [], "rescue_plan": None},
        "history": {"recent_events": [], "recent_nudges": [], "recent_completions": [], "recent_postponements": [], "onboarding_decisions": []},
        "meta": {"version": "2.0.0", "active_schema_version": "2.0.0"},
    }
    for k, v in defaults.items():
        if k not in state or not isinstance(state.get(k), dict) and not isinstance(v, dict):
            state[k] = v
        elif isinstance(v, dict):
            state.setdefault(k, {})
            for kk, vv in v.items():
                state[k].setdefault(kk, vv)
    return state
