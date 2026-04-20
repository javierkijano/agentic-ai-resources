# -*- coding: utf-8 -*-
"""Policy engine integration tests. Run:
   cd adhd-assistant && python -m tests.test_policies
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL_DIR = os.path.dirname(HERE)
if SKILL_DIR not in sys.path:
    sys.path.insert(0, SKILL_DIR)

from engine import brain, loader


def _load_fixture(name):
    with open(os.path.join(HERE, "fixtures", name), "r", encoding="utf-8") as f:
        return json.load(f)


def _config():
    # Use defaults only (no user overrides path) to keep tests hermetic
    cfg, mode_info = loader.build_effective_config(None)
    return cfg, mode_info


def _policies(mode_info):
    pols = loader.load_policies()
    return loader.filter_policies_by_mode(pols, mode_info)


def _now_at(hour, minute, second=0):
    tz = timezone(timedelta(hours=2))
    return datetime(2026, 4, 16, hour, minute, second, tzinfo=tz)


def _assert(cond, msg):
    if not cond:
        raise AssertionError(msg)
    print(f"  ok  {msg}")


def test_no_trigger_on_empty_state_before_daily_review():
    print("test_no_trigger_on_empty_state_before_daily_review")
    state = _load_fixture("state_empty.json")
    cfg, mi = _config()
    pols = _policies(mi)
    # Before daily_review_time (09:30) → nothing fires
    now = _now_at(8, 0)
    r = brain.decide(state, cfg, pols, now)
    _assert(r is None, "empty state before 09:30 produces no intervention")


def test_daily_review_fires_at_0930_once():
    print("test_daily_review_fires_at_0930_once")
    state = _load_fixture("state_empty.json")
    cfg, mi = _config()
    pols = _policies(mi)
    now = _now_at(9, 35)
    r = brain.decide(state, cfg, pols, now)
    _assert(r is not None and r["policy"]["id"] == "daily_review",
            "daily_review must trigger at 09:35")
    # simulate side_effect of mark_reviewed
    state.setdefault("history", {})["last_daily_review_date"] = now.date().isoformat()
    r2 = brain.decide(state, cfg, pols, now)
    _assert(r2 is None, "daily_review should not re-fire same day")


def test_overdue_task_triggers():
    print("test_overdue_task_triggers")
    state = _load_fixture("state_overdue.json")
    cfg, mi = _config()
    pols = _policies(mi)
    now = _now_at(19, 0)  # deadline was 18:00
    r = brain.decide(state, cfg, pols, now)
    _assert(r is not None, "overdue task must trigger")
    _assert(r["policy"]["id"] == "overdue_task", f"expected overdue_task, got {r['policy']['id']}")
    text = brain.render_message(r, cfg, state, {})
    _assert("Enviar propuesta Boost" in text, "task title appears in message")


def test_meeting_soon_triggers_critical():
    print("test_meeting_soon_triggers_critical")
    state = _load_fixture("state_meeting_in_10.json")
    now = _now_at(15, 0)
    state["commitments"]["appointments"][0]["starts_at"] = (now + timedelta(minutes=10)).isoformat()
    cfg, mi = _config()
    pols = _policies(mi)
    r = brain.decide(state, cfg, pols, now)
    _assert(r is not None, "upcoming appointment triggers")
    _assert(r["policy"]["id"] == "appointment_soon", f"got {r['policy']['id']}")
    _assert(r["policy"]["urgency"] == "critical", "appointment is critical")


def test_due_reminder_priority_over_overdue():
    print("test_due_reminder_priority_over_overdue")
    # merge overdue task + due reminder => reminder (priority 20) wins over overdue (30)
    state = _load_fixture("state_overdue.json")
    state["support"]["reminders"] = [{
        "id": "r1", "status": "scheduled", "due_at": "2026-04-16T10:00:00+02:00",
        "message": "Pagar factura eDreams"
    }]
    cfg, mi = _config()
    pols = _policies(mi)
    now = _now_at(19, 0)
    r = brain.decide(state, cfg, pols, now)
    _assert(r is not None, "something must trigger")
    _assert(r["policy"]["id"] == "due_reminder", f"reminder wins, got {r['policy']['id']}")


def test_recovery_mode_disables_daily_review():
    print("test_recovery_mode_disables_daily_review")
    state = _load_fixture("state_empty.json")
    # Force a reason for daily_review to trigger (morning time, never reviewed today)
    cfg, mi = _config()
    cfg["preferences"]["primary_mode"] = "recovery"
    # reload mode with recovery overlay + filters
    from engine.loader import load_mode, filter_policies_by_mode
    mi_recovery = {"name": "recovery", "policy_filters": (load_mode("recovery") or {}).get("policy_filters", {})}
    pols = filter_policies_by_mode(loader.load_policies(), mi_recovery)
    now = _now_at(10, 0)
    r = brain.decide(state, cfg, pols, now)
    _assert(r is None or r["policy"]["id"] != "daily_review",
            "daily_review must be filtered out in recovery")


def test_cooldown_blocks_second_nudge():
    print("test_cooldown_blocks_second_nudge")
    state = _load_fixture("state_overdue.json")
    now = _now_at(19, 0)
    # Pretend we just messaged 5 minutes ago
    state["history"]["last_proactive_message_at"] = (now - timedelta(minutes=5)).isoformat()
    cfg, mi = _config()
    pols = _policies(mi)
    r = brain.decide(state, cfg, pols, now)
    _assert(r is None, "cooldown must block")


if __name__ == "__main__":
    tests = [
        test_no_trigger_on_empty_state_before_daily_review,
        test_daily_review_fires_at_0930_once,
        test_overdue_task_triggers,
        test_meeting_soon_triggers_critical,
        test_due_reminder_priority_over_overdue,
        test_recovery_mode_disables_daily_review,
        test_cooldown_blocks_second_nudge,
    ]
    failures = 0
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failures += 1
            print(f"  FAIL {t.__name__}: {e}")
        except Exception as e:
            failures += 1
            print(f"  ERROR {t.__name__}: {e!r}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    sys.exit(1 if failures else 0)
