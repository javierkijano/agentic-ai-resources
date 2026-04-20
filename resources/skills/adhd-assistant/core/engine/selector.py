# -*- coding: utf-8 -*-
"""Cooldown and scheduling helpers used by the brain."""
from datetime import datetime
from typing import Optional


def cooldown_ok(last_dt: Optional[datetime], now: datetime, min_gap_minutes: int) -> bool:
    if last_dt is None:
        return True
    gap_min = (now - last_dt).total_seconds() / 60.0
    return gap_min >= float(min_gap_minutes)


def urgency_gap_key(urgency: str) -> str:
    return "min_gap_urgent_minutes" if urgency == "critical" else "min_gap_nonurgent_minutes"
