---
title: Personality and Context Files
created: 2026-04-18
updated: 2026-04-20
type: concept
tags: [hermes, agentic-ai, architecture, AI]
sources:
  - raw/articles/hermes-memory-behavior-research-2026.md
  - raw/articles/hermes-behavior-stack-dossier-2026-04-20.md
---

# Personality and Context Files

Hermes separates durable identity from repo-local instructions. The code and docs treat those as different layers with different discovery rules.

## `SOUL.md`: the identity layer

`SOUL.md` is the primary identity slot in the system prompt.

Important properties:

- it lives at `$HERMES_HOME/SOUL.md`
- Hermes does not search the working directory for it
- it is security-scanned before injection
- it is truncated before injection when too large
- it replaces the hardcoded default identity when present
- it is not duplicated inside the project-context block

If `SOUL.md` is absent, empty, unreadable, or skipped, Hermes falls back to `DEFAULT_AGENT_IDENTITY`.

## Startup project context

Startup project context uses first-match priority:

1. `.hermes.md` / `HERMES.md`
2. `AGENTS.md`
3. `CLAUDE.md`
4. `.cursorrules` / `.cursor/rules/*.mdc`

More precise details from the local codebase:

- `.hermes.md` is searched from the current directory up to the git root
- `.hermes.md` YAML frontmatter is stripped before prompt injection
- startup context files are security-scanned before use
- large files are truncated before prompt injection

## Progressive subdirectory context

Repo-local behavior can become more specific later in the session.

`SubdirectoryHintTracker` watches tool-call paths and shell commands, discovers local `AGENTS.md`, `CLAUDE.md`, or `.cursorrules` files in newly visited directories, and appends that context to tool results.

That discovery path has its own constraints:

- it walks up to five ancestor directories
- it loads the first supported context file per directory
- it caps each discovered hint at 8,000 characters
- it avoids mutating the cached system prompt

## What belongs where

- `SOUL.md` — identity, tone, and default stance
- project context files — repo instructions, constraints, commands, and conventions
- built-in memory — durable facts and preferences
- skills — reusable procedures

This separation is the main reason Hermes can keep a stable persona while still following workspace-specific rules.

## Related concepts

- [[memory-system]]
- [[behavior-stack-and-prompt-assembly]]
- [[built-in-memory-files]]
- [[skills-system]]
