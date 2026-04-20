# -*- coding: utf-8 -*-
"""Brain: orchestrates decide -> render -> deliver -> side-effects."""
from datetime import datetime
from typing import List, Optional

from . import clock, coach, loader, predicates, renderer
from .selector import cooldown_ok, urgency_gap_key


def _get_mode_info(cfg, mode_info):
    return mode_info


def _resolve_cooldown(policy: dict, config: dict) -> int:
    cd = policy.get("cooldown", {}) or {}
    gap = cd.get("global_min_gap_minutes")
    if isinstance(gap, (int, float)):
        return int(gap)
    # default by urgency
    urgency = policy.get("urgency", "normal")
    if urgency == "critical":
        return int(config.get("automation", {}).get("min_gap_urgent_minutes", 15))
    return int(config.get("automation", {}).get("min_gap_nonurgent_minutes", 60))


def decide(state: dict, config: dict, policies: List[dict], now: datetime) -> Optional[dict]:
    """Evaluate policies in priority order. Return first matching rendered intervention."""
    history = state.get("history", {})
    last_any = history.get("last_proactive_message_at")
    last_any_dt = clock.parse_iso(last_any) if last_any else None

    for p in policies:
        trigger = p.get("trigger", {}) or {}
        pname = trigger.get("predicate")
        if not pname:
            continue
        try:
            fn = predicates.resolve(pname)
        except KeyError:
            continue
        ok, bindings = fn(state, config, now)
        if not ok:
            continue

        # cooldown (global)
        gap_needed = _resolve_cooldown(p, config)
        if not cooldown_ok(last_any_dt, now, gap_needed):
            continue

        return {
            "policy": p,
            "bindings": bindings,
            "now": now,
        }
    return None


def render_message(intervention: dict, config: dict, state: dict, coaching_banks: dict) -> str:
    p = intervention["policy"]
    bindings = intervention["bindings"]
    now = intervention["now"]

    coaching_context = (p.get("message", {}) or {}).get("coaching_context")
    quote = None
    if coaching_context:
        quote = coach.pick_quote(
            config.get("coaching", {}) or {},
            coaching_banks,
            state,
            coaching_context,
            now,
        )

    ctx = {
        "bindings": bindings,
        "config": config,
        "state": state,
        "coaching_quote": quote,
        "now": now,
    }
    tmpl = (p.get("message", {}) or {}).get("template", "")
    text = renderer.render(tmpl, ctx)
    return text
