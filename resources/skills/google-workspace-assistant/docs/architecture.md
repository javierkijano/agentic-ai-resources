# Google Workspace Assistant Architecture

## Product framing

This skill models a personal assistant with its own Google ecosystem.

It is not a free-form multi-profile abstraction.
The right mental model is:

- many `source` accounts: human-owned accounts the assistant may read from
- one `workspace` account: the assistant's writable sandbox

The assistant reads from source accounts and writes only into the workspace account.

## Why this model

This solves two practical problems at once:

1. The assistant can read real inbox context from the user's actual accounts.
2. The assistant cannot damage those accounts through write operations.

Any notes, summaries, draft documents, trackers, or intermediate artifacts are stored in the workspace account instead.

## Roles

### Source accounts

A source account is a real user-owned Google account.

Examples:
- personal Gmail
- company inbox the user wants the assistant to read
- a second personal account

Recommended permissions for each source account:
- Gmail: readonly
- Drive: readonly only if needed
- Docs: readonly only if needed
- Sheets: readonly only if needed
- Calendar: readonly only if needed

Forbidden operations on source accounts:
- Gmail send/reply/modify
- Drive create/update/delete
- Docs create/update/delete
- Sheets update/append if the sheet is source-owned
- Calendar create/update/delete
- any destructive or state-changing operation

### Workspace account

The workspace account is the assistant's own Google environment.

Recommended permissions:
- Drive: read/write
- Docs: read/write
- Sheets: read/write
- Calendar: optional read/write
- Gmail: optional; keep send disabled by default in v1

Allowed operations in the workspace account:
- create working docs
- keep private summaries
- write draft responses into docs
- maintain trackers and spreadsheets
- store assistant-generated artifacts

## Multi-account model

This skill should support multiple source accounts.

Examples:
- `personal`
- `metabestec`
- `finance`

But it should keep a single canonical writable workspace by default:
- `assistant`

That asymmetry is important. Multi-account should expand readable sources, not multiply writable surfaces unless explicitly needed later.

## Core routing rule

Route by role first, then by alias.

Good examples:
- read Gmail thread from `source:personal`
- read Gmail thread from `source:metabestec`
- create summary doc in `workspace:assistant`
- append task row in `workspace:assistant`

Bad examples:
- arbitrary `--profile` switching where any account could become a write target

## Capability matrix

| Capability | Source accounts | Workspace account |
|---|---|---|
| Gmail search/read | Yes | Optional |
| Gmail send/reply/modify | No | Optional, disabled by default |
| Drive search/read | Yes | Yes |
| Drive create/update/delete | No | Yes |
| Docs read | Yes | Yes |
| Docs create/update/delete | No | Yes |
| Sheets read | Yes | Yes |
| Sheets update/append | No | Yes |
| Calendar list | Yes | Yes |
| Calendar create/update/delete | No | Optional |

## Why this is better than forwarding

Forwarding creates copies and often loses thread continuity.

Direct readonly access to source accounts lets the assistant inspect:
- the real thread state
- the real inbox context
- the real sender/recipient metadata

But all writing still stays in the workspace account.

## Credential design

Use one credential bundle per account alias under a dedicated Hermes data root.

Canonical storage root:
- `~/.hermes/google_workspace_assistant/`

Suggested layout:
- `~/.hermes/google_workspace_assistant/accounts.yaml`
- `~/.hermes/google_workspace_assistant/accounts/personal/token.json`
- `~/.hermes/google_workspace_assistant/accounts/personal/client_secret.json`
- `~/.hermes/google_workspace_assistant/accounts/personal/pending_oauth.json`
- `~/.hermes/google_workspace_assistant/accounts/metabestec/token.json`
- `~/.hermes/google_workspace_assistant/accounts/metabestec/client_secret.json`
- `~/.hermes/google_workspace_assistant/accounts/metabestec/pending_oauth.json`
- `~/.hermes/google_workspace_assistant/accounts/assistant/token.json`
- `~/.hermes/google_workspace_assistant/accounts/assistant/client_secret.json`
- `~/.hermes/google_workspace_assistant/accounts/assistant/pending_oauth.json`

## Account registry

The runtime should load a registry that declares:
- alias
- role (`source` or `workspace`)
- enabled services
- human description

Command routing should be enforced in code from role + command type, not as a freely editable per-command policy in the registry. This keeps the runtime deterministic and avoids slipping back into generic multi-profile thinking.

Minimal v1 registry shape:

```yaml
accounts:
  personal:
    role: source
    description: Cuenta personal principal
    services:
      gmail: readonly
      drive: readonly
      docs: readonly
      sheets: readonly
      calendar: readonly

  assistant:
    role: workspace
    description: Sandbox del asistente
    services:
      gmail: disabled
      drive: readwrite
      docs: readwrite
      sheets: readwrite
      calendar: disabled

defaults:
  workspace_alias: assistant
  default_source_alias: personal
```

## Safety invariants

1. No source account write path exists in the assistant skill.
2. All write commands resolve only to the workspace account.
3. Outbound email stays disabled in v1.
4. Multi-account applies to readable sources, not to unrestricted writes.
5. The user should be able to inspect all configured accounts and their roles.

## Current implementation gap

The builtin `google-workspace` skill is single-account.
It does not yet support this model.

A dedicated implementation for this skill should add:
- account registry support
- role-aware credential loading
- source/workspace command routing
- write-capable Docs/Drive/Sheets operations on the workspace account
- explicit prohibition of writes on source accounts
