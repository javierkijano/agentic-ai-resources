# Storage Contract: repository-manager

This document defines the expected runtime storage structure for the repository management capability.

## Runtime Structure

The base directory is resolved at runtime based on the agent context, environment, and session.
Pattern: `runtime/{{agent}}/{{env}}/repository-manager/{{session}}/`

| Path | Type | Description |
|------|------|-------------|
| `logs/repository-manager.log` | File | Detailed execution logs for the current session. |
| `session_registry.jsonl` | File | **Audit Log**: Found in the resource root runtime folder. Tracks all sessions executed by the agent. |

## Auditing
To audit the usage of this skill, inspect:
`runtime/{{agent}}/{{env}}/repository-manager/session_registry.jsonl`

Each entry contains:
- `timestamp`: When the operation occurred.
- `operation`: The specific action taken.
- `status`: Outcome of the operation.
- `session_path`: Link to the detailed logs and state of that specific run.
