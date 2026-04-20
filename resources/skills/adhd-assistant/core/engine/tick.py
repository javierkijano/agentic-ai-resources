#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ADHD Assistant tick entrypoint.

Invoked by cron every N minutes. Reads state, evaluates policies, delivers
intervention (if any), persists state, emits structured JSON log line.
"""
import json
import os
import subprocess
import sys
import traceback
from datetime import datetime, timezone

# Allow running both as 'python -m engine.tick' and direct path.
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if SKILL_DIR not in sys.path:
    sys.path.insert(0, SKILL_DIR)

from engine import brain, clock, loader, reconcile, state_store
from engine.migrate import migrate_state_in_place
from actions import registry as actions_registry

HERMES_HOME = os.environ.get("HERMES_HOME", os.path.expanduser("~/.hermes"))
RUNTIME_DIR = os.path.join(HERMES_HOME, "adhd_assistant")
STATE_PATH = os.path.join(RUNTIME_DIR, "state.json")
USER_CONFIG_PATH = os.path.join(RUNTIME_DIR, "config.yaml")
HINDSIGHT_QUEUE = os.path.join(RUNTIME_DIR, "hindsight_queue.jsonl")
LOGS_DIR = os.path.join(RUNTIME_DIR, "logs")
FLUSH_SCRIPT = os.path.join(SKILL_DIR, "scripts", "adhd_assistant_hindsight_flush.py")


def _append_log(line: dict) -> None:
    os.makedirs(LOGS_DIR, exist_ok=True)
    day = datetime.now(timezone.utc).strftime("%Y%m%d")
    path = os.path.join(LOGS_DIR, f"tick-{day}.jsonl")
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")


def _queue_depth(path: str) -> int:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return sum(1 for line in f if line.strip())
    except FileNotFoundError:
        return 0
    except Exception:
        return 0


def _flush_hindsight_queue(cfg: dict) -> dict:
    """Mirror pending hindsight queue entries right after local persistence."""
    hindsight_cfg = (cfg or {}).get("hindsight", {}) or {}
    sync_cfg = (cfg or {}).get("sync", {}) or {}
    sources_cfg = sync_cfg.get("sources", {}) or {}

    enabled = bool(hindsight_cfg.get("enabled", True)) and bool(
        sources_cfg.get("hindsight_reflection", True)
    )
    if not enabled:
        return {
            "attempted": False,
            "enabled": False,
            "reason": "hindsight_sync_disabled",
        }

    pending_before = _queue_depth(HINDSIGHT_QUEUE)
    if pending_before <= 0:
        return {
            "attempted": False,
            "enabled": True,
            "reason": "empty_queue",
            "pending_before": 0,
            "pending_after": 0,
        }

    if not os.path.exists(FLUSH_SCRIPT):
        return {
            "attempted": False,
            "enabled": True,
            "reason": "flush_script_missing",
            "script": FLUSH_SCRIPT,
            "pending_before": pending_before,
        }

    timeout = hindsight_cfg.get("flush_timeout_seconds", 90)
    try:
        timeout = int(timeout)
    except Exception:
        timeout = 90
    if timeout <= 0:
        timeout = 90

    try:
        proc = subprocess.run(
            [sys.executable, FLUSH_SCRIPT],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except Exception as e:
        return {
            "attempted": True,
            "enabled": True,
            "reason": "flush_exec_error",
            "error": str(e),
            "pending_before": pending_before,
            "pending_after": _queue_depth(HINDSIGHT_QUEUE),
        }

    stdout = (proc.stdout or "").strip()
    stderr = (proc.stderr or "").strip()
    parsed = None
    if stdout:
        lines = [ln for ln in stdout.splitlines() if ln.strip()]
        if lines:
            try:
                parsed = json.loads(lines[-1])
            except Exception:
                parsed = {"raw": lines[-1]}

    out = {
        "attempted": True,
        "enabled": True,
        "pending_before": pending_before,
        "pending_after": _queue_depth(HINDSIGHT_QUEUE),
        "exit_code": proc.returncode,
    }
    if parsed is not None:
        out["flush"] = parsed
    if stderr:
        out["stderr"] = stderr[-1000:]
    return out


def main() -> int:
    result = {"status": "ok", "sent": False, "reason": "no_trigger"}
    try:
        # Load + normalize state (handles legacy shape)
        state = state_store.load(STATE_PATH) or {}
        state = state_store.ensure_skeleton(state)
        state, migrated_hints = migrate_state_in_place(state)

        # Load effective config (defaults <- user config <- mode overrides)
        cfg, mode_info = loader.build_effective_config(USER_CONFIG_PATH)

        tz_name = cfg.get("profile", {}).get("timezone", "Europe/Madrid")
        now = clock.now(tz_name)

        # Periodic local reconciliation (legacy tasks.json -> state.json).
        sync_summary = None
        should_sync, sync_reason = reconcile.should_run_sync(state, cfg, now)
        if should_sync:
            sync_summary = reconcile.reconcile_local_tasks_json(state, cfg, now)
            sync_summary["run_reason"] = sync_reason
            history = state.setdefault("history", {})
            history["last_sync_at"] = now.isoformat()
            recent = history.setdefault("recent_events", [])
            recent.append({
                "at": now.isoformat(),
                "kind": "sync_reconcile",
                "summary": (
                    f"added={sync_summary.get('added_count', 0)} "
                    f"updated={sync_summary.get('updated_count', 0)} "
                    f"conflicts={sync_summary.get('conflicts_count', 0)}"
                ),
            })
            if len(recent) > 200:
                del recent[:-200]
        else:
            sync_summary = {"ran": False, "reason": sync_reason}

        policies = loader.load_policies()
        policies = loader.filter_policies_by_mode(policies, mode_info)

        coaching_themes = cfg.get("coaching", {}).get("themes", [])
        coaching_banks = loader.load_coaching_banks(coaching_themes)

        intervention = brain.decide(state, cfg, policies, now)

        ctx = {
            "state": state,
            "config": cfg,
            "now": now,
            "hindsight_queue_path": HINDSIGHT_QUEUE,
        }

        # Stamp last_tick regardless of outcome
        state.setdefault("history", {})["last_tick_at"] = now.isoformat()

        if intervention is None:
            result["reason"] = "no_trigger"
        else:
            policy = intervention["policy"]
            quiet = clock.within_quiet_hours(
                cfg.get("preferences", {}).get("quiet_hours")
                or cfg.get("automation", {}).get("quiet_hours"),
                now,
            )
            ignore_quiet = bool(policy.get("ignore_quiet_hours", False))
            critical = policy.get("urgency") == "critical"

            if quiet and not (ignore_quiet or critical):
                result["reason"] = "quiet_hours"
                result["policy_id"] = policy.get("id")
            else:
                text = brain.render_message(intervention, cfg, state, coaching_banks)

                # Deliver to channels
                channel_results = []
                from engine.renderer import render as tpl_render
                for ch in policy.get("channels", []) or []:
                    resolved = tpl_render(ch, {"config": cfg, "bindings": intervention["bindings"]})
                    if not resolved:
                        continue
                    cr = actions_registry.send_via_channel(resolved, text, ctx)
                    channel_results.append({"channel": resolved, **cr})

                sent_any = any(r.get("ok") for r in channel_results)
                result["sent"] = sent_any
                result["reason"] = policy.get("id")
                result["channels"] = channel_results
                result["text"] = text

                # Side effects (run regardless of channel success, they update state/history)
                side_results = []
                for se in policy.get("side_effects", []) or []:
                    action_name = se.get("action")
                    raw_args = se.get("args") or {}
                    rendered_args = {}
                    for k, v in raw_args.items():
                        if isinstance(v, str):
                            rendered_args[k] = tpl_render(
                                v, {"config": cfg, "bindings": intervention["bindings"]}
                            )
                        else:
                            rendered_args[k] = v
                    sr = actions_registry.run_side_effect(action_name, rendered_args, ctx)
                    side_results.append({"action": action_name, **sr})
                result["side_effects"] = side_results

        # Persist state
        state.setdefault("meta", {})["last_modified"] = now.isoformat()
        state_store.save(STATE_PATH, state)

        # Local-first invariant: after local persistence, explicitly mirror queue to Hindsight.
        hindsight_sync = _flush_hindsight_queue(cfg)
        if hindsight_sync.get("attempted") or hindsight_sync.get("reason") not in {
            "empty_queue",
            None,
        }:
            result["hindsight_sync"] = hindsight_sync

        sync_mode = str((cfg.get("sync", {}) or {}).get("discrepancy_summary", "default")).lower()
        if sync_summary and sync_mode != "off":
            if sync_mode == "verbose-modern":
                result["sync"] = sync_summary
            elif sync_summary.get("ran"):
                compact = {
                    "added": sync_summary.get("added_count", 0),
                    "updated": sync_summary.get("updated_count", 0),
                    "conflicts": sync_summary.get("conflicts_count", 0),
                    "missing_in_source": sync_summary.get("missing_in_source_count", 0),
                    "reminders_added": sync_summary.get("reminders_added", 0),
                    "reminders_updated": sync_summary.get("reminders_updated", 0),
                    "error": sync_summary.get("error"),
                }
                if any([
                    compact["added"],
                    compact["updated"],
                    compact["conflicts"],
                    compact["missing_in_source"],
                    compact["reminders_added"],
                    compact["reminders_updated"],
                    compact["error"],
                ]):
                    result["sync"] = compact

        result["at"] = now.isoformat()
        if migrated_hints:
            result["migration"] = migrated_hints

        _append_log(result)
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except Exception as e:
        err = {
            "status": "error",
            "error": str(e),
            "trace": traceback.format_exc(),
        }
        try:
            _append_log(err)
        except Exception:
            pass
        print(json.dumps(err, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    sys.exit(main())
