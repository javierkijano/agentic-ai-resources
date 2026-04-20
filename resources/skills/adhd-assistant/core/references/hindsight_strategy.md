# Hindsight Memory Integration Strategy

This skill synchronizes its structured state and key events with the long-term memory system (`hindsight` used locally as "Ginsai") to enable deep analysis, pattern recognition, and world-modeling.

## Core Principle: Dual-Layer Memory

1.  **Local State (`~/.hermes/adhd_assistant/state.json`):** The primary source of truth for operational, real-time data. Fast, immediate, and mutable.
2.  **Hindsight Long-Term Memory:** An indexed, searchable repository for historical data. Used for analysis, reflection, and cross-session insights.

## Data Synchronization Approach

Data is synchronized to Hindsight in the following ways:

### 1. Periodic Full Snapshot (`adhd-assistant:state-snapshot`)
    - **Trigger:** Daily review, or after significant configuration changes.
    - **Content:** The complete `adhd_assistant/state.json` (or a filtered export).
    - **Purpose:** Provides a comprehensive "restore point" and enables longitudinal trend analysis.
    - **Tags:** `adhd-assistant`, `type:state-snapshot`, `subject:full-state`, `mode:<current_mode>`, `user:<username>`

### 2. Event-Stream Logging (`adhd-assistant:event:<event_type>`)
    - **Trigger:** Key actions and state changes (task creation/completion, preference changes, mood logs, appointment upcoming, etc.).
    - **Content:** Structured JSON detailing the event (e.g., task ID, title, timestamp, priority).
    - **Purpose:** Enables fine-grained semantic recall, pattern identification (e.g., "When does Javier usually struggle?"), and chronological analysis.
    - **Tags:** `adhd-assistant`, `type:event`, `subject:<event_type>`, `task-id:<id>`, `mode:<current_mode>`, `user:<username>`

### 3. Preference Persistence (`adhd-assistant:user-preference-change`)
    - **Trigger:** When the user explicitly modifies assistant behavior (mode, coaching level, reminder intensity, etc.).
    - **Content:** JSON describing the change (field, new value, old value, reason, timestamp).
    - **Purpose:** Tracks user adaptation of the assistant's profile and allows for behavioral analysis.
    - **Tags:** `adhd-assistant`, `type:preference-change`, `subject:mode-change`, `field:<field_name>`, `user:<username>`

### 4. Coaching Log (`adhd-assistant:coaching-reflection`)
    - **Trigger:** When the assistant provides a coaching reflection or quote.
    - **Content:** JSON containing the quote, its theme, and context.
    - **Purpose:** Analyzes the effectiveness and context of the coaching interventions.
    - **Tags:** `adhd-assistant`, `type:coaching`, `subject:quote`, `theme:<theme>`, `user:<username>`

## Best Practices for Hindsight Entries

*   **JSON Content:** Always serialize complex data structures into JSON strings for `content`.
*   **Consistent Context:** Use `skill_name:data_type` (e.g., `adhd-assistant:event`).
*   **Meaningful Tags:** Employ specific, normalized tags for efficient searching and grouping.
*   **Privacy:** Ensure sensitive data is not logged directly or is anonymized/masked if necessary. Hindsight being local mitigates this, but it's good practice.

## Synchronization Logic

*   **Local first, Hindsight second:** All critical state changes are first applied to `state.json`.
*   **Explicit post-write mirror:** After local persistence, the runtime immediately attempts to flush queued Hindsight entries.
*   **Event-driven sync:** Significant changes trigger immediate structured logging to Hindsight (`adhd-assistant:event:*`).
*   **Periodic snapshots:** The `adhd_assistant_tick.py` script handles periodic full state snapshots.
*   **Queue safety invariant:** Pending entries in `hindsight_queue.jsonl` are removed only after confirmed successful retain. If retain fails or is unavailable, entries remain queued for retry.
*   **Reconciliation invariant:** If local and Hindsight diverge, rebuild from the oldest reliable combined evidence and rewrite local first, then mirror the repaired state back to Hindsight.
*   **Agent Orchestration:** The main agent loop orchestrates Hindsight calls based on events and state modifications performed by the `adhd-assistant` skill.
