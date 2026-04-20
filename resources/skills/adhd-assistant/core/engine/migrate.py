# -*- coding: utf-8 -*-
"""One-shot migration from v1 (config mixed inside state.json) to v2.

Produces a ~/.hermes/adhd_assistant/config.yaml if it doesn't exist yet,
seeded from the current state.json's profile/preferences/automation/coaching
blocks, then strips the static config from state.json (but preserves dynamic
fields like coaching.last_used).

Idempotent: if meta.active_schema_version == "2.0.0", does nothing.
"""
import os
from typing import Tuple

import yaml

HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
RUNTIME_DIR = os.path.join(HERMES_HOME, "adhd_assistant")
USER_CONFIG_PATH = os.path.join(RUNTIME_DIR, "config.yaml")


def migrate_state_in_place(state: dict) -> Tuple[dict, dict]:
    """Return (state, hints). hints is a dict describing what was migrated."""
    meta = state.setdefault("meta", {})
    schema = meta.get("active_schema_version")
    legacy_keys_present = any(
        k in state for k in ("profile", "preferences", "automation", "coaching")
    )
    # Idempotent: if already v2 AND no legacy keys lingering → nothing to do.
    if schema == "2.0.0" and not legacy_keys_present:
        return state, {}

    hints = {"from_schema": schema or "1.0.0", "to_schema": "2.0.0"}

    # --- 1) seed config.yaml if missing ---
    if not os.path.exists(USER_CONFIG_PATH):
        profile = state.get("profile", {}) or {}
        preferences = state.get("preferences", {}) or {}
        automation = state.get("automation", {}) or {}
        coaching = state.get("coaching", {}) or {}

        cfg_out = {}

        if profile:
            cfg_out["profile"] = {
                k: v for k, v in profile.items()
                if k in (
                    "name", "language", "timezone", "communication_style",
                )
            }
            # Telegram chat_id may live inside profile.delivery_channels (v1 template)
            # Legacy states may store delivery_channels as a list (e.g., ["telegram"]).
            dc = profile.get("delivery_channels") or {}
            if isinstance(dc, dict):
                tg = dc.get("telegram") or {}
                if isinstance(tg, dict) and tg.get("chat_id") and tg.get("chat_id") != "REPLACE_ME":
                    cfg_out.setdefault("delivery", {}).setdefault("telegram", {})["chat_id"] = tg["chat_id"]

        # preferences (including quiet_hours + mode naming normalization)
        prefs_out = {}
        for k in ("primary_mode", "coaching_level", "reminder_intensity",
                  "use_quotes_reflections", "prefer_direct_command"):
            if k in preferences:
                prefs_out[k] = preferences[k]
        if "mode" in preferences and "primary_mode" not in prefs_out:
            prefs_out["primary_mode"] = preferences["mode"]
        if "coaching_intensity" in preferences and "coaching_level" not in prefs_out:
            prefs_out["coaching_level"] = preferences["coaching_intensity"]
        if "quotes_enabled" in preferences and "use_quotes_reflections" not in prefs_out:
            prefs_out["use_quotes_reflections"] = preferences["quotes_enabled"]
        if "quiet_hours" in preferences:
            qh = preferences["quiet_hours"]
            if isinstance(qh, dict):
                prefs_out["quiet_hours"] = {"start": qh.get("start"), "end": qh.get("end")}
        if prefs_out:
            cfg_out["preferences"] = prefs_out

        # automation
        auto_out = {}
        name_map = {
            "tick_cadence_minutes": "tick_cadence_minutes",
            "tick_minutes": "tick_cadence_minutes",
            "min_gap_urgent_minutes": "min_gap_urgent_minutes",
            "min_gap_nonurgent_minutes": "min_gap_nonurgent_minutes",
            "postpone_escalation_threshold": "postpone_escalation_threshold",
            "daily_review_time": "daily_review_time",
        }
        for src, dst in name_map.items():
            if src in automation:
                auto_out[dst] = automation[src]
        # telegram chat_id can also live in automation.delivery.telegram.chat_id (v1)
        dlv = automation.get("delivery") or {}
        if isinstance(dlv, dict):
            atg = dlv.get("telegram") or {}
            if isinstance(atg, dict) and atg.get("chat_id") and atg.get("chat_id") != "REPLACE_ME":
                cfg_out.setdefault("delivery", {}).setdefault("telegram", {})["chat_id"] = atg["chat_id"]
        if auto_out:
            cfg_out["automation"] = auto_out

        # coaching
        coach_out = {}
        for k in ("enabled", "max_quotes_per_day", "allow_christian_reflections"):
            if k in coaching:
                coach_out[k] = coaching[k]
        if "themes" in coaching:
            themes = coaching["themes"]
            if isinstance(themes, list) and themes and themes != ["all"]:
                coach_out["themes"] = themes
            elif themes == ["all"]:
                coach_out["themes"] = ["pragmatic", "stoic", "classical"]
        if coach_out:
            cfg_out["coaching"] = coach_out

        if cfg_out:
            os.makedirs(RUNTIME_DIR, exist_ok=True)
            with open(USER_CONFIG_PATH, "w", encoding="utf-8") as f:
                yaml.safe_dump(cfg_out, f, sort_keys=False, allow_unicode=True)
            hints["wrote_config_yaml"] = USER_CONFIG_PATH

    # --- 2) strip static config from state.json ---
    # keep dynamic coaching.last_used into history instead
    if "coaching" in state and isinstance(state["coaching"], dict):
        last_used = state["coaching"].get("last_used", [])
        if last_used:
            state.setdefault("history", {})["coaching_last_used"] = last_used

    for key in ("profile", "preferences", "automation", "coaching"):
        if key in state:
            state.pop(key, None)

    meta["active_schema_version"] = "2.0.0"
    meta["version"] = "2.0.0"
    meta.setdefault("migrated_from", []).append(hints["from_schema"])
    hints["stripped_keys"] = ["profile", "preferences", "automation", "coaching"]
    return state, hints
