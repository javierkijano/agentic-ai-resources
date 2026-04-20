---
title: Built-in Memory Files
created: 2026-04-20
updated: 2026-04-20
type: concept
tags: [hermes, agentic-ai, architecture, AI]
sources:
  - raw/articles/hermes-behavior-stack-dossier-2026-04-20.md
  - raw/articles/hermes-memory-behavior-research-2026.md
---

# Built-in Memory Files

Hermes' built-in memory is a bounded two-file store under `~/.hermes/memories/`. It is separate from session history, separate from project context, and separate from external memory providers.

## The two files

| File | Purpose | Config key | Default limit |
| --- | --- | --- | --- |
| `MEMORY.md` | durable operational notes for the agent | `memory.memory_char_limit` | 2,200 chars |
| `USER.md` | durable user profile and preference notes | `memory.user_char_limit` | 1,375 chars |

## Snapshot behavior

At session start, Hermes reads both files from disk and renders them into the system prompt as a frozen snapshot.

Important consequences:

- writes persist to disk immediately
- the already-built prompt snapshot does not change mid-session
- a later session sees the updated snapshot
- the frozen pattern helps preserve prompt-cache stability

## Entry model

- entries are separated by `§`
- entries can be multiline
- duplicate entries are deduplicated on load
- the files are character-bounded rather than token-bounded

## Mutation model

The documented public actions are:

- `add`
- `replace`
- `remove`

`replace` and `remove` use short unique substring matching through `old_text` rather than numeric IDs.

## What belongs in each file

### `MEMORY.md`

Use it for:

- environment facts
- repo or workflow conventions that matter across sessions
- tool quirks and workarounds
- durable lessons learned

### `USER.md`

Use it for:

- communication preferences
- stable expectations
- identity details that keep recurring
- recurring corrections about how the agent should work with the user

## Safety and scope

Because both files are injected into the prompt, Hermes scans memory content for prompt-injection and exfiltration patterns before accepting it.

The docs also explicitly warn against using built-in memory for:

- temporary task state
- completed-work logs
- large raw data dumps
- repo instructions that belong in context files instead

## Related concepts

- [[memory-system]]
- [[session-history-and-recall]]
- [[personality-and-context-files]]
- [[memory-providers]]
