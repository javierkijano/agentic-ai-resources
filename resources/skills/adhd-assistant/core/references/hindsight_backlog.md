# Hindsight Backlog Management (v2, queue-safe)

This document defines the canonical backlog behavior for ADHD Assistant.

## Canonical queue file

- Path: `${HERMES_HOME}/adhd_assistant/hindsight_queue.jsonl`
- Format: JSONL (one JSON object per line)
- Typical entry:

```json
{
  "at": "2026-04-18T00:01:01.161673+02:00",
  "context": "adhd-assistant:event:reminder",
  "content": "reminder_due: Recordatorio: Pedir cita médico para psicólogo",
  "tags": ["adhd-assistant"]
}
```

Notes:
- `content` and `context` are the minimum required fields for `hindsight_retain`.
- `tags` are optional metadata.

## Ownership model

- Tick pipeline (`engine/tick.py`) may enqueue entries when immediate retain is unavailable.
- A flush worker may process backlog entries later.
- Flush workers MUST be state-readonly regarding `state.json`.

## Non-negotiable safety rules

1. Never use `memory` as substitute for `hindsight_retain`.
2. Never truncate the queue blindly.
3. Remove only successfully retained lines.
4. Keep failed + unprocessed lines intact.
5. If `hindsight_retain` is unavailable in runtime, do nothing (`[SILENT]` for cron context).
6. Do not modify `${HERMES_HOME}/adhd_assistant/state.json` from queue flush logic.

## Flush algorithm (strict)

1. Read queue file.
2. If file missing/empty -> success no-op.
3. Parse line-by-line JSON.
4. Process entries sequentially with `hindsight_retain(content, context)`.
5. Stop at first failure (or malformed line).
6. Rewrite queue with the failed line and all remaining lines (prefix-trim only successful lines).
7. If all entries succeed, write empty queue.

## Runtime caveat discovered in production

In some cron runtimes, `hindsight_retain` may not be exposed even when available in normal chat sessions.

Implications:
- Do not assume tool parity between chat and cron.
- A dedicated flush cron must first verify tool availability.
- If tool unavailable, keep queue untouched and return `[SILENT]`.

## Observability

Recommended flush output metrics:
- `processed`
- `remaining`
- `status` (`ok` | `partial` | `error`)
- `error` (short message)

Keep logs compact and machine-parseable (JSON preferred).
