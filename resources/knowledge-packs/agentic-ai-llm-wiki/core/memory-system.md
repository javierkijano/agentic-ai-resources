---
title: Hermes Memory System
created: 2026-04-18
updated: 2026-04-20
type: concept
tags: [hermes, agentic-ai, architecture, AI]
sources:
  - raw/articles/hermes-memory-behavior-research-2026.md
  - raw/articles/hermes-behavior-stack-dossier-2026-04-20.md
---

# Hermes Memory System

Hermes memory is a layered behavior stack, not a single store. The runtime combines identity, bounded built-in memory, repo-local instructions, skills, transcript recall, optional external providers, and a controlled learning loop.

## Layers at a glance

| Layer | Primary artifact | Load timing | Persistence | Primary role |
| --- | --- | --- | --- | --- |
| Identity | `SOUL.md` | session start | `HERMES_HOME` | durable voice and stance |
| Built-in memory | `MEMORY.md` | session start, frozen | `~/.hermes/memories/` | operational facts and lessons |
| User profile | `USER.md` | session start, frozen | `~/.hermes/memories/` | stable user preferences |
| Skills | skills index + on-demand skill bodies | index at session start, bodies on demand | `~/.hermes/skills/` + external dirs | procedural memory |
| Project context | `.hermes.md`, `AGENTS.md`, `CLAUDE.md`, `.cursorrules` | startup + progressive discovery | workspace files | repo-local rules |
| Session history | `state.db` + gateway transcripts | on demand | SQLite + JSONL | transcript recall |
| External provider | `memory.provider` plugin | pre-turn, post-turn, and prompt hooks | provider backend | additive recall and provider tools |
| Learning loop | nudges + skill creation + provider sync | across sessions | memories, skills, provider data | controlled self-improvement |

## Three memory surfaces

### 1. Always-in-prompt state

This includes the identity slot, frozen built-in memory, frozen user profile, the skills index, and startup context files.

### 2. On-demand recall

This includes `session_search`, `skill_view`, file reads, and other retrieval paths that are only used when the current task needs them.

### 3. Runtime overlays

This includes provider-prefetched context, provider prompt blocks, and progressive subdirectory hints appended to tool results.

## Why the distinction matters

- built-in memory is small and curated
- session history is broad and searchable but not always loaded
- skills store procedures, not facts
- project context stores local rules, not persona
- external providers add recall and tooling but do not replace the built-in files

## Hub pages

- [[behavior-stack-and-prompt-assembly]]
- [[built-in-memory-files]]
- [[personality-and-context-files]]
- [[session-history-and-recall]]
- [[skills-system]]
- [[memory-providers]]
- [[learning-loop]]
