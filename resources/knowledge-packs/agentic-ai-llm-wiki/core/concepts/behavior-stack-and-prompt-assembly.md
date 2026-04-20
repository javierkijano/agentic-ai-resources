---
title: Behavior Stack and Prompt Assembly
created: 2026-04-20
updated: 2026-04-20
type: concept
tags: [hermes, agentic-ai, architecture, AI]
sources:
  - raw/articles/hermes-behavior-stack-dossier-2026-04-20.md
  - raw/articles/hermes-memory-behavior-research-2026.md
---

# Behavior Stack and Prompt Assembly

Hermes' behavior stack is layered on purpose. Some inputs are frozen into the cached system prompt at session start, while other inputs are injected later at API-call time or recalled only when needed.

## Cached system-prompt order

The documented high-level order is:

1. `SOUL.md` identity
2. tool-aware behavior guidance
3. optional Honcho static block
4. optional system-message override
5. frozen `MEMORY.md` snapshot
6. frozen `USER.md` snapshot
7. skills index
8. startup context files
9. timestamp / session metadata
10. platform hint

This order is deliberate. The docs frame it as a cache-stability and memory-correctness decision, not an arbitrary formatting choice.

## Cached layers vs. runtime overlays

### Cached at session start

- identity from `SOUL.md`
- frozen built-in memory and user profile
- skills index
- startup project context
- timestamp and platform hint

### Added later at API-call time

- `ephemeral_system_prompt`
- prefill messages
- gateway-derived session overlays
- later-turn provider recall

### Loaded only when needed

- full skill bodies through `skill_view`
- transcript recall through `session_search`
- deeper repo context through file tools and subdirectory discovery

## Why the split exists

The docs and code point to four practical goals:

- preserve provider-side prompt caching
- keep memory semantics predictable
- avoid mutating the stable prefix unnecessarily
- let Hermes add fresh recall without pretending it was part of the original prompt

## Context loading has two phases

### Phase 1: startup project context

Hermes chooses one startup project-context type using first-match priority:

1. `.hermes.md` / `HERMES.md`
2. `AGENTS.md`
3. `CLAUDE.md`
4. `.cursorrules` / `.cursor/rules/*.mdc`

### Phase 2: progressive subdirectory discovery

As the agent touches new paths, `SubdirectoryHintTracker` can append local `AGENTS.md`, `CLAUDE.md`, or `.cursorrules` content to tool results. That discovery path is deliberately separate from the cached prompt.

## Identity is not project context

`SOUL.md` occupies the identity slot. It is loaded from `HERMES_HOME`, security-scanned, and not duplicated again inside the context-files block.

That separation keeps persona-level behavior distinct from repo-level instructions.

## Related concepts

- [[memory-system]]
- [[built-in-memory-files]]
- [[personality-and-context-files]]
- [[session-history-and-recall]]
- [[skills-system]]
