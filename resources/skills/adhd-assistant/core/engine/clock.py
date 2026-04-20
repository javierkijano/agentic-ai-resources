# -*- coding: utf-8 -*-
"""Time, timezone and quiet-hours utilities."""
from datetime import datetime

try:
    from zoneinfo import ZoneInfo
except Exception:  # pragma: no cover
    ZoneInfo = None


def get_tz(tz_name: str):
    if ZoneInfo and tz_name:
        try:
            return ZoneInfo(tz_name)
        except Exception:
            return None
    return None


def now(tz_name: str = "Europe/Madrid") -> datetime:
    tz = get_tz(tz_name)
    return datetime.now(tz) if tz else datetime.now()


def parse_iso(text):
    if not text:
        return None
    try:
        return datetime.fromisoformat(text)
    except Exception:
        return None


def minutes_between(a: datetime, b: datetime) -> float:
    if a is None or b is None:
        return float("inf")
    return (b - a).total_seconds() / 60.0


def _hhmm_to_minutes(hhmm: str) -> int:
    h, m = hhmm.split(":", 1)
    return int(h) * 60 + int(m)


def within_quiet_hours(quiet_cfg, current: datetime) -> bool:
    """quiet_cfg: dict with 'start' and 'end' (HH:MM) OR string 'HH:MM-HH:MM'."""
    if not quiet_cfg:
        return False
    if isinstance(quiet_cfg, str):
        if "-" not in quiet_cfg:
            return False
        start, end = quiet_cfg.split("-", 1)
    else:
        start = quiet_cfg.get("start")
        end = quiet_cfg.get("end")
    if not start or not end or start == end:
        return False
    cur = current.hour * 60 + current.minute
    s = _hhmm_to_minutes(start)
    e = _hhmm_to_minutes(end)
    if s < e:
        return s <= cur < e
    return cur >= s or cur < e
