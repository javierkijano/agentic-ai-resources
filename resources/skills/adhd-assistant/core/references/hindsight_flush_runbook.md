# Hindsight Queue Flush Runbook (Cron-safe)

Goal: keep `~/.hermes/adhd_assistant/hindsight_queue.jsonl` drained with a **local-first + explicit mirror** model.
- Primary path: `engine/tick.py` persists `state.json`, then calls the flush script immediately.
- Safety net: dedicated cron flush job retries pending backlog.

## Why this exists
Some runtimes do not expose `hindsight_retain` as a callable tool, so queue flushing must run in Python (`hindsight_client` / `HindsightEmbedded`).

## Runtime components
- Canonical skill script: `{{AGENTIC_RESOURCES}}/hermes/skills/adhd-assistant/scripts/adhd_assistant_hindsight_flush.py`
- Cron job target: `scripts/adhd_assistant_hindsight_flush.py` (resolved inside the skill tree)
- Trigger #1: post-write call from `engine/tick.py`
- Trigger #2 (backup): cron job `adhd-assistant-hindsight-queue-flush`
- Cron mode (recommended): `deliver=origin` + `[SILENT]` when status is healthy
  - This gives alerting without noise: only `partial|error` is delivered.
  - If you want zero chat delivery in all cases, switch to `deliver=local`.
- Script output: one JSON summary line
- Script log: `~/.hermes/adhd_assistant/logs/hindsight_flush.jsonl`
- Current deployment: alert mode enabled (deliver `origin` + `[SILENT]` on healthy runs).

## Script guarantees
- Never drops unsent entries
- Uses file locking so queue appends wait while a flush rewrite is in progress
- On first failure, stops and preserves failed+remaining lines
- Rewrites queue only with successfully processed entries removed
- Uses deterministic `document_id` hash for idempotent retries

## Hindsight client strategy
- Preferred: `HindsightEmbedded` (local_embedded mode)
- Client calls: `hindsight_client` async `aretain(...)`
- Suppresses daemon startup console noise in cron runs

## Ops checks
1. Queue depth
   - `wc -l ~/.hermes/adhd_assistant/hindsight_queue.jsonl`
2. Flush log
   - `tail -n 20 ~/.hermes/adhd_assistant/logs/hindsight_flush.jsonl`
3. Cron outputs
   - `~/.hermes/cron/output/<job_id>/...`

## Failure behavior
- `status=partial|error` in script JSON
- Queue is preserved (no blind truncation)
- Cron response emits short technical line when non-ok
