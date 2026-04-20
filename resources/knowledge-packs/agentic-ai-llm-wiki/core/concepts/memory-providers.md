---
title: Memory Providers
created: 2026-04-18
updated: 2026-04-20
type: concept
tags: [hermes, agentic-ai, architecture, AI]
sources:
  - raw/articles/hermes-memory-behavior-research-2026.md
  - raw/articles/hermes-behavior-stack-dossier-2026-04-20.md
---

# Memory Providers

Hermes can layer one external memory backend on top of its built-in memory files. The external provider is additive: `MEMORY.md` and `USER.md` still exist and still matter.

## Activation model

- built-in memory stays active
- only one external provider can be active at a time
- selection comes from `memory.provider` in `~/.hermes/config.yaml`
- `hermes memory status` is the live check for what is actually active and available

## What an active provider changes

According to the local docs, an active provider may:

1. contribute a provider-specific system-prompt block
2. prefetch relevant context before a turn
3. sync conversation turns after responses
4. extract memories on session end when supported
5. mirror built-in memory writes
6. add provider-specific tools

## Runtime fencing of recalled context

The local `memory_manager.py` wraps prefetched provider context in a fenced `<memory-context>` block and marks it as recalled background rather than new user input.

That detail matters because provider recall is part of the behavior stack, but it is intentionally kept separate from the live conversation stream.

## Current local instance

The live instance checked on 2026-04-20 reports:

- built-in memory: always active
- active external provider: `hindsight`
- plugin status: installed and available

The same live status output reports these installed plugins:

- byterover
- hindsight
- holographic
- honcho
- mem0
- openviking
- retaindb
- supermemory

## Complementary memory surfaces

These three surfaces serve different roles:

- built-in memory: short, curated facts that should always be in prompt
- external provider: broader background recall and provider-specific tooling
- session history: transcript recovery from `state.db`

They overlap, but they are not interchangeable.

## Related concepts

- [[memory-system]]
- [[built-in-memory-files]]
- [[session-history-and-recall]]
- [[hindsight]]
