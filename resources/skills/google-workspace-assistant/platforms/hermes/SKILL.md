---
name: google-workspace-assistant
description: "Assistant-oriented Google architecture: multiple read-only source accounts plus one writable assistant workspace account. Use when building a personal Google assistant that works across several inboxes without turning the user's real accounts into writable surfaces."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Google, Gmail, Drive, Docs, Sheets, multi-account, assistant, sandbox, readonly]
    related_skills: [google-workspace]
---

# Google Workspace Assistant

A separate skill for an assistant-centric Google setup.

This skill intentionally does not modify or redefine the original `google-workspace` skill. Instead, it defines a different product model:

- one assistant `workspace` account that is writable
- one or more user `source` accounts that stay read-only

## References

- `references/architecture.md` — full source/workspace architecture with multi-source accounts
- `references/accounts-example.yaml` — example account registry for one workspace plus multiple source accounts
- `references/implementation-plan.md` — detailed implementation plan with exact file paths, test files, commands, and rollout order

## Current status

This skill has been implemented completely according to `references/implementation-plan.md`.

## Core model

This is not a generic multi-profile system where the agent can freely pick among equivalent accounts.

It is an asymmetric model:

- `workspace` account: the assistant's own Google sandbox; writable
- `source` accounts: one or more human-owned accounts; read-only

## Intended use

Use this when the assistant must:

- read from multiple inboxes or Google accounts
- preserve real inbox/thread context in those accounts
- create notes, summaries, draft docs, and working artifacts in its own Google account
- avoid writing into the user's real accounts

## Design rules

1. Source accounts are read-only.
2. Workspace account is writable.
3. Multi-account applies to source accounts, not to unrestricted write targets.
4. Writes are routed only to the workspace account.
5. Outbound email is disabled by default even in the workspace account.
6. Commands should resolve by role and named source alias, not by arbitrary profile switching.

## Setup Walkthrough

Add your source accounts and your assistant workspace accounts:

```bash
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/setup.py add-account --alias personal --role source --description "Cuenta personal principal"
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/setup.py add-account --alias metabestec --role source --description "Inbox operativo de Metabestec"
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/setup.py add-account --alias assistant --role workspace --description "Sandbox del asistente"
```

Perform the OAuth flow for each:

```bash
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/setup.py auth-url --alias personal
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/setup.py auth-url --alias metabestec
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/setup.py auth-url --alias assistant
```

List the configured accounts and verify the status:

```bash
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/setup.py list-accounts
```

## Runtime Examples

Safely read from multiple inboxes (the tool guarantees this is read-only):

```bash
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/google_api.py source personal gmail search "label:inbox newer_than:2d"
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/google_api.py source metabestec gmail search "is:unread"
```

Write notes or output to the assistant account (source accounts are fully shielded from writes):

```bash
python /home/jq-hermes-01/hermes-workspace/agentic-ai/hermes/skills/google-workspace-assistant/scripts/google_api.py workspace docs create --title "Resumen diario" --body "..."
```

## Configuration

An internal `workspace_config.yaml` is deployed under `~/.hermes/google_workspace_assistant/` upon first run. It globally centralizes your accepted addresses and mandatory tags.

```yaml
allowed_email_destinations:
  - user1@example.com
  - user2@example.com
mandatory_labels:
  - JQASSISTANT
```

## Security Guarantees & Warnings

- **Source accounts are ALWAYS read-only**: Even if you attempt to use write scopes or construct API calls that write, the router explicitly forbids sending modifies to `source` accounts.
- **Strictly Scoped Email Destinies**: The `workspace` (assistant) account is strictly and exclusively authorized to **write/send emails ONLY to the addresses in `allowed_email_destinations`** (default: `user1@example.com`, `user2@example.com`). It cannot send or reply to any other address. Let the user know if an address isn't listed.
- **Explicit Consent Required**: The assistant **MUST ALWAYS ask for explicit permission before sending an email or draft**. Do not send any email unprompted. 
- **Mandatory Labels**: Any email sent or modified via the assistant `workspace` **MUST** include the `mandatory_labels` (default: `JQASSISTANT`). It helps differentiate AI-sent reports/notes from human interactions.
- **Forwarding is unnecessary**: You do not need to configure email forwarding, as this system securely reads the real inbox in-place using read-only API scopes.