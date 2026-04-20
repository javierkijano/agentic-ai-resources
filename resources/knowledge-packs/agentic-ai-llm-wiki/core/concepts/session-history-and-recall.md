---
title: Session History and Recall
created: 2026-04-20
updated: 2026-04-20
type: concept
tags: [hermes, agentic-ai, architecture, data]
sources:
  - raw/articles/hermes-behavior-stack-dossier-2026-04-20.md
---

# Session History and Recall

Hermes remembers more than the two built-in memory files. It also stores full conversation history and uses on-demand transcript search to recover older context when needed.

## Primary storage

The main transcript database is:

- `~/.hermes/state.db`

The documented core tables are:

- `sessions`
- `messages`
- `messages_fts`
- `schema_version`

The same docs and source code describe:

- SQLite in WAL mode
- FTS5 full-text search across message content
- session lineage via `parent_session_id`
- source tagging such as `cli`, `telegram`, and `discord`

## How `session_search` works

The documented flow is:

1. run FTS5 search across stored messages
2. group matches by session and keep the top sessions
3. load the surrounding transcript context
4. summarize the most relevant sessions with a fast model
5. return compact per-session summaries with metadata

This is why session recall is larger and slower than built-in memory, but also much broader.

## Storage beside the database

Gateway transcript artifacts also live under:

- `~/.hermes/sessions/`

The docs describe these as JSONL transcripts plus a sessions index used by gateway session management.

## What session history is for

Use session history for:

- recovering prior conversations
- recalling task history that should not live in built-in memory
- reconstructing context that would be too large or too ephemeral for `MEMORY.md`

## What session history is not

- it is not the same as built-in memory
- it is not always injected into the prompt
- it is not a substitute for stable user preferences or identity guidance

Built-in memory is for always-important facts. Session history is for searchable transcript recall.

## Related concepts

- [[memory-system]]
- [[built-in-memory-files]]
- [[behavior-stack-and-prompt-assembly]]
- [[memory-providers]]
