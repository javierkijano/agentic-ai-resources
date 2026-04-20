# -*- coding: utf-8 -*-
"""Coaching quote selection from YAML banks."""
from typing import Optional

from . import clock


def pick_quote(coaching_cfg: dict, banks: dict, state: dict, context: str, now) -> Optional[str]:
    if not coaching_cfg.get("enabled", False):
        return None
    if not state.get("preferences", {}).get("use_quotes_reflections", True):
        # legacy compat
        if state.get("preferences", {}).get("quotes_enabled") is False:
            return None
    if not banks:
        return None

    max_per_day = int(coaching_cfg.get("max_quotes_per_day", 1))
    today = now.date().isoformat()
    last_used = state.get("coaching", {}).get("last_used", [])
    used_today = [x for x in last_used if isinstance(x, str) and x.startswith(today)]
    if len(used_today) >= max_per_day:
        return None

    # candidate pool from banks whose enabled_in_contexts matches
    pool = []
    for theme, bank in banks.items():
        contexts_ok = bank.get("enabled_in_contexts") or []
        if contexts_ok and context not in contexts_ok:
            continue
        for q in bank.get("quotes", []) or []:
            pool.append((theme, q))
    if not pool:
        return None

    idx = (len(last_used) + abs(hash(context))) % len(pool)
    theme, quote = pool[idx]

    coaching_state = state.setdefault("coaching", {})
    coaching_state.setdefault("last_used", []).append(f"{today}:{context}:{theme}:{idx}")
    coaching_state["last_used"] = coaching_state["last_used"][-20:]
    return quote
