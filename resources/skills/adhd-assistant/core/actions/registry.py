# -*- coding: utf-8 -*-
"""Action registry: channels + state mutations + hindsight hooks.

Each action is a callable: fn(args: dict, ctx: dict) -> None
where ctx = {'state', 'config', 'now', 'logger', 'hindsight_queue'}.
"""
from typing import Callable, Dict

from .channels.stdout import send as stdout_send
from .channels.telegram import send as telegram_send
from .state_mutations.append_history import run as append_history
from .state_mutations.bump_nudge_count import run as bump_nudge_count
from .state_mutations.mark_reminder_sent import run as mark_reminder_sent
from .state_mutations.set_last_daily_review import run as set_last_daily_review
from .state_mutations.set_last_onboarding_nudge import run as set_last_onboarding_nudge
from .hindsight.log_event import run as hindsight_log
from .hindsight.snapshot_state import run as hindsight_snapshot


CHANNELS: Dict[str, Callable] = {
    "telegram": telegram_send,
    "stdout": stdout_send,
}

SIDE_EFFECTS: Dict[str, Callable] = {
    "append_history": append_history,
    "bump_nudge_count": bump_nudge_count,
    "mark_reminder_sent": mark_reminder_sent,
    "set_last_daily_review": set_last_daily_review,
    "set_last_onboarding_nudge": set_last_onboarding_nudge,
    "hindsight_log": hindsight_log,
    "hindsight_snapshot": hindsight_snapshot,
}


def send_via_channel(name: str, text: str, ctx: dict) -> dict:
    if name not in CHANNELS:
        return {"ok": False, "error": f"unknown_channel:{name}"}
    return CHANNELS[name](text, ctx) or {"ok": True}


def run_side_effect(action_name: str, args: dict, ctx: dict) -> dict:
    if action_name not in SIDE_EFFECTS:
        return {"ok": False, "error": f"unknown_action:{action_name}"}
    return SIDE_EFFECTS[action_name](args or {}, ctx) or {"ok": True}
