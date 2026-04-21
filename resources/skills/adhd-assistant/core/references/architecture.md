# ADHD Assistant v2 — Architecture

## One-screen mental model

```
cron (every 10m)
   │
   ▼
skills/adhd-assistant/scripts/adhd_assistant_tick.py   ← canonical cron entrypoint
   │
   ▼
skills/adhd-assistant/engine/tick.py         ← real entrypoint
   │
   ├── state_store.load(state.json)        ← dynamic state only
   ├── loader.build_effective_config()     ← defaults.yaml + config.yaml + mode overlay
   ├── loader.load_policies()              ← YAML files, priority-ordered
   ├── loader.filter_policies_by_mode()    ← operator/companion/recovery/mosca filters
   │
   ▼
brain.decide(state, config, policies, now)
   │
   ├── for each policy (priority order):
   │     predicate = predicates.REGISTRY[policy.trigger.predicate]
   │     ok, bindings = predicate(state, config, now)
   │     if ok and cooldown_ok: return intervention
   │
   ▼
intervention?
   │
   ├── quiet_hours? (skip unless urgency=critical or ignore_quiet_hours)
   ├── renderer.render(message.template, {bindings, config, state, coaching_quote})
   ├── for each channel: actions.registry.CHANNELS[ch].send(text)
   └── for each side_effect: actions.registry.SIDE_EFFECTS[name].run(args, ctx)
         ↑
         includes hindsight_log / hindsight_snapshot → writes to hindsight_queue.jsonl
   │
   ▼
state_store.save(state.json)   ← only dynamic fields (local-first write)
flush hindsight_queue.jsonl     ← explicit mirror attempt (queue-safe)
logs/tick-YYYYMMDD.jsonl       ← structured audit trail
```

## Separation of state vs configuration

state.json (dynamic, updated every tick):
  commitments, support, self_observation, execution, history, meta

config.yaml (user-editable, rarely changes):
  profile, preferences, automation, coaching, delivery, hindsight

defaults.yaml (shipped with the skill, never edited by user)

Effective config = deep_merge(defaults, user config) + mode overrides.

## Adding a new intervention

1. Create `config/policies/60-my-policy.yaml` with fields:
   id, priority, urgency, trigger.predicate, message.template, channels, side_effects.
2. If the predicate is new, add it to `engine/predicates.py` and register it in REGISTRY.
3. If new coaching frames are needed, create/expand YAML under `config/coaching/`.
4. Add a fixture to `tests/fixtures/` and an assertion in `tests/test_policies.py`.
5. No changes to the brain or tick — they discover new policies automatically.

## Adding a new mode

Create `config/modes/<name>.yaml` with:
- `overrides:` dotted keys (e.g. `automation.min_gap_urgent_minutes: 5`)
- `policy_filters:` `disable:` list / `enable_only_critical: true`

Set `preferences.primary_mode: <name>` in `config.yaml` to activate.

## Adding a new channel

1. Create `actions/channels/<name>.py` exporting `send(text, ctx) -> {'ok': bool, ...}`.
2. Register in `actions/registry.py` → `CHANNELS` dict.
3. Set `delivery.default_channel: <name>` (or reference it per-policy).

## Hindsight integration

The runtime enforces **local-first + explicit mirror**:

- `actions/hindsight/log_event.py` and `snapshot_state.py` append entries to
  `~/.hermes/adhd_assistant/hindsight_queue.jsonl`.
- After `state_store.save(...)`, `engine/tick.py` calls the canonical skill-local
  flush script `scripts/adhd_assistant_hindsight_flush.py`.
- The cron backup job targets `scripts/adhd_assistant_hindsight_flush.py` directly
  from the skill tree; no external wrapper is involved.
- If flush succeeds, queue is drained; if flush fails, queue remains intact for
  retry (never blind-truncate).
- Recovery/reconciliation still compares local stores + Hindsight evidence when
  divergence is detected.

This keeps write ordering deterministic (local first) while preserving durable,
explicit mirroring to Hindsight in the same operational cycle.

## File layout

```
adhd-assistant/
├── SKILL.md
├── manifest.yaml
├── engine/
│   ├── tick.py           ← main entrypoint
│   ├── brain.py          ← decide + render
│   ├── loader.py         ← config + policies + modes + coaching loaders
│   ├── selector.py       ← cooldown helpers
│   ├── predicates.py     ← registered trigger functions
│   ├── renderer.py       ← Jinja2 wrapper
│   ├── coach.py          ← coaching quote picker
│   ├── clock.py          ← tz + quiet_hours + iso parsing
│   ├── state_store.py    ← atomic load/save
│   └── migrate.py        ← v1 → v2 migration (idempotent)
├── scripts/
│   ├── adhd_assistant_tick.py            ← canonical skill-local launcher
│   └── adhd_assistant_hindsight_flush.py ← canonical queue flush script
├── actions/
│   ├── registry.py
│   ├── channels/{telegram,stdout}.py
│   ├── state_mutations/{append_history, bump_nudge_count, mark_reminder_sent, ...}.py
│   └── hindsight/{log_event, snapshot_state}.py
├── config/
│   ├── defaults.yaml
│   ├── policies/*.yaml       ← one policy per file, priority-ordered
│   ├── modes/*.yaml
│   └── coaching/*.yaml
├── data/
│   ├── state.initial.json
│   ├── state.schema.json
│   └── config.schema.json
├── references/*.md        ← design docs (humans only, never read at runtime)
└── tests/
    ├── test_policies.py
    └── fixtures/*.json
```

## Runtime paths (outside the skill, user-local)

- `~/.hermes/adhd_assistant/state.json`           — dynamic state
- `~/.hermes/adhd_assistant/config.yaml`          — user config (overrides defaults)
- `~/.hermes/adhd_assistant/hindsight_queue.jsonl`— pending hindsight entries
- `~/.hermes/adhd_assistant/logs/tick-*.jsonl`    — per-day tick audit trail
- No skill-owned executable artifacts live under `~/.hermes/scripts/`.

## Monitoring web app (read-only)

For integral observability and future expansion, the skill also includes a
FastAPI dashboard under `webapp/`:

- `webapp/services/runtime_monitor.py` is the extensible read-only service layer.
- `webapp/app.py` exposes JSON APIs and HTML dashboard.
- UI consumes `/api/*` endpoints; adding new panels is mostly service + JS wiring.

Run locally from skill dir:

```bash
python3 -m webapp.app
```

Default URL: `http://127.0.0.1:8765`

## Testing

```
cd {{AGENTIC_RESOURCES}}/hermes/skills/adhd-assistant
python3 -m tests.test_policies
```

## Migration from v1

Automatic and idempotent on first tick:
- Seeds `~/.hermes/adhd_assistant/config.yaml` from v1 state's profile/preferences/automation/coaching.
- Strips those keys from state.json.
- Sets `meta.active_schema_version = "2.0.0"`.
- Re-runs migration if it ever detects legacy keys back (defensive against partial writes).
